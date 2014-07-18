#! /usr/bin/env python
import getpass
import sys
import telnetlib
import re
import socket
import time
from configdahdi import *

# initialise variables and regular expression patterns.
activeDAHDIChannels = 0
channelUIDs = []

reEventType = re.compile("Event: .+")
reDAHDI = re.compile("DAHDI.+")
reChannel = re.compile("Channel: .+")
reUniqueID = re.compile("Uniqueid: .+")

last_send = 0
metric = DAHDI_METRIC

def isChannelDAHDI(event):
	"""
	Checks whethter Channel is DAHDI channel.
	Returns true if so, else false.
	Return none if no Channel found
	"""
	match = reChannel.search(event)
	if match:
		 channel = match.group(0).split(" ")[1].rstrip("\r")
		 #print channel
		 if reDAHDI.search(channel):
		 	return True
		 else:
		 	return False
	else:
		return None

def getEventType(event):
	"""
	Returns Type of Event.
	Possibilities:
		* Newchannel
		* Newstate
		* NewCallerid
		* ExtensionStatus
		* Dial
		* Hangup
		* NewAccountCode
		* Bridge
		* Unlink
		* FullyBooted
	"""
	match = reEventType.search(event)
	if match:
		return match.group(0).split(" ")[1].rstrip("\r")
	else:
		return None
		return None

def getUniqueID(event):
	"""
	Returns "channel" of event.
	"""
	match = reUniqueID.search(event)
	if match:
		result = match.group(0).split(" ")[1].rstrip("\r")
		return result
	else:
		return None

def send_msg():
	"""
	Sends message to Carbon.
	Make sure message is given as 
	<metric> <netricvalue> <timestamp>
	"""
	message = "%s %s %d\n" % (metric, activeDAHDIChannels, int(time.time()))
	# print 'sending message:\n%s' % message
	carbonSocket = socket.socket()
	carbonSocket.connect((CARBON_HOST, CARBON_PORT))
	carbonSocket.sendall(message)
	carbonSocket.close()
	last_send = int(time.time())

### START PROGRAM ###

# Initialise Telnet connection and log in.
tn = telnetlib.Telnet(ASTERISK_HOST, ASTERISK_PORT)
tn.read_until("Asterisk Call Manager/1.1")
tn.write("Action: Login\nUsername: " + ASTERISK_USER + "\nSecret: " + ASTERISK_SECRET + "\n\n")

# Infinite loop for continuous AMI communication
while True:
	time.sleep(5)
	data = tn.read_very_eager()
	if len(data) > 0:
		events = data.split("\r\n\r\n")
		for event in events:
			#if getEventType(event) == "FullyBooted": # implement fallback? (goto login and retry)
				# print "Logged In; Reading..."
			if getEventType(event) == "Newchannel":
				if isChannelDAHDI(event):
					channelUIDs.append(getUniqueID(event))
					activeDAHDIChannels+= 1
					# print "New DAHDI channel"
					# print "\t Source UniqueID: " + getUniqueID(event)
					# print "Active DAHDI channels: " + str(activeDAHDIChannels)
			elif getEventType(event) == "Hangup":
				if getUniqueID(event) in channelUIDs:
					activeDAHDIChannels+= -1
					channelUIDs.remove(getUniqueID(event))
					# print "DAHDI Channel hung up"
					# print "\t Source UniqueID: " + getUniqueID(event)
					# print "Active DAHDI channels: " + str(activeDAHDIChannels)
				send_msg()
	if (last_send + 5) < int(time.time()):
		send_msg()
		last_send = int(time.time())

#logoff. won't ever really get here as loop above infinite...
print "Done reading"
print "Logging of.."
tn.write("Action: Logoff" + "\n\n")
tn.close()
exit()