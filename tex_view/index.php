<?php
$TOP_PATH = 'http://localhost/';
$SITE_NAME = "TexView";

file_put_contents("is_active.conf", "IS_ACTIVE=true");

?>
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8" />
    <?php
    echo '<title>' . $SITE_NAME . '</title>';
    ?>
    <script src="https://github.com/github/fetch/releases/download/v3.0.0/fetch.umd.js"></script>
    <link rel="stylesheet" type="text/css" href="style.css">

</head>

<body bgcolor="#FAFAFA">
    <div class="header">
        <div class="header_rogo">
            <?php
            echo '<h1><a href=' . $TOP_PATH . ' class="noline">' . $SITE_NAME . '</a></h1>';
            ?>
        </div>
        <div class="header_center">
        </div>
        <div class="header_datetime">
            update time:<br>
            <a id="update_datetime">HH:MM.SS</a>
        </div>
    </div>
    <div class="contents">
        <div class="contents_tex">
            <details open>
                <summary>PDF</summary>
                <div class="viewer" id="viewer">
                    <canvas class="viewer_img" id="c1"></canvas>
                </div>
                <br>
                <button class="summary_button" type=button onclick="update_pdf()">手動更新</button>
            </details>
        </div>
        <div class="contents_result">
            <details>
                <summary>出力結果</summary>
                result<br>
                <button class="summary_button" type=button onclick="update_result()">手動更新</button>
            </details>
        </div>
        <div class="contents_diff">
            <details>
                <summary>差分</summary>
                diff<br>
                <button class="summary_button" type=button onclick="update_diff()">手動更新</button>
            </details>
        </div>
        <div id="result" hidden></div>
        <div id="JPG_hash_list" hidden></div>
        <div id="PDF_page_num" hidden></div>
    </div>
    <div class="bottom">
        <?php
        echo '<a href=' . $TOP_PATH . ' class="noline">' . $SITE_NAME . '</a>';
        ?>
    </div>
    <script>
        /**
         * ファイル監視のためのループ
         */
        unupdate_count = 0;
        unupdate_count_MAX = 600; //10分間
        update_datetime = "";
        JPG_hash_list = [];


        var id = setInterval(function() {
            // アクティブかどうか
            if (!document.hasFocus()) {
                // Deactive
            } else {
                // Active
                //console.log("ウィンドウがアクティブです");
                update();

                // 更新の確認
                if (update_datetime != document.getElementById("update_datetime").innerText) {
                    update_datetime = document.getElementById("update_datetime").innerText;
                    if (document.getElementById("result").innerText == "success" && JPG_hash_list != document.getElementById("JPG_hash_list").innerText) {
                        //PDFを更新
                        update_pdf(document.getElementById("JPG_hash_list").innerText.split(','));
                        JPG_hash_list = document.getElementById("JPG_hash_list").innerText.split(',');
                    } else if (document.getElementById("result").innerText == "failure") {
                        //resultを更新
                        update_result();
                    }

                    //TODO: 差分を表示
                    //update_diff()
                }
            }

            unupdate_count++
            if (unupdate_count > unupdate_count_MAX) {
                clearInterval(id); //idをclearIntervalで指定している
            }
        }, 1000);


        /**
         * 生成されたPDFファイルを更新するための関数
         */
        function update_pdf(after_JPG_hash_list) {
            console.log("update_pdf");
            viewer = document.getElementById("viewer");
            viewer.textContent = null;
            page_num = document.getElementById("PDF_page_num").innerText
            var images = [];
            var update_image_list = []
            /*
                        if (JPG_hash_list.length == 0) {
                            for (i = 0; i < page_num; i++) {
                                var image = new Image();
                                image.src = "jpg_images/report-" + ('0' + (i + 1)).slice(-2) + ".jpg";
                                images.push(image);
                                update_image_list.push(i);
                            }
                        } else {
                            for (i = 0; i < JPG_hash_list.length; i++) {
                                if (JPG_hash_list[i] != after_JPG_hash_list[i]) {
                                    var image = new Image();
                                    image.src = "jpg_images/report-" + ('0' + (i + 1)).slice(-2) + ".jpg";
                                    images.push(image);
                                    update_image_list.push(i);
                                }
                            }
                            for (; i < page_num; i++) {
                                var image = new Image();
                                image.src = "jpg_images/report-" + ('0' + (i + 1)).slice(-2) + ".jpg";
                                images.push(image);
                                update_image_list.push(i);
                            }
                        }
                        */
            for (i = 0; i < page_num; i++) {
                var image = new Image();
                image.src = "jpg_images/report-" + ('0' + (i + 1)).slice(-2) + ".jpg";
                images.push(image);
                update_image_list.push(i);
            }
            console.log("update_page:" +
                update_image_list);

            if (update_image_list.length != 0) {
                var loadedCount = 1
                for (i = 0; i < page_num; i++) {
                    images[i].addEventListener('load', function() {
                        if (loadedCount == images.length) {
                            for (j = 0; j < page_num; j++) {
                                var canvas = document.createElement('canvas');
                                canvas.classList.add("viewer_img");
                                canvas.setAttribute("id", "viewer_img_" + ('0' + (j + 1)).slice(-2));
                                var div = document.createElement("div");
                                div.style.visibility = "hidden";
                                div.setAttribute("id", "viewer_hash_" + ('0' + (j + 1)).slice(-2));
                                div.innerText = JPG_hash_list[j];
                                var ctx = canvas.getContext('2d');
                                canvas.width = images[j].width;
                                canvas.height = images[j].height;
                                ctx.drawImage(images[j], 0, 0);
                                viewer.appendChild(canvas);
                                viewer.appendChild(div);
                            }
                        }
                        loadedCount++;
                    });
                }
            }
        }


        /**
         * タイプセットの結果を更新するための関数
         */
        function update_result() {

        }

        /**
         * Texファイルの差分を更新するための関数
         */
        function update_diff() {

        }

        /**
         * アップデートがあるかどうかを確認する関数
         * アップデートがあった場合、`update_time`,`result`,`JPG_hash_list`の値を変更する。
         *
         * @return json
         */
        function update() {
            tex_result_url = "http://gme.www.motya.site/tex_view/tex_result.json";
            fetch(tex_result_url)
                .then(function(response) {
                    return response.json();
                }).then(function(json) {
                    //取得成功
                    //console.log(json);
                    if (document.getElementById("update_datetime").innerText != json["update_datetime"]) {
                        document.getElementById("update_datetime").innerText = json["update_datetime"];
                        document.getElementById("result").innerText = json["result"];
                        document.getElementById("PDF_page_num").innerText = json["PDF_page_num"];
                        document.getElementById("JPG_hash_list").innerText = json["JPG_hash_list"];
                        console.log("update fetch.js")
                    }
                }).catch(function(ex) {
                    console.log('parsing failed', ex);
                })
        }
    </script>
</body>

</html>