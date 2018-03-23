import os
import sys
import glob
import numpy as np
from numpy.random import random, permutation, randn, normal, uniform, choice
import shutil

def moveToGoodOrBad(directory, num_examples):
	g = glob.glob(directory + "*.jpg")

	num_negatives = 0
	for i in range(num_examples):
		if (os.path.basename(g[i])[0] == "-"):
			os.rename(g[i], directory + "bad/" + os.path.basename(g[i]))
			num_negatives += 1

	num_good = int(num_examples / 2) # This number can be changed for a different split between good/bad selfies
	num_bad = num_examples - num_good - num_negatives

	g = glob.glob(directory + "*.jpg")
	value_list = []

	for i in range(len(g)):
		current_file = os.path.basename(g[i])
		value_list.append((int(current_file.split("-")[0]), current_file))

	value_list.sort(key=lambda tup: tup[0]) 

	bad = value_list[:num_bad]
	good = value_list[num_bad:]

	for i in range(num_bad):
		os.rename(directory + bad[i][1], directory + "bad/" + bad[i][1])

	for i in range(num_good):
		os.rename(directory + good[i][1], directory + "good/" + good[i][1])

### Preconditions: Run this from a directory that has one folder data, which has two subfolders, male and female ###
### The directory structure should look like this:
### data
###     - male
###          - ... all male examples
###     - female
###          - ... all female examples

working_directory = sys.argv[1]
os.chdir(working_directory)
print(os.getcwd())

try:
	os.mkdir("male/train")
	os.mkdir("male/train/good")
	os.mkdir("male/train/bad")
	os.mkdir("female/train")
	os.mkdir("female/train/good")
	os.mkdir("female/train/bad")

	os.mkdir("male/valid")
	os.mkdir("male/valid/good")
	os.mkdir("male/valid/bad")
	os.mkdir("female/valid")
	os.mkdir("female/valid/good")
	os.mkdir("female/valid/bad")
except Exception as e:
	pass

g_man = glob.glob("male/*.jpg")
g_woman = glob.glob("female/*.jpg")

num_male_examples = len(g_man)
num_female_examples = len(g_woman)

print("Total male examples: " + str(num_male_examples))
print("Total female examples: " + str(num_female_examples))

shuf_man = np.random.permutation(g_man)
shuf_woman = np.random.permutation(g_woman)

num_male_examples_valid = int(0.1 * num_male_examples)
num_female_examples_valid = int(0.1 * num_female_examples)

print("Validation male examples: " + str(num_male_examples_valid))
print("Validation female examples: " + str(num_female_examples_valid))

### Moving 10% of each set to validation folder ###
for i in range(num_male_examples_valid):
    os.rename(shuf_man[i], "male/valid/" + os.path.basename(shuf_man[i]))

for i in range(num_female_examples_valid):
    os.rename(shuf_woman[i], "female/valid/" + os.path.basename(shuf_woman[i]))

### Moving the rest to train folder ###
g_man = glob.glob("male/*.jpg")
g_woman = glob.glob("female/*.jpg")

num_male_examples_train = num_male_examples - num_male_examples_valid
num_female_examples_train = num_female_examples - num_female_examples_valid

print("Train male examples: " + str(num_male_examples_train))
print("Train female examples: " + str(num_female_examples_train))

for i in range(num_male_examples_train):
    os.rename(g_man[i], "male/train/" + os.path.basename(g_man[i]))

for i in range(num_female_examples_train):
    os.rename(g_woman[i], "female/train/" + os.path.basename(g_woman[i]))

### Moving to good or bad folders respectively (assumes all negative scores will go into the bad folder) ###
moveToGoodOrBad("male/train/", num_male_examples_train)
moveToGoodOrBad("male/valid/", num_male_examples_valid)

moveToGoodOrBad("female/train/", num_female_examples_train)
moveToGoodOrBad("female/valid/", num_female_examples_valid)
