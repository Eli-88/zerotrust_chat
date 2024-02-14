# <Network Monitoring>

## Description

A very simple command line interface for chat service that requires the client to generate and shared its secret key to be use for encrypting chat messages. Hence it is known as zero trust as it does not require any server or external services to generate the keys.

## Usage

Simply just run: `go run src/cmd/main.go <own port number>` to start the chat service

Commands
- `?` to display all active client
- `> <active client>` to switch to active client for chat
- `just type any messages` send messages to current active client 
- `$ <ip addr>` connect to other chat client and your it will be switch to your current active client

## Design
![Alt text](images/secret_key_exchange.png?raw=true "Network Monitor Design")

## Usage
- launch apps of port 3000 and 4000 respectively: i.e. `python app.py 3000`
- the app will periodically broadcast their ip addresses when connected to the same network and it will display in the main screen
- click connect on the ip address you wish to communicate to and it will launch a chat box
- may type in message in message box and click send
- upon clicking send your client side will pop up a new chat box with first text messages

### Main Screen
![Alt text](images/main_screen.png?raw=true "Main Screen")

### Chat Box
![Alt text](images/chat_box.png?raw=true "Chat Box")

### Pop Up Chat Box
![Alt text](images/pop_up_chat.png?raw=true "Pop Up Chat Box")
