# Latex_auto_compile

Latexの自動コンパイル

## インストール

解凍するだけ

## 設定ファイル(latex_auto_compile.conf)

- TEX_DIR_PATH: Texファイルが入っているディレクトリのパス
- MASTER_TEX_FILE_NAME: コンパイルするファイル
- FIGURE_DIR: 画像ファイルのディレクトリ

## サンプル

### 設定ファイルのアップデート

'''
python latex_auto_compile.py -t update -cf /path/to/the/config_file.conf -s /path/to/directory/to/search/
'''

### 自動アップデートの開始

'''
python latex_auto_compile.py -t watch -cf /path/to/the/config_file.conf
'''
