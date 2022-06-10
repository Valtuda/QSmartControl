"""
    QSmartControl; to control Quantel/Lumibird QSmart lasers over LAN
    Copyright (C) 2022   Jasper Smits

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import telnetlib

class LaserCommunication:
    """
    Class to manage communication to a QSmart laser using the telnet protocol.

    This class was designed with the QSmart 450 in mind, but might work for other lasers."""

    def __init__(self,ip,port,timeout):
        """
        Initializes the telnet connection. Takes ip, port and timeout keywords to be passed to telnet.
        """
        
        ## Initialize the telnet object
        self.tn = telnetlib.Telnet(ip,port,timeout)

        ## Test the connection, the laser should always respond to STATE
        try:
            self.send_and_recv("STATE")
        except Exception as e:
            raise IOError("Unable to connect to laser:",e)

    def __send_message(self,message):
        self.tn.write(message.encode("ascii")+b'\n')
    
    def __recv_message(self,include_status=False):
        """Message receiver

        Problem occurs that messages are read too quickly, so we always want to be sure we read something.

        We read up to the first line break. If the message doesn't contain "ERROR", we have to read to another line break."""
        message = self.tn.read_until(b"\n")

        if b"ERROR" in message or b"OK" in message:
            ## If there is an error in the message, we can only read one line.
            pass
        else:
            ## If there is no error in the message, the status code will also be passed to us, so we read another line.
            message += self.tn.read_until(b"\n")

        message = message.decode("ascii")
        if include_status:
            return message
        else:
            message_parts = message.split("\n")
            return message_parts[0]

        
    def send_and_recv(self,message,include_status=False):
        self.__send_message(message)
        return self.__recv_message(include_status)
