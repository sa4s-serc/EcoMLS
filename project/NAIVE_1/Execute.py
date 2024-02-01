import pyRAPL
import csv

class Executor():

    def __init__(self):
        self.model_action = {1:"yolov5n", 2:"yolov5s", 3:"yolov5m", 4:"yolov5l"}
    
    def perform_action(self, action, energy_of_component):

        # tracker object created by pyRAPL library, starts tracking
        measure = pyRAPL.Measurement('CPU')
        measure.begin()

        print('Inside Execute, performing action: ', action)

        if action == 0:
            # stop tracking immediately after monitoring
            measure.end()
            # get the energy consumption
            pyRAPL_data = measure.result
            energy_of_component["executor"] = pyRAPL_data.pkg[0]/1000000
            print("Energy of executor: ", energy_of_component["executor"])

            # log energy of each component in a csv file
            f = open("MAPEK_energy.csv", "a")
            writer = csv.writer(f)
            writer.writerow(list(energy_of_component.values()))
            f.close()
            
            return
        

        # model switch takes place by changing model name in model.csv file.
        print(f"switching to {self.model_action[action]}")
        f = open("model.csv", "w")
        f.write(self.model_action[action])
        f.close()

        # stop tracking immediately after monitoring
        measure.end()
        # get the energy consumption
        pyRAPL_data = measure.result
        energy_of_component["executor"] = pyRAPL_data.pkg[0]/1000000
        print("Energy of executor: ", energy_of_component["executor"])
        # -------------------------------------

        # log energy of each component in a csv file
        f = open("MAPEK_energy.csv", "a")
        writer = csv.writer(f)
        writer.writerow(list(energy_of_component.values()))
        f.close()

        print("Adaptation completed.")
