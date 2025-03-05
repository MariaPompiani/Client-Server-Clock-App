import socket
import threading
import time
from datetime import datetime

# Comandos para possibilitar a memoria compartilhada 
dados_timer = {"tempo_final": None, "executando": False}

#lock para evitar varias threads ao mesmo tempo
bloqueio = threading.Lock()

#funcao para estabelecer uma conexao com cada cliente
def lidar_com_cliente(socket_cliente):
    socket_cliente.send(f"{datetime.now().strftime('%H:%M:%S')}: CONECTADO!!".encode())


    #funcao para enviar a data e a hora
    def enviar_horario():
        while True:
            try:
                socket_cliente.send(datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode())
                time.sleep(1)
            except:
                break

    #funcao para receber comandos 
    def receber_comandos():
        while True:
            try:
                dados = socket_cliente.recv(1024).decode().strip()
                if dados:
                    processar_comando(dados, socket_cliente)
            except:
                break
    
    #threads de recebimento de comandos e envio do horaio
    threading.Thread(target=enviar_horario, daemon=True).start()
    threading.Thread(target=receber_comandos, daemon=True).start()


def processar_comando(comando, socket_cliente):
    global dados_timer
    partes = comando.split()
    
    #comando timer
    if len(partes) >= 2 and partes[0] == "timer":
        try:
            valor = int(partes[1])
            unidade = partes[2] if len(partes) > 2 else "segundos"
            duracao = valor * 60 if unidade == "minutos" else valor
            with bloqueio:
                dados_timer["tempo_final"] = time.time() + duracao
                dados_timer["executando"] = True
            socket_cliente.send(f"Timer iniciado por {valor} {unidade}.".encode())
        except:
            socket_cliente.send(b"Comando invalido.")

    #comando "quanto falta?"
    elif comando == "quanto falta?":
        with bloqueio:
            if dados_timer["executando"]:
                restante = max(0, int(dados_timer["tempo_final"] - time.time()))
                socket_cliente.send(f"Tempo restante: {restante} segundos".encode())
            else:
                socket_cliente.send(b"Nenhum timer em execucao.")

    #comando stop
    elif comando == "stop":
        with bloqueio:
            dados_timer["executando"] = False
            dados_timer["tempo_final"] = None
        socket_cliente.send(b"Timer interrompido.")

#funcao que cria o socket e conecta as portas
def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("0.0.0.0", 12345))
    servidor.listen(5)
    print("Servidor rodando na porta 12345...")
    
    while True:
        socket_cliente, _ = servidor.accept()
        threading.Thread(target=lidar_com_cliente, args=(socket_cliente,), daemon=True).start()


if __name__ == "__main__":
    iniciar_servidor()
