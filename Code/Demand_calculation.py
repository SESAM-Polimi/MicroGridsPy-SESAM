
from Demand_input import data_import
import pandas as pd, numpy as np

#%% Calculates the load demand given as input the latitude, cooling period and number of households for each wealth tier and number of services (schools and hospitals)

def demand_calculation():
    
    data_demand = open("Inputs/Demand_data.dat").readlines()
    data = open("Inputs/Model_data.dat").readlines()
    
    num_h_tier = []
    
    F, cooling_period, num_h_tier, num_services, demand_growth, years = data_import(data_demand,data)
    
    class household:
      def __init__(self, zone, wealth, cooling, number):
        self.zone = zone
        self.wealth = wealth
        self.cooling = cooling
        self.number = number
    
      def load_demand(self, h_load):
          load = self.number/100 * h_load
          return load
      
    class service:
        def __init__(self, structure, number):
            self.structure = structure
            self.number = number
        
        def load_demand(self, h_load):
            load = self.number * h_load
            return load
        
    households = []
    load_households = []  
    for ii in range(1,len(num_h_tier)+1):
        households.append(household(F, ii, cooling_period, num_h_tier[ii-1]))
        h_load_name = households[ii-1].cooling + '_' + F + '_Tier-' + str(ii)
        h_load = pd.DataFrame(pd.read_excel("Demand_archetypes/" + h_load_name +".xlsx", skiprows = 0, usecols = "B")) 
        load_households.append(household.load_demand(households[ii-1], h_load))
        
    load_households = pd.concat([sum(load_households)]*years, axis = 1, ignore_index = True)
    for column in load_households:
        if column == 0:
            continue
        else: 
            load_households[column] = load_households[column-1]*(1+demand_growth/100)       #introduce yearly demand growth
    #%% Load demand of services    
    services = []
    load_tot_services = []
    for ii in range(1,len(num_services)+1):
        services.append(service(ii, num_services[ii-1]))
        if ii < 6:
            service_load_name = "HOSPITAL_Tier-"+str(ii)
        else: service_load_name = "SCHOOL" 
        service_load = pd.DataFrame(pd.read_excel("Demand_archetypes/"+service_load_name+".xlsx", skiprows = 0, usecols = "B"))
        load_tot_services.append(services[ii-1].load_demand(service_load))
    
    load_tot_services = pd.concat([sum(load_tot_services)]*years, axis = 1, ignore_index = True) 
    
    # Total load demand (households + services)   
    
    load_total = load_tot_services + load_households

    return load_total
    
    #%% Export results to excel
def excel_export(load):
    
    load = load.set_axis(np.arange(1,21), axis=1, inplace=False)
    
    load.to_excel("Inputs/Demand.xlsx")