import socket
import threading
import time
from datetime import datetime
import sys

# Estrutura de dados para o timer compartilhado
timers={}
timers_lock = threading.Lock()

# Lista para armazenar os sockets dos clientes
clientes = []
clientes_lock = threading.Lock()

def processar_comando(comando, socket_cliente):
    global dados_timer
    partes = comando.split()
    
    if len(partes) >= 2 and partes[0] == "timer":
        try:
            valor = int(partes[1])
            unidade = partes[2] if len(partes) > 2 else "segundos"
            duracao = valor * 60 if unidade == "minutos" else valor
            
            with timers_lock:
                timers[socket_cliente] = {"tempo_final": time.time() + duracao, "executando": True}
            
            socket_cliente.send(f"Timer iniciado por {valor} {unidade}.".encode())
            print(f"Cliente {socket_cliente.getpeername()} iniciou um timer de {valor} {unidade}.")

            # Timer rodando em background
            threading.Thread(target=aguardar_timer, args=(socket_cliente,), daemon=True).start()
        except Exception as e:
            socket_cliente.send(b"Comando invalido.")
            print(f"Erro ao processar comando 'timer': {e}")

    elif comando == "quanto falta?":
        with timers_lock:
            if socket_cliente in timers and timers[socket_cliente]["executando"]:
                restante = max(0, int(timers[socket_cliente]["tempo_final"] - time.time()))
                socket_cliente.send(f"Tempo restante: {restante} segundos".encode())
            else:
                socket_cliente.send(b"Nenhum timer em execucao.")

    elif comando == "stop":
        with timers_lock:
            if socket_cliente in timers and timers[socket_cliente]["executando"]:
                timers[socket_cliente]["executando"] = False
                timers[socket_cliente]["tempo_final"] = None
                socket_cliente.send(b"Timer interrompido.")
                print(f"Timer do cliente {socket_cliente.getpeername()} interrompido.")
            else:
                socket_cliente.send(b"Nenhum timer em execucao.")
        
    elif comando == "sair":
        try:
            # Envia a mensagem de desconexão
            socket_cliente.send(b"Desconectando...")
            print(f"Cliente {socket_cliente.getpeername()} solicitou desconexão.")
        except Exception as e:
            print(f"Erro ao enviar mensagem de desconexão: {e}")
        finally:
            # Fecha o socket e remove o cliente da lista (se ainda estiver na lista)
            with clientes_lock:
                if socket_cliente in clientes:
                    clientes.remove(socket_cliente)
            socket_cliente.close()
            print(f"Cliente {socket_cliente.getpeername()} desconectado.")

def aguardar_timer(socket_cliente):
    while True:
        with timers_lock:
            if socket_cliente not in timers or not timers[socket_cliente]["executando"]:
                break
            restante = max(0, int(timers[socket_cliente]["tempo_final"] - time.time()))
        
        if restante == 0:
            with timers_lock:
                timers["executando"] = False
                timers["tempo_final"] = None
            
            socket_cliente.send(b"Timer finalizado.")
            print(f"Timer do cliente {socket_cliente.getpeername()} finalizado.")
            break

        time.sleep(1)

def enviar_horario(socket_cliente):
    """Thread para enviar a data e hora a cada 30 segundos."""
    while True:
        try:
            now = datetime.now().strftime("%H:%M:%S")
            socket_cliente.send(f"Horario atual: {now}".encode('utf-8'))
            time.sleep(20)  # Envia a cada 30 segundos
        except Exception as e:
            print(f"Erro ao enviar horário: {e}")
            break

def lidar_com_cliente(socket_cliente):
    try:
        with clientes_lock:
            clientes.append(socket_cliente)
        socket_cliente.send(f"{datetime.now().strftime('%H:%M:%S')}: CONECTADO!!\nDigite um comando: ".encode())
        print(f"Novo cliente conectado: {socket_cliente.getpeername()}")

        # Thread para enviar horário a cada 30 segundos
        thread_enviar_horario = threading.Thread(target=enviar_horario, args=(socket_cliente,), daemon=True)
        thread_enviar_horario.start()

        # Thread para receber comandos
        thread_receber_comandos = threading.Thread(target=receber_comandos, args=(socket_cliente,), daemon=True)
        thread_receber_comandos.start()

        # Aguarda o término das threads
        thread_enviar_horario.join()
        thread_receber_comandos.join()

    except Exception as e:
        print(f"Erro ao lidar com o cliente: {e}")

def receber_comandos(socket_cliente):
    while True:
        try:
            dados = socket_cliente.recv(1024).decode().strip()
            if not dados:
                print(f"Cliente {socket_cliente.getpeername()} desconectado.")
                with clientes_lock:
                    if socket_cliente in clientes:
                        clientes.remove(socket_cliente)
                socket_cliente.close()
                break
            processar_comando(dados, socket_cliente)
        except Exception as e:
            print(f"Erro ao receber comandos: {e}")
            with clientes_lock:
                if socket_cliente in clientes:
                    clientes.remove(socket_cliente)
            socket_cliente.close()
            break

def iniciar_servidor(limite_clientes):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("127.0.0.1", 12345))
    servidor.listen(5)
    print("Servidor rodando na porta 12345...")
    
    while True:
        try:
            socket_cliente, endereco = servidor.accept()
            with clientes_lock:
                if len(clientes) < limite_clientes:
                    threading.Thread(target=lidar_com_cliente, args=(socket_cliente,), daemon=True).start()
                else:
                    socket_cliente.send(b"Limite de clientes atingido. Tente novamente mais tarde.")
                    socket_cliente.close()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python server.py <limite_clientes>")
        sys.exit(1)
    
    limite_clientes = int(sys.argv[1])
    iniciar_servidor(limite_clientes)