from Execute import Executor
import pandas as pd
import numpy as np
import random

class Planner():

    def __init__(self, energy_consumption, confidence, model):

        self.energy_connsumption = energy_consumption
        self.confidence = confidence
        self.model = model

        knowledge_df = pd.read_csv("knowledge.csv", header=None)
        knowledge_data = knowledge_df.to_numpy()
        self.knowledge = dict()
        self.knowledge["yolov5n"] = [knowledge_data[0][1], knowledge_data[0][2], knowledge_data[0][3], knowledge_data[0][4]]
        self.knowledge["yolov5s"] = [knowledge_data[1][1], knowledge_data[1][2], knowledge_data[1][3], knowledge_data[1][4]]
        self.knowledge["yolov5m"] = [knowledge_data[2][1], knowledge_data[2][2], knowledge_data[2][3], knowledge_data[2][4]]
        self.knowledge["yolov5l"] = [knowledge_data[3][1], knowledge_data[3][2], knowledge_data[3][3], knowledge_data[3][4]]

        # self.knowledge["yolov5n"] = [knowledge_data[0][1], knowledge_data[0][2], knowledge_data[0][3]]
        # self.knowledge["yolov5s"] = [knowledge_data[1][1], knowledge_data[1][2], knowledge_data[1][3]]
        # self.knowledge["yolov5m"] = [knowledge_data[2][1], knowledge_data[2][2], knowledge_data[2][3]]
        # self.knowledge["yolov5l"] = [knowledge_data[3][1], knowledge_data[3][2], knowledge_data[3][3]]

        self.best_model = None
        self.current_score = self.energy_connsumption * (1 - self.confidence)
        self.action = {"yolov5n" : 1, "yolov5s" : 2, "yolov5m" : 3, "yolov5l" : 4}
        self.adaptation = False

    # this function make a decision based on the knowledge.
    # decide action such that energy is less and avg_confidence is high or remains same.
    # if energy is high, switch to a model with less energy and high confidence
    # if energy is low, switch to a model with high confidence
    # if energy is medium, switch to a model with high confidence
    def generate_adaptation_plan(self, count):

        # epsilon = random.uniform(0, 1)        
        # if epsilon < 0.5:
        #     print("Random switching")
        #     action = random.randint(1, 4)
        #     exe_obj = Executor()
        #     exe_obj.perform_action(action)
        #     self.adaptation = True
        #     return
        
        model_avg_energy = (self.knowledge[self.model][0] + self.knowledge[self.model][1])/2
        print(self.energy_connsumption, self.confidence)

        # decide whether to switch
        if self.energy_connsumption > model_avg_energy: #High energy
            print("Energy is very high, need to minimize energy.")
            for model, data in self.knowledge.items():
                if model == self.model:
                    continue
                # print(model)
                avg_energy = (data[0]+data[1])/2
                recent_eng_measure = data[3]
                confidence = data[2]
                print(avg_energy, confidence)
                # if avg_energy < self.energy_connsumption:

                # score = avg_energy*(1-confidence)
                score = min(avg_energy, recent_eng_measure) * (1 - confidence)
                print(score)
                if score < self.current_score and self.confidence - confidence < 0.1:
                    print(model)
                    self.best_model = model
                    self.current_score = score

            print(f"Switching to {self.best_model} for lower energy and greater than equal to confidence\n\n")
            if self.best_model is None:
                action = 0
            else:
                action = self.action[self.best_model]
            exe_obj = Executor()
            exe_obj.perform_action(action)
            self.adaptation = True
            
        else: #medium energy
            print("Energy is medium so improving the confidence.")
            for model, data in self.knowledge.items():
                if model == self.model:
                    continue
                avg_energy = (data[0]+data[1])/2
                recent_eng_measure = data[3]
                confidence = data[2]
                print(avg_energy, confidence)
                # if confidence > self.confidence and avg_energy <= self.energy_connsumption:
                if confidence > self.confidence:
                    
                    # score = avg_energy*(1-confidence)
                    score = min(avg_energy, recent_eng_measure) * (1 - confidence)
                    print(score)
                    if score < self.current_score:
                        self.best_model = model
                        self.current_score = score

            print(f"Switching to {self.best_model} for higher confidence.\n\n")
            if self.best_model is None:
                action = 0
            else:
                action = self.action[self.best_model]
            exe_obj = Executor()
            exe_obj.perform_action(action)
            self.adaptation = True

        # no adaptation required
        if self.adaptation == False:
            print("Staying with the current model. No switching\n\n")
            return 


        

        

