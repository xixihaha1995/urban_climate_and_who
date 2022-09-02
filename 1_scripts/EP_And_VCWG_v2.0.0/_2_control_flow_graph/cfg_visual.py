from staticfg import CFGBuilder
import os
os.environ["PATH"] += os.pathsep + 'C:\\Program Files\\Graphviz\\bin'

cfg = CFGBuilder().build_from_file('quick sort', '..\BuildingEnergy.py')
cfg.build_visual('qsort', 'png')