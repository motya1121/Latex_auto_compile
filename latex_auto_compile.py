#!/usr/local/var/pyenv/shims/python3.6
# coding: utf-8

import os
import argparse
from watch import watch

parser = argparse.ArgumentParser(description='Texファイルのオートコンパイル')
parser.add_argument('-cf', '--config_file', help="Configファイルの位置", default=os.getcwd() + "/" + "latex_auto_compile.conf")
parser.add_argument('-w', '--print_warning', help="Warningを表示する", action='store_true')

args = parser.parse_args()
watch = watch.WATCH(args)
print(watch.settings)
watch.watch()
