import pytest

from domain.commit import Commit
from repository_mining import RepositoryMining
from scm.commit_visitor import CommitVisitor
from scm.git_repository import GitRepository
from scm.persistence_mechanism import PersistenceMechanism
from datetime import datetime
from dateutil import tz


def test_no_filters():
    mv = MyVisitor()
    rp = RepositoryMining('test-repos/test1/', mv)
    rp.mine()
    lc = mv.list_commits
    assert 5 == len(lc)


def test_since_filter():
    mv = MyVisitor()
    to_zone = tz.gettz('GMT+1')
    dt = datetime(2018, 3, 22, 10, 41, 30, tzinfo=to_zone)
    rp = RepositoryMining('test-repos/test1/', mv, since=dt)
    rp.mine()
    lc = mv.list_commits
    assert 4 == len(lc)


def test_to_filter():
    mv = MyVisitor()
    to_zone = tz.gettz('GMT+1')
    dt = datetime(2018, 3, 22, 10, 42, 3, tzinfo=to_zone)
    rp = RepositoryMining('test-repos/test1/', mv, to=dt)
    rp.mine()
    lc = mv.list_commits
    assert 3 == len(lc)


def test_since_and_to_filters():
    mv = MyVisitor()
    to_zone = tz.gettz('GMT+1')
    since_dt = datetime(2018, 3, 22, 10, 41, 45, tzinfo=to_zone)
    to_zone = tz.gettz('GMT+2')
    to_dt = datetime(2018, 3, 27, 17, 20, 3, tzinfo=to_zone)
    rp = RepositoryMining('test-repos/test1/', mv, since=since_dt, to=to_dt)
    rp.mine()
    lc = mv.list_commits
    assert 3 == len(lc)


def test_from_commit_filter():
    mv = MyVisitor()
    from_commit = '6411e3096dd2070438a17b225f44475136e54e3a'
    rp = RepositoryMining('test-repos/test1/', mv, from_commit=from_commit)
    rp.mine()
    lc = mv.list_commits
    assert 4 == len(lc)


def test_to_commit_filter():
    mv = MyVisitor()
    to_commit = '09f6182cef737db02a085e1d018963c7a29bde5a'
    rp = RepositoryMining('test-repos/test1/', mv, from_commit=to_commit)
    rp.mine()
    lc = mv.list_commits
    assert 3 == len(lc)


def test_from_and_to_commit_filters():
    mv = MyVisitor()
    from_commit = '6411e3096dd2070438a17b225f44475136e54e3a'
    to_commit = '09f6182cef737db02a085e1d018963c7a29bde5a'
    rp = RepositoryMining('test-repos/test1/', mv, from_commit=from_commit, to_commit=to_commit)
    rp.mine()
    lc = mv.list_commits
    assert 2 == len(lc)


def test_from_tag_filter():
    mv = MyVisitor()
    from_tag = 'v1.4'
    rp = RepositoryMining('test-repos/test1/', mv, from_tag=from_tag)
    rp.mine()
    lc = mv.list_commits
    assert 3 == len(lc)


def test_multiple_filters_exceptions():
    mv = MyVisitor()
    to_zone = tz.gettz('GMT+1')
    since_dt = datetime(2018, 3, 22, 10, 41, 45, tzinfo=to_zone)
    from_commit = '6411e3096dd2070438a17b225f44475136e54e3a'
    from_tag = 'v1.4'

    with pytest.raises(Exception):
        RepositoryMining('test-repos/test1/', mv, from_commit=from_commit, from_tag=from_tag)

    with pytest.raises(Exception):
        RepositoryMining('test-repos/test1/', mv, since=since_dt, from_commit=from_commit)

    with pytest.raises(Exception):
        RepositoryMining('test-repos/test1/', mv, since=since_dt, from_tag=from_tag)

    with pytest.raises(Exception):
        RepositoryMining('test-repos/test1/', mv, to=since_dt, to_tag=from_tag)


class MyVisitor(CommitVisitor):
    def __init__(self):
        self.list_commits = []

    def process(self, repo: GitRepository, commit: Commit, writer: PersistenceMechanism):
        self.list_commits.append(commit)