#!/usr/bin/env python
"""
classify.py is an out-of-the-box image classifer callable from the command line.

By default it configures and runs the Alexnet ImageNet model.
"""
import numpy as np
import os
import sys
import argparse
import glob
import time
from string_sorter import sort_list_natural

import caffe
from top_n_error_rate import ErrorRateCalculator


def main(argv):
    pycaffe_dir = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    # Required arguments: input and output files.
    parser.add_argument(
        "input_file",
        help="Input image, directory, or npy."
    )
    parser.add_argument(
        "output_file",
        help="Output npy filename."
    )
    # Optional arguments.
    parser.add_argument(
        "--model_def",
        default=os.path.join(pycaffe_dir,
                "../models/bvlc_alexnet/deploy.prototxt"),
        help="Model definition file."
    )
    parser.add_argument(
        "--pretrained_model",
        default=os.path.join(pycaffe_dir,
                "../models/bvlc_alexnet/bvlc_alexnet.caffemodel"),
        help="Trained model weights file."
    )
    parser.add_argument(
        "--gpu",
        action='store_true',
        help="Switch for gpu computation."
    )
    parser.add_argument(
        "--center_only",
        action='store_true',
        help="Switch for prediction from center crop alone instead of " +
             "averaging predictions across crops (default)."
    )
    parser.add_argument(
        "--images_dim",
        default='256,256',
        help="Canonical 'height,width' dimensions of input images."
    )
    parser.add_argument(
        "--mean_file",
        default=os.path.join(pycaffe_dir,
                             'caffe/imagenet/ilsvrc_2012_mean.npy'),
        help="Data set image mean of [Channels x Height x Width] dimensions " +
             "(numpy array). Set to '' for no mean subtraction."
    )
    parser.add_argument(
        "--input_scale",
        type=float,
        help="Multiply input features by this scale to finish preprocessing."
    )
    parser.add_argument(
        "--raw_scale",
        type=float,
        default=255.0,
        help="Multiply raw input by this scale before preprocessing."
    )
    parser.add_argument(
        "--channel_swap",
        default='2,1,0',
        help="Order to permute input channels. The default converts " +
             "RGB -> BGR since BGR is the Caffe default by way of OpenCV."
    )
    parser.add_argument(
        "--ext",
        default='jpg',
        help="Image file extension to take as input when a directory " +
             "is given as the input file."
    )
    args = parser.parse_args()

    image_dims = [int(s) for s in args.images_dim.split(',')]

    mean, channel_swap = None, None
    if args.mean_file:
        mean = np.load(args.mean_file)
    if args.channel_swap:
        channel_swap = [int(s) for s in args.channel_swap.split(',')]

    if args.gpu:
        caffe.set_mode_gpu()
        print("GPU mode")
    else:
        caffe.set_mode_cpu()
        print("CPU mode")

    # Make classifier.
    classifier = caffe.Classifier(args.model_def, args.pretrained_model,
            image_dims=image_dims, mean=mean,
            input_scale=args.input_scale, raw_scale=args.raw_scale,
            channel_swap=channel_swap)

    # Load numpy array (.npy), directory glob (*.jpg), or image file.
    args.input_file = os.path.expanduser(args.input_file)
    if args.input_file.endswith('npy'):
        print("Loading file: %s" % args.input_file)
        inputs = np.load(args.input_file)
    elif os.path.isdir(args.input_file):
        print("Loading folder: %s" % args.input_file)
	for im_f in glob.glob(args.input_file + '/*.' + args.ext):
	    print("file name " + im_f)
	input_files = glob.glob(args.input_file + '/*.' + args.ext)
	input_files_sorted = sort_list_natural(input_files)
        inputs =[caffe.io.load_image(im_f)
                 for im_f in input_files_sorted]
	for im_f in input_files_sorted:
	    print("file name " + im_f)
	
    else:
        print("Loading file: %s" % args.input_file)
        inputs = [caffe.io.load_image(args.input_file)]

    print("Classifying %d inputs." % len(inputs))
    batch_size = 10
    i = 0
    # Classify.
    start = time.time()
    correct_images = 0
    n = 5
    error_rate_calc = ErrorRateCalculator("../../../workspace/ILSVRC2012.yaml")
    while (i+1)*batch_size < len(inputs):
        print("classifying inputs from " + str(i*batch_size) + " to " + str((i+1) * batch_size))
        img_start = time.time()
        prediction = classifier.predict(inputs[i*batch_size:(i+1)*batch_size], oversample=False)
        print("Time for last 10 images " + str(time.time() - img_start))
        error_rate = error_rate_calc.top_n_error_rate(n, prediction, range(i*batch_size,(i+1)*batch_size))
        print(str(error_rate))
        correct_images+= (error_rate * batch_size)
        print("Top " + str(n) + " error rate: " + str(float(correct_images)/float((i+1)*batch_size)))
        i=i+1
    prediction = classifier.predict(inputs[i*batch_size:len(inputs)], oversample=False)
    error_rate = error_rate_calc.top_n_error_rate(n, prediction, range(i*batch_size,len(inputs)))
    print(str(error_rate))
    last_images = len(inputs) - (i* batch_size)
    correct_images+= (error_rate * last_images)
    print("Done in %.2f s." % (time.time() - start))
    print("All correct imgs " + str(correct_images))
    print("All imgs " + str(len(inputs)))
    print("Total top " + str(n) + " error rate: " + str(float(correct_images)/float(len(inputs))))
    start_time = time.time()
    


if __name__ == '__main__':
    main(sys.argv)
