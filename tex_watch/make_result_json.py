#!/usr/bin/env python
# coding: utf-8

# python3 make_result_json.py <タイプセットの結果> <PDFのファイルパス> <Apacheのtex_viewのパス>

import io
import os
import sys
import hashlib
import datetime
import json

sys.path.append('/home/ubuntu1604/.local/lib/python3.5/site-packages')
from pdf2image import convert_from_path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
args = sys.argv

pdf_file_path = args[2]
apache_path = args[3]
jpg_dir_path = apache_path + "jpg_images/"
if (not os.path.exists(jpg_dir_path)):
    os.mkdir(jpg_dir_path)

# result
result = args[1]

# PDF_hash
images = convert_from_path(pdf_file_path,
                           output_folder=jpg_dir_path,
                           output_file="report",
                           fmt="jpg",
                           dpi=80)

PDF_page_num = len(images)
JPG_hash_list = []

for i, image in enumerate(images, 1):
    jpg_file_path = "{0}report-{1:02}.jpg".format(jpg_dir_path, i)
    with open(jpg_file_path, 'rb') as f:
        JPG_hash_list.append(hashlib.md5(f.read()).hexdigest())

# update datetime
now = datetime.datetime.now()
update_datetime = now.strftime("%Y:%m:%d_%H:%M:%S")

tex_result = {
    "update_datetime": update_datetime,
    "result": result,
    "PDF_page_num": PDF_page_num,
    "JPG_hash_list": JPG_hash_list
}

with open(args[3] + "tex_result.json", "w") as f:
    json.dump(tex_result, f, indent=4)