import threading

qtd = input("Digite a quantidade de Processos que serão iniciados: ")

thr = input("Serão executados em threads? \n1 - Sim \n2 - Não \n\n")

def executarProcesso():
        exec(open("Processo.py").read())

if int(thr) == 1:
    for x in range(0, int(qtd)):
        th = threading.Thread(target=executarProcesso, args=())
        th.start()
else:
    for x in range(0, int(qtd)):
        executarProcesso()