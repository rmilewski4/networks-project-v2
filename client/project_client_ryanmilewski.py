#CS4850 Networks Project (client)
#Name: Ryan Milewski (rsmbby)
#Date: 09/21/2023
#Student Number: 18217022
#Description: This implements the client side of the project V2 and allows for users to login, create users, send messages and logout.


import socket
import sys
#same address and port as server
ipaddr = "127.0.0.1"
port = 17022
#global variables to check if user is currently logged and what the logged in user's name is.
loginStatus = False
username = ""

try:
    #try and open a connection with server
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ipaddr,port))
except socket.error as error:
    print("Error on active socket: ", error)
    sys.exit()
except:
    #if unable, express an error and exit safely.
    print("Client Socket couldn't be opened! Try again!")
    sys.exit()

#helper function to actually send some data to the server
def sendToServer(data):
    try:
        #try and send the data; encoded through utf-8
        clientsocket.sendall(bytes(data, 'utf-8'))
    except socket.error as error:
        #safely handle error and exit program
        print("Error on active socket: ", error)
        clientsocket.close()
        sys.exit()
#helper function to recieve data from the server
def receiveFromServer():
    try:
        #try and recieve the data over the socket with a 1024 byte buffer
        dataRecv = clientsocket.recv(1024)
        #decode the data since it was encoded at the server.
        dataDecoded  = dataRecv.decode()
        #print the decoded message to the client and return it in case a function will use the response.
        print(dataDecoded)
        return dataDecoded
    except socket.error as error:
        print("Error on active socket: ", error)
        clientsocket.close()
        sys.exit()


#helper function to logout
def logout():
    #establish link to global variables made above.
    global username, loginStatus
    #if the user is logged out, print an error message and exit the function
    if not loginStatus:
        print("You must first login to logout.")
        return
    #otherwise send the logout command plus the name of the user logging out
    dataSend = "logout " + username
    #send + recieve from the server
    sendToServer(dataSend)
    receiveFromServer()
    #close the connection
    clientsocket.close()
    #reset our global variables
    username = ""
    loginStatus = False
    #finish the program since the user has exited the chat client.
    sys.exit()
    

def send(message, toUsername):
    #if the user is not logged in, give a prompt to login first and exit the function.
    if not loginStatus:
        print("> Denied. Please login first.")
        return
    #checking to make sure message is valid length, returning if not.
    if len(message) > 256 or len(message) < 1:
        print("Message should be between 1 and 256 characters")
        return
    #checking username length is valid
    if len(toUsername) > 32 or len(toUsername) < 3:
        print("Username should be between 3 and 32 characters")
        return
    #formatting message to send to server with username and message.
    dataSend = "send " + username + " " + toUsername + " " + message
    #send message and recieve from server.
    sendToServer(dataSend)
    receiveFromServer()

#login helper function
def login(splitInput):
    global loginStatus, username
    #if user is logged in, prompt a message to logout first and exit the function.
    if loginStatus:
        print("Please logout first before trying to login")
        return
    #checking username length is valid
    if len(splitInput[1]) > 32 or len(splitInput[1]) < 3:
        print("Username should be between 3 and 32 characters")
        return
    #checking password length is valid
    if len(splitInput[2]) < 4 or len(splitInput[2]) > 8:
        print("Password should be between 4 and 8 characters")
        return
    dataSend = splitInput[0] + " " + splitInput[1] + " " + splitInput[2]
    sendToServer(dataSend)
    #send + recieve
    dataRecvDecoded = receiveFromServer()
    #if login was confirmed, update global variables
    if "confirmed" in dataRecvDecoded:
        loginStatus = True
        username = splitInput[1]

#new user helper function
def newuser(splitInput):
    #if user is logged in, prompt a message to logout first and exit the function.
    if loginStatus:
        print("Please logout first before creating a new user.")
        return
    #checking username is valid length
    if len(splitInput[1]) > 32 or len(splitInput[1]) < 3:
        print("Username should be between 3 and 32 characters")
        return
    #since our users.txt file uses a format that stores the credentials in parenthesis with a comma separating, we can't allow these to be used for the credentials as it will mess with our login function.
    if "," in splitInput[1] or "(" in splitInput[1] or ")" in splitInput[1]:
        print("Invalid Character. Please do not use commas , or parenthesis ( or ) in your username.")
        return
    #checkig password is valid length
    if len(splitInput[2]) < 4 or len(splitInput[2]) > 8:
        print("Password should be between 4 and 8 characters")
        return
    if "," in splitInput[2] or "(" in splitInput[2] or ")" in splitInput[2]:
        print("Invalid Character. Please do not use commas , or parenthesis ( or ) in your password.")
        return
    dataSend = splitInput[0] + " " + splitInput[1] + " " + splitInput[2]
    #send + recieve from server
    sendToServer(dataSend)
    receiveFromServer()


def loop():
    print("My chat room client. Version One.\n\n")
    while True:
        #get input and split it
        initInput = input(">")
        splitInput = initInput.split(' ')
        #make command all lowercase to avoid errors
        splitInput[0] = splitInput[0].lower()
        #checking to make sure valid number of arguments for login, then going to helper function
        if splitInput[0] == "login" and len(splitInput) == 3:
            login(splitInput)
        #checking to make sure valid number of arguments for newuser, then going to helper function
        elif splitInput[0] == "newuser" and len(splitInput) == 3:
            newuser(splitInput)
        elif splitInput[0] == "send" and len(splitInput) > 2:
            #recombining message since it was split at the spaces. Ignore the "send" part of the given command
            msgArr = (splitInput[2:])
            #rejoin and add spaces back
            message = " ".join(msgArr)
            send(message, splitInput[1])
        #checking to make sure valid number of arguments for logout, then going to helper function
        elif splitInput[0] == "logout" and len(splitInput) == 1:
            logout()
        else:
            #if input did not match any of the inputs, print that it could not parse the input
            print("Invalid input detected!")


if __name__ == "__main__":
    loop()