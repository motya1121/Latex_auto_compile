#!/bin/bash

if [ $# -ne 1 ]; then
    CONFIG_PATH="/home/ubuntu/Tex/tex_watch/watch.conf"
else
    CONFIG_PATH=$1
fi

# Input config file
. ${CONFIG_PATH}
md5sum ${TEX_DIR_PATH}${TEX_TOP_FILE_NAME}  > ${WORKING_DIR_PATH}Tex_tex_file.md5sum
sed -i -e 's/true/false/g' ${WORKING_DIR_PATH}is_typeset_ongoing.conf

while true
do

    . ${APACHE_DIR_PATH}is_active.conf
    if "${IS_ACTIVE}"; then
        # Texファイルが変更されたかどうか
        md5sum --status -c ${WORKING_DIR_PATH}Tex_tex_file.md5sum
        if test "$?" != "0" ; then
            # 変更あり
            md5sum ${TEX_DIR_PATH}${TEX_TOP_FILE_NAME}  > ${WORKING_DIR_PATH}Tex_tex_file.md5sum

            # 実行中かどうか
            . ${WORKING_DIR_PATH}is_typeset_ongoing.conf
            if "${is_typeset_ongoing}"; then
                # 実行中
                echo "Yes ongoing"
                :
            else
                # 実行中ではない --> typeset
                sed -i -e 's/false/true/g' ${WORKING_DIR_PATH}is_typeset_ongoing.conf

                # TODO: diffを管理するシェルスクリプト or python を呼び出し


                # TODO: 画像関連の処理を行うシェルスクリプト or python を呼び出し

                # typeset
                TEX_DVI_FILE_NAME=`echo ${TEX_TOP_FILE_NAME}|sed -e s/tex$/dvi/g`
                TEX_PDF_FILE_NAME=`echo ${TEX_TOP_FILE_NAME}|sed -e s/tex$/pdf/g`

                cd ${TEX_DIR_PATH} && platex ${TEX_DIR_PATH}${TEX_TOP_FILE_NAME} > ${TEX_DIR_PATH}output.txt
                # TODO: 成功 --> divpdfmxを実行し、result.txtをsuccessに変更
                cd ${TEX_DIR_PATH} && dvipdfmx -o ${TEX_DIR_PATH}${TEX_PDF_FILE_NAME} ${TEX_DIR_PATH}${TEX_DVI_FILE_NAME} >> ${TEX_DIR_PATH}output.txt
                echo "success" > result.txt

                # TODO: 失敗 --> result.txtをfailureに変更

                #/usr/bin/python3 ${WORKING_DIR_PATH}make_result_json.py success ${TEX_DIR_PATH}${TEX_PDF_FILE_NAME} ${APACHE_DIR_PATH}

                sed -i -e 's/true/false/g' ${WORKING_DIR_PATH}is_typeset_ongoing.conf
            fi
        else
            # 変更なし
            # TODO: 十分以上更新されてない--> 監視を終了
            :
        fi

    fi
    sleep 2s
done





