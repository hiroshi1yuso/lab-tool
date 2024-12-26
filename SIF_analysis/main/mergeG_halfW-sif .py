import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_max_k_multiple(csv_folder, output_svg):
    """
    複数のmax_K-@@@.csvを比較してグラフを作成するプログラム。

    Parameters:
        csv_folder (str): max_K-@@@.csv ファイルが格納されているフォルダのパス。
        output_svg (str): 出力するグラフのファイル名（SVG形式）。
    """
    # フォルダ内の max_K-*.csv ファイルを取得
    csv_files = [f for f in os.listdir(csv_folder) if f.startswith("max_K-") and f.endswith(".csv")]
    
    if not csv_files:
        print("フォルダ内に max_K-*.csv ファイルが見つかりませんでした。")
        return

    # グラフの準備
    plt.figure(figsize=(8, 6))
    colors = plt.cm.tab10.colors  # カラーマップ（最大10色）

    for i, csv_file in enumerate(csv_files):
        # ファイルパスと凡例名を取得
        file_path = os.path.join(csv_folder, csv_file)
        legend_name = csv_file.split("max_K-")[1].split(".csv")[0]  # "TypeA" などを取得

        # CSVファイルを読み込み
        data = pd.read_csv(file_path, header=None)

        # 最後の2行を無視
        data = data.iloc[:-2]

        # ペアごとに計算
        x = []  # 横軸データ
        y = []  # 縦軸データ

        for j in range(0, len(data), 2):  # 2行ごとに処理
            if j + 1 >= len(data):  # ペアが揃わない場合はスキップ
                break

            # 1行目と2行目を取得
            row1 = data.iloc[j]
            row2 = data.iloc[j + 1]

            # 3列目が大きい方から小さい方を引いた値の1/2を計算
            diff_half = abs(row1[2] - row2[2]) / 2
            x.append(diff_half)  # 横軸に追加

            # 3列目の値が小さい方の6列目を取得
            if row1[2] < row2[2]:
                y.append(row1[5])
            else:
                y.append(row2[5])

        # グラフをプロット
        plt.plot(x, y, marker='o', linestyle='-', color=colors[i % len(colors)], label=legend_name)
    
    # グラフの詳細設定
    plt.xlabel("Crack half-width [mm]", fontsize=12)
    plt.ylabel("SIF [MPa*m^1/2]", fontsize=12)
    plt.grid(True)
    plt.legend(title=" ", fontsize=10)
    plt.tight_layout()

    # グラフを保存
    try:
        plt.savefig(output_svg, format="svg")
        plt.close()
        print(f"グラフが正常に保存されました: {output_svg}")
    except Exception as e:
        print(f"グラフの保存中にエラーが発生しました: {e}")

# 使用例
if __name__ == "__main__":
    # ユーザーが指定する情報
    csv_folder = r"C:\Users\masahiro\Desktop\maxK"  # CSVファイルのフォルダ
    output_svg = r"C:\Users\masahiro\Desktop\maxK\max_k_comparison.svg"  # 出力ファイル名

    # グラフを作成
    plot_max_k_multiple(csv_folder, output_svg)



