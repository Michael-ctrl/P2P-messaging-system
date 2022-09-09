"""
    Python 3
    Usage: python3 server.py localhost 12000
    Coding: utf-8
    
    References:
        Used sample code by Wei Song (Tutor)
"""
from socket import *
from threading import Thread
import sys, select, os.path

clientActive = False
clientAuth = False
clientAddress = None
clientList = [] # the current client connected to server
threads = []
serverThreads = {}

# acquire server host and port from command line parameter
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT ======\n")
    exit(0)
serverHost = "127.0.0.1" # localhost
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

# define UDP socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)

# Class to store each thread info
class ThreadInfo:
    def __init__(self, name, nMessages, owner):
        self.name = name
        self.nMessages = nMessages
        self.owner = owner

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientAlive = False
        self.clientAuth = False
        self.clientUsername = ""
        self.fileToSend = ""
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        print("Client authenticating")

    def process_data(self, data):
        if not self.clientAuth:
            self.process_login(data)
            return
        if data == "Initiate File Send":
            self.file_send()
            return
        command = data.split()[0]
        if command == 'XIT':
            self.process_exit()
        elif command == 'CRT':
            self.create_thread(data)
        elif command == 'MSG':
            self.post_message(data)
        elif command == 'DLT':
            self.delete_message(data)
        elif command == 'EDT':
            self.edit_message(data)
        elif command == 'LST':
            self.list_threads()
        elif command == 'RDT':
            self.read_thread(data)
        elif command == 'UPD':
            self.upload_file(data)
        elif command == 'DWN':
            self.download_file(data)
        elif command == 'RMV':
            self.remove_thread(data)
        else:
            print('This command somehow bypassed checks...')


    def process_login(self, data):
        if self.clientUsername == "":
            if data in clientList:
                sendMessage = data + ' has already logged in'
                print(sendMessage)
                serverSocket.sendto(sendMessage.encode(), self.clientAddress)
                return
            self.clientUsername = data
            self.check_exists_username(data)
        else: # data should be password
            self.clientAuth = self.check_credentials(self.clientUsername, data)
            if not self.clientAuth:
                sendMessage = 'incorrect password'
                serverSocket.sendto(sendMessage.encode(), self.clientAddress)
                self.clientUsername = ""
            else:
                serverSocket.sendto("successful login".encode(), self.clientAddress) # welcome user to forum
                clientList.append(self.clientUsername)
                serverSocket.sendto('display commands'.encode(), self.clientAddress)
            

    def process_exit(self):
        print(self.clientUsername + ' exited')
        print('Waiting for clients')
        clientList.remove(self.clientUsername)
        serverThreads.pop(self.clientAddress)
        serverSocket.sendto('user exited'.encode(), self.clientAddress)

    def file_send(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(serverAddress)
        fileSend = open(self.fileToSend, "rb")
        fileData = fileSend.read(1024)
        print("Sending file...")
        while fileData:
            s.send(fileData)
            fileData = fileSend.read(1024)
        fileSend.close()
        s.shutdown(2)
        s.close()
        print(self.fileToSend.split('-')[1] + ' downloaded from Thread ' + self.fileToSend.split('-')[0])
        self.fileToSend = ""

    def check_credentials(self, username, password):
        with open('credentials.txt', 'r+') as fp:
            lines = fp.readlines()
            for line in lines:
                savedDetails = line.split()
                if username == savedDetails[0] and password == savedDetails[1]:
                    print(username + ' successful login')
                    return True
                elif username == savedDetails[0] and password != savedDetails[1]:
                    print('Incorrect password')
                    return False
            fp.writelines(username + ' ' + password + '\n')
            print(username + ' successfully logged in')
            return True

    def check_exists_username(self, username):
        with open('credentials.txt') as fp:
            lines = fp.readlines()
            for line in lines:
                savedDetails = line.split()
                if (username == savedDetails[0]):
                    send_message = 'existing user password request'
                    serverSocket.sendto(send_message.encode(), self.clientAddress)
                    return True
            print('New user')
            send_message = 'new user password request'
            serverSocket.sendto(send_message.encode(), self.clientAddress)
            return False

    def create_thread(self, message):
        print(self.clientUsername + ' issued CRT command')
        message = message.split()
        if os.path.isfile(message[1]):
            sendMessage = 'Thread ' + message[1] + ' exists'
            print(sendMessage)
            serverSocket.sendto(sendMessage.encode(), self.clientAddress)
        else:
            with open(message[1], 'a+') as f:
                f.write(self.clientUsername + '\n')
            t1 = ThreadInfo(message[1], 0, self.clientUsername)
            threads.append(t1)
            sendMessage = 'Thread ' + message[1] + ' created'
            print(sendMessage)
            serverSocket.sendto(sendMessage.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def post_message(self, message):
        global threads
        message = message.split(' ', 2) # MSG THREAD STRING
        if os.path.isfile(message[1]): # thread exists
            print(self.clientUsername + ' issued MSG command')
            for thread in threads:
                if (thread.name == message[1]):
                    thread.nMessages += 1
                    with open(message[1], 'a+') as fp:
                        fp.write(str(thread.nMessages) + ' ' + self.clientUsername + ': ' + message[2] + '\n')
                        print('Message posted to ' + message[1] + ' thread')
                        response = 'Message posted to ' + message[1] + ' thread'
                        serverSocket.sendto(response.encode(), self.clientAddress)
        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def delete_message(self, message):
        global threads
        message = message.split()
        if os.path.isfile(message[1]): # thread exists
            for thread in threads:
                if (thread.name == message[1]): 
                    if thread.nMessages < int(message[2]):
                        print('Message does not exist')
                        serverSocket.sendto('Message Does Not Exist'.encode(), self.clientAddress)
                        serverSocket.sendto('display commands'.encode(), self.clientAddress)
                        return
                    with open(message[1], 'r') as fp:
                        lines = fp.readlines()
                    # gotta check if it's an actual message line first
                    counter = 1
                    for line in lines:
                        print(line)
                        if line == lines[0]:
                            continue
                        elif counter == int(message[2]):
                            if line.split()[0].isdigit() and (line.split()[1])[:-1] != self.clientUsername:
                                print(line)
                                print((line.split()[1])[:-1])
                                print(self.clientUsername)
                                response = "Message was sent by another user and cannot be deleted"
                                print(response)
                                serverSocket.sendto(response.encode(), self.clientAddress)
                                serverSocket.sendto('display commands'.encode(), self.clientAddress)
                                return
                            break
                        elif line.split()[0].isdigit(): # dont count uploaded files as messages
                            counter += 1
                    with open(message[1], 'w') as fp:
                        for line in lines:
                            number = line.split()[0]
                            lineList = line.split(' ', 2)
                            if line == lines[0]:
                                fp.write(line)
                            elif number.isdigit() and number != message[2] and number > message[2]:
                                newLine = str(int(lineList[0]) - 1) + ' ' + lineList[1] + ' ' + lineList[2]
                                fp.write(newLine)
                            elif number.isdigit() and number != message[2]:
                                newLine = lineList[0] + ' ' + lineList[1] + ' ' + lineList[2]
                                fp.write(newLine)
                            elif not number.isdigit():
                                fp.write(line)
                    response = "Message has been deleted"
                    print(response)
                    serverSocket.sendto(response.encode(), self.clientAddress)
                    thread.nMessages -= 1 # remove number of messages in that thread
        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def edit_message(self, message):
        message = message.split(' ', 3)
        if os.path.isfile(message[1]): # thread exists
            for thread in threads:
                if (thread.name == message[1]): 
                    if thread.nMessages < int(message[2]):
                        print('Message does not exist')
                        serverSocket.sendto('Message Does Not Exist'.encode(), self.clientAddress)
                        serverSocket.sendto('display commands'.encode(), self.clientAddress)
                        return
            with open(message[1], 'r') as fp:
                lines = fp.readlines()
            counter = 1
            for line in lines:
                if line == lines[0]:
                    continue
                elif counter == int(message[2]):
                    if line.split()[0].isdigit() and (line.split()[1])[:-1] != self.clientUsername:
                        response = "The message was sent by another user and cannot be edited"
                        print('Message cannot be edited')
                        serverSocket.sendto(response.encode(), self.clientAddress)
                        serverSocket.sendto('display commands'.encode(), self.clientAddress)
                        return
                    break
                elif line.split()[0].isdigit(): # dont count uploaded files as messages
                    counter += 1
            with open(message[1], 'w') as fp:
                for line in lines:
                    number = line.split()[0]
                    lineList = line.split(' ', 2)
                    if line == lines[0]:
                        fp.write(line)
                    elif number == message[2]:
                        newLine = number + ' ' + lineList[1] + ' ' + message[3] + '\n'
                        fp.write(newLine)
                    else:
                        fp.write(line)
            response = "Message has been edited"
            print(response)
            serverSocket.sendto(response.encode(), self.clientAddress)
                
        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def list_threads(self):
        print(self.clientUsername + ' issued LST command')
        responseList = []
        for thread in threads:
            responseList.append(thread.name)
        responseList = str(responseList)
        serverSocket.sendto(responseList.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def read_thread(self, message): # need to return files aswell when implemented data structure
        print(self.clientUsername + ' issued RDT command')
        message = message.split()
        messages = []
        if os.path.isfile(message[1]): # thread exists
            print('Thread ' + message[1] + ' read')
            with open(message[1], 'r') as fp:
                lines = fp.readlines()
            for line in lines:
                if line != lines[0]:
                    messages.append(line)
            messages = str(messages)
            serverSocket.sendto(messages.encode(), self.clientAddress)
        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def upload_file(self, message):
        print(self.clientUsername + ' issued UPD command')
        message = message.split()
        if os.path.isfile(message[1]): # see if thread exists
            fileName = message[1] + '-' + message[2]
            if os.path.isfile(fileName): # this file has been uploaded to server
                print('File already exists for thread')
                serverSocket.sendto('File Exists For Thread'.encode(), self.clientAddress)
            else: # can be uploaded
                TCPserverSocket = socket(AF_INET, SOCK_STREAM)
                TCPserverSocket.bind(serverAddress)
                serverSocket.sendto('Initiate File Upload'.encode(), self.clientAddress)
                TCPserverSocket.listen(1)
                TCPclientSockt, TCPclientAddress = TCPserverSocket.accept()
                fileDown = open(fileName, "wb")
                print("Receiving file...")
                while True:
                    fileData = TCPclientSockt.recv(1024)
                    fileDown.write(fileData)
                    if len(fileData) < 1024:
                        break
                print(self.clientUsername + ' uploaded file ' + message[2] + ' to ' + message[1] + ' thread')
                serverSocket.sendto('File Uploaded'.encode(), self.clientAddress)
                with open(message[1], 'a+') as fp:
                    fp.write(self.clientUsername + ' uploaded ' + message[2] + '\n')
                fileDown.close()
                TCPclientSockt.shutdown(2)
                TCPclientSockt.close()
                TCPserverSocket.close()

        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def download_file(self, message):
        print(self.clientUsername + ' issued DWN command')
        message = message.split()
        if os.path.isfile(message[1]): # see if thread exists
            fileName = message[1] + '-' + message[2]
            if not os.path.isfile(fileName): # this file has NOT been uploaded to server
                print(message[2] + ' does not exist in Thread ' + message[1])
                serverSocket.sendto('File Does Not Exist For Thread'.encode(), self.clientAddress)
            else: # can be downloaded
                serverSocket.sendto('Initiate File Download'.encode(), self.clientAddress)
                self.fileToSend = fileName
        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)

    def remove_thread(self, message):
        message = message.split()
        if os.path.isfile(message[1]): # see if thread exists
            for thread in threads:
                if (thread.name == message[1]):
                    if (self.clientUsername == thread.owner):
                        os.remove(message[1])
                        threads.remove(thread)
                        for file in os.listdir('.'):
                            uploadedFileNames = thread.name + '-'
                            if file.startswith(uploadedFileNames):
                                os.remove(file)
                        print('Thread ' + message[1] + ' removed')
                        serverSocket.sendto('Thread Deleted'.encode(), self.clientAddress)
                    else:
                        print('Thread ' + message[1] + ' cannot be removed')
                        serverSocket.sendto('User Does Not Own Thread'.encode(), self.clientAddress)
        else:
            print('Incorrect thread specified')
            serverSocket.sendto('Thread Does Not Exist'.encode(), self.clientAddress)
        serverSocket.sendto('display commands'.encode(), self.clientAddress)


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    if clientAddress in serverThreads:
        serverThreads[clientAddress].process_data(data.decode())
    else:
        clientThread = ClientThread(clientAddress)
        serverThreads[clientAddress] = clientThread
        clientThread.start()
        clientThread.process_data(data.decode())

