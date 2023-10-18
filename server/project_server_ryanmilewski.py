#CS4850 Networks Project (server)
#Name: Ryan Milewski (rsmbby)
#Date: 09/21/2023
#Student Number: 18217022
#Description: This implements the server side of the project V2 and allows for users to login, create users, send messages and logout.

#TODO: Finish implementing send, sendall. Will also need to add all connected sockets to the connectionArr and remove them when disconnecting. Can send messages by accessing all sockets in the array.


#setting IP Addresss (localhost) and my port of 1 + 7022 which is my student ID.
import socket
import sys
from _thread import *
import threading

print_lock = threading.Lock()
ipaddr = "127.0.0.1"
port = 17022
MAXCLIENTS = 3
#use dictionary to store who is currently logged in.
loggedIn = {}
#array to store all active sockets
connectionArr = []
def threaded(clientsocket, address):
    with clientsocket:
        while True:
            #get the incoming data using recv with a 1024 byte buffer
            dataRecv = clientsocket.recv(1024)
            # if no data is recieved, then break out and close the connection.
            if not dataRecv:
                break
            #decode the data and split it accordingly
            decodedData = dataRecv.decode()
            dataArr = decodedData.split(' ')
            if dataArr[0] == "login":
                #if we get to login, go to the login function, passing it the username and password recieved
                returndata = loginUser(dataArr[1], dataArr[2], address)
            elif dataArr[0] == "newuser":
                #if we are creating a new user, pass it to the setupAccount function with username and password recieved
                returndata = setupAccount(dataArr[1], dataArr[2])
            elif dataArr[0] == "send" and dataArr[1] == "all":
                #we know that the message is stored in the 3rd element of the data array and on so we will extract it and restore the message
                msgArr = (dataArr[3:])
                #rejoin the message and add the spaces back
                message = " ".join(msgArr)
                #set the return message to be the username plus the message.
                returndata = sendToAll(dataArr[1], message)
            elif dataArr[0] == "send":
                #we know that the message is stored in the 3rd element of the data array and on so we will extract it and restore the message
                msgArr = (dataArr[3:])
                #rejoin the message and add the spaces back
                message = " ".join(msgArr)
                #set the return message to be the username plus the message.
                returndata = sendTo(dataArr[2], dataArr[1], message)      
            elif dataArr[0] == "who":
                returndata = who(dataArr[1])
            elif dataArr[0] == "logout":
                #if the user is logging out, we will prompt all devices to let them know that the user left the chat room.
                returndata = "> " + dataArr[1] + " left."
                print(dataArr[1] + " logout.")
            else:
                returndata = "> an error occured, please check the syntax of your command and try again."
            #we will send all the data back after going through one of those functions.
            clientsocket.sendall(bytes(returndata, 'utf-8'))

def who(username):
    print(loggedIn.keys())
    response = ", ".join(loggedIn.keys())
    return response

#helper function for when the user is trying to login
def loginUser(username, password, address):
    global loggedIn
    #try to open the file and perform the login, if unable to open because the file doesn't exist, then throw an error.
    try:
        #open file and scan it line by line
        with open('users.txt') as fp:
                for line in fp:
                    split = []
                    #remove leading and trailing whitespace, remove all formatting characters such as () and ,
                    data = line.strip()
                    data = data.replace("(", "")
                    data = data.replace(")","")
                    data = data.replace(",", "")
                    split = data.split(" ")
                    #parsed so split[0] is the username and split[1] is password. If they match the ones from client, then login is confirmed
                    if split[0] == username and split[1] == password:
                        print(username + " login.")
                        loggedIn[username] = address
                        return "> login confirmed."
        #otherwise login is denied and returned back to user.
        return "> Denied. User name or password incorrect"
    except FileNotFoundError:
        print("no users found.")
        return "> No users have been created. Please create a new user before trying to login."
    except:
        print("File operation error.")
        return "> Error, please repeat last operation."

def setupAccount(username, password):
    #opening with x will cause the file to be created if it does not exist. (Python 3.3 feature)
    try:
        file = open("users.txt","x")
        file.close()
    except:
        #if the file already exists, we will ignore the error and do nothing.
        pass
    with open('users.txt') as f:
        #parse line by line
        for line in f:
            split = []
            #remove leading and trailing whitespace, remove all formatting characters such as () and ,
            data = line.strip()
            data = data.replace("(", "")
            data = data.replace(")","")
            data = data.replace(",", "")
            split = data.split(" ")
            #username stored in split[0] so check it if the username is found in the file, deny the creation of the user.
            if split[0] == username:
                return "> Denied. User account already exists."
    #if the username is good, we create the user by opening the file for writing
    file = open("users.txt","a+")
    #write to the file with the given file formatting
    file.write("\n(" + username + ", " + password + ")")
    file.close()
    #print success message
    print("New user account created.")
    return "> New user account created. Please login"

def sendTo(toUsername, fromUsername, message):
    pass

def sendToAll(fromUsername, message):
    pass
def loop():
    print("My chat room server. Version One.\n\n")
    #create server socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #try to bind and start listening
        serversocket.bind((ipaddr, port))
        serversocket.listen(MAXCLIENTS)
    except socket.error as error:
        #if the socket is unable to bind or start listening, exit safely and respond with the error message.
        print("Error on active socket: ",error)
        serversocket.close()
        sys.exit()
    while True:
        try:
            #wating for connections, will accept when one is recieved.
            (clientsocket, address) = serversocket.accept()
            connectionArr.append(clientsocket)
            start_new_thread(threaded,(clientsocket,address[1],))
        except:
            serversocket.close()
            sys.exit()

if __name__ == "__main__":
    loop()