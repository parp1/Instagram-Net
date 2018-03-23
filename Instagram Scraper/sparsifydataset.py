import os
import sys
import glob
import numpy as np
from numpy.random import random, permutation, randn, normal, uniform, choice
import shutil

def sparsify_directory(directory, keep_top_half):
	g = glob.glob(directory + "*.jpg")
	value_list = []

	for i in range(len(g)):
		current_file = os.path.basename(g[i])

		file_split = current_file.split("-")

		try: score = int(file_split[0])
		except: score = 0

		value_list.append((score, current_file))

		value_list.sort(key=lambda tup: tup[0])
	
	if keep_top_half:
		delete = value_list[ : int(len(g) / 2)]
	else:
		delete = value_list[int(len(g) / 2) : ]

	print("Deleting " + str(len(delete)) + " examples.")

	for i in range(len(delete)):
		os.remove(directory + delete[i][1])

working_directory = sys.argv[1]
os.chdir(working_directory)
print(os.getcwd())

sparsify_directory(directory = working_directory + "female/train/good/", keep_top_half = True)
sparsify_directory(directory = working_directory + "female/train/bad/", keep_top_half = False)
sparsify_directory(directory = working_directory + "female/valid/good/", keep_top_half = True)
sparsify_directory(directory = working_directory + "female/valid/bad/", keep_top_half = False)

sparsify_directory(directory = working_directory + "male/train/good/", keep_top_half = True)
sparsify_directory(directory = working_directory + "male/train/bad/", keep_top_half = False)
sparsify_directory(directory = working_directory + "male/valid/good/", keep_top_half = True)
sparsify_directory(directory = working_directory + "male/valid/bad/", keep_top_half = False)