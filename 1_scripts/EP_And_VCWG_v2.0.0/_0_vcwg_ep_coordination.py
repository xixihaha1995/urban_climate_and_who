
import threading, sys
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api
    ep_api = EnergyPlusAPI()
def init_semaphore_lock_settings():
    global sem_vcwg, sem_energyplus
    sem_vcwg = threading.Semaphore(0)
    sem_energyplus = threading.Semaphore(1)

def init_ep_hanle_related_variables():
    global one_time
    one_time = False

def init_variables_for_vcwg_ep():
    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, ep_floor_fluxMass_w_m2, ep_fluxRoof_w_m2, ep_fluxWall_w_m2, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, ep_wall_Text_K, ep_wall_Tint_K, blf_floor_area_m2
    blf_floor_area_m2 = 3135
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

def BEMCalc_Element(canTemp,canHum, BEM, it, simTime, MeteoData,FractionsRoof, Geometry_m):
    """
    type(self.BEM[i])
    <class 'BEMDef.BEMDef'>

    type(self.BEM[i].building)
    <class 'BuildingEnergy.Building'>
    """
    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, ep_floor_fluxMass_w_m2, ep_fluxRoof_w_m2, ep_fluxWall_w_m2, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, ep_wall_Text_K, ep_wall_Tint_K
    
    sem_energyplus.acquire()
    BEM_building = BEM.building
    BEM_building.nFloor = max(Geometry_m.Height_canyon / float(BEM_building.floorHeight), 1)

    vcwg_time_index_in_seconds = (it + 1) * simTime.dt
    # print(f'VCWG: Update needed time index[accumulated seconds]: {vcwg_time_index_in_seconds}\n')
    vcwg_needed_time_idx_in_seconds = vcwg_time_index_in_seconds
    vcwg_canTemp_K = canTemp
    vcwg_canSpecHum_Ratio = canHum
    vcwg_canPress_Pa = MeteoData.Pre

    BEM_building.ElecTotal = ep_sensWaste_w_m2_per_floor_area * BEM_building.nFloor
    ep_sensWaste_w_m2_per_floor_area = 0

    BEM_building.sensWaste = ep_elecTotal_w_m2_per_floor_area * BEM_building.nFloor

    BEM.mass.Text = ep_floor_Text_K
    BEM.mass.Tint = ep_floor_Tint_K
    BEM.wallSun.Text = ep_wall_Text_K
    BEM.wallSun.Tint = ep_wall_Tint_K
    BEM.wallShade.Text = ep_wall_Text_K
    BEM.wallShade.Tint = ep_wall_Tint_K

    # floor mass, wallSun, wallShade, roofImp, roofVeg
    if FractionsRoof.fimp > 0:
        BEM.roofImp.Text = ep_roof_Text_K
        BEM.roofImp.Tint = ep_roof_Tint_K
    if FractionsRoof.fveg > 0:
        BEM.roofVeg.Text = ep_roof_Text_K
        BEM.roofVeg.Tint = ep_roof_Tint_K

    BEM_building.sensCoolDemand = ep_sensCoolDemand_w_m2
    BEM_building.sensHeatDemand = ep_sensHeatDemand_w_m2
    BEM_building.coolConsump = ep_coolConsump_w_m2
    BEM_building.heatConsump = ep_heatConsump_w_m2
    BEM_building.indoorTemp = ep_indoorTemp_C + 273.15
    BEM_building.indoorHum = ep_indoorHum_Ratio
    BEM_building.fluxWall = ep_fluxWall_w_m2
    BEM_building.fluxRoof = ep_fluxRoof_w_m2
    BEM_building.fluxMass = ep_floor_fluxMass_w_m2

    BEM_building.indoorRhum = 0.6
    BEM_building.sensWasteCoolHeatDehum = 0.0  # Sensible waste heat per unit building footprint area only including cool, heat, and dehum [W m-2]
    BEM_building.dehumDemand = 0.0  # Latent heat demand for dehumidification of air per unit building footprint area [W m^-2]
    BEM_building.dehumDemand = 0.5
    BEM_building.fluxSolar = 0.5
    BEM_building.fluxWindow = 0.5
    BEM_building.fluxInterior = 0.5
    BEM_building.fluxInfil = 0.5
    BEM_building.fluxVent = 0.5
    BEM_building.QWater = 0.5
    BEM_building.QGas = 0.5
    BEM_building.Qhvac = 0.5
    BEM_building.Qheat = 0.5
    BEM_building.GasTotal = 0.5
    # wall load per unit building footprint area [W m^-2]
    BEM_building.QWall = 0.5
    # other surfaces load per unit building footprint area [W m^-2]
    BEM_building.QMass = 0.5
    # window load due to temperature difference per unit building footprint area [W m^-2]
    BEM_building.QWindow = 0.5
    # ceiling load per unit building footprint area [W m^-2]
    BEM_building.QCeil = 0.5
    # infiltration load per unit building footprint area [W m^-2]
    BEM_building.QInfil = 0.5
    # ventilation load per unit building footprint area [W m^-2]
    BEM_building.QVen = 0.5
    BEM_building.QWindowSolar = 0.5
    BEM_building.elecDomesticDemand = 0.5
    BEM_building.sensWaterHeatDemand = 0.5

    sem_vcwg.release()

    return BEM
