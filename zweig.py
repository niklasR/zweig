#! /usr/bin/env python
import getpass
import telnetlib
import socket
import time
import re
from config import *

# initialise variables and regular expression patterns.
activeCalls = None

reActiveCall = re.compile("\d+ active call")
reActiveChannel = re.compile("\d+ active channel")
reTotalCalls = re.compile("\d+ calls processed")


def send_msg(message):
	"""
	Sends message to Carbon.
	Make sure message is given as 
	<metric> <netricvalue> <timestamp>
	"""
	# print 'sending message:\n%s' % message
	carbonSocket = socket.socket()
	carbonSocket.connect((CARBON_HOST, CARBON_PORT))
	carbonSocket.sendall(message)
	carbonSocket.close()
	last_send = int(time.time())

def recordActiveCalls(data):
	"""
	Takes the number of active calls from data and sends them Carbon using send_msg)
	"""
	match = reActiveCall.search(data)
	if match:
		activeCalls = int(match.group(0).split(" ")[0])
		message = "%s %s %d\n" % (CALLS_ACTIVE_METRIC, activeCalls, int(time.time()))
		send_msg(message)

def recordActiveChannels(data):
	"""
	Takes the number of active channels from data and sends them Carbon using send_msg).
	"""
	match = reActiveChannel.search(data)
	if match:
		activeChannels = int(match.group(0).split(" ")[0])
		message = "%s %s %d\n" % (CHANNELS_ACTIVE_METRIC, activeChannels, int(time.time()))
		send_msg(message)

def recordTotalCalls(data):
	"""
	Takes the number of total calls from data and sends them Carbon using send_msg).
	Not sure how asterisk computes this number...
	"""
	match = reTotalCalls.search(data)
	if match:
		totalCalls = int(match.group(0).split(" ")[0])
		message = "%s %s %d\n" % (CALLS_PROCESSED_METRIC, totalCalls, int(time.time()))
		send_msg(message)

### START PROGRAM ###

# Initialise Telnet connection and log in.
tn = telnetlib.Telnet(ASTERISK_HOST, ASTERISK_PORT)
tn.read_until("Asterisk Call Manager/1.1")
tn.write("Action: Login\nUsername: " + ASTERISK_USER + "\nSecret: " + ASTERISK_SECRET + "\n\n")

# Infinite loop for continuous AMI communication
while True:
	tn.write("Action: Command\nCommand: core show channels\n\n")
	data = tn.read_very_eager()
	if len(data) > 0:
		recordActiveCalls(data)
		recordTotalCalls(data)
		recordActiveChannels(data)
	# sleep for 5 seconds, as retention pattern only stored a datapaoint every 10 secs anyway.
	time.sleep(5)


#logoff. won't ever really get here as loop above infinite...
# print "Done reading"
# print "Logging of.."
tn.write("Action: Logoff" + "\n\n")
tn.close()
exit()
