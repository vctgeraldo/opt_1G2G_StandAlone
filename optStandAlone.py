#------------------------------------------------------------#
#Title: Optimization of a Stand Alone mill...                #
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

    return 1.987347 + 0.652139*CA - 0.215191*CA*CA - 0.021653*ECF - 0.047731*ECF*ECF \
           - 0.000052*EU -0.054590*EU*EU - 0.015525*CA*ECF - 0.035575*CA*EU \
           + 0.008675*ECF*EU

#---Avoided CO2
def co2AvoidedResult(CA,ECF,EU):

    return 26.64475 + 1.68662*CA - 0.50258*CA*CA + 0.28547*ECF + 0.02429*ECF*ECF\
           - 2.54509*EU + 0.53556*EU*EU + 0.02525*CA*ECF + 0.37715*CA*EU \
           - 0.04118*ECF*EU
#------------------------------------------------------------#



#------------------------------------------------------------#
#                    OBJETIVE FUNCTION                       #
#------------------------------------------------------------#

#---IRR
def irr(modelOpt,flag,Irr_sup):

    return (1.987347 + 0.652139 * modelOpt.CA - 0.215191 * modelOpt.CA * modelOpt.CA - 0.021653 * modelOpt.ECF \
            - 0.047731 * modelOpt.ECF * modelOpt.ECF - 0.000052 * modelOpt.EU - 0.054590 * modelOpt.EU * modelOpt.EU \
            - 0.015525 * modelOpt.CA * modelOpt.ECF - 0.035575 * modelOpt.CA * modelOpt.EU + \
            0.008675 * modelOpt.ECF * modelOpt.EU) / Irr_sup


#---CO2 avoided
def co2_avoid(modelOpt,flag,COdois_sup):

    return (26.64475 + 1.68662 * modelOpt.CA - 0.50258 * modelOpt.CA * modelOpt.CA + 0.28547 * modelOpt.ECF
            + 0.02429 * modelOpt.ECF * modelOpt.ECF - 2.54509 * modelOpt.EU + 0.53556 * modelOpt.EU * modelOpt.EU
            + 0.02525 * modelOpt.CA * modelOpt.ECF + 0.37715 * modelOpt.CA * modelOpt.EU
            - 0.04118 * modelOpt.ECF * modelOpt.EU) / COdois_sup

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
    modelOpt.ECF = Var(bounds=(-1.681792831, 1.681792831))
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

    return modelOpt.CA.value, modelOpt.ECF.value, modelOpt.EU.value
#------------------------------------------------------------#



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
    ECF_lista = []
    EU_lista = []

    #List of weight
    w_irr = []
    w_co2 = []

    #List of the result
    irr_lista = []
    co2_lista = []


    i = 0

    #---Iterating over the pareto points	
    for w in val_w:

        #Running the model
        CA, ECF, EU = mainModel(w, 3,Irr_sup,COdois_sup)

	#--Storing the results of the optimization 
	
        #---Coded variables 
        CA_lista.append( CA )
        ECF_lista.append(ECF)
        EU_lista.append(EU)

        #Objective function
        irr_lista.append( irrResult(CA,ECF,EU) )
        co2_lista.append( co2AvoidedResult(CA, ECF, EU) )

        #Guardando os pesos
        w_irr.append(w)
        w_co2.append(1.0-w)

        
        i += 1
        print(i)



    #Constructing a dictionary with the results
    dt = {

        'CA' : CA_lista,
        'ECF' : ECF_lista,
        'EU' : EU_lista,
        'irr_obj': irr_lista,
        'CO2_obj': co2_lista,
        'Peso_irr': w_irr,
        'Peso_CO2':  w_co2

    }

    #Saving results in a pandas dataframes and write it down on a 
    #".csv" file.
    pd.DataFrame(dt).to_csv('2G_standAlone.csv', sep = ';', index=False)



    #Generating graph with the pareto frontier
    plt.scatter(x = irr_lista, y= co2_lista)
    plt.title("Pareto frontier")
    plt.ylabel("CO2 evoided")
    plt.xlabel("IRR")
    plt.show()
#------------------------------------------------------------#


