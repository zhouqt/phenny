#!/usr/bin/env python
"""
group.py - User Group Facilities

Author: Qingtang Zhou <qzhou@redhat.com>
About: http://inamidst.com/phenny/
"""

import os
import cPickle


class GroupManager(object):
    def __init__(self, phenny, channel):
        self.phenny = phenny
        self.channel = channel
        fn = "%s-%s-%s.group.db" % (self.phenny.config.nick, self.channel,
                                    self.phenny.config.host)
        self.db_filename = os.path.join(os.path.expanduser('~/.phenny'), fn)
        self.group_list = []
        self.reserved_group = []
        if hasattr(self.phenny.config, "reserved_group"):
            self.reserved_group = self.phenny.config.reserved_group
        self.load_group_list()

    def load_group_list(self, filename=None):
        fn = filename or self.db_filename
        try:
            f = open(fn, 'r')
            self.group_list = cPickle.load(f)
            f.close()
            return "Okay"
        except Exception, e:
            return "Error when loading group info: %s" % e


    def save_group_list(self, filename=None):
        fn = filename or self.db_filename
        f = open(fn, 'w')
        cPickle.dump(self.group_list, f)
        f.close()
        return "Okay"

    def get_group(self, group_name):
        grp = [grp for grp in self.group_list if (grp.name == group_name)]
        if grp:
            return grp[0]
        return None

    def has_group(self, group_name):
        if self.get_group(group_name):
            return True
        return False

    def add_group(self, name, creator, members=[]):
        if not name:
            return ("Incorrect group name. "
                    "Please add a '@' in front of group name")

        if name in self.reserved_group:
            return "Group name '%s' is reserved." % name

        if self.has_group(name):
            return "There is alreay a group called '%s'" % name
        grp = Group(name, creator)
        self.group_list.append(grp)
        self.save_group_list()
        return "Okay"

    def del_group(self, name, user, members=[]):
        grp = self.get_group(name)
        if not grp:
            return "No such group '%s'" % name
        if user != grp.creator:
            return ("You're not the group creator,"
                   " ask group creator '%s' for help" % grp.creator)
        self.group_list.remove(grp)
        self.save_group_list()
        return "Okay"


class Group(object):
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.members = []

    def lookup_member(self, member):
        if member in self.members:
            return True
        return False

    def add_member(self, member):
        if self.lookup_member(member):
            return False

        self.members.append(member)
        return True

    def del_member(self, member):
        if not self.lookup_member(member):
            return False

        self.members.remove(member)
        return True


if __name__ == "__main__":
    pass
