#!/usr/local/var/pyenv/shims/python3.6
# coding: utf-8

import os
import argparse
from watch import watch

parser = argparse.ArgumentParser(description='Texファイルのオートコンパイル')
parser.add_argument('-cf', '--config_file', help="Configファイルの位置", default=os.getcwd() + "/" + "latex_auto_compile.conf")

args = parser.parse_args()
print(args.config_file)
print(os.getcwd())
watch = watch.WATCH(args.config_file)
print(watch.settings)
watch.watch()
