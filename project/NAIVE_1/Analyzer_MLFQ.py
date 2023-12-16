from Planner_MLFQ import Planner
import pandas as pd
import numpy as np
import time

class Analyzer():

    def __init__(self):

        self.time = -1
        self.count = 0

        knowledge_df = pd.read_csv("knowledge.csv", header=None)
        knowledge_data = knowledge_df.to_numpy()
        print(knowledge_data[0][3])
        self.knowledge = dict()
        self.knowledge["yolov5n"] = [knowledge_data[0][1], knowledge_data[0][2], knowledge_data[0][3]]
        self.knowledge["yolov5s"] = [knowledge_data[1][1], knowledge_data[1][2], knowledge_data[1][3]]
        self.knowledge["yolov5m"] = [knowledge_data[2][1], knowledge_data[2][2], knowledge_data[2][3]]
        self.knowledge["yolov5l"] = [knowledge_data[3][1], knowledge_data[3][2], knowledge_data[3][3]]
        
        # self.planner = Planner(list(self.knowledge.keys()))

        # self.scores = dict()
        # for model, data in self.knowledge.items():
        #     avg_energy = (data[0]+data[1])/2
        #     confidence = data[2]
        #     score = avg_energy * (1 - confidence)
        #     self.scores[model] = score

    def perform_analysis(self, monitor_dict):

        print("Inside the Analyzer: Performing the analysis")

        energy_consumption = monitor_dict["energy_consumption"]
        confidence = monitor_dict["confidence"]
        model = monitor_dict["model"]

        min_energy = self.knowledge[model][0]
        max_energy = self.knowledge[model][1]
        avg_conf = self.knowledge[model][2]
        # print(max_energy)

        avg_energy = (min_energy+max_energy)/2
        score = avg_energy*(1 - avg_conf)
        curr_score = energy_consumption*(1 - confidence)

        # Update scores and priorities
        # self.scores[model] = curr_score
        # self.planner.update_priorities(self.scores)


        # score should be low, if the current score is greater than the modell score then adaptation is required
        if curr_score > score:

            self.count += 1
            print("Calling Planner: ")
            # plan_obj = Planner(energy_consumption, confidence, model)
            # plan_obj.generate_adaptation_plan(self.count)
            # self.planner.set_execute_flag()


        

