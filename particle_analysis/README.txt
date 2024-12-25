実行前にAnaconda Promptで
pip install opencv-python opencv-python-headless numpy matplotlib
を実行

particle size3.pyをspyderもしくはプログラムから開くでPython(白抜きのやつ）をデフォルトで選択すれば1クリックで実行可能

【使い方】
画像ファイルがあるディレクトリを参照し画像を選択
↓
基本的にパラメータはデフォルトのままである程度動くが画像によっては数値を微調整
↓
scale_bar_length_pixelsの数値は何ピクセルが１μmかを意味するので画像によって調整
↓
「解析を開始」ボタンでoutputファイルが画像と同じディレクトリ内に生成されcsvファイルとmatplotにより生成された分布図，認識した粒の画像が出力される．解析をするごとに上書きされるので注意
