#Lais Kumasaka Santos | RA:23006548
#Maria Eduarda Souza Araujo Pompiani Costa | RA:23005493

import socket
import threading
import time
from datetime import datetime
import sys

# Estrutura de dados para o timer compartilhado
timers = {}
timers_lock = threading.Lock()

# Lista sockets dos clientes
clientes = []
clientes_lock = threading.Lock()

def processar_comando(comando, socket_cliente):
    global timers
    partes = comando.split()

    if len(partes) >= 2 and partes[0] == "timer":
        try:
            valor = int(partes[1])
            unidade = partes[2] if len(partes) > 2 else "segundos"
            duracao = valor * 60 if unidade == "minutos" else valor

            with timers_lock:
                if socket_cliente not in timers:
                    timers[socket_cliente] = []

                # Criar um identificador único para o timer
                timer_id = f"Timer{len(timers[socket_cliente]) + 1}"

                # Adicionar o novo timer à lista
                timers[socket_cliente].append({
                    "id": timer_id,
                    "tempo_final": time.time() + duracao,
                    "executando": True
                })

            socket_cliente.send(f"{timer_id} iniciado por {valor} {unidade}.".encode("utf-8"))
            print(f"Cliente {socket_cliente.getpeername()} iniciou {timer_id} de {valor} {unidade}.")

            # Iniciar uma nova thread para monitorar o timer
            threading.Thread(target=aguardar_timer, args=(socket_cliente, timer_id), daemon=True).start()

        except Exception as e:
            socket_cliente.send("Comando inválido.".encode("utf-8"))
            print(f"Erro ao processar comando 'timer': {e}")

    elif partes[0].lower() == "quanto" and partes[1].lower() == "falta" and len(partes) == 3:
        timer_id = partes[2].strip("?").lower()  # Remove "?" e padroniza para minúsculas

        with timers_lock:
            timer_atual = next((t for t in timers.get(socket_cliente, []) if t["id"].lower() == timer_id), None)

            if timer_atual and timer_atual["executando"]:
                restante = max(0, int(timer_atual["tempo_final"] - time.time()))
                if restante > 60:
                    restante1 = restante/60
                    socket_cliente.send(f"Tempo restante para {timer_atual['id']}: {restante1} minutos.".encode("utf-8"))
                else:
                    socket_cliente.send(f"Tempo restante para {timer_atual['id']}: {restante} segundos.".encode("utf-8"))
            else:
                socket_cliente.send(f"{timer_id} não está em execução.".encode("utf-8"))


    elif partes[0].lower() == "stop" and len(partes) == 2:
        timer_id = partes[1].lower()  # Padroniza para minúsculas

        with timers_lock:
            timer_atual = next((t for t in timers.get(socket_cliente, []) if t["id"].lower() == timer_id), None)

            if timer_atual and timer_atual["executando"]:
                timer_atual["executando"] = False
                socket_cliente.send(f"{timer_atual['id']} interrompido.".encode("utf-8"))
                print(f"{timer_atual['id']} do cliente {socket_cliente.getpeername()} interrompido.")
            else:
                socket_cliente.send(f"{timer_id} não está em execução.".encode("utf-8"))

    elif comando == "sair":
        try:
            # Envia a mensagem de desconexão
            socket_cliente.send(b"Desconectando...")
            print(f"Cliente {socket_cliente.getpeername()} solicitou desconexão.")
        except Exception as e:
            print(f"Erro ao enviar mensagem de desconexão: {e}")
        finally:
            # Fecha o socket e remove o cliente da lista
            with clientes_lock:
                if socket_cliente in clientes:
                    clientes.remove(socket_cliente)
            socket_cliente.close()
            print(f"Cliente {socket_cliente.getpeername()} desconectado.")

def aguardar_timer(socket_cliente, timer_id):
    while True:
        with timers_lock:
            # Procurar o timer específico do cliente
            timer_atual = next((t for t in timers.get(socket_cliente, []) if t["id"] == timer_id), None)

            if not timer_atual or not timer_atual["executando"]:
                break

            restante = max(0, int(timer_atual["tempo_final"] - time.time()))

        if restante == 0:
            with timers_lock:
                # Finalizar o timer e removê-lo da lista
                timer_atual["executando"] = False

            socket_cliente.send(f"{timer_id} finalizado.".encode("utf-8"))
            print(f"{timer_id} do cliente {socket_cliente.getpeername()} finalizado.")
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
    finally:
        remover_cliente(socket_cliente)  # Chama a nova função


def receber_comandos(socket_cliente):
    while True:
        try:
            dados = socket_cliente.recv(1024).decode().strip()
            if not dados:
                raise ConnectionResetError
            
            processar_comando(dados, socket_cliente)

        except(ConnectionResetError, BrokenPipeError):
            print(f"Cliente {socket_cliente.getpeername()} desconectado abruptamente")
            with clientes_lock:
                if socket_cliente in clientes:
                    clientes.remove(socket_cliente)
                socket_cliente.close()
            break      
        except Exception as e:
            print(f"Erro ao receber comandos: {e}")
            remover_cliente(socket_cliente)  # Chama a nova função
            
    with clientes_lock:
        if socket_cliente in clientes:
            clientes.remove(socket_cliente)
    socket_cliente.close()

def remover_cliente(socket_cliente):
    """Remove um cliente da lista de clientes e fecha sua conexão"""
    with clientes_lock:
        if socket_cliente in clientes:
            clientes.remove(socket_cliente)
    try:
        socket_cliente.close()
    except Exception as e:
        print(f"Erro ao fechar conexão do cliente {socket_cliente.getpeername()}: {e}")
    print(f"Cliente {socket_cliente.getpeername()} removido corretamente.")


def iniciar_servidor(limite_clientes):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("127.0.0.1", 12345))
    servidor.listen(5)
    print("Servidor rodando na porta 12345...")

    while True:
        try:
            socket_cliente, endereco = servidor.accept()
            
            with clientes_lock:
                if len(clientes) <= limite_clientes:  
                    clientes.append(socket_cliente)  
                    threading.Thread(target=lidar_com_cliente, args=(socket_cliente,), daemon=True).start()
                    print(f"Novo cliente conectado: {endereco}.")
                else:
                    print(f"Conexão recusada para {endereco}: limite de {limite_clientes} clientes atingido.")
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

