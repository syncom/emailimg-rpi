#!/bin/bash
ROOTDIR=`dirname $0`
DATE=$(date +"%Y-%m-%d_%H%M")
saved_file=/mnt/ramdisk_still/${DATE}.jpg
raspistill -w 1280 -h 960 -t 10 -e jpg -q 15 -o ${saved_file}
python ${ROOTDIR}/email_image.py ${saved_file}
rm -rf ${saved_file}
