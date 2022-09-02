import threading
def init_semaphore_lock_settings():
    global sem_vcwg, sem_energyplus
    sem_vcwg = threading.Semaphore(0)
    sem_energyplus = threading.Semaphore(1)

def init_variables_for_vcwg_ep():
    global ep_oat, ep_accumulated_waste_heat, vcwg_needed_time_idx_in_seconds
    ep_oat = 0
    ep_accumulated_waste_heat = 0
    vcwg_needed_time_idx_in_seconds = 0