import _0_vcwg_ep_coordination as coordination
def BEMCalc_Element(canTemp,canHum, BEM, simTime, MeteoData,FractionsRoof):
    """
    type(self.BEM[i])
    <class 'BEMDef.BEMDef'>

    type(self.BEM[i].building)
    <class 'BuildingEnergy.Building'>
    """
    coordination.sem_energyplus.acquire()
    start_day = 9
    vcwg_time_index_in_seconds = (simTime.day - start_day) * 3600 * 24 + simTime.secDay
    print(f'VCWG: Update needed time index[accumulated seconds]: {vcwg_time_index_in_seconds}\n')
    coordination.vcwg_needed_time_idx_in_seconds = vcwg_time_index_in_seconds
    coordination.vcwg_canTemp_K = canTemp
    coordination.vcwg_canSpecHum_Ratio = canHum
    coordination.vcwg_canPress_Pa = MeteoData.Pre

    BEM_building = BEM.building
    BEM_building.sensWaste = coordination.ep_sensWaste_w_m2
    BEM_building.ElecTotal = coordination.ep_elecTotal_w_m2

    BEM.mass.Text = coordination.ep_floor_Text_K
    BEM.mass.Tint = coordination.ep_floor_Tint_K
    BEM.wallSun.Text = coordination.ep_wall_Text_K
    BEM.wallSun.Tint = coordination.ep_wall_Tint_K
    BEM.wallShade.Text = coordination.ep_wall_Text_K
    BEM.wallShade.Tint = coordination.ep_wall_Tint_K

    # floor mass, wallSun, wallShade, roofImp, roofVeg
    if FractionsRoof.fimp > 0:
        BEM.roofImp.Text = coordination.ep_roof_Text_K
        BEM.roofImp.Tint = coordination.ep_roof_Tint_K
    if FractionsRoof.fveg > 0:
        BEM.roofVeg.Text = coordination.ep_roof_Text_K
        BEM.roofVeg.Tint = coordination.ep_roof_Tint_K

    BEM_building.sensCoolDemand = coordination.ep_sensCoolDemand_w_m2
    BEM_building.sensHeatDemand = coordination.ep_sensHeatDemand_w_m2
    BEM_building.coolConsump = coordination.ep_coolConsump_w_m2
    BEM_building.heatConsump = coordination.ep_heatConsump_w_m2
    BEM_building.indoorTemp = coordination.ep_indoorTemp_C + 273.15
    BEM_building.indoorHum = coordination.ep_indoorHum_Ratio
    BEM_building.fluxWall = coordination.ep_fluxWall_w_m2
    BEM_building.fluxRoof = coordination.ep_fluxRoof_w_m2
    BEM_building.fluxMass = coordination.ep_floor_fluxMass_w_m2



    coordination.sem_vcwg.release()

    return BEM
