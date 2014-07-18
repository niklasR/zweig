zweig
=====

Collect asterisk call metrics in Carbon.

## Screenshot

Screenshot of Graphite showing the collected data.
![Screenshot](https://raw.githubusercontent.com/niklasR/zweig/master/zweig_graph.png)

## Ingedients

zweig is a compilation of short python scripts that interact with an asterik telephony server using the AMI over a telnet connection
The data it collects from there is then sent to Carbon using a TCP connection.

## Requirements

zweig runs in environments with:

* Python 2.7
* Asterisk 1.8+
* Carbon Server

## Installation

Copy the files into a directory of choice on a machine that can connect to Asterisk and Carbon and make sure the permissions are set correctly.
Add AMI users in asterisks. The DADHI user needs read-permissions for "call" and the general one needs write-permissions for "command".
For more information about this please consult the Asterisk documentation.

## Configuration

Enter the details for the servers, including host, port, username (asterisk only) and secret (asterisk only).

## Run
	python zweig.py &
	python zweig_DADHI.py &
And you should start seeing the call statistics in graphite!


