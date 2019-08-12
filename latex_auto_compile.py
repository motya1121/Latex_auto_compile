#!/usr/bin/python
# coding: utf-8

import os
import argparse
from watch import watch
from search_updated_tex import search_updated_tex


parser = argparse.ArgumentParser(description='Texファイルのオートコンパイル')
parser.add_argument('-t', '--type', metavar='{update, watch}', type=str, help='update: 設定ファイルのアップデート, watch: Texファイルの自動コンパイル', required=True)
parser.add_argument('-cf', '--config_file', help="Configファイルの位置", default=os.getcwd() + "/" + "latex_auto_compile.conf")
parser.add_argument('-s', '--search_path', help="検索するディレクトリ", default=os.getcwd())

args = parser.parse_args()
if args.type == "update":
    search_updated_tex.update(args)
elif args.type == "watch":
    watch.watch(args)