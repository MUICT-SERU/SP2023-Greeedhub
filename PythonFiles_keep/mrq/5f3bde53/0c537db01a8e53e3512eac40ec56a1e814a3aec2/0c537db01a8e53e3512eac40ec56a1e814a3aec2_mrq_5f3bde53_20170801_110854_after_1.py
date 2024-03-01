from .context import get_current_config, connections, log, run_task
import time
import datetime
import gevent
import argparse
import shlex
import random
import math
import re
import traceback
from collections import defaultdict
from bson import ObjectId
from redis.lock import LuaLock
from .processes import Process, ProcessPool
from .config import add_parser_args
from .utils import MovingETA
from .queue import Queue


class Agent(Process):
    """ MRQ Agent manages its local worker pool and takes turns in orchestrating the others in its group. """

    def __init__(self, worker_group=None):
        self.greenlets = {}
        self.id = ObjectId()
        self.worker_group = worker_group or get_current_config()["worker_group"]
        self.pool = ProcessPool(extra_env={
            "MRQ_AGENT_ID": str(self.id),
            "MRQ_WORKER_GROUP": self.worker_group
        })
        self.config = get_current_config()
        self.status = "started"

        self.dateorchestrated = None

    def work(self):

        self.install_signal_handlers()
        self.datestarted = datetime.datetime.utcnow()

        self.pool.start()
        self.manage()

        self.greenlets["orchestrate"] = gevent.spawn(self.greenlet_orchestrate)
        self.greenlets["orchestrate"].start()

        self.greenlets["manage"] = gevent.spawn(self.greenlet_manage)
        self.greenlets["manage"].start()

        # Disabled for now
        # self.greenlets["queuestats"] = gevent.spawn(self.greenlet_queuestats)
        # self.greenlets["queuestats"].start()

        try:
            self.pool.wait()
        finally:
            self.shutdown_now()
            self.status = "stop"
            self.manage()

    def shutdown_now(self):
        self.pool.terminate()

        for g in self.greenlets.values():
            g.kill()

    def shutdown_graceful(self):
        self.pool.stop(timeout=None)

    def greenlet_manage(self):
        """ This greenlet always runs in background to update current status
            in MongoDB every N seconds.
         """

        while True:
            try:
                self.manage()
            except Exception as e:  # pylint: disable=broad-except
                log.error("When reporting: %s" % e)
            finally:
                time.sleep(self.config["report_interval"])

    def manage(self):

        report = self.get_agent_report()

        try:
            db = connections.mongodb_jobs.mrq_agents.find_and_modify({
                "_id": ObjectId(self.id)
            }, {"$set": report}, upsert=True)
            if not db:
                return
        except Exception as e:  # pylint: disable=broad-except
            log.debug("Agent report failed: %s" % e)
            return

        # If the desired_workers was changed by an orchestrator, apply the changes locally
        if self.status != "stop" and sorted(db.get("desired_workers", [])) != sorted(self.pool.desired_commands):

            group = self.fetch_worker_group_definition()
            process_termination_timeout = float(group.get("process_termination_timeout") or 60)
            self.pool.set_commands(db.get("desired_workers", []), timeout=process_termination_timeout)

    def get_agent_report(self):
        report = {
            "current_workers": [p["command"] for p in self.pool.processes],
            "total_cpu": get_current_config()["total_cpu"],
            "total_memory": get_current_config()["total_memory"],
            "worker_group": self.worker_group,
            "status": self.status,
            "dateorchestrated": self.dateorchestrated,
            "datestarted": self.datestarted,
            "datereported": datetime.datetime.utcnow(),
            "dateexpires": datetime.datetime.utcnow() + datetime.timedelta(seconds=(self.config["report_interval"] * 3) + 5)
        }
        return report

    def greenlet_orchestrate(self):

        while True:

            orchestrated = False

            with LuaLock(connections.redis, self.redis_orchestrator_lock_key,
                         timeout=self.config["orchestrate_interval"] * 2 + 10, thread_local=False, blocking=False):

                try:
                    self.orchestrate()
                except Exception as e:
                    log.error("Orchestration error! %s" % e)
                    traceback.print_exc()

                orchestrated = True
                time.sleep(self.config["orchestrate_interval"])

            if not orchestrated:
                time.sleep(self.config["orchestrate_interval"])

    @property
    def redis_orchestrator_lock_key(self):
        """ Returns the global redis key used to ensure only one agent orchestrator runs at a time """
        return "%s:orchestratorlock:%s" % (get_current_config()["redis_prefix"], self.worker_group)

    def orchestrate(self):
        """ Executed periodically on one of the agents, to manage the desired workers of *all* the agents in its group """

        group = self.fetch_worker_group_definition()
        if not group:
            log.error("Worker group %s has no definition yet. Can't orchestrate!" % self.worker_group)
            return

        log.debug("Starting orchestration run for worker group %s" % self.worker_group)

        agents = self.fetch_worker_group_agents()

        desired_workers = self.get_desired_workers_for_group(group, agents)

        # Evaluate what workers are currently, rightfully there. They won't be touched.
        current_workers = defaultdict(int)
        for agent in agents:
            agent["free_memory"] = agent["total_memory"]
            agent["free_cpu"] = agent["total_cpu"]
            agent["new_desired_workers"] = []
            for worker in agent.get("desired_workers", []):
                if worker in desired_workers:
                    cpu = desired_workers[worker]["cpu"]
                    memory = desired_workers[worker]["memory"]

                    # If no more memory for currently existing workers: their requirements must have changed.
                    # We need to schedule it somewhere else
                    if cpu <= agent["free_cpu"] and memory <= agent["free_memory"]:
                        current_workers[worker] += 1
                        agent["free_cpu"] -= cpu
                        agent["free_memory"] -= memory
                        agent["new_desired_workers"].append(worker)

        # What changes need to be made in worker count
        deltas = {
            worker: (worker_info["desired_count"] - current_workers[worker])
            for worker, worker_info in desired_workers.items()
            if worker_info["desired_count"] != current_workers[worker]
        }

        # Remove workers from the most loaded machines (TODO improve)
        for worker, delta in deltas.items():
            if delta >= 0:
                continue

            for _ in range(delta, 0):
                found = False
                for agent in sorted(agents, key=lambda a: float(a["free_cpu"]) / a["total_cpu"]):
                    for i in range(len(agent["new_desired_workers"])):
                        if agent["new_desired_workers"][i] == worker:
                            agent["new_desired_workers"].pop(i)
                            agent["free_cpu"] += desired_workers[worker]["cpu"]
                            agent["free_memory"] += desired_workers[worker]["memory"]
                            found = True
                            break
                    if found:
                        break

                assert found

        needs_new_agents = False

        # Add new workers to the least loaded machines
        for worker, delta in deltas.items():
            if delta <= 0:
                continue

            cpu = desired_workers[worker]["cpu"]
            memory = desired_workers[worker]["memory"]

            for _ in range(delta):
                found = False
                for agent in sorted(agents, key=lambda a: float(a["free_cpu"]) / a["total_cpu"], reverse=True):
                    if cpu <= agent["free_cpu"] and memory <= agent["free_memory"]:
                        agent["new_desired_workers"].append(worker)
                        agent["free_cpu"] -= cpu
                        agent["free_memory"] -= memory
                        found = True
                        break

                if not found:
                    log.debug("Worker orchestration: no agent had enough CPU & memory (%s & %s) to schedule a new worker" % (cpu, memory))
                    needs_new_agents = True
                    break

        # Worker diversity enforcement: if we are under-scaled, make sure that at least one worker
        # of each profile is launched. if not, make space forcefully on other workers.
        if needs_new_agents:

            all_profiles = defaultdict(int)
            for agent in agents:
                for w in agent["new_desired_workers"]:
                    all_profiles[w] += 1

            removable = sorted([list(x) for x in all_profiles.items() if x[1] > 1], key=lambda item: item[1], reverse=True)

            for profile in desired_workers:
                if desired_workers[profile]["desired_count"] == 0:
                    continue
                if profile not in all_profiles:
                    found = False
                    # This profile is not currently represented in the workers. Make some space for it.
                    for rem in removable:
                        for agent in agents:
                            for i in range(len(agent["new_desired_workers"])):
                                if agent["new_desired_workers"][i] == rem[0] and rem[1] > 1:
                                    agent["new_desired_workers"][i] = None
                                    agent["free_cpu"] += desired_workers[rem[0]]["cpu"]
                                    agent["free_memory"] += desired_workers[rem[0]]["memory"]
                                    rem[1] -= 1
                                if desired_workers[profile]["cpu"] <= agent["free_cpu"] and desired_workers[profile]["memory"] <= agent["free_memory"]:
                                    log.debug("Orchestration: enforcing worker diversity with %s => %s" % (rem[0], profile))
                                    agent["new_desired_workers"].append(profile)
                                    agent["free_cpu"] -= desired_workers[profile]["cpu"]
                                    agent["free_memory"] -= desired_workers[profile]["memory"]
                                    found = True
                                    break

                            agent["new_desired_workers"] = [x for x in agent["new_desired_workers"] if x is not None]
                            if found:
                                break

                        if found:
                            break

                    if not found:
                        log.debug("Orchestration couldn't enforce worker diversity for profile '%s'" % profile)

        # User-provided autoscaling task
        if self.config.get("autoscaling_taskpath"):
            result = run_task(self.config["autoscaling_taskpath"], {
                "agents": agents,
                "needs_new_agents": needs_new_agents,
                "worker_group": self.worker_group
            })
            needs_new_agents = result["needs_new_agents"]
            agents = result["agents"]

        # Save the new values in the DB. They will be applied by each agent process.
        connections.mongodb_jobs.worker_groups.update_one({"_id": self.worker_group}, {"$set": {
            "needs_new_agents": needs_new_agents
        }})

        for agent in agents:
            if sorted(agent["new_desired_workers"]) != sorted(agent.get("desired_workers", [])):
                connections.mongodb_jobs.mrq_agents.update_one({"_id": agent["_id"]}, {"$set": {
                    "desired_workers": agent["new_desired_workers"],
                    "free_cpu": agent["free_cpu"],
                    "free_memory": agent["free_memory"]
                }})

        # Remember the date of the last successful orchestration (will be reported)
        self.dateorchestrated = datetime.datetime.utcnow()

        log.debug("Orchestration finished.")

    def get_desired_workers_for_group(self, group, agents):

        workers = {}

        def unpack(v):
            s = v.split(" ")
            return (int(s[0]), None if s[1] == "N" else float(s[1]), int(s[2]))

        # count_jobs, eta, last_time
        etas = {
            k: unpack(v)
            for k, v in connections.redis.hgetall(self.redis_queuestats_key).items()
        }

        # Compute average usage of each worker profile
        worker_reports = self.fetch_worker_group_reports(projection=[
            "_id", "config.worker_profile", "usage_avg", "status", "datestarted"  # , "process.cpu", "process.mem"
        ])

        worker_warmups_by_profile = defaultdict(int)
        worker_usages_by_profile = defaultdict(list)
        for rep in worker_reports:
            profileid = rep["config"].get("worker_profile")
            if not profileid or rep.get("status") not in ("wait", "spawn", "full"):
                continue
            # Don't take brand new workers into account yet.
            age = (datetime.datetime.utcnow() - rep["datestarted"]).total_seconds()
            if age < group.get("profiles", {}).get(profileid, {}).get("warmup", 60):
                worker_warmups_by_profile[profileid] += 1
                continue
            worker_usages_by_profile[profileid].append(rep["usage_avg"])

        worker_count_by_profile = defaultdict(int)
        for agent in agents:
            for command in agent.get("desired_workers", []):
                profile = re.search(r"^MRQ_WORKER_PROFILE=([^\s]+)", command)
                if profile:
                    profile = profile.group(1)
                    worker_count_by_profile[profile] += 1

        # Compute the desired count for each profile
        # This is the real "autoscaling" part.
        for profileid, profile in group.get("profiles", {}).items():

            cfg = self.get_config_for_profile(profile)
            eta_queues = [q for q in cfg.queues if (q in etas and etas[q][1] is not None)]
            worker_usage = sum(worker_usages_by_profile.get(profileid, []))
            report_count = len(worker_usages_by_profile.get(profileid, []))
            current_desired_count = worker_count_by_profile[profileid]
            total_greenlets = (cfg.greenlets or 1) * (cfg.processes or 1)
            warmups = worker_warmups_by_profile[profileid]

            # By default, try not to change count
            desired_count = current_desired_count

            # If the queue is doing OK, are all instances necessary?
            if warmups == 0 and report_count > 0:
                desired_count = math.ceil(worker_usage * (float(current_desired_count) / report_count))

            if len(eta_queues) > 0:

                total_jobs = sum(etas[q][0] for q in eta_queues)
                max_eta = max(etas[q][1] for q in eta_queues)

                max_allowed_eta = profile.get("max_eta", 3600)

                # Queue is taking too long, try to add an instance.
                if max_eta > max_allowed_eta or any(etas[q][1] < 0 for q in eta_queues):

                    # Don't add a worker if the absolute number of remaining jobs is less than the number of
                    # greenlets. (They may become available right now)
                    # Also don't add a worker if the reported, warmed-up worker count is not yet the desired one.
                    if total_jobs > total_greenlets and report_count == current_desired_count:
                        desired_count = current_desired_count + 1

            final_count = min(max(desired_count, profile.get("min_count", 0)), profile.get("max_count", 100))

            if final_count != current_desired_count:
                log.debug("Autoscaling: Changing worker profile %s count from %s to %s" % (
                    profileid, current_desired_count, final_count
                ))

            workers[profile["command"]] = {
                "desired_count": final_count,
                "memory": profile["memory"],
                "cpu": profile["cpu"]
            }

        return workers

    def get_config_for_profile(self, profile):
        parser = argparse.ArgumentParser()
        add_parser_args(parser, "worker")
        parts = shlex.split(profile["command"])
        if "mrq-worker" in parts:
            parts = parts[parts.index("mrq-worker") + 1:]
        return parser.parse_args(parts)

    def greenlet_queuestats(self):

        interval = min(self.config["orchestrate_interval"], 1 * 60)
        lock_timeout = 5 * 60 + (interval * 2)

        while True:
            lock = LuaLock(connections.redis, self.redis_queuestats_lock_key,
                           timeout=lock_timeout, thread_local=False, blocking=False)
            with lock:
                lock_expires = time.time() + lock_timeout
                self.queue_etas = defaultdict(lambda: MovingETA(5))

                while True:
                    self.queuestats()

                    # Because queue stats can be expensive, we try to keep the lock on the same agent
                    lock_extend = (time.time() + lock_timeout) - lock_expires
                    lock_expires += lock_extend
                    lock.extend(lock_extend)

                    time.sleep(interval)

            time.sleep(interval)

    @property
    def redis_queuestats_lock_key(self):
        """ Returns the global redis key used to ensure only one agent orchestrator runs at a time """
        return "%s:queuestatslock" % (get_current_config()["redis_prefix"])

    @property
    def redis_queuestats_key(self):
        """ Returns the global HSET redis key used to store queue stats """
        return "%s:queuestats" % (get_current_config()["redis_prefix"])

    def queuestats(self):
        """ Compute ETAs for every known queue & subqueue """

        start_time = time.time()
        log.debug("Starting queue stats...")

        # Fetch all known queues
        queues = list(Queue.instanciate_queues(Queue.known_queues.keys()))

        new_queues = {queue.id for queue in queues}
        old_queues = set(self.queue_etas.keys())

        for deleted_queue in old_queues.difference(new_queues):
            self.queue_etas.pop(deleted_queue)

        t = time.time()
        stats = {}

        for queue in queues:
            cnt = queue.count_jobs_to_dequeue()
            eta = self.queue_etas[queue.id].next(cnt, t=t)

            # Number of jobs to dequeue, ETA, Time of stats
            stats[queue.id] = "%d %s %d" % (cnt, eta if eta is not None else "N", int(t))

        with connections.redis.pipeline(transaction=True) as pipe:
            if random.randint(0, 100) == 0 or len(stats) == 0:
                pipe.delete(self.redis_queuestats_key)
            if len(stats) > 0:
                pipe.hmset(self.redis_queuestats_key, stats)
            pipe.execute()

        log.debug("... done queue stats in %0.4fs" % (time.time() - start_time))

    def fetch_worker_group_agents(self):
        return list(connections.mongodb_jobs.mrq_agents.find({"worker_group": self.worker_group, "status": "started"}))

    def fetch_worker_group_reports(self, projection=None):
        return list(connections.mongodb_jobs.mrq_workers.find({
            "config.worker_group": self.worker_group
        }, projection=projection))

    def fetch_worker_group_definition(self):
        definition = connections.mongodb_jobs.mrq_workergroups.find_one({"_id": self.worker_group})

        # Prepend all commands by their worker profile.
        for profileid, profile in (definition or {}).get("profiles", {}).items():
            profile["command"] = "MRQ_WORKER_PROFILE=%s %s" % (profileid, profile["command"])

        return definition
