#!/usr/bin/env python
"""
startup.py - Phenny Group Module

Author: Qingtang Zhou <qzhou@redhat.com>
"""

import sys
import re
import group

def setup(phenny):
    phenny.group_managers = {}
    for c in phenny.channels:
        phenny.group_managers[c] = group.GroupManager(phenny, c)


def group_cmd(phenny, input_msg):
    usage = "Usage: .group list/add/del/load/save @groupname"

    def list_grp():
        if gm.group_list:
            grp =  "@" + " @".join([g.name for g in gm.group_list])
        else:
            grp = "(N/A)"
        return "Existed groups: %s" % grp

    gm = phenny.group_managers.get(input_msg.sender)
    if not gm:
        print >> sys.stderr, ("GroupManager init failed for"
                             " channel '%s'" % input_msg.sender)
        return phenny.reply("OOPS!")

    args = input_msg.group(2)
    if not args:
        phenny.reply(usage)
        return phenny.reply(list_grp())

    print >> sys.stderr, input_msg.bytes
    regex_str = r"\.group\s+(\w{3,4})(?:\s+@(\w+)|(?:.*))"
    try:
        cmd, name = re.findall(regex_str, input_msg.bytes)[0]
    except Exception, e:
        print >> sys.stderr, "Err: %s (in group_cmd.py)" % e
        return phenny.reply(usage)

    cmd_dict = {}
    cmd_dict["list"] = lambda x,y: list_grp()
    cmd_dict["add"] = gm.add_group
    cmd_dict["del"] = gm.del_group
    cmd_dict["load"] = lambda x,y: gm.load_group_list()
    cmd_dict["save"] = lambda x,y: gm.save_group_list()

    try:
        if callable(cmd_dict[cmd]):
            ret = cmd_dict[cmd](name, input_msg.nick.lower())
            return phenny.reply(ret)
    except KeyError:
        print >> sys.stderr, "Can't find function for %s" % cmd
        return phenny.reply(usage)

group_cmd.commands = ["group"]
group_cmd.example = ".group list/add/del/load/save @groupname"
group_cmd.priority = "low"


def member_cmd(phenny, input_msg):
    usage = "Usage: .member list/add/del/save @groupname nick nick nick"

    def grp_member_info(grp):
        m =  " ".join(grp.members)
        if not m:
            m = "(N/A)"
        return ("Group @%s is created by %s,"
                " nicks in this groups: %s" % (grp.name, grp.creator, m))

    def grp_member_add(grp, user, nicks):
        msg = grp.add_member(user, nicks)
        # Call GroupManager to save new group info.
        if "Okay" in msg:
            gm.save_group_list()
        return msg

    def grp_member_del(grp, user, nicks):
        msg = grp.del_member(user, nicks)
        # Call GroupManager to save new group info.
        if "Okay" in msg:
            gm.save_group_list()
        return msg

    gm = phenny.group_managers.get(input_msg.sender)
    if not gm:
        print >> sys.stderr, ("GroupManager init failed for"
                             " channel '%s'" % input_msg.sender)
        return phenny.reply("OOPS!")

    args = input_msg.group(2)
    if not args:
        return phenny.reply(usage)

    print >> sys.stderr, input_msg.bytes
    regex_str = r"\.member\s+(\w{3,4})\s+@(\w+)\s*(.*)"
    try:
        cmd, name, nicks = re.findall(regex_str, input_msg.bytes)[0]
    except Exception, e:
        print >> sys.stderr, "Err: %s (in group_cmd.py)" % e
        return phenny.reply(usage)

    grp = gm.get_group(name)
    if not grp:
        return phenny.reply("No such group '%s'" % name)

    cmd_dict = {}
    cmd_dict["list"] = lambda x,y,z: grp_member_info(x)
    cmd_dict["add"] = grp_member_add
    cmd_dict["del"] = grp_member_del
    cmd_dict["save"] = lambda x,y,z: gm.save_group_list()

    try:
        if callable(cmd_dict[cmd]):
            ret = cmd_dict[cmd](grp, input_msg.nick.lower(), nicks)
            return phenny.reply(ret)
    except KeyError:
        print >> sys.stderr, "Can't find function for %s" % cmd
        return phenny.reply(usage)
member_cmd.commands = ["member"]
member_cmd.example = ".member list/add/del/save @groupname nick nick nick"
member_cmd.priority = "low"

def say_cmd(phenny, input_msg):
    """say something to a group."""
    usage = "Usage: .say @groupname balabala"

    gm = phenny.group_managers.get(input_msg.sender)
    if not gm:
        print >> sys.stderr, ("GroupManager init failed for"
                             " channel '%s'" % input_msg.sender)
        return phenny.reply("OOPS!")

    args = input_msg.group(2)
    if not args:
        phenny.reply(usage)

    print >> sys.stderr, input_msg.bytes
    regex_str = r"\.say\s+@(\w+)\s+(.*)"
    try:
        grp_name, words = re.findall(regex_str, input_msg.bytes)[0]
    except Exception, e:
        print >> sys.stderr, "Err: %s (in group_cmd.py)" % e
        return phenny.reply(usage)

    grp = gm.get_group(grp_name)
    if not grp:
        return phenny.reply("No such group '%s'" % grp_name)

    m_list = " ".join(grp.members)
    if not m_list:
        return phenny.replay("No member in this group.")

    phenny.say("%s:   %s has a message for you!" % (m_list, input_msg.nick))
    phenny.say(words)
    return
say_cmd.commands = ['say']
say_cmd.example = ".say @groupname balabala"
say_cmd.priority = 'low'


if __name__ == '__main__':
   print __doc__.strip()
