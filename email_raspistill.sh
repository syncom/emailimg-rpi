#!/bin/bash
ROOTDIR=`dirname $0`
saved_file=/mnt/ramdisk_still/capture.jpg
raspistill -w 1280 -h 960 -t 10 -e jpg -q 15 -o ${saved_file}
python ${ROOTDIR}/email_image.py ${saved_file}

