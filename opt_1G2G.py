# Importando biblioteca usadas
from pyomo.environ import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



def irr_resultado(CA,EC,EU):
    return 8.903801 + 0.820775 * CA - 0.809301 * CA *CA - 0.637673 *EC \
           - 0.087893 * EC * EC - 0.233889 * EU - 0.387459 *EU * EU \
           - 0.213700 * CA * EC + 0.600275 *CA * EU + 0.339975 * EC * EU

def co2_avoid_resultado(CA,EC,EU):
    return 18.90206 + 0.83915 * CA - 0.37436 * CA * CA + 0.74775 *EC \
           + 0.03957 * EC * EC - 1.00481 * EU + 0.01141 * EU * EU \
           + 0.05126 * CA * EC + 0.42576 * CA * EU - 0.04161 * EC *EU


#Restricao
def restricao(CA,EC,EU):
    return 2.95291-3.29602*CA+1.75062*CA*CA -1.18355*EC+0.03588*EC*EC+3.37391*EU\
           +0.51318*EU*EU + 0.16250*CA*EC  -2.18750*CA*EU  -0.61250*EC*EU


#FUNCAO PARA USAR NOS MODELOS
def irr(modelo,flag,Irr_sup):
    return (8.903801 + 0.820775 * modelo.CA - 0.809301 * modelo.CA * modelo.CA - 0.637673 * modelo.EC \
           - 0.087893 * modelo.EC * modelo.EC - 0.233889 * modelo.EU - 0.387459 * modelo.EU * modelo.EU \
           - 0.213700 * modelo.CA * modelo.EC + 0.600275 * modelo.CA * modelo.EU + 0.339975 * modelo.EC \
           * modelo.EU)/Irr_sup

def co2_avoid(modelo,flag,COdois_sup):
    return (18.90206 + 0.83915 * modelo.CA - 0.37436 * modelo.CA * modelo.CA + 0.74775 * modelo.EC \
           + 0.03957 * modelo.EC * modelo.EC - 1.00481 * modelo.EU + 0.01141 * modelo.EU * modelo.EU \
           + 0.05126 * modelo.CA * modelo.EC + 0.42576 * modelo.CA * modelo.EU - 0.04161 * modelo.EC \
          * modelo.EU)/COdois_sup

#-----------------------------------------------------------------
def rodando_modelo(w, flag, Irr_sup,COdois_sup):

    # Instanciando o modelo que usaremos
    modelo = ConcreteModel(name="(Jessica_doc)")

    # Definindo variaveis do modelo
    modelo.CA = Var(bounds=(-1.681792831, 1.681792831))
    modelo.EC = Var(bounds=(-1.681792831, 1.681792831))
    modelo.EU = Var(bounds=(-1.681792831, 1.681792831))

    #Restricoes
    modelo.rest = Constraint(expr=2.95291-3.29602*modelo.CA+1.75062*modelo.CA*modelo.CA
                         -1.18355*modelo.EC+0.03588*modelo.EC*modelo.EC+3.37391*modelo.EU
                         +0.51318*modelo.EU*modelo.EU+0.16250*modelo.CA*modelo.EC
                         -2.18750*modelo.CA*modelo.EU-0.61250*modelo.EC*modelo.EU >= 0.00001)


    # Definindo funcao objetivo

    if flag ==1:
        modelo.obj = Objective(expr=irr(modelo,flag,Irr_sup), sense=-1)

    if flag == 2:
        modelo.obj = Objective(expr=co2_avoid(modelo,flag,COdois_sup), sense=-1)

    if flag == 3:
        modelo.obj = Objective(expr=w * irr(modelo,flag,Irr_sup) \
                     + (1.0 - w) * co2_avoid(modelo,flag,COdois_sup), sense=-1)

    #Resolvendo o problema de otimização
    opt = SolverFactory('ipopt')
    resultado = opt.solve(modelo)

    return modelo.CA.value, modelo.EC.value, modelo.EU.value
#----------------------------------------------------------------------------


if __name__ == "__main__":

    #----Limite sup Irr-----------#
    CA, EC, EU = rodando_modelo(1, 1, 1,1)
    Irr_sup = irr_resultado(CA,EC,EU)
    print(Irr_sup)

    # ----Limite sup CO2-----------#
    CA, EC, EU = rodando_modelo(1, 2, 1,1)
    COdois_sup = co2_avoid_resultado(CA, EC, EU)
    print(COdois_sup)


    #Valores nos pesos variando entre 0 e 1
    # na variavel num temos numero de elementos que estarão presentes
    val_w = np.linspace(0.0, 1.0, num=10000)

    #Lista de variaveis
    CA_lista = []
    EC_lista = []
    EU_lista = []

    #Lista de pesos
    w_irr = []
    w_co2 = []

    #Lista contendo os valores das obj funtions
    irr_lista = []
    co2_lista = []

    #Retricao
    restricao_lista =[]

    i = 0

    for w in val_w:

        #Rodando o modelo de otimizacao
        CA, EC, EU = rodando_modelo(w, 3,Irr_sup,COdois_sup)

        #Quardando as variaveis codificadas
        CA_lista.append( CA )
        EC_lista.append(EC)
        EU_lista.append(EU)

        #Guardando os valores da funcao objetivo
        irr_lista.append( irr_resultado(CA,EC,EU) )
        co2_lista.append( co2_avoid_resultado(CA, EC, EU) )

        #Guardando os pesos
        w_irr.append(w)
        w_co2.append(1.0-w)

        #Guardando restricao
        restricao_lista.append(restricao(CA, EC, EU))

        #Contador para mostrar a evolucao do processamento
        i += 1
        print(i)



#Guardando respostas
dt = {

    'CA' : CA_lista,
    'EC' : EC_lista,
    'EU' : EU_lista,
    'irr_obj': irr_lista,
    'CO2_obj': co2_lista,
    'Restricao': restricao_lista,
    'Peso_irr': w_irr,
    'Peso_CO2':  w_co2

}

#Salvando em um csv
pd.DataFrame(dt).to_csv('resultados.csv', sep = ';', index=False)








#Gerando o grafico com os resultados
plt.scatter(x = irr_lista, y= co2_lista)
plt.title("Fronteira de Pareto para 10000 pontos")
plt.ylabel("CO2 evitado")
plt.xlabel("IRR")
plt.show()