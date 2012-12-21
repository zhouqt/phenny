#!/usr/bin/env python
"""
info.py - Phenny Information Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

def doc(phenny, input_msg):
   """Shows a command's documentation, and possibly an example."""
   name = input_msg.group(1)
   name = name.lower()

   if phenny.doc.has_key(name):
      phenny.reply(phenny.doc[name][0])
      if phenny.doc[name][1]:
         phenny.say('e.g. ' + phenny.doc[name][1])
doc.rule = ('$nick', '(?i)(?:help|doc) +([A-Za-z]+)(?:\?+)?$')
doc.example = '$nickname: doc tell?'
doc.priority = 'low'

def commands(phenny, input_msg):
   # This function only works in private message
   if input_msg.sender.startswith('#'): return
   names = ', '.join(sorted(phenny.doc.iterkeys()))
   phenny.say('Commands I recognise: ' + names + '.')
   phenny.say(("For help, do '%s: help example?' where example is the " +
               "name of the command you want help for.") % phenny.nick)
commands.commands = ['commands']
commands.priority = 'low'
commands.last_cmd = True

def help_info(phenny, input_msg):
   resp = 'Hi, I\'m a bot. Say ".commands" to me in private for a list of my'
   resp += ' commands, or see https://wiki.test.redhat.com/KvmQE/IamABot'
   resp += ' for more general details. My owner is %s.' % phenny.config.owner
   phenny.reply(resp)
help_info.rule = ('$nick', r'(?i)help(?:[?!]+)?$')
help_info.priority = 'low'
help_info.last_cmd = True

def stats(phenny, input_msg):
   """Show information on command usage patterns."""
   commands = {}
   users = {}
   channels = {}

   ignore = set(['f_note', 'startup', 'message', 'noteuri'])
   for (name, user), count in phenny.stats.items():
      if name in ignore: continue
      if not user: continue

      if not user.startswith('#'):
         try: users[user] += count
         except KeyError: users[user] = count
      else:
         try: commands[name] += count
         except KeyError: commands[name] = count

         try: channels[user] += count
         except KeyError: channels[user] = count

   comrank = sorted([(b, a) for (a, b) in commands.iteritems()], reverse=True)
   userank = sorted([(b, a) for (a, b) in users.iteritems()], reverse=True)
   charank = sorted([(b, a) for (a, b) in channels.iteritems()], reverse=True)

   # most heavily used commands
   creply = 'most used commands: '
   for count, command in comrank[:10]:
      creply += '%s (%s), ' % (command, count)
   phenny.say(creply.rstrip(', '))

   # most heavy users
   reply = 'power users: '
   for count, user in userank[:10]:
      reply += '%s (%s), ' % (user, count)
   phenny.say(reply.rstrip(', '))

   # most heavy channels
   chreply = 'power channels: '
   for count, channel in charank[:3]:
      chreply += '%s (%s), ' % (channel, count)
   phenny.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'
stats.last_cmd = True

if __name__ == '__main__':
   print __doc__.strip()
