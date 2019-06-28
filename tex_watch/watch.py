#!/usr/bin/python
# coding: utf-8

import io
import os
import sys
import pathlib
import argparse
import configparser
import datetime
import subprocess


def parse_config(args):
    '''設定ファイルをパースする．なお，値チェックも行う

    Parameters
    ----------
    args : argparse.Namespace
        argparseで得られた結果

    Returns
    -------
    成功の場合: tuple (string)
        TEX_DIR_PATH, FILE_NAME
    失敗の場合: tuple (int)
        -1, -1
    '''

    # check config file
    CONFIG_FILE = ""
    if args.config_file is None:
        if os.path.isfile(os.getcwd() + "/watch.conf"):
            CONFIG_FILE = os.getcwd() + "/watch.conf"
    elif args.config_file[0] == "/":
        if os.path.isfile(args.config_file):
            CONFIG_FILE = args.config_file
    else:
        if os.path.isfile(os.getcwd() + "/" + args.config_file):
            CONFIG_FILE = os.getcwd() + "/" + args.config_file
    if CONFIG_FILE == "":
        print("[error] 設定ファイルが見つかりませんでした．")
        return -1

    # parse config
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, 'UTF-8')
    if config['LATEX']['TEX_DIR_PATH'] is None:
        print("['LATEX']['TEX_DIR_PATH']が存在しません")
    elif os.path.isdir(config['LATEX']['TEX_DIR_PATH']):
        TEX_DIR_PATH = config['LATEX']['TEX_DIR_PATH']
        if TEX_DIR_PATH[-1] != "/":
            TEX_DIR_PATH += "/"
    else:
        print("[error] 設定ファイルで指定されたディレクトリ(TEX_DIR_PATH)が見つかりませんでした．")
        return -1

    if config['LATEX']['TEX_TOP_FILE_NAME'] is None:
        print("['LATEX']['TEX_TOP_FILE_NAME']が存在しません")
    elif os.path.isfile(TEX_DIR_PATH + config['LATEX']['TEX_TOP_FILE_NAME']):
        TEX_FILE_NAME = config['LATEX']['TEX_TOP_FILE_NAME']
    else:
        print("[error] 設定ファイルで指定されたファイル(TEX_TOP_FILE_NAME)が見つかりませんでした．")
        return - 1
    FILE_NAME = TEX_FILE_NAME[0:TEX_FILE_NAME.find(".")]

    return TEX_DIR_PATH, FILE_NAME


parser = argparse.ArgumentParser(description='Latexの自動タイプセット')

parser.add_argument('-cf', '--config_file', help="Configファイルの位置")

args = parser.parse_args()

TEX_DIR_PATH, FILE_NAME = parse_config(args)

if TEX_DIR_PATH == -1:
    print("[error] エラーが発生したため，処理を停止します．")
    sys.exit()

# make command
p = pathlib.Path(TEX_DIR_PATH + FILE_NAME + ".tex")
st_atime = p.stat().st_atime
st_mtime = p.stat().st_mtime
st_ctime = p.stat().st_ctime

try:
    while True:
        if p.stat().st_atime != st_atime or p.stat().st_mtime != st_mtime or p.stat().st_ctime != st_ctime:
            # tex to dvi
            print("updated")
            print(datetime.datetime.now())
            cmd = "cd {0} && platex -interaction nonstopmode {0}{1}.tex > {0}output.txt".format(TEX_DIR_PATH, FILE_NAME)
            process = (subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]).decode('utf-8')

            # check log
            with open(TEX_DIR_PATH + "output.txt", "r") as logfile:
                line_list = logfile.readlines()
                print_flag = 0
                error_flag = False
                for line in line_list:
                    if line[0] == "!":
                        print("[error]")
                        print_flag = 1
                        error_flag = True
                    if print_flag != 0:
                        print(line)
                        print_flag += 1
                    if print_flag == 10:
                        print_flag = 0

            if error_flag is False:
                cmd = "cd {0} && dvipdfmx -o {0}{1}.pdf {0}{1}.dvi >> {0}output.txt".format(TEX_DIR_PATH, FILE_NAME)
                process = (subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]).decode('utf-8')
                with open(os.getcwd() + "result.txt", "w") as result_file:
                    result_file.write("sucess")
            else:
                with open(os.getcwd() + "result.txt", "w") as result_file:
                    result_file.write("error")

        st_atime = p.stat().st_atime
        st_mtime = p.stat().st_mtime
        st_ctime = p.stat().st_ctime
except KeyboardInterrupt:
    print('動作を停止しました．')

