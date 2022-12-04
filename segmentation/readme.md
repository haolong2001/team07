Point all notebooks (top few cells) to the right data directories (sub-directory images/labels)

model_queued_training.ipynb

Run this file for training UNet or other segmentation backbones. Model architecture and pretrained backbones can be set along with typical traning hyperparameter (e.g. learning rate, epoch count). In addition, the script allows for multiple runs to be scheduled, with random data subset-ing available as an option.

get_test_scores_batch.ipynb

Notebook to gather common segmentation metrics for a given class of models (searched via folder name regex). Metrics such as Precision/Recall/F1, IOU, DICE are computed and averaged per image, and then averaged across images. Scores are returned per model instance, and can be averaged for a generalized performance.

