#!/home/ubuntu/.pyenv/shims/python
# coding: utf-8

import os
import argparse
from watch import watch

parser = argparse.ArgumentParser(description='Texファイルのオートコンパイル')
parser.add_argument('-d', '--tex_path', help="texファイルのディレクトリ", default=os.getcwd())
parser.add_argument('-cf', '--config_file', help="Configファイルの位置", default=os.getcwd() + "/" + "latex_auto_compile.conf")
'''
parser.add_argument('-t', '--type', metavar='{update, watch}', type=str, help='update: 設定ファイルのアップデート, watch: Texファイルの自動コンパイル', required=True)
parser.add_argument('-cf', '--config_file', help="Configファイルの位置", default=os.getcwd() + "/" + "latex_auto_compile.conf")
parser.add_argument('-s', '--search_path', help="検索するディレクトリ", default=os.getcwd())
'''

args = parser.parse_args()
watch = watch.WATCH("bachelor_thesis.conf")
print(watch.settings)
watch.watch()