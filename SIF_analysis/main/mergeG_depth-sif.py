import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_min_k_comparison(csv_folder, output_svg, plate_thickness):
    """
    複数のmin_K-@@@.csvを集めて比較グラフを作成するプログラム。

    Parameters:
        csv_folder (str): min_K-@@@.csvファイルが格納されているフォルダのパス。
        output_svg (str): 出力するグラフのファイル名（SVG形式）。
        plate_thickness (float): 板厚。
    """
    # フォルダ内の min_K-*.csv ファイルを取得
    csv_files = [f for f in os.listdir(csv_folder) if f.startswith("min_K-") and f.endswith(".csv")]
    
    if not csv_files:
        print("フォルダ内に min_K-*.csv ファイルが見つかりませんでした。")
        return
    
    # グラフの準備
    plt.figure(figsize=(8, 6))
    colors = plt.cm.tab10.colors  # カラーマップ（最大10色）

    for i, csv_file in enumerate(csv_files):
        # ファイルパスと凡例名を取得
        file_path = os.path.join(csv_folder, csv_file)
        legend_name = csv_file.split("min_K-")[1].split(".csv")[0]  # "TypeA" などを取得

        # CSVファイルを読み込み
        data = pd.read_csv(file_path, header=None)
        data = data.iloc[:-1]  # 最後の行を無視

        # 横軸と縦軸のデータを準備
        x = plate_thickness - data.iloc[:, 3]
        y = data.iloc[:, 5]

        # グラフをプロット
        plt.plot(x, y, label=legend_name, color=colors[i % len(colors)], marker='o')
    
    # グラフの詳細設定
    plt.xlabel("Crack Depth [mm]", fontsize=12)
    plt.ylabel("SIF [MPa*m^1/2]", fontsize=12)
    plt.grid(True)
    plt.legend(title="Legend", fontsize=10)
    plt.tight_layout()
    
    # グラフを保存
    plt.savefig(output_svg, format="svg")
    print(f"グラフが生成されました: {output_svg}")

# 使用例
if __name__ == "__main__":
    # ユーザーが指定する情報
    csv_folder = r"C:\Users\masahiro\Desktop\minK"  # CSVファイルのフォルダ
    output_svg = r"C:\Users\masahiro\Desktop\minK\min_k_comparison.svg"  # 出力ファイル名
    plate_thickness = 16  # 板厚

    # グラフを作成
    plot_min_k_comparison(csv_folder, output_svg, plate_thickness)

