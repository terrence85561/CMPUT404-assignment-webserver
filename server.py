#  coding: utf-8 
import socketserver
import os
import re

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # For stream services, self.request is a socket object
        self.data = self.request.recv(1024).strip()

        # if receive an empty string
        if not self.data:
            return
        
        print ("Got a request of: %s\n" % self.data.decode('utf-8'))

        request_string = self.data.decode('utf-8')
        # get the request method
        method = request_string.split()[0]
        
        # only consider GET method
        if method == 'GET':
            path = request_string.split()[1]
            print('path is',path)
            is_forbidden = re.search(r'\/etc\/|\/group\/',path)
            if is_forbidden != None:
                f = open('./www/notfound.html','r')
                header = "HTTP/1.1 404 Not Found\r\n\r\n"
                content = f.read()
                data = header + content
                self.request.sendall(data.encode('utf-8'))
                f.close()
                return
            
            
            try:
                # it is in root dir
                if path == "/":
                    filepath = "./www" + "/index.html"
                    f = open(filepath,'r')
                    content = f.read()
                    header = "HTTP/1.1 200 OK\r\nContent-Type:text/{}\r\n\r\n".format("html")
                    data = header + content
                    self.request.sendall(data.encode('utf-8'))
                    f.close()
                
                # it is not root dir
                else:
                    filepath = "./www" + path
                    
                    reDirect_bool = self.reDirect(path)
                    if reDirect_bool:
                        # need reDirect_bool,so that it is a dir
                        newPath = path + "/index.html"
                        header = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\n\r\n".format(newPath)
                        self.request.sendall(header.encode('utf-8'))
                    
                    else:
                        # dir or file
                        is_file = self.isFile(path)
                        if is_file:
                            suffix = filepath.split('.')[-1]
                            #print(filepath)
                            f = open(filepath,'r')
                            content = f.read()
                            header = 'HTTP/1.1 200 OK\r\nContent-Type:text/{}\r\n\r\n'.format(suffix)
                            data = header + content
                            self.request.sendall(data.encode('utf-8'))
                            f.close()
                        else:
                            newPath = filepath + "index.html"
                            f = open(newPath,'r')
                            content = f.read()
                            header = 'HTTP/1.1 200 OK\r\nContent-Type:text/{}\r\n\r\n'.format("html")
                            data = header + content
                            self.request.sendall(data.encode('utf-8'))
                            f.close()
        
            except:
                header = "HTTP/1.1 404 NOT FOUND\r\n\r\n"
                filepath = "./www/notfound.html"
                f = open(filepath,'r')
                content = f.read()
                self.request.sendall(header.encode('utf-8'))
                for i in range(len(content)):
                    self.request.sendall(content[i].encode('utf-8')) 
                f.close()               
        else:
            header = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            self.request.sendall(header.encode('utf-8'))
    def reDirect(self,path):
        end_with_slash = re.search(r'\/$',path) # end as / 
        is_file = re.search(r'\.',path) # has file in path
        if end_with_slash != None and is_file == None:
            print('has slash,no file')
            # end with slash and is not linked to a file. it is not going to be re-directed
            return False
        elif end_with_slash != None and is_file != None:
            print('has slash has file')
            raise Exception
        
        elif end_with_slash == None and is_file != None:
            print('no slash has file')
            return False
        
        elif end_with_slash == None:
            print('redirect')
            return True
            
             

    def isFile(self,path):
        is_file = re.search(r'\.',path)
        if is_file != None:
            print('is file')
            return True
        else:
            print('is not file')
            return False



            
        
        #self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
