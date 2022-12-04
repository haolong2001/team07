### Augmented Cyclegan

The code has been ported over and adapted from https://github.com/aalmah/augmented_cyclegan.git, which was initially in an outdated pytorch version.

git clone the repository
`cd augmented_cyclegan` 

##Set-up instructions
`pip install -r requirements.txt`

##Data prepartation
we have prepared the required npy used for our training, in order to use it on your custom dataset, follow the instructions below. 

1) `./datasets/download_pix2pix_dataset.sh edges2shoes download data from source`
2) `/datasets/python split_A_and_B.py --split train and python split_A_and_B.py --split train split paired images to separate ones`
3) `python create_edges2shoes_np.py create 64x64 numpy data`


##Training augmented_CycleGAN model 

`python edges2shoes_exp/train.py --dataroot /datasets/edges2shoes/ --name augcgan_model`

