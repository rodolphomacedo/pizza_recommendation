#! -*- coding: utf-8 -*-

"""
Mix de produção ótimo de pizzas em Rodizios
"""
import numpy as np
import pandas as pd
from ortools.linear_solver import pywraplp
import datetime
import time

# Lendo a base de dados
base = pd.read_excel('pizzaria.xlsx', sheet_name='pizzas', header = None)
qtds = pd.read_excel('pizzaria.xlsx', sheet_name='Qtds', header = None)

ingredientes = base.iloc[3: , 0:1].values
custoGrama = base.iloc[3: ,3:4].values
pizzas = base.iloc[:, 6:].values
disponibilidade = base.iloc[3:,5:6].values

# Restriçoes de mínimo a ser produzido
minimoPizza = qtds.iloc[1:2, 1:]
maximoPizza = qtds.iloc[2:3, 1:]
minimoPizzaGeral = qtds.iloc[4:5, 1:2].values
maximoPizzaGeral = qtds.iloc[5:6, 1:2].values

# Definindo o solver da PL
solver = pywraplp.Solver('Pizzaria', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

# Criando as variáveis
#   pizza[i] é a pizza_i a ser produzida
pizza = [solver.NumVar(0.0, solver.infinity(), pizzas[0:1,i:i+1].item()) for i in range((pizzas[0:1,:].shape)[1])]

# Definindo as variáveis
restricoes = []
for i, disp in np.ndenumerate(disponibilidade):
    restricoes.append(solver.Constraint(-solver.infinity(), disp))
    i = i[0] # ajustando o indice para int
    
    for j, ingrediente in np.ndenumerate(pizzas[i+3:i+4,:]):
        j = j[1] # Ajustando o indice para int 
        
        if not np.isnan(ingrediente): 
            restricoes[i].SetCoefficient(pizza[j], ingrediente)
    
# Retrições de mínimo de produção para cada sabor
restricoes_min = []   
for i in minimoPizza:
    restricoes_min.append(solver.Constraint(minimoPizza[i].item(), solver.infinity()))

for i in minimoPizza:
    restricoes_min[i-1].SetCoefficient(pizza[i-1], 1)

# Retrições de mínimo de produção para cada sabor
restricoes_max = []   
for i in minimoPizza:
    restricoes_max.append(solver.Constraint(-solver.infinity(), maximoPizza[i].item()))

for i in minimoPizza:
    restricoes_max[i-1].SetCoefficient(pizza[i-1], 1)


# Retrições gerais ( Mínimo de produção)
restricoes_gerais_min = solver.Constraint(minimoPizzaGeral.item(), solver.infinity())

for i in minimoPizza:
    restricoes_gerais_min.SetCoefficient(pizza[i-1], 1)


# Retrições gerais ( Máximo de pizzas homen-pizzas)
restricoes_gerais_max = solver.Constraint(-solver.infinity(), maximoPizzaGeral.item())

for i in minimoPizza:
    restricoes_gerais_max.SetCoefficient(pizza[i-1], 1)


# Definindo a função obejetivo
solucao = solver.Objective()
for i, _ in np.ndenumerate(pizzas[0:1,:]):
    
    pizza_i = pizza[i[1]] # Nome da Pizza
    custo = pizzas[1:2,i[1]:i[1]+1].item() # Custo da pizza 
    preco = pizzas[2:3,i[1]:i[1]+1].item() # Preço da Pizza
    lucro = preco - custo # Lucro líquido

    solucao.SetCoefficient(pizza_i, lucro)

#solucao.SetMinimization()
solucao.SetMaximization()

# Chamando o solver
solver.Solve()

# Recuperando o timestamp atual
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# -- Solução --
print('******************************************************\n')
print('\t\tRelatório de Produção\n')
print('\t\t',st,'\n')
print('******************************************************\n')
print('  Deverão ser produzidas as seguintes quantidades: \n') 
lucroTotal = 0.0
quantidadeTotal = 0

for i, _ in np.ndenumerate(pizzas[0:1,:]):
    print('\n\t---------------------------')
    print('\t==> ',pizza[i[1]]) 
    
    quantidade =  int(pizza[i[1]].solution_value()) 
    custo = pizzas[1:2,i[1]:i[1]+1].item() # Custo da pizza 
    preco = pizzas[2:3,i[1]:i[1]+1].item() # Preço da Pizza
    lucro = preco - custo # Lucro líquido
    
    print('\t\t\t\tQuantidade: ', round(quantidade, 2)) 
    print('\t\t\t\tCusto: \tR$', round(custo, 2)) 
    print('\t\t\t\tLucro: \tR$', round(lucro, 2)) 
    
    lucroTotal += lucro*quantidade
    quantidadeTotal += quantidade

print('\n**********************************************')
print('\tQuantidade a ser produzida: ', quantidadeTotal)
print('\tLucro Total Presumido: R$', round(lucroTotal, 2))
print('**********************************************')




