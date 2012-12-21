#!/usr/bin/env python
"""
redmine.py - Phenny Redmine Module

Author: Qingtang Zhou <qzhou@redhat.com>
"""

import sys
import re
import redmineapi

REDMINE_URL = "redmine.englab.nay.redhat.com"

usage = """"""

RM_FMT_STR = ("#%(issue_id)s: %(done_ratio)s%% - %(status)s - %(assigned_to)s"
        " - Subject: %(subject)s | Start: %(start_date)s - Due: %(due_date)s")


def query_issue_with_id(phenny, issue_id):
    rm = redmineapi.Redmine(REDMINE_URL, apikey="", ssl=True)
    try:
        rm_issue_info = rm.issues.get(issue_id).__dict__
    except ValueError, e:
        print >> sys.stderr, "Error to get issue id [%s], %s" % (issue_id, e)
        return

    info = {}
    info["issue_id"] = rm_issue_info.get("id", "")
    info["done_ratio"] = rm_issue_info.get("done_ratio", "")
    info["status"] = rm_issue_info.get("status_id", "")
    info["assigned_to"] = rm_issue_info.get("assigned_to_id", "")
    info["subject"] = rm_issue_info.get("subject", "")
    info["start_date"] = rm_issue_info.get("start_date", "")
    info["due_date"] = rm_issue_info.get("due_date", "")
    return phenny.say(RM_FMT_STR % info)


def issue(phenny, input_msg):
    args = input_msg.group(2)
    if not args:
        return phenny.reply(usage)

    args = args.strip()

    if args.isdigit():
        query_issue_with_id(phenny, args)
        return
    return
issue.commands = ['issue']
issue.name = 'issue'
issue.example = '.issue issue_id'
issue.priority = 'low'
issue.last_cmd = True


redmine_url_pattern = r'.*?https?:\/\/redmine\.englab\.nay\.redhat\.com\/issues/(\d+).*?'
def issue_info(phenny, input_msg):
    if not input_msg.sender.startswith('#'):
        return

    for _ in re.findall(redmine_url_pattern, input_msg.msg_bytes):
        query_issue_with_id(phenny, _)
    return
issue_info.rule = redmine_url_pattern
issue_info.priority = 'high'
issue_info.last_cmd = True

if __name__ == '__main__':
    print __doc__.strip()
