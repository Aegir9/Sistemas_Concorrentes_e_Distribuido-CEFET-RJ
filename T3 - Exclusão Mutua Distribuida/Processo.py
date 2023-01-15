import socket
from enum import Enum 
from datetime import datetime
import os
import time
import random

HOST = 'localhost'
PORTA = 3456

class Mensagem(Enum):
    REQUEST = "1"
    GRANT = "2"
    RELEASE = "3"

pid = os.getpid()
pid = pid + random.randint(0, 999)

print("\n\n\n")
print("[Processo - 0] Processo cliente comecou a rodar.");

for x in range(0, 4):
    print("\n\n[Processo - 1] Usando o servidor {} e a porta {}.".format(HOST, PORTA));

    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, int(PORTA)))
    sckt.sendall(str.encode("{}|{}".format(Mensagem.REQUEST.value, pid)))

    dadosResp = sckt.recv(20)
    print("[Processo - 2] Recebeu: {}".format(dadosResp.decode()))
    msgResp = dadosResp.decode().split("|")

    if Mensagem(msgResp[0]) == Mensagem.GRANT:
        print("[Processo - 3] Acesso na região crítica iniciou!")
        
        now = datetime.now()
        tempo_atual = now.strftime("%H:%M:%S:%f")

        w = open("resultado.txt", "a")
        w.write("tempo atual: {}, id do processo: {};\n".format(tempo_atual, pid))
        w.close()

        time.sleep(2)
        sckt.close()
        
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.connect((HOST, int(PORTA)))
        sckt.sendall(str.encode("{}|{}".format(Mensagem.RELEASE.value, pid)))
        print("[Processo - 4] Acesso na região crítica terminou!")

    sckt.close()