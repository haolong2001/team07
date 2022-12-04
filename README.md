# team07
Generative augmentation methods for more robust wound segmentation models

Demo notebooks/scripts are provided, implementing two generative networks (pix2pix and Augmented CycleGAN). These networks are used to generate synthetic wound images, with tune-able latent spaces for controlling wound attributes.

Generated data should replace/be combined with the original dataset, and placed in the project root directory (see sample images).

A segmentation network is then trained and evaluated to compare the performance with and without augmenting the original training dataset.
