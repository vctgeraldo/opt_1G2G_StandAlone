#------------------------------------------------------------#
#Title: Optimization of ...                                  #
#Authors:                                                    #
#    1 - Jessica Marcon Bressanin                            #
#    2 - Victor Coelho Geraldo                               #
#      - ...                                                 #
#                                                            #
#Institution: CTBE                                           #
#------------------------------------------------------------#


#------------------------------------------------------------#
#                   IMPORTING LIBRARIES                      #
#------------------------------------------------------------#

#---Pyomo
from pyomo.environ import *

#---
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# ------------------------------------------------------------#


def irr_resultado(CA,EC,EU):
    return 1.987347 + 0.652139*CA - 0.215191*CA*CA - 0.021653*EC - 0.047731*EC*EC \
           - 0.000052*EU -0.054590*EU*EU - 0.015525*CA*EC - 0.035575*CA*EU \
           + 0.008675*EC*EU


def co2_avoid_resultado(CA,EC,EU):

    return 26.64475 + 1.68662*CA - 0.50258*CA*CA + 0.28547*EC + 0.02429*EC*EC\
           - 2.54509*EU + 0.53556*EU*EU + 0.02525*CA*EC + 0.37715*CA*EU \
           - 0.04118*EC*EU


#FUNCAO PARA USAR NOS MODELOS
def irr(modelo,flag,Irr_sup):

    return (1.987347 + 0.652139 * modelo.CA - 0.215191 * modelo.CA * modelo.CA - 0.021653 * modelo.EC \
    - 0.047731 * modelo.EC * modelo.EC - 0.000052 * modelo.EU - 0.054590 * modelo.EU * modelo.EU \
    - 0.015525 * modelo.CA * modelo.EC - 0.035575 * modelo.CA * modelo.EU +\
    0.008675 * modelo.EC * modelo.EU)/Irr_sup


def co2_avoid(modelo,flag,COdois_sup):

    return (26.64475 + 1.68662*modelo.CA - 0.50258*modelo.CA*modelo.CA + 0.28547*modelo.EC
            + 0.02429*modelo.EC*modelo.EC - 2.54509*modelo.EU + 0.53556*modelo.EU*modelo.EU
            + 0.02525*modelo.CA*modelo.EC + 0.37715*modelo.CA*modelo.EU
            - 0.04118*modelo.EC*modelo.EU)/COdois_sup

#-----------------------------------------------------------------
def rodando_modelo(w, flag, Irr_sup,COdois_sup):

    # Instanciando o modelo que usaremos
    modelo = ConcreteModel(name="(Jessica_doc)")

    # Definindo variaveis do modelo
    modelo.CA = Var(bounds=(-1.681792831, 1.681792831))
    modelo.EC = Var(bounds=(-1.681792831, 1.681792831))
    modelo.EU = Var(bounds=(-1.681792831, 1.681792831))

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


#------------------------------------------------------------#
#                  RUNNING THE OPTMIZATION MODEL
#------------------------------------------------------------#
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
        'Peso_irr': w_irr,
        'Peso_CO2':  w_co2

    }

    #Salvando em um csv
    pd.DataFrame(dt).to_csv('2G_standAlone.csv', sep = ';', index=False)



    #Gerando o grafico com os resultados
    plt.scatter(x = irr_lista, y= co2_lista)
    plt.title("Fronteira de Pareto para 10000 pontos")
    plt.ylabel("CO2 evitado")
    plt.xlabel("IRR")
    plt.show()
#------------------------------------------------------------#


