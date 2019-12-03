#!/usr/bin/python
# coding: utf-8

import os
import sys
import configparser
import datetime
import subprocess
import time
import glob
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import img2pdf


class WATCH():

    def __init__(self, args: str):
        self.settings = SETTINGS(args)

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

    def __init__(self, args: str):
        self.config_file_path = ""
        self.tex_dir_path = ""
        self.master_tex_file_path = ""
        self.figure_dir_path = ""
        self.listing_dir_path = ""
        self.print_warning = args.print_warning
        self.error_str = []
        self.warning_str = []
        self.SetConfigFilePath(args.config_file)
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
            print("[error] 設定ファイルが見つかりませんでした．")
            print("設定ファイルの指定方法は-hで確認してください．")
            sys.exit(1)

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
        return_strs = "##### SETTING value #####\n"
        return_strs += "\tconf file path:{}\n".format(self.config_file_path)
        return_strs += "\tTexDir:{}\n".format(self.tex_dir_path)
        return_strs += "\tMasterTex:{}\n".format(self.master_tex_file_path)
        return_strs += "\tFigDir:{}\n".format(self.figure_dir_path)
        return_strs += "\tLisDir:{}\n".format(self.listing_dir_path)
        return_strs += "\n"
        return_strs += "\terror:{}\n".format(",".join(self.error_str))
        return_strs += "\twarning:{}\n".format(",".join(self.warning_str))

        return return_strs


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
            line_count = 1
            error_line_count = 0
            error_count = -1
            error_messages = []
            warning_line_count = 0
            warning_count = -1
            warning_messages = []
            error_flag = False
            for line in line_list:
                # check error and warning
                if line[0] == "!":
                    # print("[error] output.txt l.{}".format(line_count))
                    error_line_count = 1
                    error_count += 1
                    error_messages.append("[error] output.txt l.{}\n".format(line_count))
                    error_flag = True
                if line.startswith("LaTeX Warning"):
                    # print("[warning] output.txt l.{}".format(line_count))
                    warning_line_count = 1
                    warning_count += 1
                    warning_messages.append("[warning] output.txt l.{}\n".format(line_count))

                # get error and warning message
                if error_line_count != 0:
                    error_messages[-1] += "\t" + line
                    error_line_count += 1
                if warning_line_count != 0:
                    warning_messages[-1] += "\t" + line
                    warning_line_count += 1

                if error_line_count == 10:
                    error_line_count = 0
                if warning_line_count == 2:
                    warning_line_count = 0
                line_count += 1
            if error_count != 0:
                print(error_messages)
                print("--------------------\n".join(error_messages))
            if warning_count != 0 and self.settings.print_warning is True:
                print("".join(warning_messages))

        if error_flag is False:
            # make pdf
            cmd = "cd {0} && dvipdfmx -o {1}.pdf {1}.dvi >> {0}output.txt".format(
                self.settings.tex_dir_path, self.settings.master_tex_file_path[:-4])
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        else:
            # delete aux files
            for rm_file in glob.glob(self.settings.tex_dir_path + '*.aux'):
                if os.path.isfile(rm_file):
                    os.remove(rm_file)

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
