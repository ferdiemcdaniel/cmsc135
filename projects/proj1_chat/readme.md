MACHINE PROBLEM #1 Chat


This is a simple application that links different users over to a network. Similar to various existing chat programs, the server has the basic commands to let users converse in different channels.
Getting Started
    1. There are 2 files: server.py and client.py
    2. Any willing user to act as server shall run server.py with the following arguements:
        a. hostname
        b. port number
    3. Once the server is run, anyone can use the chat service by connecting to the server with the following:
        a. client name
        b. hostname
        c. port number

Clients
    A client is a potential user of the services offered by a running server. In this application, there are three commands a client can use:

    1. /list - This lets the user know the existing channel rooms
    2. /join - Once the user has decided which room to join, this command allows users to converse in that channel
    3. /create - There might be instances when there is no available channel, this command will let a user create a channel room and wait for potential users to come in


CREDITS
    This codebase is a solution to a Machine Problem presented to Professor John Ulra on February 16, 2017 in partial fulfillment of the requirements for CS 135.
    
    All work is done by Ferdinand McDaniel Amano
