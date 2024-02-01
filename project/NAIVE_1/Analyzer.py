from Planner import Planner
import pandas as pd
import numpy as np
import time
import csv
import pyRAPL

class Analyzer():

    def __init__(self):

        self.time = -1
        self.count = 0

        knowledge_df = pd.read_csv("knowledge.csv", header=None)
        knowledge_data = knowledge_df.to_numpy()
        print(knowledge_data[0][3])
        self.knowledge = dict()
        self.knowledge["yolov5n"] = [1, knowledge_data[0][1], knowledge_data[0][2], knowledge_data[0][3], knowledge_data[0][4], knowledge_data[0][5]]
        self.knowledge["yolov5s"] = [2, knowledge_data[1][1], knowledge_data[1][2], knowledge_data[1][3], knowledge_data[1][4], knowledge_data[1][5]]
        self.knowledge["yolov5m"] = [3, knowledge_data[2][1], knowledge_data[2][2], knowledge_data[2][3], knowledge_data[2][4], knowledge_data[2][5]]
        self.knowledge["yolov5l"] = [4, knowledge_data[3][1], knowledge_data[3][2], knowledge_data[3][3], knowledge_data[3][4], knowledge_data[3][5]]
        
        pyRAPL.setup()

    def update_knowledge(self, monitor_dict):

        if monitor_dict["last_n_avg_conf"] != -1:
            self.knowledge[monitor_dict["model"]][3] = monitor_dict["last_n_avg_conf"]      #replacing the avg confidence in Runtime adaptation Rules to the avg of last n monitored

        if monitor_dict["last_n_energy"] != -1:
            self.knowledge[monitor_dict["model"]][4] = monitor_dict["last_n_energy"]   #updating the last n energy consumption value of the model in Runtime adaptation Rules

        if monitor_dict["last_n_boxes_det"] != -1:  
            self.knowledge[monitor_dict["model"]][5] = monitor_dict["last_n_boxes_det"]

        # updating knowledge.csv (Runtime adaptation Rules)
        f = open("knowledge.csv", "w")
        writer = csv.writer(f)
        writer.writerow(self.knowledge["yolov5n"])
        writer.writerow(self.knowledge["yolov5s"])
        writer.writerow(self.knowledge["yolov5m"])
        writer.writerow(self.knowledge["yolov5l"])
        f.close()
        return
    

    def perform_analysis(self, monitor_dict, energy_of_component):

        print("Inside the Analyzer: Performing the analysis")

        # tracker object created by pyRAPL library, starts tracking
        measure = pyRAPL.Measurement('CPU')
        measure.begin()
        # -------------------------------------

        energy_consumption = monitor_dict["energy_consumption"]
        confidence = monitor_dict["confidence"]
        model = monitor_dict["model"]
        total_confidence = monitor_dict["total_confidence"]
        curr_boxes = monitor_dict["curr_boxes"]

        min_energy = self.knowledge[model][1]
        max_energy = self.knowledge[model][2]
        avg_conf = self.knowledge[model][3]
        # print(max_energy)

        avg_energy = (min_energy+max_energy)/2

        model_avg_score = avg_energy*(1 - avg_conf)
        curr_score = energy_consumption*(1 - confidence)

        # score should be low, if the current score is greater than the model score then adaptation is required
        if curr_score > model_avg_score:

            # stop tracking immediately after analyzer
            measure.end()
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["analyzer"] = pyRAPL_data.pkg[0]/1000000
            # -------------------------------------

            self.count += 1
            print("Creating planner object: ")
            print()
            plan_obj = Planner(energy_consumption, confidence, total_confidence, curr_boxes, model, self.knowledge)
            self.update_knowledge(monitor_dict)
            plan_obj.generate_adaptation_plan(self.count, energy_of_component)
        else:
            # stop tracking immediately after analyzer
            measure.end()
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["analyzer"] = pyRAPL_data.pkg[0]/1000000
            print("\nEnergy of analyzer: ", energy_of_component["analyzer"])
            # -------------------------------------

            # log energy of each component in a csv file
            f = open("MAPEK_energy.csv", "a")
            writer = csv.writer(f)
            writer.writerow(list(energy_of_component.values()))
            f.close()




        

