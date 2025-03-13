# Relógio-Timer

Este é um projeto da disciplina de Redes e Conexões, cujo objetivo é introduzir conceitos fundamentais de comunicação cliente-servidor, protocolo TCP, threads e sockets em Python. O sistema implementa um servidor que gerencia conexões de clientes, fornece a hora atualizada periodicamente e permite a interação dos clientes com um timer.

## Estrutura do Projeto
O projeto consiste em dois arquivos principais:

- **server.py** (Servidor):
  - Gerencia múltiplas conexões de clientes.
  - Envia periodicamente a hora atual para os clientes conectados.
  - Processa comandos recebidos dos clientes, como iniciar, verificar e interromper timers.
  - Utiliza threads para lidar com cada cliente individualmente.

- **client.py** (Cliente):
  - Conecta-se ao servidor.
  - Envia comandos ao servidor, como iniciar timers e consultar o tempo restante.
  - Recebe e exibe mensagens enviadas pelo servidor, incluindo o horário atualizado e respostas aos comandos.
  - Implementa threads para gerenciar simultaneamente a entrada do usuário e a recepção de mensagens do servidor.

## Funcionalidades Implementadas

- O servidor aceita conexões de múltiplos clientes simultaneamente.
- Envio automático da hora atual do servidor para os clientes conectados a cada 20 segundos.
- Comandos suportados pelo cliente:
  - `timer XX segundos/minutos`: Inicia um timer pelo tempo especificado.
  - `quanto falta?`: Consulta o tempo restante do timer ativo.
  - `stop`: Interrompe um timer em execução.
  - `sair`: Desconecta o cliente do servidor.

## Como Executar

### Iniciando o Servidor
No terminal, execute o seguinte comando para iniciar o servidor, definindo um limite de conexões simultâneas:
```sh
python server.py <limite_conexoes>
```
Exemplo:
```sh
python server.py 5
```
Se configurado corretamente, a seguinte mensagem será exibida:
```
Servidor rodando na porta 12345...
```

### Iniciando o Cliente
Em outro terminal, execute:
```sh
python client.py
```
O cliente exibirá um menu de comandos disponíveis e aguardará a entrada do usuário.

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

## Tecnologias Utilizadas
- Python 3
- Biblioteca `socket` para comunicação via TCP
- Biblioteca `threading` para manipulação de múltiplas conexões
- Biblioteca `datetime` para gestão do horário
- Biblioteca `sys` para manipulação de argumentos

## Autores
- **Lais Kumasaka Santos**
- **Maria Eduarda Souza Araujo Pompiani Costa** 

Projeto desenvolvido como parte da disciplina de Redes e Conexões - Pontifícia Universidade Católica de Campinas
