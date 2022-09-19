from VCWG_Hydrology import VCWG_Hydro

def run_vcwg():
    epwFileName = 'ERA5_Basel.epw'
    TopForcingFileName = None
    VCWGParamFileName = 'replicate_Basel_MOST.uwg'
    ViewFactorFileName = 'ViewFactor_Basel_MOST.txt'
    # Case name to append output file names with
    case = 'bypass_Basel_MOST'


    # epwFileName = 'TopForcing_year.epw'
    # TopForcingFileName = None
    # # TopForcingFileName = 'Vancouver2008_ERA5.csv'
    # VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    # ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # # Case name to append output file names with
    # case = '_bypass_year_Vancouver_LCZ1'

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()
