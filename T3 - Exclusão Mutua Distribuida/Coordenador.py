from threading  import Lock
from enum import Enum 
from _thread import *
import threading
import socket
from datetime import datetime

DEBUG = False
HOST = 'localhost'
PORTA = 3456
executarCoordenador = True
Lock = Lock()
Hostname = socket.gethostname()
print("\n\n\n")
print("[Coordenador] Coordenador entrando em funcionamento.\n    Host: {}.\n    Usando a porta {}.\n    gethostname: {}.\n".format(HOST, PORTA, Hostname))

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sckt.bind((HOST, int(PORTA)))
sckt.listen()

filaDeEspera = []
qtdProcessoAtendido = {}

def printMsg(msg):
    if DEBUG:
        print(msg)

def addQtdProcessoAtendido(processo):
    if processo.id in qtdProcessoAtendido:
        qtdProcessoAtendido[processo.id] = qtdProcessoAtendido[processo.id] + 1
    else:
        qtdProcessoAtendido[processo.id] = 1

class Mensagem(Enum):
    REQUEST = "1"
    GRANT = "2"
    RELEASE = "3"

def geraLog(processo, origemOuDestino):
    with Lock:
        now = datetime.now()
        tempo_atual = now.strftime("%H:%M:%S:%f")
            
        w = open("log-coordenador.log", "a")
        w.write("tempo atual: {}, tipo da mensagem: {}, Id do processo de {}: {}; \n".format(tempo_atual, processo.mensagem, origemOuDestino, processo.id))
        w.close()

class Processo:
    def __init__(self, conn, ender):
        msg = conn.recv(20).decode().split("|")
        printMsg("[Coordenador] Mensagem recebida: {}\n".format(msg))
        self.mensagem = Mensagem(msg[0])
        self.id = msg[1]
        self.conn = conn
        self.ender = ender
        geraLog(self, "origem")
        

    def responder(self, tipoMensagem):
        self.mensagem = tipoMensagem
        msg = str.encode("{}|{}".format(tipoMensagem.value, self.id))
        geraLog(self, "destino")
        printMsg("[Coordenador] Mensagem enviada: {}".format(msg))
        self.conn.sendall(msg)


def imprimirFilaDeEspera():
    print("\n ========================================================== \n")
    count = 0
    if len(filaDeEspera) == 0 :
        print(" A fila de espera está vazia.")
    else:
        for processo in filaDeEspera:
            print(" Pedido posição {} - Processo id: {}, Mensagem: {}.".format(count, processo.id, processo.mensagem))
            count+=1
    print("\n ========================================================== \n")

def imprimirQtdProcessoAtendido():
    print("\n ========================================================== \n")
    if len(qtdProcessoAtendido) == 0 :
        print(" Nenhum processo foi atendido.")
    else:
        for key, value in qtdProcessoAtendido.items():
            print(" O Processo {} - Foi atendido {} vezes.".format(key, value))
    print("\n ========================================================== \n")

def interface(executarCoordenador):
    while executarCoordenador:
        print("Comandos disponíveis: \n")
        print("    1 - Imprimir a fila de pedidos atual.\n")
        print("    2 - Imprimir quantas vezes cada processo foi atendido.\n")
        print("    3 - Encerrar a execução.\n")
        print("    4 - Limpar arquivo de log do Coordenador.\n")
        print("    5 - Limpar arquivo de resultado dos Processos.\n")
        comando = int(input())

        if comando == 5:
            limparArquivoResultadoDosProcessos()
        elif comando == 4:
            limparArquivoLogsDoCoordenador()
        elif comando == 3:
            executarCoordenador = False
        elif comando == 2:
            imprimirQtdProcessoAtendido()
        elif comando == 1:
            imprimirFilaDeEspera()

def limparArquivoLogsDoCoordenador():
    open('log-coordenador.log', 'w').close()

def limparArquivoResultadoDosProcessos():
    open('resultado.txt', 'w').close()

def algoritmoExclusaoMutua(processo):
    if processo.mensagem == Mensagem.REQUEST:
        if len(filaDeEspera) == 0:
            printMsg("[Coordenador] O Processo {} vai entrar na região critica.".format(processo.id))
            processo.responder(Mensagem.GRANT) #Retorna a mensagem para quem fez a requisição
        filaDeEspera.append(processo)
        printMsg("[Coordenador] O Processo {} entrou na fila de espera.".format(processo.id))

    if processo.mensagem == Mensagem.RELEASE:
        filaDeEspera.pop(0)
        addQtdProcessoAtendido(processo=processo)
        printMsg("[Coordenador] O Processo {} SAIU da região critica e da fila de espera.".format(processo.id))
        if len(filaDeEspera) > 0:
            processo = filaDeEspera[0]
            printMsg("[Coordenador] O Processo {} vai entrar na região critica.".format(processo.id))
            processo.responder(Mensagem.GRANT) #Retorna a mensagem para o próximo processo na fila

def receberConexoes(executarCoordenador):
    while executarCoordenador:
        printMsg("[Coordenador] Esperando mensagem de algum processo.")

        conn, ender = sckt.accept()
        processo = Processo(conn, ender)

        printMsg("[Coordenador] O Processo {} enviou a mensagem {}.".format(processo.id, processo.mensagem))

        th = threading.Thread(target=algoritmoExclusaoMutua, args=(processo,))
        th.start()

th = threading.Thread(target=receberConexoes, args=(executarCoordenador,))
th.daemon = True
th.start()

th = threading.Thread(target=interface, args=(executarCoordenador,))
th.start()