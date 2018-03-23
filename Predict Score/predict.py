import os
import sys
import cv2
import glob
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from wide_resnet import WideResNet
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import InceptionV3
from keras.layers import Dense, GlobalAveragePooling2D, Dropout
from keras.utils.training_utils import multi_gpu_model
from keras.models import Model
from utilities import *

# Constants
gender_img_size = 64
predict_img_size = 256

# Loading models
gender_model = WideResNet(gender_img_size, depth=16, k=8)()
gender_model.load_weights(os.path.join("pretrained weights", "weights.18-4.06.hdf5"))
print("Gender models loaded.")

female_base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(predict_img_size, predict_img_size, 3))
male_base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(predict_img_size, predict_img_size, 3))
print("Base models loaded.")

x_female = female_base_model.output
x_female = GlobalAveragePooling2D()(x_female)
x_female = Dense(1024, activation='relu')(x_female)
predictions_female = Dense(2, activation='softmax')(x_female)
female_model = Model(inputs=female_base_model.input, outputs=predictions_female)

x_male = male_base_model.output
x_male = GlobalAveragePooling2D()(x_male)
x_male = Dense(1024, activation='relu')(x_male)
predictions_male = Dense(2, activation='softmax')(x_male)
male_model = Model(inputs=male_base_model.input, outputs=predictions_male)

female_model = multi_gpu_model(female_model, gpus=2)
male_model = multi_gpu_model(male_model, gpus=2)

female_model.load_weights(os.path.join("pretrained weights", "inception_finetuned_female.h5"))
male_model.load_weights(os.path.join("pretrained weights", "inception_finetuned_male.h5"))
print("Finetuned models loaded.")

# Cropping images and labelling appropriately. This will create temporary sub folders for each image, and will contain the subimage(s) within
final_dict = []
image_glob = glob.glob("../examples/*.jpg")
os.mkdir("../examples/distribute")
for i in range(len(image_glob)):
    fname, ext = os.path.splitext(image_name)
    print("Distributing " + fname)
    final_dict.append((fname, 0, 0))
    os.rename(image_glob[i], "../examples/distrubute/" + os.path.basename(image_glob[i]))

print("All images distributed.")

sys.exit()

# Propagating examples through gender + age classifier
gen = image.ImageDataGenerator()
gender_batches = gen.flow_from_directory("../examples/", target_size=(gender_img_size,gender_img_size), class_mode=None, shuffle=False, batch_size=1)
predict_batches = gen.flow_from_directory(examples_directory, target_size(predict_img_size,predict_img_size), class_mode=None, shuffle=False, batch_size=1)

results = model.predict_generator(gender_batches, verbose = 1)

predicted_genders = results[0]
print(predicted_genders)
ages = np.arange(0, 101).reshape(101, 1)
predicted_ages = results[1].dot(ages).flatten()

print("Got predictions.")

max_score_pic = ""
max_fem_prob = 0
max_male_prob = 0

for i in range(len(predicted_genders)):
    if predicted_ages[i] >= 13:
        current_filename_basename = os.path.basename(batches.filenames[i])
        print(current_filename_basename)
        if predicted_genders[i][0] >= 0.8:
            print("Female image.")
            os.rename(data_directory + current_filename_basename, dataset_directory + "female\\" + current_filename_basename)
        elif predicted_genders[i][1] >= 0.8:
            os.rename(data_directory + current_filename_basename, dataset_directory + "male\\" + current_filename_basename)
            print("Male image.")
        else:
            print("Unclear!")