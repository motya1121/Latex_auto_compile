# Latex_auto_compile

Latexの自動コンパイル

## インストール

解凍するだけで実行可能．

コマンドとして認識させたい場合はパスが通っている場所に配置する．
もしくは，このディレクトリにパスを通す．

## 設定ファイル(latex_auto_compile.conf)

- TEX_DIR_PATH: Texファイルが入っているディレクトリのパス
- MASTER_TEX_FILE_NAME
  - Texを分割管理する場合: トップのTexファイル
  - Texを分割管理しない場合: 作成したTexファイル
- FIGURE_DIR: 画像ファイルのディレクトリ
- LISTING_DIR: ソースコードのディレクトリ

## オプション

### -cf

設定ファイルを指定する．
コマンドを実行したディレクトリ内に`latex_auto_compile.conf`という設定ファイルが存在する場合は省略可能．

### -w

Warning情報を表示する．
デフォルトは非表示．

## サンプル

### 自動タイプセット

Texファイルを監視し，自動的にタイプセットする．

```
python latex_auto_compile -cf latex_auto_compile.conf
```

