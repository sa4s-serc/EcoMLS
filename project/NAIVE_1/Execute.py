class Executor():

    def __init__(self):
        self.model_action = {1:"yolov5n", 2:"yolov5s", 3:"yolov5m", 4:"yolov5l"}
    
    def perform_action(self, action):

        print('Inside Execute, performing action: ', action)

        if action == 0:
            return
        # model switch takes place by changing model name in model.csv file .

        print(f"switching to {self.model_action[action]}")
        f = open("model.csv", "w")
        f.write(self.model_action[action])
        f.close()
        print("Adaptation completed.")
