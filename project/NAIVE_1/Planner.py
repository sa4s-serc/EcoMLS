from Execute import Executor
import pandas as pd
import numpy as np
import random
import pyRAPL
import csv

class Planner():

    def __init__(self, energy_consumption, confidence, total_confidence, curr_boxes, model, knowledge):

        self.energy_consumption = energy_consumption
        self.confidence = confidence
        self.model = model
        self.total_confidence = total_confidence
        self.curr_boxes = curr_boxes
        self.knowledge = knowledge

        self.best_model = None
        self.current_score = self.energy_consumption * (1 - self.confidence)
        self.action = {"yolov5n" : 1, "yolov5s" : 2, "yolov5m" : 3, "yolov5l" : 4}
        self.adaptation = False
        self.best_score = float('inf')

    def generate_adaptation_plan(self, count, energy_of_component):

        # tracker object created by pyRAPL library, starts tracking
        measure = pyRAPL.Measurement('CPU')
        measure.begin()
        # -------------------------------------


        print("----------------------------------------------")
        print("Inside the Planner: Generating the adaptation plan")


        epsilon = random.uniform(0, 1)        
        if epsilon < 0.2:
            print("Random switching")
            print("----------------------------------------------")

            # stop tracking immediately after planner
            measure.end()
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["planner"] = pyRAPL_data.pkg[0]/1000000
            # -------------------------------------

            action = random.randint(1, 4)
            exe_obj = Executor()
            exe_obj.perform_action(action, energy_of_component)
            self.adaptation = True
            return
        
        model_avg_energy = (self.knowledge[self.model][0] + self.knowledge[self.model][1])/2
        print(self.energy_consumption, self.confidence)

        # decide whether to switchmax
        if self.energy_consumption > (1+0.25)*model_avg_energy: #High energy
            print("Energy is very high, need to minimize energy.\n")
            for model, data in self.knowledge.items():

                if model == self.model:
                    continue

                avg_energy = (data[1]+data[2])/2
                last_n_energy = data[4]
                confidence = data[3]
                boxes = data[5]

                # score = avg_energy*(1-confidence)
                score = min(avg_energy, last_n_energy) * (1 - confidence)
                print("model: ", model)
                print("energy: ", avg_energy)
                print("confidence: ", confidence)
                print("boxes: ", boxes)
                print("score: ", score)
                print()

                if avg_energy < self.energy_consumption and self.confidence - confidence <= 0.1:
                    # print("model: ", model)
                    # print("energy: ", avg_energy)
                    # print("confidence: ", confidence)
                    # print("boxes: ", boxes)
                    # print("score: ", score)
                    # print()

                    self.best_score = min(self.best_score, score)
                    self.best_model = model if self.best_score == score else self.best_model
                    print("best score: ", self.best_score)
                    print("best model: ", self.best_model)
                    print()

            print(f"Switching to {self.best_model} for lower energy and greater than equal to confidence\n\n")
            if self.best_model is None:
                action = 0
                print("----------------------------------------------")
            else:
                action = self.action[self.best_model]
                print("----------------------------------------------")

            # stop tracking immediately after planner
            measure.end()   
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["planner"] = pyRAPL_data.pkg[0]/1000000
            # -------------------------------------

            exe_obj = Executor()
            exe_obj.perform_action(action, energy_of_component)
            self.adaptation = True
            
        else: #medium energy
            print("Energy is medium so improving the confidence.\n")
            for model, data in self.knowledge.items():

                if model == self.model:
                    continue

                avg_energy = (data[1]+data[2])/2
                last_n_energy = data[4]
                confidence = data[3]
                boxes = data[5]

                score = min(avg_energy, last_n_energy) * (1 - confidence)
                print("model: ", model)
                print("energy: ", avg_energy)
                print("confidence: ", confidence)
                print("boxes: ", boxes)
                print("score: ", score)
                print()

                # if confidence > self.confidence and avg_energy <= self.energy_consumption:
                if confidence > self.confidence:                    
                    # print("model: ", model)
                    # print("energy: ", avg_energy)
                    # print("confidence: ", confidence)
                    # print("boxes: ", boxes)
                    # print("score: ", score)
                    # print()

                    self.best_score = max(self.best_score, score)
                    self.best_model = model if self.best_score == score else self.best_model
                    print("best score: ", self.best_score)
                    print("best model: ", self.best_model)
                    print()
                    
            print(f"Switching to {self.best_model} for higher confidence.\n\n")
            if self.best_model is None:
                action = 0
                print("----------------------------------------------")
            else:
                action = self.action[self.best_model]
                print("----------------------------------------------")
            
            # stop tracking immediately after planner
            measure.end()
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["planner"] = pyRAPL_data.pkg[0]/1000000
            # -------------------------------------

            exe_obj = Executor()
            exe_obj.perform_action(action, energy_of_component)
            self.adaptation = True


        # no adaptation required
        if self.adaptation == False:

            # stop tracking immediately after planner
            measure.end()
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["planner"] = pyRAPL_data.pkg[0]/1000000
            # -------------------------------------

            # log energy of each component in a csv file
            f = open("MAPEK_energy.csv", "a")
            writer = csv.writer(f)
            writer.writerow(list(energy_of_component.values()))
            f.close()

            print("Staying with the current model. No switching\n\n")
            print("----------------------------------------------")
            return 


        

        

