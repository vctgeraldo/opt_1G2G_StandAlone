#------------------------------------------------------------#
#Title: Optimization of a 1G 2G mill...                      #
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

#---Library to handle dataframes
import pandas as pd
# ------------------------------------------------------------#


#------------------------------------------------------------#
#     COMPUTING THE RESULTS OF THE OPTMIZATION PROCEDURE     #
#------------------------------------------------------------#
#The following functions (i.e., irrResult, co2AvoidedResult)
#compute the results of the model.


#---Irr
def irr_resultado(CA,EC,EU):
    return 8.903801 + 0.820775 * CA - 0.809301 * CA *CA - 0.637673 *EC \
           - 0.087893 * EC * EC - 0.233889 * EU - 0.387459 *EU * EU \
           - 0.213700 * CA * EC + 0.600275 *CA * EU + 0.339975 * EC * EU
#---Avoided CO2
def co2_avoid_resultado(CA,EC,EU):
    return 18.90206 + 0.83915 * CA - 0.37436 * CA * CA + 0.74775 *EC \
           + 0.03957 * EC * EC - 1.00481 * EU + 0.01141 * EU * EU \
           + 0.05126 * CA * EC + 0.42576 * CA * EU - 0.04161 * EC *EU
#------------------------------------------------------------#



#------------------------------------------------------------#
#                    OBJETIVE FUNCTION                       #
#------------------------------------------------------------#

#---IRR
def irr(modelo,flag,Irr_sup):
    return (8.903801 + 0.820775 * modelo.CA - 0.809301 * modelo.CA * modelo.CA - 0.637673 * modelo.EC \
           - 0.087893 * modelo.EC * modelo.EC - 0.233889 * modelo.EU - 0.387459 * modelo.EU * modelo.EU \
           - 0.213700 * modelo.CA * modelo.EC + 0.600275 * modelo.CA * modelo.EU + 0.339975 * modelo.EC \
           * modelo.EU)/Irr_sup

#---CO2 avoided
def co2_avoid(modelo,flag,COdois_sup):
    return (18.90206 + 0.83915 * modelo.CA - 0.37436 * modelo.CA * modelo.CA + 0.74775 * modelo.EC \
           + 0.03957 * modelo.EC * modelo.EC - 1.00481 * modelo.EU + 0.01141 * modelo.EU * modelo.EU \
           + 0.05126 * modelo.CA * modelo.EC + 0.42576 * modelo.CA * modelo.EU - 0.04161 * modelo.EC \
          * modelo.EU)/COdois_sup

#------------------------------------------------------------#
#                    RESTRICTION FUNCTION                    #
#------------------------------------------------------------#

def restricao(CA,EC,EU):
    return 2.95291-3.29602*CA+1.75062*CA*CA -1.18355*EC+0.03588*EC*EC+3.37391*EU\
           +0.51318*EU*EU + 0.16250*CA*EC  -2.18750*CA*EU  -0.61250*EC*EU
#-----------------------------------------------------------------



#------------------------------------------------------------#
#                       MAIN MODEL
#------------------------------------------------------------#

#In the function bellow (i.e., mainModel), it is defined the
#optmization model. Therefore, it contains the equations repre-
#senting the objective function and the restrictions.
#"mainModel" also contains the calling of Pyomo library, as well
#as the definition of the solver used in the optimization proce-
#dure.

def rodando_modelo(w, flag, Irr_sup,COdois_sup):

    #---Defining the optimization model
    modelo = ConcreteModel(name="(Jessica_doc)")
    

    #---Instantiating the variables of the model, and their
    #respective baundaries
    modelo.CA = Var(bounds=(-1.681792831, 1.681792831))
    modelo.EC = Var(bounds=(-1.681792831, 1.681792831))
    modelo.EU = Var(bounds=(-1.681792831, 1.681792831))

    #Defining the restriction function. 
    modelo.rest = Constraint(expr=2.95291-3.29602*modelo.CA+1.75062*modelo.CA*modelo.CA
                         -1.18355*modelo.EC+0.03588*modelo.EC*modelo.EC+3.37391*modelo.EU
                         +0.51318*modelo.EU*modelo.EU+0.16250*modelo.CA*modelo.EC
                         -2.18750*modelo.CA*modelo.EU-0.61250*modelo.EC*modelo.EU >= 0.00001)


    #Defining the objective function

    if flag ==1:
        modelo.obj = Objective(expr=irr(modelo,flag,Irr_sup), sense=-1)

    if flag == 2:
        modelo.obj = Objective(expr=co2_avoid(modelo,flag,COdois_sup), sense=-1)

    if flag == 3:
        modelo.obj = Objective(expr=w * irr(modelo,flag,Irr_sup) \
                     + (1.0 - w) * co2_avoid(modelo,flag,COdois_sup), sense=-1)

    #Solving the optmization model
    opt = SolverFactory('ipopt')
    resultado = opt.solve(modelo)

    return modelo.CA.value, modelo.EC.value, modelo.EU.value
#----------------------------------------------------------------------------


#------------------------------------------------------------#
#                  RUNNING THE OPTMIZATION MODEL
#------------------------------------------------------------#

if __name__ == "__main__":

    #----Superior limit of Irr-----------#
    CA, EC, EU = rodando_modelo(1, 1, 1,1)
    Irr_sup = irr_resultado(CA,EC,EU)
    print(Irr_sup)

    # ----Superior limit of CO2-----------#
    CA, EC, EU = rodando_modelo(1, 2, 1,1)
    COdois_sup = co2_avoid_resultado(CA, EC, EU)
    print(COdois_sup)


    #weight of the objective function varying between 0 and 1
    val_w = np.linspace(0.0, 1.0, num=10000)

    #------------------------------------------------------------#
    #             DEFINING THE LIST OF REPORTED RESULTS
    #------------------------------------------------------------#


     #List of variable
    CA_lista = []
    EC_lista = []
    EU_lista = []

    #List of weight
    w_irr = []
    w_co2 = []

    #List of the result
    irr_lista = []
    co2_lista = []

    #Retricao
    restricao_lista =[]

    i = 0

    #---Iterating over the pareto points
    for w in val_w:

        #Running the model
        CA, EC, EU = rodando_modelo(w, 3,Irr_sup,COdois_sup)

        #--Storing the results of the optimization 
	
        #---Coded variables 
        CA_lista.append( CA )
        EC_lista.append(EC)
        EU_lista.append(EU)

        #Objective function
        irr_lista.append( irr_resultado(CA,EC,EU) )
        co2_lista.append( co2_avoid_resultado(CA, EC, EU) )

        #weight values
        w_irr.append(w)
        w_co2.append(1.0-w)

        #Restriction values
        restricao_lista.append(restricao(CA, EC, EU))

        
        i += 1
        print(i)



#Constructing a dictionary with the results
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

#Saving results in a pandas dataframes and write it down on a 
#".csv" file.
pd.DataFrame(dt).to_csv('resultados.csv', sep = ';', index=False)


#Generating graph with the pareto frontier
plt.scatter(x = irr_lista, y= co2_lista)
plt.title("Fronteira de Pareto para 10000 pontos")
plt.ylabel("CO2 evitado")
plt.xlabel("IRR")
plt.show()




