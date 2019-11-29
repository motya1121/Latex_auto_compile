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


class SETTING():

    def __init__(self, config_file_path: str):
        self.config_file_path = ""
        self.tex_dir_path = ""
        self.master_tex_file_path = ""
        self.figure_dir_path = ""
        self.listing_dir_path = ""
        self.error_str = []
        self.warning_str = []
        self.SetConfigFilePath(config_file_path)
        if len(self.error_str) == 0:
            self.SetConfigValue()

    def SetConfigFilePath(self, config_file_path: str):
        error_flag = False
        if config_file_path is None:
            error_flag = True
        elif config_file_path[0] == "/":
            if os.path.isfile(config_file_path):
                self.config_file_path = config_file_path
            else:
                error_flag = True
        else:
            if os.path.isfile(os.getcwd() + "/" + config_file_path):
                self.config_file_path = os.getcwd() + "/" + config_file_path
            else:
                error_flag = True
        if error_flag is True:
            self.error_str.append("[error] 設定ファイルが見つかりませんでした．")

    def SetConfigValue(self):

        config = configparser.ConfigParser()
        config.read(self.config_file_path, 'UTF-8')

        # check tex dir path
        try:
            if config['LATEX']['TEX_DIR_PATH'] is None:
                self.error_str.append("['LATEX']['TEX_DIR_PATH']は必須項目です．")
            elif os.path.isdir(config['LATEX']['TEX_DIR_PATH']):
                self.tex_dir_path = config['LATEX']['TEX_DIR_PATH']
                if self.tex_dir_path[-1] != "/":
                    self.tex_dir_path += "/"
            else:
                self.error_str.append("[error] 設定ファイルで指定されたディレクトリ(TEX_DIR_PATH)が見つかりませんでした．")
        except KeyError:
            self.error_str.append("['LATEX']['TEX_DIR_PATH']が存在しません")

        # check master tex file path
        try:
            if config['LATEX']['MASTER_TEX_FILE_NAME'] is None:
                self.error_str.append("['LATEX']['MASTER_TEX_FILE_NAME']は必須項目です．")
            elif os.path.isfile(self.tex_dir_path + config['LATEX']['MASTER_TEX_FILE_NAME']):
                self.master_tex_file_path = self.tex_dir_path + config['LATEX']['MASTER_TEX_FILE_NAME']
            else:
                self.error_str.append("[error] 設定ファイルで指定されたファイル(MASTER_TEX_FILE_NAME)が見つかりませんでした．")
        except KeyError:
            self.error_str.append("['LATEX']['MASTER_TEX_FILE_NAME']が存在しません")

        # check figure direstory(option)
        try:
            if config['LATEX']['FIGURE_DIR'] is None:
                self.figure_dir_path = ""
            elif os.path.isdir(self.tex_dir_path + config['LATEX']['FIGURE_DIR']):
                self.figure_dir_path = config['LATEX']['FIGURE_DIR']
            else:
                self.warning_str.append("[warning] 設定ファイルで指定されたディレクトリ(FIGURE_DIR)が見つかりませんでした．")
        except KeyError:
            self.figure_dir_path = ""

        # check listing direstory(option)
        try:
            if config['LATEX']['LISTING_DIR'] is None:
                self.listing_dir_path = ""
            elif os.path.isdir(self.tex_dir_path + config['LATEX']['LISTING_DIR']):
                self.listing_dir_path = config['LATEX']['LISTING_DIR']
            else:
                self.warning_str.append("[warning] 設定ファイルで指定されたディレクトリ(FIGURE_DIR)が見つかりませんでした．")
        except KeyError:
            self.listing_dir_path = ""

    def __str__(self):
        return "##### SETTING value #####\n\tconf file path:{}\n\tTexDir:{}\n\tMasterTex:{}\n\tFigDir:{}\n\tLisDir:{}\n\n\terror:{},\n\twarning:{}".format(
            self.config_file_path, self.tex_dir_path, self.master_tex_file_path, self.figure_dir_path,
            self.listing_dir_path, ",".join(self.error_str), ",".join(self.warning_str))


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
    fig_files = [
        TEX_DIR_PATH + FIGURE_DIR + "/" + f.name
        for f in os.scandir(TEX_DIR_PATH + FIGURE_DIR)
        if f.is_file() and f.name.split(".")[-1] in ["png", "jpg"]
    ]
    for fig in fig_files:
        with open(fig[:fig.rfind(".")] + ".pdf", "wb") as f:
            f.write(img2pdf.convert(fig))


# find tex files
        FILE_NAME_LIST = [f.name for f in os.scandir(TEX_DIR_PATH) if f.is_file() and f.name.split(".")[-1] == "tex"]


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
                print(
                    "[update] {0}{1}.tex {2}".format(TEX_DIR_PATH, MASTER_TEX_FILE_NAME, datetime.datetime.now()),
                    flush=True)
                cmd = "cd {0} && platex -interaction nonstopmode {0}{1}.tex > {0}output.txt".format(
                    TEX_DIR_PATH, MASTER_TEX_FILE_NAME)
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
                    cmd = "cd {0} && dvipdfmx -o {0}{1}.pdf {0}{1}.dvi >> {0}output.txt".format(
                        TEX_DIR_PATH, MASTER_TEX_FILE_NAME)
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                else:
                    # delete aux files
                    os.remove("{0}{1}.aux".format(TEX_DIR_PATH, MASTER_TEX_FILE_NAME))
            time.sleep(3)
    except KeyboardInterrupt:
        print('動作を停止しました．')
