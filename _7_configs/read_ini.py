import configparser

config = configparser.ConfigParser()
config.read('case8_CAPITOUL_MNP.ini')

print(config.sections())