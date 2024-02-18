import csv
import io
from PIL import Image
import time
import torch
import psutil
import pandas as pd
import imghdr
import os
import numpy as np
import pyRAPL
from ultralytics import YOLO

class ImageProcessor:

    def __init__(self):

        self.models = self.load_models()
        self.total_processed = 0
        self.global_start_time = 0
        self.image_quality = 0
        self.input_rate = self.get_input_rate()
        self.avg_conf = 0
        self.current_boxes = 0
        self.absolute_time = -1

        pyRAPL.setup()

        self.logs = {'yolov5n':'log_yolov5n.csv', 'yolov5s':'log_yolov5s.csv', 'yolov5m':'log_yolov5m.csv', 'yolov5l':'log_yolov5l.csv', 'yolov5x':'log_yolov5x.csv'}
        self.make_header()
        self.model_n = {'yolov5n':1, 'yolov5s':1, 'yolov5m':1, 'yolov5l':1, 'yolov5x':1}


    # loads all 5 models at the start in an array named models
    def load_models(self):
        models = {}

        for m in {'yolov5n', 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x'}:
            z = m + 'u.pt'
            models[m] = YOLO(z)        
        return models
    

    def get_input_rate(self):
        # Read in the inter-arrival times from the CSV file
        file_path = 'resampled_scaled_inter_arrivals.csv'

        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                # Exclude zero inter-arrival times
                inter_arrivals = [float(row[0].strip()) for row in reader if float(row[0].strip()) != 0] 
        except FileNotFoundError:
            print("File not found. Please check the file path.")
            exit()

        # Convert inter-arrival times to arrival rates
        input_rate = 1.0 / np.array(inter_arrivals)
        return input_rate


    def make_header(self):
        header = ["total_processed","input_rate","image_quality","file_size(kB)","current_model",
                    "total_conf","avg_conf","current_boxes","energy_consumption(J)","current_cpu",
                    "measure_duration(s)","current_time","start_time","absolute_time"]

        f = open("log.csv", "w")
        writer = csv.writer(f)
        writer.writerow(header)
        f.close()

        # making separate log files to monitor each model
        for i in self.logs.values():
            f = open(i, "w")
            writer = csv.writer(f)
            writer.writerow(header)
            f.close()

        return


    def get_current_model(self):

        df = pd.read_csv('model.csv', header=None)
        array = df.to_numpy()
        print(array[0][0])
        return array[0][0]
    

    def update_knowledge(self):


        knowledge_df = pd.read_csv("knowledge.csv", header=None)
        knowledge_data = knowledge_df.to_numpy()
        knowledge = dict()
        knowledge["yolov5n"] = [0, knowledge_data[0][1], knowledge_data[0][2], knowledge_data[0][3], knowledge_data[0][4]]
        knowledge["yolov5s"] = [1, knowledge_data[1][1], knowledge_data[1][2], knowledge_data[1][3], knowledge_data[1][4]]
        knowledge["yolov5m"] = [2, knowledge_data[2][1], knowledge_data[2][2], knowledge_data[2][3], knowledge_data[2][4]]
        knowledge["yolov5l"] = [3, knowledge_data[3][1], knowledge_data[3][2], knowledge_data[3][3], knowledge_data[3][4]]

        m = knowledge[self.current_model][3]
        n = self.model_n[self.current_model] = self.model_n[self.current_model]+1
        knowledge[self.current_model][3] = m + (self.avg_conf - m)/n
        knowledge[self.current_model][4] = self.energy_consumption

        # updating the averge confidence of the current model
        f = open("knowledge.csv", "w")
        writer = csv.writer(f)
        writer.writerow(knowledge["yolov5n"])
        writer.writerow(knowledge["yolov5s"])
        writer.writerow(knowledge["yolov5m"])
        writer.writerow(knowledge["yolov5l"])
        f.close()
        return
    

    # run's the object detection on the received data
    def process_row(self, im_bytes):
        image_format = imghdr.what(None, h=im_bytes)
        if image_format is None:
            return
        
        self.current_model  = self.get_current_model()
        if self.current_model in self.models:
            try:
                if (self.total_processed == 0):
                    self.global_start_time = time.time()
                
                print("In process_row")

                im = Image.open(io.BytesIO(im_bytes))
                self.current_time = time.time()
            
                results = self.models[self.current_model](im)

                self.current_cpu = psutil.cpu_percent(interval=None)
                self.total_processed += 1

                confidences = results[0].boxes.conf.tolist()
                self.current_conf = sum(confidences)  ####
                self.current_boxes = len(confidences)
                print(self.current_boxes)

                if (self.current_boxes != 0):
                    self.avg_conf = self.current_conf/self.current_boxes
                    print(self.avg_conf)

                t = time.time()
                self.current_time = t - self.current_time
                self.start_time = t - self.start_time
                self.absolute_time = t - self.global_start_time

            except Exception as e:
                print(str(e))
                return {'error': str(e)}

        else:
            return {'error': f'Model {self.current_model} not found'}


    # checks for the current image csv file in images folder, and if it exists, it sends the image_data to process_row function   
    def start_processing(self):

        while self.total_processed < 25000:

            r = 0
            image_path = f"images/queue{self.total_processed}.csv"
            image_path_next = f"images/queue{self.total_processed+1}.csv"

            if os.path.exists(image_path) == False:
                print(f"File not exist {self.total_processed}")

                if (os.path.exists(image_path_next) == False):
                    time.sleep(0.03)
                    continue
                else:
                    print("Skipping file...........................")
                    self.total_processed += 1
                    image_path = image_path_next
                
            with open(image_path, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if len(rows) >= 4:
                try:
                    first_row = rows[1]
                    self.start_time = float(rows[0][0])
                    self.image_quality = rows[2][0]
                    self.file_size = int(rows[3][0])/1000
                    print(self.start_time)
                    first_row = [int(x) for x in first_row]
                    first_row = bytes(first_row)

                    # tracker object created by pyRAPL library, starts tracking
                    measure = pyRAPL.Measurement('CPU')
                    measure.begin()
                    # Process the first row
                    self.process_row(first_row)
                    # stop tracking immediately after the function call
                    measure.end()

                    print(self.file_size)
                    print(measure.result)

                    pyRAPL_data = measure.result
                    self.energy_consumption = pyRAPL_data.pkg[0]/1000000
                    measure_duration = pyRAPL_data.duration/1000000

                    # writes the logs in a log.csv file.
                    print("To write in log file.")
                    f = open("log.csv", "a")
                    f.write(
                        f'{self.total_processed},{self.input_rate[self.total_processed]},{self.image_quality},{self.file_size},{self.current_model},{self.current_conf},{self.avg_conf},{self.current_boxes},{self.energy_consumption},{self.current_cpu},{measure_duration},{self.current_time},{self.start_time},{self.absolute_time}\n')
                    f.close()

                    # writes the logs in a separate log file for each model.
                    f = open(self.logs[self.current_model], "a")
                    f.write(
                        f'{self.total_processed},{self.input_rate[self.total_processed]},{self.image_quality},{self.file_size},{self.current_model},{self.current_conf},{self.avg_conf},{self.current_boxes},{self.energy_consumption},{self.current_cpu},{measure_duration},{self.current_time},{self.start_time},{self.absolute_time}\n')
                    f.close()

                    monitor_f = open("monitor.csv", "w")
                    writer = csv.writer(monitor_f)
                    writer.writerow([self.total_processed])
                    writer.writerow([self.energy_consumption])
                    writer.writerow([self.avg_conf])
                    writer.writerow([self.current_conf])
                    writer.writerow([self.current_boxes])
                    monitor_f.close()
                    
                    # Delete the processed CSV image file from the folder
                    os.remove(image_path)
                    print("Finished processing.\n")

                except Exception as e:
                    print("Inside exception")
                    print("skipping file--------------------------------")
                    print(e)
                    self.total_processed += 1

            elif len(rows) == 1:
                print("skipping file----------------------------------")
                self.total_processed += 1
            else:
                print("Empty")
                time.sleep(0.5)
                continue

        return

if __name__ == '__main__':

    image_processor = ImageProcessor()

    # start processing the images.
    image_processor.start_processing()

    print("Finished processing all images.")


    