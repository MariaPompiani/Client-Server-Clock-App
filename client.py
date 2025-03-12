import socket
import threading
import sys

#recebe as mensagens do servidor
def receber_horario(socket_cliente):
    while True:
        try:
            dados = socket_cliente.recv(1024).decode()
            if not dados:
                break  # Se não receber dados, encerra a thread
            sys.stdout.write("\r" + dados + "\n")  
            sys.stdout.flush()
            sys.stdout.write("Digite um comando: ") 
            sys.stdout.flush()
        except:
            break

def enviar_comandos(socket_cliente):
    while True:
        try:
            comando = input("Digite um comando: ")
            socket_cliente.send(comando.encode())
            if comando.lower() == "stop":
                break
        except:
            break

def iniciar_cliente():
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect(("127.0.0.1", 12345))
        print(cliente.recv(1024).decode())
        
        # Criando threads separadas para envio e recebimento
        thread_receber = threading.Thread(target=receber_horario, args=(cliente,), daemon=True)
        thread_enviar = threading.Thread(target=enviar_comandos, args=(cliente,), daemon=True)
        
        thread_receber.start()
        thread_enviar.start()
        
        thread_enviar.join()  # Aguarda o término da thread de envio
        cliente.close()
    except Exception as e:
        print(f"Erro ao conectar ao servidor: {e}")

if __name__ == "__main__":
    iniciar_cliente()
