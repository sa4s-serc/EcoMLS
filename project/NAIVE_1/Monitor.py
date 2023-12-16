import requests
from Analyzer import Analyzer
import time
import pandas as pd
import numpy as np
import os

class Monitor():

    def __init__(self):
        self.analyzer_obj = Analyzer() 
        self.monitor_dict = dict()
        self.time = -1

    def continuous_monitoring(self):

        # indicates monitoring has started
        print("Running the adaptation effector module")
        self.time = time.time()

        while True:

            # monitoring ever 1 second
            if time.time() - self.time > 1:

                if not os.path.exists("monitor.csv"):
                    continue

                data = pd.read_csv("monitor.csv", header=None) 
                if data.empty:
                    continue

                data1 = data.to_numpy()
                
                data2 = pd.read_csv("model.csv", header=None)
                data2 = data2.to_numpy()
            
                self.monitor_dict['energy_consumption'] = data1[0][0]
                self.monitor_dict['confidence'] = data1[1][0]
                self.monitor_dict['model'] = data2[0][0]

                if (data2 != 'yolov5n' and data2 != 'yolov5s' and data2 != 'yolov5l' and data2 != 'yolov5m' and data2 != 'yolov5x'):
                    continue

                print(self.monitor_dict)

                # call the Analyzer methods
                self.analyzer_obj.perform_analysis(self.monitor_dict)

                self.time = time.time()


if __name__ == '__main__':
    monitor_obj = Monitor()
    monitor_obj.continuous_monitoring()
