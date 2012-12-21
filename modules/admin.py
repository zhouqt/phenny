#!/usr/bin/env python
"""
admin.py - Phenny Admin Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

def join(phenny, input_msg):
   """Join the specified channel. This is an admin-only command."""
   # Can only be done in privmsg by an admin
   if input_msg.sender.startswith('#'): return
   if input_msg.admin:
      channel, key = input_msg.group(1), input_msg.group(2)
      if not key:
         phenny.write(['JOIN'], channel)
      else: phenny.write(['JOIN', channel, key])
join.rule = r'\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'
join.last_cmd = True

def part(phenny, input_msg):
   """Part the specified channel. This is an admin-only command."""
   # Can only be done in privmsg by an admin
   if input_msg.sender.startswith('#'): return
   if input_msg.admin:
      phenny.write(['PART'], input_msg.group(2))
part.commands = ['part']
part.priority = 'low'
part.example = '.part #example'
part.last_cmd = True

def quit(phenny, input_msg):
   """Quit from the server. This is an owner-only command."""
   # Can only be done in privmsg by the owner
   if input_msg.sender.startswith('#'): return
   if input_msg.owner:
      phenny.write(['QUIT'])
      __import__('os')._exit(0)
quit.commands = ['quit']
quit.priority = 'low'
quit.last_cmd = True

def msg(phenny, input_msg):
   # Can only be done in privmsg by an admin
   if input_msg.sender.startswith('#'): return
   a, b = input_msg.group(2), input_msg.group(3)
   if (not a) or (not b): return
   if input_msg.admin:
      phenny.msg(a, b)
msg.rule = (['msg'], r'(#?\S+) (.+)')
msg.priority = 'low'
msg.last_cmd = True

def me(phenny, input_msg):
   # Can only be done in privmsg by an admin
   if input_msg.sender.startswith('#'): return
   if input_msg.admin:
      msg = '\x01ACTION %s\x01' % input_msg.group(3)
      phenny.msg(input_msg.group(2) or input_msg.sender, msg)
me.rule = (['me'], r'(#?\S+) (.+)')
me.priority = 'low'
me.last_cmd = True

if __name__ == '__main__':
   print __doc__.strip()
