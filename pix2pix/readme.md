# Pix2Pix Implementation for binary/ multiclass generation of images 

This code has been officially adapted from https://phillipi.github.io/pix2pix/ 

Please note that the direction of the generation occurs depending on the dataset inputs which was preprocessed from the concatenation of the output image (original wound image) and the input image (mask image). 

## Preprocessing the data
Before training the data with the pix2pix model, the data was preprocessed in a few different ways, one including the combined_A_and_B.ipynb which concatenates the images together and the sep_footulcer.ipynb which has the code for conversion of the binary masks into the multiclass colour datasetin the following colours- red, blue and green. As the original images were of size 128 by 128, we resized the images to 256 by 256 to fit our model requirements. 
## training the model
Refer to footulcer.ipynb for information to train the model. 

Train:
python train.py --dataroot ./datasets/footulcer_256 --name footulcer_resized_256 --model pix2pix --gpu_ids 0 --display_id 0 --batch_size 16 --netD n_layers --n_layers_D 4 --direction BtoA 


## testing the model
Refer to the footulcer.ipynb for information to train the model 

We have developed a script that generates more augmentations repeatedly in one testing script adapted from the test script.
To use the above script, run the following:
python test_aug.py --dataroot ./datasets/footulcer_256 --model pix2pix --name footulcer_resized_256 --gpu_ids -1 --num_test 114 --direction BtoA

## Postprocessing methods
For computational reasons, we resized our output images back to the original size of 128 by 128 and fed it through the segmentation model for evaulation against our original model. 
