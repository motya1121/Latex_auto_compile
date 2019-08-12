#!/usr/bin/python
# coding: utf-8

import os
import sys
import pathlib
import configparser
import datetime
import subprocess
import time
import img2pdf

CONFIG_FILE = ""
TEX_DIR_PATH = ""
MASTER_TEX_FILE_NAME = ""
FILE_NAME_LIST = ""
FIGURE_DIR = ""


def parse_config(args):
    '''設定ファイルをパースする．なお，値チェックも行う

    Parameters
    ----------
    args : argparse.Namespace
        argparseで得られた結果

    Returns
    -------
    成功の場合: tuple (string)
        TEX_DIR_PATH, MASTER_TEX_FILE_NAME, FILE_NAME_LIST, FIGURE_DIR
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

    # find tex files
    FILE_NAME_LIST = [f.name for f in os.scandir(TEX_DIR_PATH) if f.is_file() and f.name.split(".")[-1] == "tex"]

    # check master tex file
    if config['LATEX']['MASTER_TEX_FILE_NAME'] is None:
        print("['LATEX']['MASTER_TEX_FILE_NAME']が存在しません")
    elif os.path.isfile(TEX_DIR_PATH + config['LATEX']['MASTER_TEX_FILE_NAME']):
        MASTER_TEX_FILE_NAME = config['LATEX']['MASTER_TEX_FILE_NAME']
    else:
        print("[error] 設定ファイルで指定されたファイル(MASTER_TEX_FILE_NAME)が見つかりませんでした．")
        return - 1
    MASTER_TEX_FILE_NAME = MASTER_TEX_FILE_NAME[0:MASTER_TEX_FILE_NAME.find(".")]

    # check figure direstory
    FIGURE_DIR = ""
    if config['LATEX']['FIGURE_DIR'] is None:
        pass
    elif os.path.isdir(TEX_DIR_PATH + config['LATEX']['FIGURE_DIR']):
        FIGURE_DIR = config['LATEX']['FIGURE_DIR']

    return TEX_DIR_PATH, MASTER_TEX_FILE_NAME, FILE_NAME_LIST, FIGURE_DIR


def check_update(mtime_list):
    is_update = False
    for mtimes in mtime_list:
        if mtimes[0].stat().st_mtime != mtimes[1]:
            mtimes[1] = mtimes[0].stat().st_mtime
            is_update = True
            if str(mtimes[0]).split("/")[-1] == FIGURE_DIR:
                update_figure()
    return is_update


def update_figure():
    fig_files = [TEX_DIR_PATH + FIGURE_DIR + "/" + f.name for f in os.scandir(TEX_DIR_PATH + FIGURE_DIR) if f.is_file() and f.name.split(".")[-1] in ["png", "jpg"]]
    for fig in fig_files:
        with open(fig[:fig.rfind(".")] + ".pdf", "wb") as f:
            f.write(img2pdf.convert(fig))


def watch(args):
    TEX_DIR_PATH, MASTER_TEX_FILE_NAME, FILE_NAME_LIST, FIGURE_DIR = parse_config(args)

    if TEX_DIR_PATH == -1:
        print("[error] エラーが発生したため，処理を停止します．")
        sys.exit()

    # 更新時間取得
    mtime_list = []
    for FILE_NAME in FILE_NAME_LIST:
        p_temp = pathlib.Path(TEX_DIR_PATH + FILE_NAME)
        mtime_list.append([p_temp, p_temp.stat().st_mtime])

    p_temp = pathlib.Path(TEX_DIR_PATH + FIGURE_DIR)
    mtime_list.append([p_temp, p_temp.stat().st_mtime])

    # watch
    try:
        while True:
            if check_update(mtime_list):
                # tex to dvi
                print("[update] {0}{1}.tex {2}".format(TEX_DIR_PATH, MASTER_TEX_FILE_NAME, datetime.datetime.now()))
                cmd = "cd {0} && platex -interaction nonstopmode {0}{1}.tex > {0}output.txt".format(TEX_DIR_PATH, MASTER_TEX_FILE_NAME)
                process = (subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]).decode('utf-8')

                # check log
                with open(TEX_DIR_PATH + "output.txt", "r", encoding="utf8", errors='ignore') as logfile:
                    line_list = logfile.readlines()
                    print_flag = 0
                    error_flag = False
                    for line in line_list:
                        if line[0] == "!":
                            print("[error]")
                            print_flag = 1
                            error_flag = True
                        if print_flag != 0:
                            print(line.replace("\n", ""))
                            print_flag += 1
                        if print_flag == 10:
                            print_flag = 0

                if error_flag is False:
                    # make pdf
                    cmd = "cd {0} && dvipdfmx -o {0}{1}.pdf {0}{1}.dvi >> {0}output.txt".format(TEX_DIR_PATH, MASTER_TEX_FILE_NAME)
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                else:
                    # delete aux files
                    os.remove("{0}{1}.aux".format(TEX_DIR_PATH, MASTER_TEX_FILE_NAME))
            time.sleep(3)
    except KeyboardInterrupt:
        print('動作を停止しました．')
