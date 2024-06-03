import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from lib_file import lib_path


model = load_model("model/ConvolutionalNeuralNetwork_model.h5", compile=False)


class_labels = ['Apple', 'Blueberry', 'Cherry', 'Corn',
                'Grape', 'Peach', 'Pepper', 'Potato', 'Raspberry', 'Soybean']


def leaf_prediction(user_input):
    print("user_input : ", user_input)
    filepath = user_input

    image = cv2.imread(filepath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (128, 128))

    plt.imshow(image)
    plt.title(label="Input Image")
    plt.axis("off")
    # plt.show()

    image = image/255.0
    image = np.expand_dims(image, axis=0)
    # image.shape

    prediction = model.predict(image, verbose=1)
    # print(prediction)

    class_index = prediction.argmax()
    class_label = class_labels[class_index]
    probability = prediction[0][class_index]

    print(class_index)
    print(class_label)
    print(probability)

    for text in os.listdir("info"):
        label = text.split(".")[0]
        if label == class_label.lower():
            filepath = os.path.join("info", f"{label}.txt")
            with open(file=filepath, mode='r') as file:
                data = file.read()
                # print(data)
        else:
            continue

    return class_label, probability, data
