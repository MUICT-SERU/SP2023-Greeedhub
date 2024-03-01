import datetime

import cassiopeia.riotapi
import cassiopeia.type.dto.common
import cassiopeia.type.core.common

class Match(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "Match {id}".format(id=self.id)

    def __iter__(self):
        return iter(self.participants)

    def __len__(self):
        return len(self.participants)

    def __getitem__(self, index):
        return self.participants[index]

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    @property
    def map(self):
        return cassiopeia.type.core.common.Map(self.data.mapId) if self.data.mapId else None

    @cassiopeia.type.core.common.lazyproperty
    def creation(self):
        return datetime.datetime.utcfromtimestamp(self.data.matchCreation) if self.data.matchCreation else None

    @cassiopeia.type.core.common.lazyproperty
    def duration(self):
        return datetime.timedelta(seconds=self.data.matchDuration) if self.data.matchDuration else None

    @property
    def id(self):
        return self.data.matchId

    @property
    def mode(self):
        return cassiopeia.type.core.common.GameMode(self.data.matchMode) if self.data.matchMode else None

    @property
    def type(self):
        return cassiopeia.type.core.common.GameType(self.data.matchType) if self.data.matchType else None

    @property
    def version(self):
        return self.data.matchVersion

    @cassiopeia.type.core.common.lazyproperty
    def participants(self):
        participants = []
        for i in range(len(self.data.participants)):
            p = CombinedParticipant(self.data.participants[i], self.data.participantIdentities[i])
            participants.append(Participant(p))
        return sorted(participants, key=lambda p: p.id)

    @property
    def platform(self):
        return cassiopeia.type.core.common.Platform(self.data.platformId) if self.data.platformId else None

    @property
    def queue(self):
        return cassiopeia.type.core.common.Queue(self.data.queueType) if self.data.queueType else None

    @property
    def region(self):
        return cassiopeia.type.core.common.Region(self.data.region) if self.data.region else None

    @property
    def season(self):
        return cassiopeia.type.core.common.Season(self.data.season) if self.data.season else None

    @cassiopeia.type.core.common.lazyproperty
    def blue_team(self):
        for team in self.data.teams:
            if(team.teamId == cassiopeia.type.core.common.Side.blue.value):
                return Team(team)
        return None

    @cassiopeia.type.core.common.lazyproperty
    def red_team(self):
        for team in self.data.teams:
            if(team.teamId == cassiopeia.type.core.common.Side.red.value):
                return Team(team)
        return None

    @cassiopeia.type.core.common.lazyproperty
    def timeline(self):
        return Timeline(self.data.timeline, self.participants) if self.data.timeline else None


class CombinedParticipant(cassiopeia.type.dto.common.CassiopeiaDto):
    def __init__(self, participant, identity):
        self.participant = participant
        self.identity = identity


class Participant(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "{player} ({champ})".format(player=self.summoner, champ=self.champion)

    @cassiopeia.type.core.common.lazyproperty
    def champion(self):
        return cassiopeia.riotapi.get_champion_by_id(self.data.participant.championId) if self.data.championId else None

    @property
    def previous_season_tier(self):
        return cassiopeia.type.core.common.Tier(self.data.participant.highestAchievedSeasonTier) if self.data.participant.highestAchievedSeasonTier else None

    @cassiopeia.type.core.common.lazyproperty
    def masteries(self):
        masteries = []
        ranks = []
        for mastery in self.data.participant.masteries:
            masteries.append(mastery.masteryId)
            ranks.append(mastery.rank)
        return list(zip(cassiopeia.riotapi.get_masteries(masteries), ranks))

    @property
    def id(self):
        return self.data.participant.participantId

    @cassiopeia.type.core.common.lazyproperty
    def runes(self):
        runes = [rune.runeId for rune in self.data.participant.runes for _ in range(rune.rank)]
        return cassiopeia.riotapi.get_runes(runes)

    @cassiopeia.type.core.common.lazyproperty
    def summoner_spell_d(self):
        cassiopeia.riotapi.get_summoner_spell(self.data.participant.spell1Id) if self.data.spell1Id else None

    @cassiopeia.type.core.common.lazyproperty
    def summoner_spell_f(self):
        cassiopeia.riotapi.get_summoner_spell(self.data.participant.spell2Id) if self.data.spell2Id else None

    @cassiopeia.type.core.common.lazyproperty
    def stats(self):
        return ParticipantStats(self.data.participant.stats) if self.data.participant.stats else None

    @property
    def side(self):
        return cassiopeia.type.core.common.Side(self.data.participant.teamId) if self.data.participant.teamId else None

    @cassiopeia.type.core.common.lazyproperty
    def timeline(self):
        return ParticipantTimeline(self.data.participant.timeline) if self.data.participant.timeline else None

    @property
    def match_history_uri(self):
        return self.data.identity.player.matchHistoryUri

    @cassiopeia.type.core.common.lazyproperty
    def summoner(self):
        return cassiopeia.riotapi.get_summoner_by_id(self.data.identity.player.summonerId) if self.data.identity.player and self.data.identity.player.summonerId else None


class Team(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "{side} team".format(side=self.side)

    @cassiopeia.type.core.common.lazyproperty
    def bans(self):
        return [Ban(ban) for ban in self.data.bans]

    @property
    def baron_kills(self):
        return self.data.baronKills

    @property
    def victory_score(self):
        return self.data.dominionVictoryScore

    @property
    def dragon_kills(self):
        return self.data.dragonKills

    @property
    def first_baron(self):
        return self.data.firstBaron

    @property
    def first_blood(self):
        return self.data.firstBlood

    @property
    def first_dragon(self):
        return self.data.firstDragon

    @property
    def first_inhibitor(self):
        return self.data.firstInhibitor

    @property
    def first_turret(self):
        return self.data.firstTower

    @property
    def inhibitor_kills(self):
        return self.data.inhibitorKills

    @property
    def side(self):
        return cassiopeia.type.core.common.Side(self.data.participant.teamId) if self.data.teamId else None

    @property
    def turret_kills(self):
        return self.data.towerKills

    @property
    def spider_kills(self):
        return self.data.vilemawKills

    @property
    def winner(self):
        return self.data.winner


class Timeline(cassiopeia.type.core.common.CassiopeiaObject):
    def __init__(self, data, participants):
        super().__init__(data)
        self.__participants = participants

    def __str__(self):
        return "Timeline"

    def __iter__(self):
        return iter(self.frames)

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, index):
        return self.frames[index]

    @cassiopeia.type.core.common.lazyproperty
    def frame_interval(self):
        return datetime.timedelta(milliseconds=self.data.frameInterval)

    @cassiopeia.type.core.common.lazyproperty
    def frames(self):
        participants = {participant.id: participant for participant in self.__participants}
        value = [Frame(frame, participants) for frame in self.data.frames]
        del self.__participants
        return value


class ParticipantStats(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "Participant Stats"

    # int # Number of assists
    @property
    def assists(self):
        return self.data.assists

    # int # Champion level achieved
    @property
    def champion_level(self):
        return self.data.champLevel

    # int # If game was a dominion game, player's combat score, otherwise 0
    @property
    def combat_player_score(self):
        return self.data.combatPlayerScore

    # int # Number of deaths
    @property
    def deaths(self):
        return self.data.deaths

    # int # Number of double kills
    @property
    def double_kills(self):
        return self.data.doubleKills

    # bool # Flag indicating if participant got an assist on first blood
    @property
    def first_blood_assist(self):
        return self.data.firstBloodAssist

    # bool # Flag indicating if participant got first blood
    @property
    def first_blood(self):
        return self.data.firstBloodKill

    # bool # Flag indicating if participant got an assist on the first inhibitor
    @property
    def first_inhibitor_assist(self):
        return self.data.firstInhibitorAssist

    # bool # Flag indicating if participant destroyed the first inhibitor
    @property
    def first_inhibitor(self):
        return self.data.firstInhibitorKill

    # bool # Flag indicating if participant got an assist on the first tower
    @property
    def first_turret_assist(self):
        return self.data.firstTowerAssist

    # bool # Flag indicating if participant destroyed the first tower
    @property
    def first_turret(self):
        return self.data.firstTowerKill

    # int # Gold earned
    @property
    def gold_earned(self):
        return self.data.goldEarned

    # int # Gold spent
    @property
    def gold_spent(self):
        return self.data.goldSpent

    # int # Number of inhibitor kills
    @property
    def inhibitor_kills(self):
        return self.data.inhibitorKills

    # Item # First item
    @cassiopeia.type.core.common.lazyproperty
    def item0(self):
        return cassiopeia.riotapi.get_item(self.data.item0) if self.data.item0 else None

    # Item # Second item
    @cassiopeia.type.core.common.lazyproperty
    def item1(self):
        return cassiopeia.riotapi.get_item(self.data.item1) if self.data.item1 else None

    # Item # Third item
    @cassiopeia.type.core.common.lazyproperty
    def item2(self):
        return cassiopeia.riotapi.get_item(self.data.item2) if self.data.item2 else None

    # Item # Fourth item
    @cassiopeia.type.core.common.lazyproperty
    def item3(self):
        return cassiopeia.riotapi.get_item(self.data.item3) if self.data.item3 else None

    # Item # Fifth item
    @cassiopeia.type.core.common.lazyproperty
    def item4(self):
        return cassiopeia.riotapi.get_item(self.data.item4) if self.data.item4 else None

    # Item # Sixth item
    @cassiopeia.type.core.common.lazyproperty
    def item5(self):
        return cassiopeia.riotapi.get_item(self.data.item5) if self.data.item5 else None

    # Item # Seventh item
    @cassiopeia.type.core.common.lazyproperty
    def item6(self):
        return cassiopeia.riotapi.get_item(self.data.item6) if self.data.item6 else None

    # int # Number of killing sprees
    @property
    def killing_sprees(self):
        return self.data.killingSprees

    # int # Number of kills
    @property
    def kills(self):
        return self.data.kills

    # int # Largest critical strike
    @property
    def largest_critical_strike(self):
        return self.data.largestCriticalStrike

    # int # Largest killing spree
    @property
    def largest_killing_spree(self):
        return self.data.largestKillingSpree

    # int # Largest multi kill
    @property
    def largest_multi_kill(self):
        return self.data.largestMultiKill

    # int # Magical damage dealt
    @property
    def magic_damage_dealt(self):
        return self.data.magicDamageDealt

    # int # Magical damage dealt to champions
    @property
    def magic_damage_dealt_to_champions(self):
        return self.data.magicDamageDealtToChampions

    # int # Magic damage taken
    @property
    def magic_damage_taken(self):
        return self.data.magicDamageTaken

    # int # Minions killed
    @property
    def minions_killed(self):
        return self.data.minionsKilled

    # int # Neutral minions killed
    @property
    def neutral_minions_killed(self):
        return self.data.neutralMinionsKilled

    # int # Neutral jungle minions killed in the enemy team's jungle
    @property
    def neutral_minions_killed_enemy_jungle(self):
        return self.data.neutralMinionsKilledEnemyJungle

    # int # Neutral jungle minions killed in your team's jungle
    @property
    def neutral_minions_killed_team_jungle(self):
        return self.data.neutralMinionsKilledTeamJungle

    # int # If game was a dominion game, number of node captures
    @property
    def nodes_captured(self):
        return self.data.nodeCapture

    # int # If game was a dominion game, number of node capture assists
    @property
    def node_capture_assists(self):
        return self.data.nodeCaptureAssist

    # int # If game was a dominion game, number of node neutralizations
    @property
    def node_neutralizations(self):
        return self.data.nodeNeutralize

    # int # If game was a dominion game, number of node neutralization assists
    @property
    def node_neutralization_assists(self):
        return self.data.nodeNeutralizeAssist

    # int # If game was a dominion game, player's objectives score, otherwise 0
    @property
    def objective_player_score(self):
        return self.data.objectivePlayerScore

    # int # Number of penta kills
    @property
    def penta_kills(self):
        return self.data.pentaKills

    # int # Physical damage dealt
    @property
    def physical_damage_dealt(self):
        return self.data.physicalDamageDealt

    # int # Physical damage dealt to champions
    @property
    def physical_damage_dealt_to_champions(self):
        return self.data.physicalDamageDealtToChampions

    # int # Physical damage taken
    @property
    def physical_damage_taken(self):
        return self.data.physicalDamageTaken

    # int # Number of quadra kills
    @property
    def quadra_kills(self):
        return self.data.quadraKills

    # int # Sight wards purchased
    @property
    def sight_wards_bought(self):
        return self.data.sightWardsBoughtInGame

    # int # If game was a dominion game, number of completed team objectives (i.e., quests)
    @property
    def team_objectives(self):
        return self.data.teamObjective

    # int # Total damage dealt
    @property
    def damage_dealt(self):
        return self.data.totalDamageDealt

    # int # Total damage dealt to champions
    @property
    def damage_dealt_to_champions(self):
        return self.data.totalDamageDealtToChampions

    # int # Total damage taken
    @property
    def damage_taken(self):
        return self.data.totalDamageTaken

    # int # Total heal amount
    @property
    def healing_done(self):
        return self.data.totalHeal

    # int # If game was a dominion game, player's total score, otherwise 0
    @property
    def player_score(self):
        return self.data.totalPlayerScore

    # int # If game was a dominion game, team rank of the player's total score (e.g., 1-5)
    @property
    def player_score_rank(self):
        return self.data.totalScoreRank

    # int # Total dealt crowd control time
    @property
    def time_crowd_control_dealt(self):
        return self.data.totalTimeCrowdControlDealt

    # int # Total units healed
    @property
    def units_healed(self):
        return self.data.totalUnitsHealed

    # int # Number of tower kills
    @property
    def turret_kills(self):
        return self.data.towerKills

    # int # Number of triple kills
    @property
    def triple_kills(self):
        return self.data.tripleKills

    # int # True damage dealt
    @property
    def true_damage_dealt(self):
        return self.data.trueDamageDealt

    # int # True damage dealt to champions
    @property
    def true_damage_dealt_to_champions(self):
        return self.data.trueDamageDealtToChampions

    # int # True damage taken
    @property
    def true_damage_taken(self):
        return self.data.trueDamageTaken

    # int # Number of unreal kills
    @property
    def unreal_kills(self):
        return self.data.unrealKills

    # int # Vision wards purchased
    @property
    def vision_wards_bought(self):
        return self.data.visionWardsBoughtInGame

    # int # Number of wards killed
    @property
    def wards_killed(self):
        return self.data.wardsKilled

    # int # Number of wards placed
    @property
    def wards_placed(self):
        return self.data.wardsPlaced

    # bool # Flag indicating whether or not the participant won
    @property
    def winner(self):
        return self.data.winner


class ParticipantTimeline(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "Participant Timeline"

    # ParticipantTimelineData # Ancient golem assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def ancient_golem_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.ancientGolemAssistsPerMinCounts) if self.data.ancientGolemAssistsPerMinCounts else None

    # ParticipantTimelineData # Ancient golem kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def ancient_golem_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.ancientGolemKillsPerMinCounts) if self.data.ancientGolemKillsPerMinCounts else None

    # ParticipantTimelineData # Assisted lane deaths per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def assisted_lane_deaths_per_min_deltas(self):
        return ParticipantTimelineData(self.data.assistedLaneDeathsPerMinDeltas) if self.data.assistedLaneDeathsPerMinDeltas else None

    # ParticipantTimelineData # Assisted lane kills per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def assisted_lane_kills_per_min_deltas(self):
        return ParticipantTimelineData(self.data.assistedLaneKillsPerMinDeltas) if self.data.assistedLaneKillsPerMinDeltas else None

    # ParticipantTimelineData # Baron assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def baron_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.baronAssistsPerMinCounts) if self.data.baronAssistsPerMinCounts else None

    # ParticipantTimelineData # Baron kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def baron_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.baronKillsPerMinCounts) if self.data.baronKillsPerMinCounts else None

    # ParticipantTimelineData # Creeps per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def creeps_per_min_deltas(self):
        return ParticipantTimelineData(self.data.creepsPerMinDeltas) if self.data.creepsPerMinDeltas else None

    # ParticipantTimelineData # Creep score difference per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def cs_diff_per_min_deltas(self):
        return ParticipantTimelineData(self.data.csDiffPerMinDeltas) if self.data.csDiffPerMinDeltas else None

    # ParticipantTimelineData # Damage taken difference per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def damage_taken_diff_per_min_deltas(self):
        return ParticipantTimelineData(self.data.damageTakenDiffPerMinDeltas) if self.data.damageTakenDiffPerMinDeltas else None

    # ParticipantTimelineData # Damage taken per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def damage_taken_per_min_deltas(self):
        return ParticipantTimelineData(self.data.damageTakenPerMinDeltas) if self.data.damageTakenPerMinDeltas else None

    # ParticipantTimelineData # Dragon assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def dragon_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.dragonAssistsPerMinCounts) if self.data.dragonAssistsPerMinCounts else None

    # ParticipantTimelineData # Dragon kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def dragon_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.dragonKillsPerMinCounts) if self.data.dragonKillsPerMinCounts else None

    # ParticipantTimelineData # Elder lizard assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def elder_lizard_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.elderLizardAssistsPerMinCounts) if self.data.elderLizardAssistsPerMinCounts else None

    # ParticipantTimelineData # Elder lizard kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def elder_lizard_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.elderLizardKillsPerMinCounts) if self.data.elderLizardKillsPerMinCounts else None

    # ParticipantTimelineData # Gold per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def gold_per_min_deltas(self):
        return ParticipantTimelineData(self.data.goldPerMinDeltas) if self.data.goldPerMinDeltas else None

    # ParticipantTimelineData # Inhibitor assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def inhibitor_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.inhibitorAssistsPerMinCounts) if self.data.inhibitorAssistsPerMinCounts else None

    # ParticipantTimelineData # Inhibitor kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def inhibitor_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.inhibitorKillsPerMinCounts) if self.data.inhibitorKillsPerMinCounts else None

    # str # Participant's lane
    @property
    def lane(self):
        lane = self.data.lane
        lane = "MIDDLE" if lane == "MID" else lane
        lane = "BOTTOM" if lane == "BOT" else lane
        return cassiopeia.type.core.common.Lane(lane) if lane else None

    # str # Participant's role
    @property
    def role(self):
        return cassiopeia.type.core.common.Role(self.data.role) if self.data.role else None

    # ParticipantTimelineData # Tower assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def turret_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.towerAssistsPerMinCounts) if self.data.towerAssistsPerMinCounts else None

    # ParticipantTimelineData # Tower kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def turret_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.towerKillsPerMinCounts) if self.data.towerKillsPerMinCounts else None

    # ParticipantTimelineData # Tower kills per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def turret_Kills_per_min_deltas(self):
        return ParticipantTimelineData(self.data.towerKillsPerMinDeltas) if self.data.towerKillsPerMinDeltas else None

    # ParticipantTimelineData # Vilemaw assists per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def spider_assists_per_min_counts(self):
        return ParticipantTimelineData(self.data.vilemawAssistsPerMinCounts) if self.data.vilemawAssistsPerMinCounts else None

    # ParticipantTimelineData # Vilemaw kills per minute timeline counts
    @cassiopeia.type.core.common.lazyproperty
    def spider_kills_per_min_counts(self):
        return ParticipantTimelineData(self.data.vilemawKillsPerMinCounts) if self.data.vilemawKillsPerMinCounts else None

    # ParticipantTimelineData # Wards placed per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def wards_per_min_deltas(self):
        return ParticipantTimelineData(self.data.wardsPerMinDeltas) if self.data.wardsPerMinDeltas else None

    # ParticipantTimelineData # Experience difference per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def xp_diff_per_min_deltas(self):
        return ParticipantTimelineData(self.data.xpDiffPerMinDeltas) if self.data.xpDiffPerMinDeltas else None

    # ParticipantTimelineData # Experience per minute timeline data
    @cassiopeia.type.core.common.lazyproperty
    def xp_per_min_deltas(self):
        return ParticipantTimelineData(self.data.xpPerMinDeltas) if self.data.xpPerMinDeltas else None


class Ban(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return str(champion)

    @cassiopeia.type.core.common.lazyproperty
    def champion(self):
        return cassiopeia.riotapi.get_champion_by_id(self.data.championId) if self.data.championId else None

    @property
    def pick_turn(self):
        return self.data.pickTurn


class Frame(cassiopeia.type.core.common.CassiopeiaObject):
    __participant_quota = 2

    def __init__(self, data, participants):
        super().__init__(data)
        self.__participants = participants
        self.__counter = 0

    def __str__(self):
        return "Frame ({time})".format(time=self.timestamp)

    def __iter__(self):
        return iter(self.events)

    def __len__(self):
        return len(self.events)

    def __getitem__(self, index):
        return self.events[index]

    def __count_participant(self):
        self.__counter += 1
        if(self.__counter >= __participant_quota):
            del self.__counter
            del self.__participants

    @cassiopeia.type.core.common.lazyproperty
    def events(self):
        value = [Event(event, participants) for event in self.data.events]
        self.__count_participant()
        return value

    @cassiopeia.type.core.common.lazyproperty
    def participant_frames(self):
        value = {participant: ParticipantFrame(self.data.participantFrames[str(id_)], participants) for id_, participant in self.__participants.items()}
        self.__count_participant()
        return value

    @cassiopeia.type.core.common.lazyproperty
    def timestamp(self):
        return datetime.timedelta(milliseconds=self.data.timestamp) if self.data.timestamp else None


class ParticipantTimelineData(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "Participant Timeline Data"

    @property
    def ten_to_twenty(self):
        return self.data.tenToTwenty

    @property
    def thirty_to_end(self):
        return self.data.thirtyToEnd

    @property
    def twenty_to_thirty(self):
        return self.data.twentyToThirty

    @property
    def zero_to_ten(self):
        return self.data.zeroToTen


class Event(cassiopeia.type.core.common.CassiopeiaObject):
    __participant_quota = 5

    def __str__(self):
        return "Event ({type})".format(type=self.type)

    def __init__(self, data, participants):
        super().__init__(data)
        self.__participants = participants
        self.__counter = 0

    def __count_participant(self):
        self.__counter += 1
        if(self.__counter >= __participant_quota):
            del self.__counter
            del self.__participants

    @property
    def ascended(self):
        return cassiopeia.type.core.common.Ascended(self.data.ascendedType) if self.data.ascendedType else None

    @cassiopeia.type.core.common.lazyproperty
    def assists(self):
        value = [self.__participants[i] for i in self.data.assistingParticipantIds]
        self.__count_participant()
        return value

    @property
    def building(self):
        return cassiopeia.type.core.common.Building(self.data.buildingType) if self.data.buildingType else None

    @cassiopeia.type.core.common.lazyproperty
    def creator(self):
        value = participants[self.data.creatorId] if self.data.creatorId else None
        self.__count_participant()
        return value

    @property
    def type(self):
        return cassiopeia.type.core.common.EventType(self.data.eventType) if self.data.eventType else None

    @cassiopeia.type.core.common.lazyproperty
    def item_after(self):
        return cassiopeia.riotapi.get_item(self.data.itemAfter) if self.data.itemAfter else None

    @cassiopeia.type.core.common.lazyproperty
    def item_before(self):
        return cassiopeia.riotapi.get_item(self.data.itemBefore) if self.data.itemBefore else None

    @cassiopeia.type.core.common.lazyproperty
    def item(self):
        return cassiopeia.riotapi.get_item(self.data.itemId) if self.data.itemId else None

    @cassiopeia.type.core.common.lazyproperty
    def killer(self):
        value = participants[self.data.killerId] if self.data.killerId else None
        self.__count_participant()
        return value

    @property
    def lane(self):
        return cassiopeia.type.core.common.LaneType(self.data.laneType) if self.data.laneType else None

    @property
    def level_up(self):
        return cassiopeia.type.core.common.LevelUp(self.data.levelUpType) if self.data.levelUpType else None

    @property
    def monster(self):
        return cassiopeia.type.core.common.Monster(self.data.monsterType) if self.data.monsterType else None

    @cassiopeia.type.core.common.lazyproperty
    def participant(self):
        value = participants[self.data.participantId] if self.data.participantId else None
        self.__count_participant()
        return value

    @property
    def point_captured(self):
        return cassiopeia.type.core.common.oint(self.data.pointCaptured) if self.data.pointCaptured else None

    @cassiopeia.type.core.common.lazyproperty
    def position(self):
        return cassiopeia.type.core.common.Position(self.data.position) if self.data.position else None

    @property
    def skill_slot(self):
        return self.data.skillSlot

    @property
    def side(self):
        return cassiopeia.type.core.common.Side(self.data.teamId) if self.data.teamId else None

    @cassiopeia.type.core.common.lazyproperty
    def timestamp(self):
        return datetime.timedelta(milliseconds=self.data.timestamp) if self.data.timestamp else None

    @property
    def side(self):
        return cassiopeia.type.core.common.Tower(self.data.towerType) if self.data.towerType else None

    @cassiopeia.type.core.common.lazyproperty
    def victim(self):
        value = participants[self.data.victimId] if self.data.victimId else None
        self.__count_participant()
        return value

    @property
    def ward(self):
        return cassiopeia.type.core.common.Ward(self.data.wardType) if self.data.wardType else None


class ParticipantFrame(cassiopeia.type.core.common.CassiopeiaObject):
    def __init__(self, data, participants):
        super().__init__(data)
        self.__participant = participants[self.data.participantId]

    def __str__(self):
        return "Participant Frame ({player})".format(player=self.__participant)

    @property
    def gold(self):
        return self.data.currentGold

    @property
    def score(self):
        return self.data.dominionScore

    @property
    def jungle_minions(self):
        return self.data.jungleMinionsKilled

    @property
    def level(self):
        return self.data.level

    @property
    def minions(self):
        return self.data.minionsKilled

    @property
    def participant(self):
        return self.__participant

    @cassiopeia.type.core.common.lazyproperty
    def position(self):
        return cassiopeia.type.core.common.Position(self.data.position) if self.data.position else None

    @property
    def team_score(self):
        return self.data.teamScore

    @property
    def xp(self):
        return self.data.xp


class Position(cassiopeia.type.core.common.CassiopeiaObject):
    def __str__(self):
        return "({x}, {y})".format(x=self.x, y=self.y)

    @property
    def x(self):
        return self.data.x

    @property
    def y(self):
        return self.data.y