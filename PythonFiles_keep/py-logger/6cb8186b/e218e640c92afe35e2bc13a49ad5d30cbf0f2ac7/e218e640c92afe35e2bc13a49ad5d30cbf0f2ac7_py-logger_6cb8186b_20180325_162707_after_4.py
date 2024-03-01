from . import slack
from . import sendgrid


def test_sendgrid():
    res = sendgrid.send('SG title', 'SG message')
    assert res.status_code == 202


def test_slack():
    res = slack.send('Slack title', 'Slack message')
    assert res.status_code == 200
