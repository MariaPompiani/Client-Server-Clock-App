#Lais Kumasaka Santos | RA:23006548
#Maria Eduarda Souza Araujo Pompiani Costa | RA:23005493

import socket
import threading
import sys
import queue
import time
import os

# Fila para armazenar mensagens recebidas do servidor
mensagens = queue.Queue()

# Sinalizador para encerrar as threads
encerrar_threads = threading.Event()

def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_legenda():
    """Exibe a legenda comandos disponíveis."""
    print("=== Comandos Disponíveis ===")
    print("1. timer XX segundos/minutos - Inicia um timer.")
    print("2. quanto falta? - Consulta o tempo restante do timer.")
    print("3. stop - Interrompe o timer.")
    print("4. sair - Desconecta do servidor e encerra o cliente.")
    print("============================")
    print()

def receber_horario(socket_cliente):
    """Thread para receber mensagens do servidor e colocá-las na fila."""
    while not encerrar_threads.is_set():
        try:
            dados = socket_cliente.recv(1024).decode()
            if not dados:
                print("Conexão com o servidor encerrada.")
                encerrar_threads.set()
                break
            mensagens.put(dados)  # Adiciona a mensagem à fila
        except ConnectionResetError:
            print("Conexão com o servidor foi resetada.")
            encerrar_threads.set()
            break
        except Exception as e:
            if not encerrar_threads.is_set():
                print(f"Erro ao receber mensagens: {e}")
            break

def exibir_mensagens():
    """Thread para exibir mensagens da fila."""
    while not encerrar_threads.is_set():
        try:
            if not mensagens.empty():
                mensagem = mensagens.get()
                # Exibe a mensagem acima do prompt de comando
                sys.stdout.write("\r" + " " * 50 + "\r")  # Limpa a linha atual
                sys.stdout.write(mensagem + "\n")  # Exibe a mensagem
                sys.stdout.write("Digite um comando: ")  # Mantém o prompt de comando
                sys.stdout.flush()
            time.sleep(0.1)  # Evita uso excessivo da CPU
        except Exception as e:
            if not encerrar_threads.is_set():
                print(f"Erro ao exibir mensagens: {e}")
            break

def enviar_comandos(socket_cliente):
    """Thread para capturar e enviar comandos do usuário."""
    while not encerrar_threads.is_set():
        try:
            comando = input("Digite um comando: ")
            socket_cliente.send(comando.encode())
            if comando.lower() == "sair":
                encerrar_threads.set()  # Sinaliza para encerrar as threads
                time.sleep(0.5)  # Aguarda a mensagem "Desconectando..." ser exibida
                break
        except ConnectionResetError:
            print("Conexão com o servidor foi resetada.")
            encerrar_threads.set()
            break
        except Exception as e:
            if not encerrar_threads.is_set():
                print(f"Erro ao enviar comando: {e}")
            break

def iniciar_cliente():
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect(("127.0.0.1", 12345))
        print("Conectado ao servidor.")
        print(cliente.recv(1024).decode())  # Exibe a mensagem inicial do servidor

        # Limpa a tela e exibe a legenda
        limpar_tela()
        exibir_legenda()

        # Cria threads para envio, recebimento e exibição
        thread_receber = threading.Thread(target=receber_horario, args=(cliente,))
        thread_exibir = threading.Thread(target=exibir_mensagens)
        thread_enviar = threading.Thread(target=enviar_comandos, args=(cliente,))

        thread_receber.start()
        thread_exibir.start()
        thread_enviar.start()

        # Aguarda o término da thread de envio
        thread_enviar.join()

        # Sinaliza para encerrar as threads
        encerrar_threads.set()

        # Aguarda as threads terminarem
        thread_receber.join()
        thread_exibir.join()

        # Fecha o socket do cliente
        cliente.close()
        print("Conexão encerrada.")
        sys.exit(0)
    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor. Verifique se o servidor está rodando.")
    except Exception as e:
        print(f"Erro ao conectar ao servidor: {e}")
    finally:
        if 'cliente' in locals():
            cliente.close()

if __name__ == "__main__":
    iniciar_cliente()