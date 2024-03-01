#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Unit tests for the Gerrit event stream handler and event objects. """

import json
import os
import unittest

from pygerrit.events import PatchsetCreatedEvent, \
    RefUpdatedEvent, ChangeMergedEvent, CommentAddedEvent, \
    ChangeAbandonedEvent, ChangeRestoredEvent, \
    DraftPublishedEvent
from pygerrit.client import GerritClient


def _create_event(name, gerrit):
    """ Create a new event.

    Read the contents of the file specified by `name` and load as JSON
    data, then add as an event in the `gerrit` client.

    """
    data = open(os.path.join(os.environ["TESTDIR"], name + ".txt"))
    json_data = json.loads(data.read().replace("\n", ""))
    gerrit.put_event(json_data)


class TestGerritEvents(unittest.TestCase):
    def setUp(self):
        self.gerrit = GerritClient("review.sonyericsson.net")

    def test_patchset_created(self):
        _create_event("patchset-created-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, PatchsetCreatedEvent))
        self.assertEquals(event.name, "patchset-created")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.uploader.name, "Uploader Name")
        self.assertEquals(event.uploader.email, "uploader@example.com")

    def test_draft_published(self):
        _create_event("draft-published-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, DraftPublishedEvent))
        self.assertEquals(event.name, "draft-published")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.uploader.name, "Uploader Name")
        self.assertEquals(event.uploader.email, "uploader@example.com")

    def test_ref_updated(self):
        _create_event("ref-updated-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, RefUpdatedEvent))
        self.assertEquals(event.name, "ref-updated")
        self.assertEquals(event.ref_update.project, "project-name")
        self.assertEquals(event.ref_update.oldrev,
                          "0000000000000000000000000000000000000000")
        self.assertEquals(event.ref_update.newrev,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.ref_update.refname, "refs/tags/refname")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")

    def test_change_merged(self):
        _create_event("change-merged-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeMergedEvent))
        self.assertEquals(event.name, "change-merged")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")

    def test_comment_added(self):
        _create_event("comment-added-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, CommentAddedEvent))
        self.assertEquals(event.name, "comment-added")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(len(event.approvals), 2)
        self.assertEquals(event.approvals[0].category, "CRVW")
        self.assertEquals(event.approvals[0].description, "Code Review")
        self.assertEquals(event.approvals[0].value, "1")
        self.assertEquals(event.approvals[1].category, "VRIF")
        self.assertEquals(event.approvals[1].description, "Verified")
        self.assertEquals(event.approvals[1].value, "1")
        self.assertEquals(event.author.name, "Author Name")
        self.assertEquals(event.author.email, "author@example.com")

    def test_change_abandoned(self):
        _create_event("change-abandoned-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeAbandonedEvent))
        self.assertEquals(event.name, "change-abandoned")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.abandoner.name, "Abandoner Name")
        self.assertEquals(event.abandoner.email, "abandoner@example.com")
        self.assertEquals(event.reason, "Abandon reason")

    def test_change_restored(self):
        _create_event("change-restored-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeRestoredEvent))
        self.assertEquals(event.name, "change-restored")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.restorer.name, "Restorer Name")
        self.assertEquals(event.restorer.email, "restorer@example.com")
        self.assertEquals(event.reason, "Restore reason")

if __name__ == '__main__':
    unittest.main()
