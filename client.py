"""
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    References:
        Used sample code by Wei Song (Tutor)
"""
from socket import *
import sys

#Server would be running on the same host as Client
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_PORT ======\n")
    exit(0)

serverPort = int(sys.argv[1])
serverAddress = ("127.0.0.1", serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_DGRAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)


def enter_username():
    global serverAddress
    username = input("Enter username: ")
    clientSocket.sendto(username.encode(), serverAddress)

def create_thread(command):
    global serverAddress
    if len(command) == 2:
        message = command[0] + ' ' + command[1]
        clientSocket.sendto(message.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode()
        print(data)
        return True
    else:
        print('Incorrect Syntax for CRT')
        return False

def post_message(command):
    global serverAddress
    if len(command) == 3:
        message = command[0] + ' ' + command[1] + ' ' + command[2]
        clientSocket.sendto(message.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print(data)
            return True # it's true since smth is sent to the server
        else:
            print(data)
            return True
    else:
        print('Incorrect Syntax for MSG')
        return False # false since nothing was sent to server
        


def delete_message(command):
    global serverAddress
    if len(command) == 3 and command[2].isdigit():
        message = command[0] + ' ' + command[1] + ' ' + str(command[2])
        clientSocket.sendto(message.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print(data)
            return True
        elif data == 'Message Does Not Exist':
            print(data)
            return True
        elif data == 'Message was sent by another user and cannot be deleted':
            print(data)
            return True
        else:
            print(data)
            return True
    else:
        print('Incorrect Syntax for DLT')
        return False

def edit_message(command):
    global serverAddress
    if len(command) == 4 and command[2].isdigit():
        message = command[0] + ' ' + command[1] + ' ' + command[2] + ' ' + command[3]
        clientSocket.sendto(message.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print(data)
            return True
        elif data == 'Message Does Not Exist':
            print(data)
            return True
        elif data == 'The message was sent by another user and cannot be edited':
            print(data)
            return True
        else:
            print(data)
            return True
    else:
        print('Incorrect Syntax for EDT')
        return False

def list_threads(command):
    global serverAddress
    if len(command) == 1:
        clientSocket.sendto('LST'.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode() # data should contain a list of servers. print it one by one
        data = eval(data)
        if not data:
            print('No threads to list')
        else:
            print('List of active threads:')
            for thread in data:
                print(thread)
        return True
    else:
        print('Incorrect Syntax for LST')
        return False

def read_thread(command):
    if len(command) == 2:
        message = command[0] + ' ' + command[1]
        clientSocket.sendto(message.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print('Thread ' + command[1] + ' does not exist')
            return True
        data = eval(data)
        if not data:
            print('Thread ' + command[1] + ' is empty')
            return True
        else:
            for messages in data:
                print(messages.rstrip())
            return True
    else:
        print('Incorrect Syntax for RDT')
        return False

def upload_file(command):
    if len(command) == 3:
        message = command[0] + ' ' + command[1] + ' ' + command[2]
        clientSocket.sendto(message.encode(), serverAddress)
        data = clientSocket.recv(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print(data)
            return True
        elif data == 'File Exists For Thread':
            print('File already exists for thread')
            return True
        elif data == 'Initiate File Upload':
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(serverAddress)
            print("Sending file...")
            fileSend = open(command[2], "rb")
            fileData = fileSend.read(1024)
            while fileData:
                s.send(fileData)
                fileData = fileSend.read(1024)
            fileSend.close()
            s.shutdown(2)
            s.close()
            data, clientAddress = clientSocket.recvfrom(1024)
            data = data.decode()
            if data == 'File Uploaded':
                print(command[2] + ' uploaded to ' + command[1] + ' thread')
            return True
    else:
        print('Incorrect Syntax for UPD')
        return False

def download_file(command):
    if len(command) == 3:
        message = command[0] + ' ' + command[1] + ' ' + command[2]
        clientSocket.sendto(message.encode(), serverAddress)
        data, clientAddress = clientSocket.recvfrom(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print(data)
            return True
        elif data == 'File Does Not Exist For Thread':
            print('File does not exist in Thread ' + command[1])
            return True
        elif data == 'Initiate File Download':
            TCPserverSocket = socket(AF_INET, SOCK_STREAM)
            TCPserverSocket.bind(serverAddress)
            clientSocket.sendto('Initiate File Send'.encode(), serverAddress)
            TCPserverSocket.listen(1)
            TCPclientSockt, TCPclientAddress = TCPserverSocket.accept()
            fileDown = open(command[2], "wb")
            print("Receiving file...")
            while True:
                fileData = TCPclientSockt.recv(1024)
                fileDown.write(fileData)
                if len(fileData) < 1024:
                    break
            fileDown.close()
            TCPclientSockt.shutdown(2)
            TCPclientSockt.close()
            TCPserverSocket.close()
            print(command[2] + ' downloaded from thread ' + command[1])
            return True
    else:
        print('Incorrect Syntax for DWN')
        return False

def remove_thread(command):
    if len(command) == 2:
        message = command[0] + ' ' + command[1]
        clientSocket.sendto(message.encode(), serverAddress)
        data, clientAddress = clientSocket.recvfrom(1024)
        data = data.decode()
        if data == 'Thread Does Not Exist':
            print(data)
            return True
        elif data == 'User Does Not Own Thread':
            print('The thread was created by another user and cannot be removed')
            return True
        elif data == 'Thread Deleted':
            print('The thread ' + command[1] + ' has been removed')
    else:
        print('Incorrect Syntax for RMV')
        return False
    return True

def exit_server(command):
    global serverAddress
    if len(command) == 1:
        print('Goodbye')
        clientSocket.sendto('XIT'.encode(), serverAddress) 
        return True
    else:
        print('Incorrect Syntax for XIT')
        return False

def display_commands():
    command = input("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: ")
    if command == "":
        print('Invalid Command')
        return False
    operation = command.split()[0]
    if operation == 'XIT':
        command = command.split()
        commandSent = exit_server(command)
        if commandSent:
            clientSocket.close()
            quit() 
    elif operation == 'CRT':
        command = command.split()
        commandSent = create_thread(command)
    elif operation == 'MSG':
        command = command.split(' ', 2)
        commandSent = post_message(command)
    elif operation == 'DLT':
        command = command.split()
        commandSent = delete_message(command)
    elif operation == 'EDT':
        command = command.split(' ', 3)
        commandSent = edit_message(command)
    elif operation == 'LST':
        command = command.split()
        commandSent = list_threads(command)
    elif operation == 'RDT':
        command = command.split()
        commandSent = read_thread(command)
    elif operation == 'UPD':
        command = command.split()
        commandSent = upload_file(command)
    elif operation == 'DWN':
        command = command.split()
        commandSent = download_file(command)
    elif operation == 'RMV':
        command = command.split()
        commandSent = remove_thread(command)
    else:
        print('Invalid Command')
        commandSent = False

    return commandSent

enter_username()

while True:
    commandSent = False
    # receive response from the server
    data = clientSocket.recv(1024)
    receivedMessage = data.decode()
    # parse the message received from server and take corresponding actions
    if receivedMessage == "":
        print("Message from server is empty!")
    elif receivedMessage == "incorrect password":
        print('Invalid password')
        enter_username()
    elif receivedMessage.split(' ',1)[1] == 'has already logged in':
        print(receivedMessage)
        enter_username()
    elif receivedMessage == "existing user password request":
        password = input("Enter password: ")
        clientSocket.sendto(password.encode(), serverAddress)
    elif receivedMessage == "new user password request":
        password = input("New user, enter password: ")
        clientSocket.sendto(password.encode(), serverAddress)
    elif receivedMessage == "successful login":
        print('Welcome to the forum')
    elif receivedMessage == "display commands":
        while not commandSent:
            commandSent = display_commands()
    elif receivedMessage == "user exited":
        break
    else:
        print("Message from server makes no sense")

# close the socket
clientSocket.close()
