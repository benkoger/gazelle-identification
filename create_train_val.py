'''
takes in a directory and creates a train_val.txt file like one
gets in the pets data set and is nessisary for create_~_tf_record.py
in tensorflow/models/object_detection 
'''

import os
import tensorflow as tf
from tensorflow.python.platform import gfile



flags = tf.app.flags
flags.DEFINE_string('data_dir', '', 'directory to raw dataset that you want to use for train tfrecord.')
FLAGS = flags.FLAGS


def main():
    output_file = 'trainval.txt' 
    data_dir = FLAGS.data_dir
    files = [x[2] for x in gfile.Walk(data_dir)]
    with open(output_file, 'w') as f:
        for file_name in files[0]:
            f.write(os.path.splitext(file_name)[0] + ' \n')


if __name__ == "__main__":
    main()