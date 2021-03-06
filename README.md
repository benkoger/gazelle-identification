![alt text](https://github.com/benkoger/gazelle-identification/blob/master/loopy_compatible.png)


## While the example of gazelle face recognition is used, this approach can sucessfully be used for many different applications.


# gazelle-identification
Automated individual gazelle identification

![alt text](https://puxccbo05z-flywheel.netdna-ssl.com/wp-content/uploads/2015/02/thomsons-gazelle-2.jpg)

## Description of the full pipeline for recognition and classification problems

For some tensorflow object detection background, start [here](https://research.googleblog.com/2017/06/supercharge-your-computer-vision-models.html).

### Extracting Gazelle heads

[This](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_pets.md) blog post from tensorflow is an example that learns pet localization.  The following is basically just the nessasary changes so that it runs on the gazelle data set.  Use this for info on getting the general environment set up.

1. You need annotated training images with bounding boxes around the object you want to extract and ultimately classify.

   - If you are using [Loopy](loopbio.com/loopy/), then you can use the [loopy_to_PASCALVOC.ipynb](https://github.com/benkoger/gazelle-identification/blob/master/loopy_to_PASCALVOC.ipynb) notebook to convert the loopy annotation files to the .xml files that the TensorFlow object detection api uses as default. 

   - The easist way I have found outside of Loopy to do this is with the app called [RectLabel](https://itunes.apple.com/us/app/rectlabel-labeling-images-for-object-detection/id1210181730?mt=12).  I think it is only avaiable for mac.

   - What you ultimately want is a folder containing the raw images and, within that, a second folder call *annotations* with the .xml annotation       files for some subset of the raw images in PASCAL VOC format.
   
2. Once you have the annotated data, you must prepare to retrain a pretrained tensorflow model as described [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md).  
   - As described in the link, you ultimately want to get your relevant directories and files in the following form:
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
      First, you need to create all the nessesary files:
      
       **label_map**
      
      label_map is a .pbtxt file which describes the object classes.  In this, the simplest case, you only have two classes: gazelle head; not gazelle head.  This is the corresponding label_map file:
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
      
      I modified [this](https://github.com/tensorflow/models/blob/master/research/object_detection/create_pascal_tf_record.py) program
      to work with the way my data is annotated.  The result is [create_gazelle_tf_record.py](https://github.com/benkoger/gazelle-identification/blob/master/create_gazelle_tf_record.py) 
      
      It can be run as follows:
      
      ```
      ./create_gazelle_tf_record --data_dir='path to images' \
        --output_dir='path to output' --label_map_path='path to label_map'
      ```
      **n.b.**  The program assumes that the folder of all the raw images that *data_dir* leads to contains both a folder called *annotations* which contains all the .xml annotaions (as described above) and a file called *trainval.txt* which you create below. 
      
      - **trainval.txt**
      
        trainval.txt can be created with [create_train_val.py](https://github.com/benkoger/gazelle-identification/blob/master/create_train_val.py).  The resulting file is just a list of the names of all the images that you want to   
        use for training with the file extension removed.  Therefore it's easist to run the following:
        ```
        ./create_train_val --data_dir='path to annotaions' 
        ```
     **pipeline config**
     
     This is directly from the general tensorflow pet example post mentioned at the top of this section:
     
      In the Tensorflow Object Detection API, the model parameters, training
      parameters and eval parameters are all defined by a config file. More details
      can be found [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/configuring_jobs.md). For this tutorial, you will use some
      predefined templates provided with the source code. The skeleton graph config files can be found in the models/research/object_detection/samples/configs folder.  The tensorflow model zoo from which you can get the files assosiated with the pretrained graphs can be found [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md). I use `faster_rcnn_resnet101_pets.config` as a
      starting point for configuring the pipeline. Open the file with a
      text editor.

      You need to configure some paths in order for the template to work. Search the
      file for instances of `PATH_TO_BE_CONFIGURED` and replace them with the
      appropriate value (typically `gs://${YOUR_GCS_BUCKET}/data/`). Afterwards
      upload your edited file onto GCS, making note of the path it was uploaded to
      (you'll need it when starting the training/eval jobs).

      ``` 
      bash
      # From tensorflow/models/

      # Edit the faster_rcnn_resnet101_pets.config template. Please note that there
      # are multiple places where PATH_TO_BE_CONFIGURED needs to be set.
      sed -i "s|PATH_TO_BE_CONFIGURED|"gs://${YOUR_GCS_BUCKET}"/data|g" \
          object_detection/samples/configs/faster_rcnn_resnet101_pets.config

      # Copy edited template to cloud.
      gsutil cp object_detection/samples/configs/faster_rcnn_resnet101_pets.config \
          gs://${YOUR_GCS_BUCKET}/data/faster_rcnn_resnet101_pets.config
         
      ```
      
      You can also choose to add some data augmentation to the training set.  Possible augmentation techniques are described [here](https://github.com/tensorflow/models/blob/master/research/object_detection/protos/preprocessor.proto).  
      
      Like this:
      ```
       data_augmentation_options {
          random_horizontal_flip {
          }
          random_vertical_flip {
          }
       }
      ```
      
3. Once all of the files are all set as described above, you are ready to train the network.  The details for training the network are directly copied from [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md).

- **Running the Training Job**

   A local training job can be run with the following command:

   ```bash
   # From the tensorflow/models/research/ directory
   CUDA_VISIBLE_DEVICES=0 python object_detection/train.py \
       --logtostderr \
       --pipeline_config_path=${PATH_TO_YOUR_PIPELINE_CONFIG} \
       --train_dir=${PATH_TO_TRAIN_DIR}
   ```

   where `${PATH_TO_YOUR_PIPELINE_CONFIG}` points to the pipeline config and
   `${PATH_TO_TRAIN_DIR}` points to the directory in which training checkpoints
   and events will be written to. By default, the training job will
   run indefinitely until the user kills it.

- **Running the Evaluation Job**

   Evaluation is run as a separate job. The eval job will periodically poll the
   train directory for new checkpoints and evaluate them on a test dataset. The
   job can be run using the following command (this assumes you have two GPUs otherwise see [here](https://github.com/tensorflow/models/issues/1854) for more info):

   ```bash
   # From the tensorflow/models/research/ directory
   CUDA_VISIBLE_DEVICES=1 python object_detection/eval.py \
       --logtostderr \
       --pipeline_config_path=${PATH_TO_YOUR_PIPELINE_CONFIG} \
       --checkpoint_dir=${PATH_TO_TRAIN_DIR} \
       --eval_dir=${PATH_TO_EVAL_DIR}
   ```

   where `${PATH_TO_YOUR_PIPELINE_CONFIG}` points to the pipeline config,
   `${PATH_TO_TRAIN_DIR}` points to the directory in which training checkpoints
   were saved (same as the training job) and `${PATH_TO_EVAL_DIR}` points to the
   directory in which evaluation events will be saved. As with the training job,
   the eval job run until terminated by default.

- **Running Tensorboard**

   Progress for training and eval jobs can be inspected using Tensorboard. If
   using the recommended directory structure, Tensorboard can be run using the
   following command:

   ```bash
   tensorboard --logdir=${PATH_TO_MODEL_DIRECTORY}
   ```

   where `${PATH_TO_MODEL_DIRECTORY}` points to the directory that contains the
   train and eval directories. Please note it may take Tensorboard a couple minutes
   to populate with data.
     
4. Now that the model is trained, you need to export the model so that it can be used other places.  This is discussed in    
detail [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/exporting_models.md).

   Run the following:
   ```
   # From tensorflow/models/research/
   python object_detection/export_inference_graph.py \
       --input_type image_tensor \
       --pipeline_config_path ${PIPELINE_CONFIG_PATH} \
       --trained_checkpoint_prefix ${PATH}model.ckpt-${CHECKPOINT_NUMBER} \
       --output_directory output_inference_graph.pb
   ```
   
5. Now you can use your saved model to extract the gazelle face images from the raw images.  This is done with [extract_gazelle_heads.py](https://github.com/benkoger/gazelle-identification/blob/master/extract_gazelle_heads.py).
   
   You just need to change PATH_TO_CKPT, PATH_TO_LABELS, NUM_CLASSES, and PATH_TO_IMAGES_DIR to apropriate values for your    computer.
   
   If all went well you will have a folder full of gazelle faces like this:
   ![alt text](/extracted_gazelle_heads.png)
  
     
     
### Individual Recognition

1. [Simply follow this tutorial for retraining a classification network.](https://www.tensorflow.org/tutorials/image_retraining)

2. Use [use_retrained_inception.ipynb](https://github.com/benkoger/gazelle-identification/blob/master/use_retrained_inception.ipynb) to classify new images.  See [this](https://www.tensorflow.org/tutorials/image_recognition) tutorial for a detailed general description.

![alt text](/individual_gazelles_heads.png)



###Things that I have changed in the object detection API (not a complete list)

Feb 13, 2018:
1. To generate precision recall curves

https://github.com/tensorflow/models/blob/master/research/object_detection/utils/object_detection_evaluation.py

original:

```
(per_class_ap, mean_ap, _, _, per_class_corloc, mean_corloc) = (
        self._evaluation.evaluate())

```
changed:
```
(per_class_ap, mean_ap, precisions_per_class, reacalls_per_class, per_class_corloc, mean_corloc) = (
        self._evaluation.evaluate())
...

pascal_metrics['precisions_per_class'] = precisions_per_class
pascal_metrics['recalls_per_class'] = recalls_per_class

```

object_detection/eval_util.py


added in def repeated_checkpoint_run(tensor_dict,... ln293:
```
np.save(os.path.join(summary_dir, 'precisions_' + str(global_step)), metrics.pop('precisions_per_class', None))
np.save(os.path.join(summary_dir, 'recalls_' + str(global_step)), metrics.pop('recalls_per_class', None))
#Must be above this line
write_metrics(metrics, global_step, summary_dir)
```

        
      
      


