#! -*- encoding: utf-8 -*-
import psycopg2
import pandas as pd
from apyori import apriori


# ----- Conecção com o BD  ------

conn = psycopg2.connect(database="rodolpho", user="rodolpho", host="localhost", password="macav810")

cursor = conn.cursor()

cursor.execute("SET search_path to pizzaria")


# ---- Montando a estrutura de leitura do algoritmo

pedidos = []

cursor.execute("SELECT * FROM pedidos LIMIT 10");

query = cursor.fetchall()

tam = True

for p in query:
    
    #XXX: MELHORAR ISSO
    if tam:
        total = len(p)
        tam = False
    
    pedidos.append([str(p[i]) for i in range(0,total)])

print pedidos

# ----- Gerando as Regras ------

regras = apriori(pedidos, min_support = 0.003, min_confidence = 0.8, min_lift = 2)

resultados = [list(x) for x in regras]
print resultados




conn.close()
