from Execute import Executor
import pandas as pd
import numpy as np
import random
import time

class Planner():

    def __init__(self):

        # self.energy_connsumption = energy_consumption
        # self.confidence = confidence
        # self.current_model = model
        pass

    def update_priorities(self, scores):
        # Update priorities based on scores
        for model in self.models:
            if scores[model] > 0.8:
                self.queues[0].append(model)
            elif scores[model] > 0.5:
                self.queues[1].append(model)
            else:
                self.queues[2].append(model)

        # Reset time slice and current model
        self.time_slice = 0
        self.current_model = None

    def run(self):
        while True:

            # Read scores from knowledge.csv
            knowledge_df = pd.read_csv("knowledge.csv", header=None)
            knowledge_data = knowledge_df.to_numpy()
            print(knowledge_data[0][3])
            self.knowledge = dict()
            self.knowledge["yolov5n"] = [knowledge_data[0][1], knowledge_data[0][2], knowledge_data[0][3]]
            self.knowledge["yolov5s"] = [knowledge_data[1][1], knowledge_data[1][2], knowledge_data[1][3]]
            self.knowledge["yolov5m"] = [knowledge_data[2][1], knowledge_data[2][2], knowledge_data[2][3]]
            self.knowledge["yolov5l"] = [knowledge_data[3][1], knowledge_data[3][2], knowledge_data[3][3]]
            
            scores = dict()
            for model, data in self.knowledge.items():
                avg_energy = (data[0]+data[1])/2
                confidence = data[2]
                score = avg_energy * (1 - confidence)
                scores[model] = score + random.uniform(-0.1, 0.1)

            # Update priorities based on scores
            self.update_priorities(scores)

            time.sleep(1)

if __name__ == "__main__":
    models = ["yolov5n", "yolov5s", "yolov5m", "yolov5l"]
    planner = Planner(models)
    planner.run()
