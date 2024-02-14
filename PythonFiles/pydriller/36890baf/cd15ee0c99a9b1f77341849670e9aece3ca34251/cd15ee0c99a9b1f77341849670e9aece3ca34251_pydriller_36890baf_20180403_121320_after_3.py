from domain.commit import Commit
from scm.commit_visitor import CommitVisitor
from scm.git_repository import GitRepository
from scm.persistence_mechanism import PersistenceMechanism


class ConcurrencyVisitorTest(CommitVisitor):
    def __init__(self):
        self.visited_hashes = set()
        self.visited_times = set()
        self.visited_commits = set()

    def process(self, repo: GitRepository, commit: Commit, writer: PersistenceMechanism):
        self.visited_hashes.add(commit.hash)
        self.visited_times.add(commit.author_date)
        self.visited_commits.add(commit)