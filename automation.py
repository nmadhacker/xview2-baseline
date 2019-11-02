#!/usr/bin/python

import os
import sys
import getopt
import subprocess
import shutil

currentPath = os.getcwd()
xViewRoot = currentPath
xViewParent=xViewRoot+"/.."
xViewUtils = currentPath + "/utils"

trainPath = xViewParent+"/train"
xDBPath = xViewParent+"/xDB"

spacenetSrcModelsPath = xViewRoot+"/spacenet/src/models"
xSpaceNetDBPath = xDBPath+"/spacenet_gt"

#sample inference image paths
inference_path=xViewParent+"/inference"
inference_pre_dissaster_path=inference_path+"/pre_dissaster.png"
inference_post_dissaster_path=inference_path+"/post_dissaster.png"
inference_result_path=inference_path+"/inference_result.png"

inference_localization_path=xViewParent"/localization.h5"
inference_classification_path=xViewParent+"/classification.hdf5"

#train values
cropSize="128"
epoch="2"

argv = sys.argv[1:]

opts, args = getopt.getopt(argv,"o:",["option="])

for opt, arg in opts:
    if opt in ("-o","--option"):
        if (arg == "1"):
            print ("running: split train data into disasters: ")
            cmd="python " +xViewUtils+"/split_into_disasters.py"
            cmd+=" --input " + trainPath
            cmd+=" --output " + xDBPath
            subprocess.call(cmd, shell=True)
        elif (arg == "2"):
            print ("running: mask polygons. make sure xDB path is not empty")
            cmd="python "+xViewUtils+"/mask_polygons.py"
            cmd+=" --input "+xDBPath
            cmd+=" --single-file"
            cmd+=" --border 2"
            subprocess.call(cmd, shell=True)
        elif (arg == "3"):
            print ("running: data finalize. make sure you ran option 2 first")
            os.system("rm -rf "+xDBPath+"/spacenet_gt")
            os.system(xViewUtils+"/data_finalize.sh -i "+xDBPath+" -x "+xViewRoot+" -s .75")
        elif (arg=="4"):
            print ("running: model training. using crop: " +cropSize+ " and epoch: " +epoch)
            sys.path.append(spacenetSrcModelsPath) #set running path
            cmd="python "+spacenetSrcModelsPath+"/train_model.py"
            cmd+=" "+xSpaceNetDBPath+"/dataSet"
            cmd+=" "+xSpaceNetDBPath+"/images"
            cmd+=" "+xSpaceNetDBPath+"/labels"
            cmd+=" -g -1"
            cmd+=" --tcrop " +cropSize
            cmd+=" -e " +epoch
            subprocess.call(cmd,shell=True)
        elif (arg=="5"):
            print ("processing training data:")
            #remove all contents from polygons path
            subprocess.call("rm -rf "+xDBPath+"/../polygons",shell=True)
            subprocess.call("rm -rf "+xDBPath+"/../polygons_csv",shell=True)
            subprocess.call("mkdir "+xDBPath+"/../polygons",shell=True)
            subprocess.call("mkdir "+xDBPath+"/../polygons_csv",shell=True)
            cmd="python " +xViewRoot+"/model/process_data.py"
            cmd+=" --input_dir " +xDBPath
            cmd+=" --output_dir "+xDBPath+"/../polygons"
            cmd+=" --output_dir_csv "+xDBPath+"/../polygons_csv"
            cmd+=" --val_split_pct 0.75"
            subprocess.call(cmd,shell=True)
        elif (arg == "6"):
            print ("running: damage classification")
            cmd="python "+xViewRoot+"/model/damage_classification.py"
            cmd+=" --train_data "+xDBPath+"/../polygons"
            cmd+=" --train_csv "+xDBPath+"/../polygons_csv/train.csv"
            cmd+=" --test_data "+xDBPath+"/../polygons"
            cmd+=" --test_csv "+xDBPath+"/../polygons_csv/test.csv"
            cmd+=" --model_out "+xDBPath+"/../baseline_trial"
            subprocess.call(cmd,shell=True)
        elif (arg == "7"):
            print ("running: inference test")
            print ("pre_dissaster_path: "+inference_pre_dissaster_path)
            print ("post_dissaster_path: "+inference_post_dissaster_path)
            cmd="./utils/inference.sh"
            cmd+=" -x "+xViewRoot
            cmd+=" -i "+inference_pre_dissaster_path
            cmd+=" -p "+inference_post_dissaster_path
            cmd+=" -l "+inference_localization_path
            cmd+=" -c "+inference_classification_path
            cmd+=" -o "+inference_result_path            
            cmd+=" -y"
            #subprocess.call(cmd,shell=True)            
            os.system(cmd)
        else:
            print ("unknown option. Try from 1 to 7")
