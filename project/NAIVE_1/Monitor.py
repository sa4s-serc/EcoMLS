import requests
from Analyzer import Analyzer
import time
import pandas as pd
import numpy as np
import os
import pyRAPL
import csv


class Monitor():

    def __init__(self):
        self.analyzer_obj = Analyzer() 
        self.monitor_dict = dict()
        self.time = -1
        self.global_start_time = 0

        f = open("MAPEK_energy.csv", "w")
        writer = csv.writer(f)
        writer.writerow(["time", "monitor", "analyzer", "planner", "executor"])
        f.close()
        
        pyRAPL.setup()

    def get_last_n(self, model, n=20):
        log_file = f"log_{model}.csv"

        df = pd.read_csv(log_file, header=None)
        last_n_rows = df.tail(n) if df.shape[0] > n else df

        if last_n_rows.index[0] == df.index[0]:
            last_n_rows = last_n_rows.iloc[1:]

        avg_conf_col_no = 6
        energy_col_no = 8
        curr_boxes_col_no = 7

        avg_conf = last_n_rows[avg_conf_col_no].str.split().apply(pd.to_numeric, errors='coerce')
        energy = last_n_rows[energy_col_no].str.split().apply(pd.to_numeric, errors='coerce')
        boxes = last_n_rows[curr_boxes_col_no].str.split().apply(pd.to_numeric, errors='coerce')
        
        if avg_conf.empty:
            return -1, -1, -1
        else:    
            avg_conf = avg_conf.mean()
            energy = energy.mean()
            boxes = boxes.mean()
            return avg_conf[0], energy[0], boxes[0]
        

    def continuous_monitoring(self, n=20):

        # indicates monitoring has started
        print("Running the adaptation effector module")
        self.time = time.time()

        while True:

            # monitoring ever 1 second
            if time.time() - self.time > 1:

                if not os.path.exists("monitor.csv"):
                    continue

                # get runtime performance metrics
                try:
                    data = pd.read_csv("monitor.csv", header=None)
                except pd.errors.EmptyDataError:
                    print("No data found. Waiting for data to be parsed...")
                    time.sleep(1)
                    continue
                except Exception as e:
                    print("An error occurred:", e)
                    break
    
                data1 = data.to_numpy()
                # adaptation starts only after first n
                if data1[0][0] <= n:
                    continue

                if data1[0][0] == 1000:
                    print("Exiting...")
                    return 
                
                # tracker object created by pyRAPL library, starts tracking
                energy_of_component = {"time_stamp": 0, "monitor": 0, "analyzer": 0, "planner": 0, "executor": 0}
                energy_of_component["time_stamp"] = time.time() - self.global_start_time
                measure = pyRAPL.Measurement('CPU')
                measure.begin()
                # -------------------------------------

                # get current model
                data2 = pd.read_csv("model.csv", header=None)
                data2 = data2.to_numpy()
                if (data2[0][0] != 'yolov5n' and data2[0][0] != 'yolov5s' and data2[0][0] != 'yolov5l' and data2[0][0] != 'yolov5m' and data2[0][0] != 'yolov5x'):
                    continue
                
                # get the last n values
                last_n_avg_conf, last_n_energy, last_n_boxes_det = self.get_last_n(data2[0][0], n)
            
                # update the monitor dictionary
                self.monitor_dict['energy_consumption'] = data1[1][0]
                self.monitor_dict['confidence'] = data1[2][0]
                self.monitor_dict['model'] = data2[0][0]
                self.monitor_dict['total_confidence'] = data1[3][0]
                self.monitor_dict['curr_boxes'] = data1[4][0]
                self.monitor_dict['last_n_avg_conf'] = last_n_avg_conf
                self.monitor_dict['last_n_energy'] = last_n_energy
                self.monitor_dict['last_n_boxes_det'] = last_n_boxes_det


                print(self.monitor_dict)
                print()

                # stop tracking immediately after monitoring
                measure.end()
                # get the energy consumption
                pyRAPL_data = measure.result
                energy_of_component["monitor"] = pyRAPL_data.pkg[0]/1000000
                # -------------------------------------

                # call the Analyzer methods
                self.analyzer_obj.perform_analysis(self.monitor_dict, energy_of_component)

                self.time = time.time()


if __name__ == '__main__':
    monitor_obj = Monitor()

    monitor_obj.global_start_time = time.time()
    monitor_obj.continuous_monitoring()
