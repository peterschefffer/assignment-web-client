#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data = data.split('\n')
        data = data[0]
        data = data.split(' ')
        code = int(data[1])
        return code

    def get_headers(self,data):
        data = data.splitlines()
        index = data.index('')
        head = data[:index]
        header = ''.join(head)
        return header

    def get_body(self, data):
        data = data.splitlines()
        index = data.index('')
        body_l = data[index+1:]
        body = ''.join(body_l)
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        # connecting
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        port = parsed.port

        if not port:
            port = 80
        path = parsed.path
        
        self.connect(host, port)        
        
        if path == "":
            path = '/'

        # create req
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
        request += "Connection: close\r\n\r\n"

        #print(request)

        #send req
        self.sendall(request)

        #close write
        #self.socket.shutdown(socket.SHUT_WR)

        #receive
        result = self.recvall(self.socket)

        #close socket
        self.close()
        print(result)

        #get code
        code = self.get_code(result)

        #get body
        body = self.get_body(result)

        #get header
        head = self.get_headers(result)

        if len(body) < 10:
            body += parsed.path

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        parsed = urllib.parse.urlparse(url)

        loc = parsed.netloc
        port = parsed.port
        host = parsed.hostname
        path = parsed.path
        #loc = loc.split(':')
        self.connect(host, port)

        final_args = args

        if args:
            final_args = urllib.parse.urlencode(final_args)
        else:
            final_args = ""
            
        length = len(final_args)
        request = f"POST {path} HTTP/1.1\nHost: {host}\n"
        request += "Content-Type: application/x-www-form-urlencoded\n"
        request += f'Content-Length: {length}\n\n'
        request += final_args

        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)
        result = self.recvall(self.socket)
        print(result)
        self.close()
    
        code = self.get_code(result)
        body = self.get_body(result)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
