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
def irrResult(CA,ECF,EU):
    return 8.903801 + 0.820775 * CA - 0.809301 * CA *CA - 0.637673 *ECF \
           - 0.087893 * ECF * ECF - 0.233889 * EU - 0.387459 *EU * EU \
           - 0.213700 * CA * ECF + 0.600275 *CA * EU + 0.339975 * ECF * EU
#---Avoided CO2
def co2AvoidedResult(CA,ECF,EU):
    return 18.90206 + 0.83915 * CA - 0.37436 * CA * CA + 0.74775 *ECF \
           + 0.03957 * ECF * ECF - 1.00481 * EU + 0.01141 * EU * EU \
           + 0.05126 * CA * ECF + 0.42576 * CA * EU - 0.04161 * ECF *EU

#---Restriction function
def restriction(CA,ECF,EU):
    return 2.95291-3.29602*CA+1.75062*CA*CA -1.18355*ECF+0.03588*ECF*ECF+3.37391*EU\
           +0.51318*EU*EU + 0.16250*CA*ECF  -2.18750*CA*EU  -0.61250*ECF*EU
#------------------------------------------------------------#



#------------------------------------------------------------#
#                    OBJETIVE FUNCTION                       #
#------------------------------------------------------------#

#---IRR
def irr(modelOpt,flag,Irr_sup):
    return (8.903801 + 0.820775 * modelOpt.CA - 0.809301 * modelOpt.CA * modelOpt.CA - 0.637673 * modelOpt.ECF \
           - 0.087893 * modelOpt.ECF * modelOpt.ECF - 0.233889 * modelOpt.EU - 0.387459 * modelOpt.EU * modelOpt.EU \
           - 0.213700 * modelOpt.CA * modelOpt.ECF + 0.600275 * modelOpt.CA * modelOpt.EU + 0.339975 * modelOpt.ECF \
           * modelOpt.EU)/Irr_sup

#---CO2 avoided
def co2_avoid(modelOpt,flag,COdois_sup):
    return (18.90206 + 0.83915 * modelOpt.CA - 0.37436 * modelOpt.CA * modelOpt.CA + 0.74775 * modelOpt.ECF \
           + 0.03957 * modelOpt.ECF * modelOpt.ECF - 1.00481 * modelOpt.EU + 0.01141 * modelOpt.EU * modelOpt.EU \
           + 0.05126 * modelOpt.CA * modelOpt.ECF + 0.42576 * modelOpt.CA * modelOpt.EU - 0.04161 * modelOpt.ECF \
          * modelOpt.EU)/COdois_sup


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
    modelOpt = ConcreteModel(name="(Jessica_doc)")
    

    #---Instantiating the variables of the model, and their
    #respective baundaries
    modelOpt.CA = Var(bounds=(-1.681792831, 1.681792831))
    modelOpt.ECF = Var(bounds=(-1.681792831, 1.681792831))
    modelOpt.EU = Var(bounds=(-1.681792831, 1.681792831))

    #Defining the restriction function. 
    modelOpt.rest = Constraint(expr=2.95291-3.29602*modelOpt.CA+1.75062*modelOpt.CA*modelOpt.CA
                         -1.18355*modelOpt.ECF+0.03588*modelOpt.ECF*modelOpt.ECF+3.37391*modelOpt.EU
                         +0.51318*modelOpt.EU*modelOpt.EU+0.16250*modelOpt.CA*modelOpt.ECF
                         -2.18750*modelOpt.CA*modelOpt.EU-0.61250*modelOpt.ECF*modelOpt.EU >= 0.00001)


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

    return modelOpt.CA.value, modelOpt.ECF.value, modelOpt.EU.value
#----------------------------------------------------------------------------


#------------------------------------------------------------#
#                  RUNNING THE OPTMIZATION MODEL
#------------------------------------------------------------#

if __name__ == "__main__":

    #----Superior limit of Irr-----------#
    CA, ECF, EU = mainModel(1, 1, 1,1)
    Irr_sup = irrResult(CA,ECF,EU)
    print(Irr_sup)

    # ----Superior limit of CO2-----------#
    CA, ECF, EU = mainModel(1, 2, 1,1)
    COdois_sup = co2AvoidedResult(CA, ECF, EU)
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
        CA, ECF, EU = mainModel(w, 3,Irr_sup,COdois_sup)

        #--Storing the results of the optimization 
	
        #---Coded variables 
        CA_lista.append( CA )
        EC_lista.append(ECF)
        EU_lista.append(EU)

        #Objective function
        irr_lista.append( irrResult(CA,ECF,EU) )
        co2_lista.append( co2AvoidedResult(CA, ECF, EU) )

        #weight values
        w_irr.append(w)
        w_co2.append(1.0-w)

        #Restriction values
        restricao_lista.append(restriction(CA, ECF, EU))

        
        i += 1
        print(i)



#Constructing a dictionary with the results
dt = {

    'CA' : CA_lista,
    'ECF' : EC_lista,
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
plt.title("Pareto frontier")
plt.ylabel("CO2 evoided")
plt.xlabel("IRR")
plt.show()




