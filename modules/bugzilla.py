#!/usr/bin/env python
"""
bugzilla.py - Phenny Bugzilla Module

Author: Qingtang Zhou <qzhou@redhat.com>
"""

import os
import commands
import re


BUGZILLA_URL = "https://bugzilla.redhat.com/"

usage = """Use '.bz <bugid>' or '.bz <status> <component> <product>' to query bugs.
Remember to use comma ',' when status/component/product .
eg. query all NEW and ASSIGNED bugs in qemu-kvm component of product 'Red Hat Enterprise Linux 6',
type: '.bz NEW qemu-kvm rhel6'"""

BZ_FORMAT_STR = "#%{bug_id}: %{status} - %{assigned_to} - %{short_desc} [%{target_milestone}] [%{flags}] %{qa_whiteboard}"

def get_bz_tool_path(phenny):
    if hasattr(phenny.config, 'bugzilla_tool_path'):
         return phenny.config.bugzilla_tool_path

    phenny.say("Missing bugzilla tools, add 'bugzilla_tool_path'"
               " in my config file.")
    return ""


def query_bug_with_id(phenny, bugid):
    cmd = get_bz_tool_path(phenny)
    if not cmd:
        return
    cmd += " query"
    cmd += " --outputformat '%s'" % BZ_FORMAT_STR
    cmd += " -b %s" % bugid
    print cmd
    s, out = commands.getstatusoutput(cmd)
    if s:
        return phenny.say("Failed to call bugzilla cli tool!")
    return phenny.say(out)


def bz(phenny, input_msg):
    cmd = get_bz_tool_path(phenny)
    if not cmd:
        return

    args = input_msg.group(2)
    if not args:
        return phenny.reply(usage)

    args = args.strip()

    if args.isdigit():
        query_bug_with_id(phenny, args)
        return

    # query component.
    args = args.split()
    if len(args) < 3:
        return phenny.reply(usage)
    status, component, product = args
    if product.lower() == "rhel6":
        product = "Red Hat Enterprise Linux 6"
    elif product.lower() == "rhel5":
        product = "Red Hat Enterprise Linux 5"
    cmd += " query -t %s -c %s -p '%s'" % (status, component, product)
    s, out = commands.getstatusoutput(cmd)
    if s:
        return phenny.say("Failed to call bugzilla cli tool!")
    if "\n" in out:
        phenny.reply("Many outputs! Send you private message instead.")
        for line in out.split("\n"):
            phenny.msg(input_msg.nick, line)
        return
    else:
        return phenny.reply(out)
bz.commands = ['bz']
bz.name = 'bz'
bz.example = '.bz bzid/ <status> <component> <product>'
bz.priority = 'low'


bz_url_pattern = r'.*?https:\/\/bugzilla\.redhat\.com\/show_bug.*?(\d{1,6}).*?'
def bz_info(phenny, input_msg):
    if not input_msg.sender.startswith('#'):
        return

    cmd = get_bz_tool_path(phenny)
    if not cmd:
        return

    for m in re.findall(bz_url_pattern, input_msg.msg_bytes):
        query_bug_with_id(phenny, m)
    return
bz_info.rule = bz_url_pattern
bz_info.priority = 'high'

def bz_url(phenny, input_msg):
    if not input_msg.sender.startswith('#'):
        return

    arg = input_msg.group(1)
    phenny.reply("Bugzilla URL: %s" % os.path.join(BUGZILLA_URL, arg))
    query_bug_with_id(phenny, arg)
    return
bz_url.rule = r'.*?[Bb](?:[Uu][Gg]|[Zz])[: ,#]*(\d{1,6}).*'
bz_url.priority = 'high'

if __name__ == '__main__':
   print __doc__.strip()
