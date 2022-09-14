import threading
def init_semaphore_lock_settings():
    global sem_vcwg, sem_energyplus
    sem_vcwg = threading.Semaphore(0)
    sem_energyplus = threading.Semaphore(1)

def init_variables_for_vcwg_ep():
    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, ep_floor_fluxMass_w_m2, ep_fluxRoof_w_m2, ep_fluxWall_w_m2, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, ep_wall_Text_K, ep_wall_Tint_K
    vcwg_needed_time_idx_in_seconds = 0
    vcwg_canTemp_K = 0
    vcwg_canSpecHum_Ratio = 0
    vcwg_canPress_Pa = 0
    ep_indoorTemp_C = 20
    ep_indoorHum_Ratio = 0.006
    ep_sensCoolDemand_w_m2 = 0
    ep_sensHeatDemand_w_m2 = 0
    ep_coolConsump_w_m2 = 0
    ep_heatConsump_w_m2 = 0
    ep_elecTotal_w_m2_per_floor_area = 0
    ep_sensWaste_w_m2_per_floor_area = 0
    ep_floor_fluxMass_w_m2 = 0
    ep_fluxRoof_w_m2 = 0
    ep_fluxWall_w_m2 = 0
    ep_floor_Text_K = 300
    ep_floor_Tint_K = 300
    ep_roof_Text_K = 300
    ep_roof_Tint_K = 300
    ep_wall_Text_K = 300
    ep_wall_Tint_K = 300
