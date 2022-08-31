import threading
def init_semaphore_settings():
    """
    Initialize the semaphore settings for the EnergyPlus API.
    """
    global sem_vcwg, sem_energyplus
    sem_vcwg = threading.Semaphore()
    sem_energyplus = threading.Semaphore()

def init_temp_waste_heat():
    global ep_hvac_demand, ep_oat
    ep_hvac_demand = 0
    ep_oat = 0