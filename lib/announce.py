# Forban - a simple link-local opportunistic p2p free software
#
# For more information : http://www.foo.be/forban/
#
# Copyright (C) 2009-2012 Alexandre Dulaunoy - http://www.foo.be/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import socket
import string
import time
import datetime
try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1
import hmac
import re
import sys


flogger = None

# forban internal junk
sys.path.append('.')
import fid

debug = 0

class message:

    def __init__(self,name="notset", uuid=None, port="12555", timestamp=None,
    auth=None, destination=["ff02::1","255.255.255.255", ], dynpath="../var"):
            self.name       = name
            self.uuid       = uuid
            self.port       = port
            self.count      = 0
            self.destination = destination
            self.dynpath    = dynpath
            self.ipv6_disabled = 0

    def disableIpv6(self):
            self.ipv6_disabled = 1
            self.destination   = ["255.255.255.255", ]

    def setDestination(self, destination=["ff02::1","255.255.255.255", ] ):
             self.destination = destination

    def gen (self):
            self.payload    = "forban;name;" + self.name + ";"
            myid = fid.manage(dynpath=self.dynpath)
            self.payload    = self.payload + "uuid;" + myid.get()

    def auth(self,value=None):

        if value is None or value is False:
            self.payload = self.payload
        else:
            self.payload = self.payload + ";hmac;" + value

    def get (self):
            return self.payload

    def __debugMessage (self, msg ):
        if  flogger is not None:
            flogger.debug ( msg )
        elif debug == 1:
            print msg

    def __errorMessage (self, msg):
        if flogger is not None:
            flogger.error ( msg )
        elif debug == 1:
            print msg


    def send(self):
        for destination in self.destination:
            if socket.has_ipv6 and re.search(":", destination) and not  self.ipv6_disabled == 1:
               
		self.__debugMessage(  "working in ipv6 part on destination " + destination )

                # Even if Python is compiled with IPv6, it doesn't mean that the os
                # is supporting IPv6. (like the Nokia N900)
                try:
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                    # Required on some version of MacOS X while sending IPv6 UDP
                    # datagram
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                except:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

            else:
                self.__debugMessage (  "open ipv4 socket on destination " + destination )
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            try:
                sock.sendto(self.payload, (destination, int(self.port)))
            except socket.error, msg:
                self.__errorMessage ( "Error sending to "+ destination + " : " + msg.strerror  )
                continue
        sock.close()



def managetest():
    msg = message()
    msg.gen()
    msg.auth()
    print msg.get()
    msg.send()
    msg.auth("forbankey")
    print msg.get()

if __name__ == "__main__":
    managetest()

