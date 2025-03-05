import socket
import threading
import sys

#recebe as mensagens do servidor
def receber_horario(socket_cliente):
    while True:
        try:
            dados = socket_cliente.recv(1024).decode()
            if dados:
                sys.stdout.write("\r" + dados + "\n")  
                sys.stdout.flush()
                sys.stdout.write("Digite um comando: ") 
                sys.stdout.flush()
        except:
            break

#funcao para digitar comandos 
def enviar_comandos(socket_cliente):
    while True:
        comando = input("Digite um comando: ")
        socket_cliente.send(comando.encode())
        if comando.lower() == "stop":
            break

#funcao para conectar ao servidor e recebe mensagens de conexao 
def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("192.168.0.99", 12345))
    print(cliente.recv(1024).decode())
    
    threading.Thread(target=receber_horario, args=(cliente,), daemon=True).start()
    
    enviar_comandos(cliente)
    cliente.close()

if __name__ == "__main__":
    iniciar_cliente()
