#!python3.6
# coding: utf-8

import io
import os
import subprocess
import sys
import pathlib
import shutil
import re
from datetime import datetime as dt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DEBUG = False


def search_tex_file(search_path):
    '''
    ディレクトリ内のTexファイルを検索する

    Parameters
    ----------
    search_path :
        type: str
        内容: Texファイルを検索するディレクトリ(絶対パス)

    Returns
    -------
    tex_file_list:
        type: list(dict)
        内容: Texファイルが入っているディレクトリまでのパス,ファイル名，更新時間のリスト
    '''
    # initialize
    tex_file_list = []

    if DEBUG:
        print("*INFO: in dir:{0}".format(search_path))

    proc = subprocess.run(["ls", "-1"],
                          cwd=search_path,
                          stdout=subprocess.PIPE)
    ls_results = proc.stdout.decode("utf8").splitlines()

    for ls_result in ls_results:
        file_path = search_path + "/" + ls_result
        if os.path.isdir(file_path):
            tex_file_list.extend(search_tex_file(file_path))
        elif ls_result.split(".")[-1] not in ["tex"]:
            pass
        elif ls_result == "settings.tex":
            pass
        else:
            tex_file_list.append({
                "path":
                search_path,
                "file_name":
                ls_result,
                "st_mtime":
                pathlib.Path(file_path).stat().st_mtime
            })
    if DEBUG:
        print("*INFO: out dir: {0}".format(search_path))

    return tex_file_list


# MAIN

args = sys.argv
if len(args) == 3 and os.path.exists(args[1]) and os.path.isfile(args[2]):
    SEARCH_ROOT_PATH = args[1]
    TEX_WATCH_PATH = args[2]
else:
    print("引数がない，もしくは指定されたPATHが存在しないため，デフォルトの値を使用します．\n")
    # Mac
    # SEARCH_ROOT_PATH = "/Users/motya/Dropbox/Workspace/aws2/Tex/search_updated_tex"
    SEARCH_ROOT_PATH = "/Users/motya/Dropbox/TMCIT/advanced_courses"
    TEX_WATCH_PATH = "/Users/motya/Dropbox/Workspace/aws2/Tex/watch/watch.conf"

    # Win
    # SEARCH_ROOT_PATH = "/mnt/c/Dropbox/Workspace/aws2/Tex/search_updated_tex"
    # SEARCH_ROOT_PATH = "/mnt/c/Dropbox/TMCIT/advanced_courses"
    # TEX_WATCH_PATH = "/mnt/c/Dropbox/Workspace/aws2/Tex/watch/watch.conf"

    # AWS(Ubuntu)
    # SEARCH_ROOT_PATH = "/home/ubuntu/Dropbox/TMCIT/advanced_courses"
    # TEX_WATCH_PATH = "/home/ubuntu/Tex/tex_watch/watch.conf"

# Search

print("「{0}」内のディレクトリを検索します．".format(SEARCH_ROOT_PATH), flush=True)

tex_file_list = search_tex_file(SEARCH_ROOT_PATH)

tex_file_list_sorted = sorted(tex_file_list,
                              key=lambda x: x['st_mtime'],
                              reverse=True)

# Plint
print("\n最近更新された最大10件のデータを表示します．")
i = 0
for tex_file_dict in tex_file_list_sorted:
    print("[{0}]".format(i))
    print("path:{0}/{1}, 更新日時:{2}".format(
        tex_file_dict["path"], tex_file_dict["file_name"],
        dt.fromtimestamp(
            tex_file_dict["st_mtime"]).strftime('%Y/%m/%d-%H:%M:%S')))
    if i >= 10:
        break
    else:
        i += 1

# Select
print("\nTex_watchに登録したいファイルの番号を入植してください．")
print("存在しない or 登録しない場合はｎを入力してください．")
while True:
    tex_number = input('>> ')

    if tex_number in ["n", "N"]:
        print("\nOK!")
        print("何も登録せず終了します．")
        sys.exit()
    elif 0 <= int(tex_number) and int(tex_number) < i:
        tex_file_dict = tex_file_list_sorted[int(tex_number)]
        print("\nOK!")
        print("[{3}]:path:{0}/{1}, 更新日時:{2}".format(
            tex_file_dict["path"],
            tex_file_dict["file_name"],
            dt.fromtimestamp(tex_file_dict["st_mtime"]).strftime(
                '%Y/%m/%d-%H:%M:%S'),
            int(tex_number)))
        print("をtex_watchに登録します．")
        break
    else:
        print("\nERROR!!")
        print("Tex_watchに登録したいファイルの番号を入植してください．")
        print("存在しない or 登録しない場合はｎを入力してください．")

# regist
if os.path.isfile(TEX_WATCH_PATH + ".bak") is False:
    shutil.copyfile(TEX_WATCH_PATH, TEX_WATCH_PATH + ".bak")
    print("バックアップファイルが存在しなかったため，作成しました．")

with open(TEX_WATCH_PATH, 'r', encoding='utf-8') as conf_file:
    conf_file_lines = conf_file.readlines()

for i in range(0, len(conf_file_lines)):
    pattern = '^TEX_DIR_PATH'
    result = re.match(pattern, conf_file_lines[i])
    if result:
        conf_file_lines[i] = 'TEX_DIR_PATH="' + tex_file_dict["path"] + '/"\n'

    pattern = '^TEX_TOP_FILE_NAME'
    result = re.match(pattern, conf_file_lines[i])
    if result:
        conf_file_lines[i] = 'TEX_TOP_FILE_NAME="' + \
            tex_file_dict["file_name"] + '"\n'

with open(TEX_WATCH_PATH, 'w', encoding='utf-8') as conf_file:
    conf_file.writelines(conf_file_lines)

print("please execute")
print("sudo service tex_auto_typeset restart")
