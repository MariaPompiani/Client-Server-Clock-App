import socket
import threading
import time
from datetime import datetime

# Estrutura de dados para o timer compartilhado
dados_timer = {"tempo_final": None, "executando": False}
bloqueio = threading.Lock()

def lidar_com_cliente(socket_cliente):
    socket_cliente.send(f"{datetime.now().strftime('%H:%M:%S')}: CONECTADO!!\nDigite um comando: ".encode())

    # Thread para enviar horário a cada 3 segundos
    threading.Thread(target=enviar_horario, args=(socket_cliente,), daemon=True).start()

    # Thread para receber comandos
    threading.Thread(target=receber_comandos, args=(socket_cliente,), daemon=True).start()

def receber_comandos(socket_cliente):
    while True:
        try:
            dados = socket_cliente.recv(1024).decode().strip()
            if not dados:
                break
            processar_comando(dados, socket_cliente)
        except:
            break

def processar_comando(comando, socket_cliente):
    global dados_timer
    partes = comando.split()
    
    if len(partes) >= 2 and partes[0] == "timer":
        try:
            valor = int(partes[1])
            unidade = partes[2] if len(partes) > 2 else "segundos"
            duracao = valor * 60 if unidade == "minutos" else valor
            with bloqueio:
                dados_timer["tempo_final"] = time.time() + duracao
                dados_timer["executando"] = True
            socket_cliente.send(f"Timer iniciado por {valor} {unidade}.".encode())

            # Timer rodando em background
            threading.Thread(target=aguardar_timer, args=(socket_cliente,), daemon=True).start()
        except:
            socket_cliente.send(b"Comando invalido.")

    elif comando == "quanto falta?":
        with bloqueio:
            if dados_timer["executando"]:
                restante = max(0, int(dados_timer["tempo_final"] - time.time()))
                socket_cliente.send(f"Tempo restante: {restante} segundos".encode())
            else:
                socket_cliente.send(b"Nenhum timer em execucao.")

    elif comando == "stop":
        with bloqueio:
            dados_timer["executando"] = False
            dados_timer["tempo_final"] = None
        socket_cliente.send(b"Timer interrompido.")

def aguardar_timer(socket_cliente):
    while True:
        with bloqueio:
            if not dados_timer["executando"]:
                break
            restante = max(0, int(dados_timer["tempo_final"] - time.time()))
        if restante == 0:
            with bloqueio:
                dados_timer["executando"] = False
                dados_timer["tempo_final"] = None
            socket_cliente.send(b"Timer finalizado.")
            break
        time.sleep(1)

def enviar_horario(socket_cliente):
    while True:
        try:
            socket_cliente.send(f"Horario atual: {datetime.now().strftime('%H:%M:%S')}".encode())
            time.sleep(20)
        except:
            break

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("127.0.0.1", 12345))
    servidor.listen(5)
    print("Servidor rodando na porta 12345...")
    
    while True:
        socket_cliente, _ = servidor.accept()
        threading.Thread(target=lidar_com_cliente, args=(socket_cliente,), daemon=True).start()

if __name__ == "__main__":
    iniciar_servidor()
