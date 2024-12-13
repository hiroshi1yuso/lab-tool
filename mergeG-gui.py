import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, filedialog, Listbox, StringVar, colorchooser, messagebox

def select_folder(entry):
    """フォルダ選択ダイアログを表示してパスを設定する"""
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, "end")
        entry.insert(0, folder_path)

def select_color(listbox, legend_colors, index):
    """色選択ダイアログを表示して凡例の色を設定する"""
    color = colorchooser.askcolor()[1]  # 選択した色のHEXコード
    if color:
        legend_name = listbox.get(index)
        legend_colors[legend_name] = color
        listbox.itemconfig(index, {'bg': color})  # リストボックスに色を反映

def load_csv_files(csv_folder, legend_colors, listbox):
    """CSVファイルを読み込んで凡例を表示"""
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv") and (f.startswith("min_K-") or f.startswith("max_K-"))]
    if not csv_files:
        messagebox.showerror("エラー", "CSVファイルが見つかりませんでした。")
        return

    # 凡例名を取得してリストに追加
    legend_names = [f.split("-")[1].split(".csv")[0] for f in csv_files]
    unique_legend_names = sorted(set(legend_names))  # 重複を排除してソート

    listbox.delete(0, "end")  # 既存の項目をクリア
    for legend_name in unique_legend_names:
        listbox.insert("end", legend_name)
        legend_colors[legend_name] = plt.cm.tab10.colors[len(legend_colors) % 10]  # 初期色を割り当て

def process_and_plot(csv_folder, plate_thickness, output_dir, legend_colors):
    """グラフを描画して保存する"""
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]

    if not csv_files:
        print("指定されたフォルダに CSV ファイルが見つかりませんでした。")
        return

    # min_K と max_K に分ける
    min_k_files = [f for f in csv_files if f.startswith("min_K-")]
    max_k_files = [f for f in csv_files if f.startswith("max_K-")]

    # min_K のグラフ描画
    if min_k_files:
        plt.figure(figsize=(8, 6))
        for csv_file in min_k_files:
            file_path = os.path.join(csv_folder, csv_file)
            legend_name = csv_file.split("min_K-")[1].split(".csv")[0]

            # CSV読み込み
            data = pd.read_csv(file_path, header=None).iloc[:-1]
            x = plate_thickness - data.iloc[:, 3]
            y = data.iloc[:, 5]

            plt.plot(x, y, label=legend_name, color=legend_colors.get(legend_name, "black"), marker='o')

        plt.xlabel("Crack Depth [mm]", fontsize=12)
        plt.ylabel("SIF [MPa*m^1/2]", fontsize=12)
        plt.legend(title="Legend", fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "min_k_comparison.svg"), format="svg")
        plt.close()
        print("min_K グラフが保存されました。")

    # max_K のグラフ描画
    if max_k_files:
        plt.figure(figsize=(8, 6))
        for csv_file in max_k_files:
            file_path = os.path.join(csv_folder, csv_file)
            legend_name = csv_file.split("max_K-")[1].split(".csv")[0]

            # CSV読み込み
            data = pd.read_csv(file_path, header=None).iloc[:-2]
            x = []
            y = []
            for j in range(0, len(data), 2):
                if j + 1 >= len(data):
                    break
                row1 = data.iloc[j]
                row2 = data.iloc[j + 1]
                x.append(abs(row1[2] - row2[2]) / 2)
                y.append(row1[5] if row1[2] < row2[2] else row2[5])

            plt.plot(x, y, label=legend_name, color=legend_colors.get(legend_name, "black"), marker='o')

        plt.xlabel("Crack half-width [mm]", fontsize=12)
        plt.ylabel("SIF [MPa*m^1/2]", fontsize=12)
        plt.legend(title="Legend", fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "max_k_comparison.svg"), format="svg")
        plt.close()
        print("max_K グラフが保存されました。")

def main():
    """GUI のメイン関数"""
    # GUI 初期化
    root = Tk()
    root.title("グラフマージ")
    root.geometry("600x400")

    legend_colors = {}

    # ディレクトリ入力
    Label(root, text="CSV ディレクトリ:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    folder_entry = Entry(root, width=40)
    folder_entry.grid(row=0, column=1, padx=10, pady=10)
    Button(root, text="選択", command=lambda: select_folder(folder_entry)).grid(row=0, column=2, padx=10, pady=10)

    # 凡例リストボックス
    Label(root, text="凡例と色:").grid(row=1, column=0, padx=10, pady=10, sticky="nw")
    listbox = Listbox(root, selectmode="single", width=30, height=10)
    listbox.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # 色選択ボタン
    Button(root, text="色を選択", command=lambda: select_color(listbox, legend_colors, listbox.curselection()[0])).grid(row=1, column=2, padx=10, pady=10)

    # CSV読み込みボタン
    Button(root, text="CSV読み込み", command=lambda: load_csv_files(folder_entry.get(), legend_colors, listbox)).grid(row=2, column=1, pady=10)

    # 板厚入力
    Label(root, text="板厚:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    thickness_entry = Entry(root, width=10)
    thickness_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # 実行ボタン
    Button(root, text="グラフマージ", command=lambda: process_and_plot(
        csv_folder=folder_entry.get(),
        plate_thickness=float(thickness_entry.get()),
        output_dir=folder_entry.get(),
        legend_colors=legend_colors
    )).grid(row=4, column=1, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()





