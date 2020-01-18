#!/usr/local/var/pyenv/shims/python3.6
# coding: utf-8

import os
import argparse
from watch import watch

parser = argparse.ArgumentParser(description='Texファイルのオートコンパイル')
parser.add_argument('-cf', '--config_file', help="Configファイルの位置", default=os.getcwd() + "/" + "latex_auto_compile.conf")
parser.add_argument('-w', '--print_warning', help="Warningを表示する", action='store_true')
parser.add_argument('-t', '--typeset_once', help="1回だけタイプセットする", action='store_true')
parser.add_argument('-p', '--update_picture', help="画像の更新だけする", action='store_true')
parser.add_argument('-tp', '--typeset_picture', help="1回だけタイプセットする(画像の更新も行う)", action='store_true')

args = parser.parse_args()
watch = watch.WATCH(args)
print(watch.settings)
if args.typeset_once is True or args.update_picture is True or args.typeset_picture is True:
    if args.update_picture is True or args.typeset_picture is True:
        watch.update_pdf()
    if args.update_picture is True or args.typeset_once is True:
        watch.typeset_once()
else:
    watch.watch()
