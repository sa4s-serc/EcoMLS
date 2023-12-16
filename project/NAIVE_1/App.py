import argparse
import io
import csv
from PIL import Image
import argparse
import time
import numpy as np
from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI()
input_rate = 0
start_time = 0
total_in = 0
pic_quality = 100
file_size = 0

DETECTION_URL = '/v1/object-detection'

def compress_image(image_bytes):

    global pic_quality
    global file_size

    # Open the image
    img = Image.open(io.BytesIO(image_bytes))

    # Compress the image (adjust quality as needed)
    compressed_image = io.BytesIO()
    img.save(compressed_image, format="JPEG", quality=pic_quality)

    # Convert compressed image to bytes
    compressed_image_bytes = compressed_image.getvalue()

    # getting the size of image file
    image_file = io.BytesIO(compressed_image_bytes)
    file_size = len(image_file.getvalue())

    return compressed_image_bytes


@app.post(DETECTION_URL)
async def predict( image: UploadFile = File(...) ):
    # print(image)
    global start_time
    global input_rate
    global total_in
    global pic_quality
    global file_size
    
    # if(time.time() - start_time > 1 ):
    #         f = open("monitor.csv", "w")
    #         f.write(f'{input_rate}')
    #         f.close()
    #         start_time = time.time()
    #         input_rate = 0

    # input_rate+=1
    im_bytes = await image.read()
    compressed_im_bytes = compress_image(im_bytes)

    # print(im_bytes)
    x = time.time()
    filename = f"images/queue{total_in}.csv"

    f = open(filename, "w")
    writer = csv.writer(f)
    writer.writerow([x])
    # writer.writerow(im_bytes)
    writer.writerow(compressed_im_bytes)
    writer.writerow([pic_quality]) ################
    writer.writerow([file_size])
    f.close()

    # with open("x.jpg", "wb") as file:
    #     file.write(compressed_im_bytes)
    
    total_in += 1
    return    
    

if __name__ == '__main__':

    port = 5000
    parser = argparse.ArgumentParser(description='Flask API exposing YOLOv5 model')
    parser.add_argument('--port', default=port, type=int, help='port number')
    parser.add_argument('--model', nargs='+', default=['yolov5s'], help='model(s) to run, i.e. --model yolov5n yolov5s')
    opt = parser.parse_args()
    current_model = opt.model[0]  # use the first model in the list as the default
    uvicorn.run(app, host='0.0.0.0', port=opt.port)
    # app.run(host='0.0.0.0', port=opt.port)