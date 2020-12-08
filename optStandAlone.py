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

#---Pyomo for optimization
from pyomo.environ import *

#---Numerical and plot libraries
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------#


#------------------------------------------------------------#
#     COMPUTING THE RESULTS OF THE OPTMIZATION PROCEDURE     #
#------------------------------------------------------------#
#The following functions (i.e., irrResult, co2AvoidedResult)
#compute the results of the model.


#---Irr
def irrResult(CA,EC,EU):

    return 1.987347 + 0.652139*CA - 0.215191*CA*CA - 0.021653*EC - 0.047731*EC*EC \
           - 0.000052*EU -0.054590*EU*EU - 0.015525*CA*EC - 0.035575*CA*EU \
           + 0.008675*EC*EU

#---Avoided CO2
def co2AvoidedResult(CA,EC,EU):

    return 26.64475 + 1.68662*CA - 0.50258*CA*CA + 0.28547*EC + 0.02429*EC*EC\
           - 2.54509*EU + 0.53556*EU*EU + 0.02525*CA*EC + 0.37715*CA*EU \
           - 0.04118*EC*EU
#------------------------------------------------------------#



#------------------------------------------------------------#
#                    OBJETIVE FUNCTION                       #
#------------------------------------------------------------#

#---IRR
def irr(modelo,flag,Irr_sup):

    return (1.987347 + 0.652139 * modelOpt.CA - 0.215191 * modelOpt.CA * modelOpt.CA - 0.021653 * modelOpt.EC \
            - 0.047731 * modelOpt.EC * modelOpt.EC - 0.000052 * modelOpt.EU - 0.054590 * modelOpt.EU * modelOpt.EU \
            - 0.015525 * modelOpt.CA * modelOpt.EC - 0.035575 * modelOpt.CA * modelOpt.EU + \
            0.008675 * modelOpt.EC * modelOpt.EU) / Irr_sup


#---CO2 avoided
def co2_avoid(modelo,flag,COdois_sup):

    return (26.64475 + 1.68662 * modelOpt.CA - 0.50258 * modelOpt.CA * modelOpt.CA + 0.28547 * modelOpt.EC
            + 0.02429 * modelOpt.EC * modelOpt.EC - 2.54509 * modelOpt.EU + 0.53556 * modelOpt.EU * modelOpt.EU
            + 0.02525 * modelOpt.CA * modelOpt.EC + 0.37715 * modelOpt.CA * modelOpt.EU
            - 0.04118 * modelOpt.EC * modelOpt.EU) / COdois_sup

#------------------------------------------------------------#


#------------------------------------------------------------#
#                       MAIN MODEL
#------------------------------------------------------------#

#In the function bellow (i.e., mainModel), it is defined the
#optmization model. Therefore, it contains the equations repre-
#senting the objective function and the restrictions.
#"mainModel" also contains the calling of Pyomo library, as well
#as the definition of the solver used in the optimization proce-
#dure.


def mainModel(w, flag, Irr_sup,COdois_sup):

    #---Defining the optimization model
    modelOpt = ConcreteModel(name="(mainModel)")

    #---Instantiating the variables of the model, and their
    #respective baundaries
    modelOpt.CA = Var(bounds=(-1.681792831, 1.681792831))
    modelOpt.EC = Var(bounds=(-1.681792831, 1.681792831))
    modelOpt.EU = Var(bounds=(-1.681792831, 1.681792831))

    #Defining the objective function

    if flag ==1:
        modelOpt.obj = Objective(expr=irr(modelOpt,flag,Irr_sup), sense=-1)

    if flag == 2:
        modelOpt.obj = Objective(expr=co2_avoid(modelOpt,flag,COdois_sup), sense=-1)

    if flag == 3:
        modelOpt.obj = Objective(expr=w * irr(modelOpt,flag,Irr_sup) \
                     + (1.0 - w) * co2_avoid(modelOpt,flag,COdois_sup), sense=-1)

    #Solving the optmization model
    opt = SolverFactory('ipopt')
    resultado = opt.solve(modelOpt)

    return modelOpt.CA.value, modelOpt.EC.value, modelOpt.EU.value
#------------------------------------------------------------#



#------------------------------------------------------------#
#                  RUNNING THE OPTMIZATION MODEL
#------------------------------------------------------------#
if __name__ == "__main__":

    #----Superior limit of Irr-----------#
    CA, EC, EU = mainModel(1, 1, 1,1)
    Irr_sup = irrResult(CA,EC,EU)
    print(Irr_sup)

    # ----Superior limit of CO2-----------#
    CA, EC, EU = mainModel(1, 2, 1,1)
    COdois_sup = co2AvoidedResult(CA, EC, EU)
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
        CA, EC, EU = mainModel(w, 3,Irr_sup,COdois_sup)

        #Quardando as variaveis codificadas
        CA_lista.append( CA )
        EC_lista.append(EC)
        EU_lista.append(EU)

        #Guardando os valores da funcao objetivo
        irr_lista.append( irrResult(CA,EC,EU) )
        co2_lista.append( co2AvoidedResult(CA, EC, EU) )

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


