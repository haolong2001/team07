FILE=$1
URL=http://efrosgans.eecs.berkeley.edu/pix2pix/datasets/edges2shoes.tar.gz
TAR_FILE=./$FILE.tar.gz
TARGET_DIR=./$FILE/
curl -N $URL -O $TAR_FILE
mkdir $TARGET_DIR
tar -zxvf $TAR_FILE -C ./
# rm $TAR_FILE
$SHELL
