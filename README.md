# Clock-Timer Server

This is a project for the Networks and Connections course, designed to introduce fundamental concepts of client-server communication, the TCP protocol, threads, and sockets in Python. The system implements a server that manages client connections, periodically provides the current time, and allows clients to interact with a timer.

## Project Structure
The project consists of two main files:

- **`server.py` (Server):**
  - Manages multiple client connections.
  - Periodically sends the current time to connected clients.
  - Processes commands received from clients, such as starting, checking, and stopping timers.
  - Uses threads to handle each client individually.

- **`client.py` (Client):**
  - Connects to the server.
  - Sends commands to the server, such as starting timers and querying the remaining time.
  - Receives and displays messages sent by the server, including the updated time and command responses.
  - Implements threads to simultaneously manage user input and receive messages from the server.

## Implemented Features

- The server accepts connections from multiple clients simultaneously.
- Automatic broadcast of the server's current time to all connected clients every 20 seconds.
- Client-side commands supported:
  - `timer XX segundos/minutos`: Starts a timer for the specified duration.
  - `quanto falta?`: Checks the remaining time on the active timer.
  - `stop`: Stops a running timer.
  - `sair`: Disconnects the client from the server.

## How to Run

### Starting the Server
In a terminal, run the following command to start the server, defining a limit for simultaneous connections:
```sh
python server.py <connection_limit>
```
Example:
```sh
python server.py 5
```
If configured correctly, the following message will be displayed:
```
Servidor rodando na porta 12345...
```

### Starting the Client
In another terminal, run:
```sh
python client.py
```
The client will display a menu of available commands and await user input.

## Exemplo de Uso
```sh
Digite um comando: timer 30 segundos
Timer iniciado por 30 segundos.
Digite um comando: quanto falta?
Tempo restante: 25 segundos
Digite um comando: stop
Timer interrompido.
Digite um comando: sair
Desconectando...
```

## Technologies Used
- Python 3
- `socket` library for TCP communication
- `threading`  library for handling multiple connections
- `datetime` library for time management
- `sys` library for handling command-line arguments

## Authors
- **Lais Kumasaka Santos**
- **Maria Eduarda Souza Araujo Pompiani Costa** 

Project developed as part of the Networks and Connections course at Pontifical Catholic University of Campinas.
