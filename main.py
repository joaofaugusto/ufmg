import numpy as np
def ler_cidades_de_arquivo(nome_arquivo):
    try:
        lista_cidades = []
        i = 0
        with open(nome_arquivo, "r") as arquivo:
            for linha in arquivo:
              cidade = (linha.strip(), i)
              lista_cidades.append(cidade)
              i+=1
            return lista_cidades
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []
    
try:
  a = float(input("A"))
  b = float(input("B"))
  c = b/a
  print("RESPOSTA -> ", c)
except ZeroDivisionError:
  a += 1
  c = b/a
  print("EX: ", c)
except ValueError:
  print("VOCE DIGITOU UM VALOR INVALIDO")


lista = []
tupla = ()
dicionario = {}

tupla = ("BH", 0)
lista.append(tupla)
tupla = ("SP", 1)
lista.append(tupla)

dicionario = dict(lista)
print(dicionario.get("BH"), dicionario.get("SP"))


string = "  RODRIGO RODRIGO RODRIGO  "
print(string)
string = string.strip()
print(string)

lista =  []
a = ('R', 3)
lista.append(a)
print(lista)

def ler_mapa(nome_arquivo, cidades_lidas, quantidade_cidades):
    mapa = np.zeros((quantidade_cidades, quantidade_cidades))
    try:
        with open(nome_arquivo, "r") as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas:
                cidade_info = linha.strip().split(",")
                try:
                   if len(cidade_info) == 3:
                      origem, destino, custo = cidade_info
                      mapa[cidades_lidas[origem]][cidades_lidas[destino]] = int(custo)
                      mapa[cidades_lidas[destino]][cidades_lidas[origem]] = int(custo)
                except:
                   #print(f"Formato inválido na linha: {linha}")
                   print("")
            return mapa
    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}' não encontrado.")
        return []