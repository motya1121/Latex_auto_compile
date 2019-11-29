#!/usr/bin/python
# coding: utf-8

import os
import configparser
import datetime
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import img2pdf


class WATCH():

    def __init__(self, config_file_path: str):
        self.settings = SETTINGS(config_file_path)

    def watch(self):
        event_handler = TexHandler(self.settings)
        Tex_observer = Observer()
        Tex_observer.schedule(event_handler, self.settings.tex_dir_path, recursive=True)
        Tex_observer.start()

        event_handler = FigHandler(self.settings)
        Fig_observer = Observer()
        Fig_observer.schedule(event_handler, self.settings.figure_dir_path, recursive=True)
        Fig_observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            Tex_observer.stop()
            Fig_observer.stop()
        Tex_observer.join()
        Fig_observer.join()


class SETTINGS():

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
                self.figure_dir_path = self.tex_dir_path + config['LATEX']['FIGURE_DIR']
            else:
                self.warning_str.append("[warning] 設定ファイルで指定されたディレクトリ(FIGURE_DIR)が見つかりませんでした．")
        except KeyError:
            self.figure_dir_path = ""

        # check listing direstory(option)
        try:
            if config['LATEX']['LISTING_DIR'] is None:
                self.listing_dir_path = ""
            elif os.path.isdir(self.tex_dir_path + config['LATEX']['LISTING_DIR']):
                self.listing_dir_path = self.tex_dir_path + config['LATEX']['LISTING_DIR']
            else:
                self.warning_str.append("[warning] 設定ファイルで指定されたディレクトリ(FIGURE_DIR)が見つかりませんでした．")
        except KeyError:
            self.listing_dir_path = ""

    def __str__(self):
        return "##### SETTING value #####\n\tconf file path:{}\n\tTexDir:{}\n\tMasterTex:{}\n\tFigDir:{}\n\tLisDir:{}\n\n\terror:{}\n\twarning:{}".format(
            self.config_file_path, self.tex_dir_path, self.master_tex_file_path, self.figure_dir_path,
            self.listing_dir_path, ",".join(self.error_str), ",".join(self.warning_str))


class TexHandler(PatternMatchingEventHandler):

    def __init__(self, settings: SETTINGS, patterns: list = ["*.tex"]):
        super(TexHandler, self).__init__(patterns=patterns)
        self.settings = settings

    def _run_typeset(self):
        # tex to dvi
        print("[update] {0} {1}".format(self.settings.master_tex_file_path, datetime.datetime.now()), flush=True)
        cmd = "cd {0} && platex -interaction nonstopmode {1} > {0}output.txt".format(
            self.settings.tex_dir_path, self.settings.master_tex_file_path)
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]

        # check log
        with open(self.settings.tex_dir_path + "output.txt", "r", encoding="utf8", errors='ignore') as logfile:
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
            cmd = "cd {0} && dvipdfmx -o {1}.pdf {1}.dvi >> {0}output.txt".format(
                self.settings.tex_dir_path, self.settings.master_tex_file_path[:-4])
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        else:
            # delete aux files
            os.remove("{0}.aux".format(self.settings.master_tex_file_path[:-4]))

    def on_moved(self, event):
        self._run_typeset()

    def on_created(self, event):
        self._run_typeset()

    def on_deleted(self, event):
        self._run_typeset()

    def on_modified(self, event):
        self._run_typeset()


class FigHandler(PatternMatchingEventHandler):

    def __init__(self, settings: SETTINGS, patterns: list = ["*.png", "*.jpg"]):
        super(FigHandler, self).__init__(patterns=patterns)
        self.settings = settings

    def _run_convert(self, pic_file_path):
        try:
            with open(pic_file_path[:pic_file_path.rfind(".")] + ".pdf", "wb") as f:
                f.write(img2pdf.convert(pic_file_path))
        except Exception:
            pass

    def on_moved(self, event):
        self._run_convert(event.src_path)

    def on_created(self, event):
        self._run_convert(event.src_path)

    def on_modified(self, event):
        self._run_convert(event.src_path)
