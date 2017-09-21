# gazelle-identification
Automated individual gazelle identification

![alt text](https://puxccbo05z-flywheel.netdna-ssl.com/wp-content/uploads/2015/02/thomsons-gazelle-2.jpg)

## Description of the full pipeline for recognition and classification problems
### Extracting Gazelle heads

1. You need annotated training images with bounding boxes around the object you want to extract and ultimately classify.

   - The easist way I have found to do this is with the app called [RectLabel](https://itunes.apple.com/us/app/rectlabel-labeling-images-for-object-detection/id1210181730?mt=12).  I think it is unfourtunately only avaiable for mac.

   - What you ultimately want is a folder containing the raw images and, within that, a second folder call *annotations* with the .xml annotation       files for some subset of the raw images in PASCAL VOC format.
   
2. Once you have the annotated data, we are going retrain a pretrained tensorflow model as described [here](https://github.com/tensorflow/models/blob/master/object_detection/g3doc/running_locally.md).  
   - As described in the link, we ultimately want to get our relevant directories and files in the following form:
     ```
      +data
        -label_map file
        -train TFRecord file
        -eval TFRecord file
      +models
        + model
          -pipeline config file
          +train
          +eval
      ```
      First, we need to create the all the nessesary files.
      
       **label_map**
      
      label_map is a .pbtxt file which describes the object classes.  In this, the simplest case, we only have two classes: gazelle head; not gazelle head.  This is the corresponding label_map file:
      ```
      item {
        id: 0
        name: 'none_of_the_above'
      }

      item {
        id: 1
        name: 'gazelle_head'
      }
      ```
      
      **train/test TFRECORD file**
      
      I modified [this](https://github.com/tensorflow/models/blob/master/object_detection/create_pascal_tf_record.py) program
      to work with the way my data is annotated.  The result is [create_gazelle_tf_record.py](https://github.com/benkoger/gazelle-identification/blob/master/create_gazelle_tf_record.py) 
      
      It can be run as follows:
      
      ```
      ./create_gazelle_tf_record --data_dir='path to images' \
        --output_dir='path to output' --label_map_path='path to label_map'
      ```
      **n.b.**  The program assumes that the folder of all the raw images that *data_dir* leads to contains both a folder called *annotations* which contains all the .xml annotaions (as described above) and a file called *trainval.txt* which we create below. 
      
      - **trainval.txt**
      
        trainval.txt can be created with [create_train_val.py](https://github.com/benkoger/gazelle-identification/blob/master/create_train_val.py).  This file is just a list of the names of all the images that you want to use for training with the file extension removed.  Therefore it's easist to run the following:
        ```
        ./create_train_val --data_dir='path to annotaions' 
        ```
        
      
      


