import Label
import yaml
import time
import numpy
#this module needs to get a ground truth file which contains for each class a list of all images of that class
"""example (ground truth for ImageNet ILSVRC2012), in yaml format: 

            "n01532829": [
                872,
                1555,
                2356,
                48641
            ],
            "n01534433": [
                246,
                712,
                1914
            ]



""" 

#example call: top_n_error_rate(1, out, "../../ILSVRC2012.yaml", range(9))
def top_n_error_rate(n, predictions, path_to_ground_truth, file_ids):
	ground_truth = prepare_ground_truth_dict(path_to_ground_truth)
	print("imported ground truth")
	file_number = 0
	all_correct_files = 0
	all_files = 0
	
	for pred in predictions:
		start = time.time()
		current_file_id = file_ids[file_number]
		top_n_indices = pred.argsort()[-n:][::-1]
		files_in_top_n_categories = set()
		for index in top_n_indices:	
			category_label = Label.Class_names_alexnet[index]		
			print("predicted class: " + category_label + " with value " + str(pred[index]))
			
			category_Id = Label.Class_ids_alexnet[index]
			print(category_Id + " " + category_label)
			if category_Id in ground_truth:
				for file_id in ground_truth[category_Id]:
					files_in_top_n_categories.add(int(file_id))
		if int(current_file_id) in files_in_top_n_categories:
			print("found correct class")
			all_correct_files +=1
		else:
			print("did not find correct class")

		file_number += 1
		all_files += 1
		print("all classified images " + str(all_files))
		print("all correct images " + str(all_correct_files))
		print("time for last img: " + str(time.time()-start))
	return float(all_correct_files)/float(all_files)

def prepare_ground_truth_dict(path_to_ground_truth):
	ground_truth = dict()
	with open(path_to_ground_truth) as ground_truth_file:
		doc = yaml.load(ground_truth_file)
		
		for cat in doc["val"]["gt"]:
			ground_truth[cat] = doc["val"]["gt"][cat]
		ground_truth_file.close()
	return ground_truth
