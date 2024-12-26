import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt


# データ処理関数
def merge_files(base_path, max_number):
    """CSVファイルをフォルダごとにマージする処理"""
    output_file = os.path.join(base_path, "merged_data.csv")
    all_data = []

    for i in range(1, max_number + 1):
        folder_name = f"step{i}_-1sec"
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            print(f"フォルダが見つかりません: {folder_path}")
            continue

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                try:
                    df = pd.read_csv(file_path, skiprows=2, header=None)
                    all_data.append(df)
                    print(f"読み込み成功: {file_path}")
                except Exception as e:
                    print(f"エラー: {file_path}, {e}")

    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_df.to_csv(output_file, index=False, header=False)
        print(f"マージが完了しました: {output_file}")
    else:
        print("データが見つかりませんでした。")

def process_max_K(base_path, chunk_size, diff_threshold, plate_thickness):
    """4列目の最大値処理とグラフ作成"""
    input_file = os.path.join(base_path, "merged_data.csv")
    output_csv = os.path.join(base_path, "max_K.csv")
    output_svg = os.path.join(base_path, "max_K_graph.svg")

    data = pd.read_csv(input_file, header=None)
    selected_rows = []

    for start_row in range(0, len(data), chunk_size):
        chunk = data.iloc[start_row:start_row + chunk_size]
        if chunk.empty:
            break

        sorted_chunk = chunk.sort_values(by=3, ascending=False)
        max_row = sorted_chunk.iloc[0]
        max_row_3_value = max_row[2]

        second_max_row = None
        for _, row in sorted_chunk.iterrows():
            if abs(row[2] - max_row_3_value) >= diff_threshold:
                second_max_row = row
                break

        selected_rows.append(max_row.tolist())
        if second_max_row is not None:
            selected_rows.append(second_max_row.tolist())

    result_df = pd.DataFrame(selected_rows)
    result_df.to_csv(output_csv, index=False, header=False)
    print(f"max_K.csv が生成されました: {output_csv}")

    # グラフ作成
    max_k_data = result_df.iloc[:-2]
    x = []
    y = []
    for i in range(0, len(max_k_data), 2):
        if i + 1 >= len(max_k_data):
            break
        row1 = max_k_data.iloc[i]
        row2 = max_k_data.iloc[i + 1]
        diff_half = abs(row1[2] - row2[2]) / 2
        x.append(diff_half)
        y.append(row1[5] if row1[2] < row2[2] else row2[5])

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    plt.xlabel("Crack half-width [mm]", fontsize=12)
    plt.ylabel("SIF [MPa*m^1/2]", fontsize=12)
    plt.grid(True)
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(output_svg, format='svg')
    print(f"グラフがSVG形式で保存されました: {output_svg}")

def process_min_K(base_path, chunk_size, plate_thickness):
    """4列目の最小値処理とグラフ作成"""
    input_file = os.path.join(base_path, "merged_data.csv")
    output_csv = os.path.join(base_path, "min_K.csv")
    output_svg = os.path.join(base_path, "min_K_graph.svg")

    data = pd.read_csv(input_file, header=None)
    selected_rows = []

    for start_row in range(0, len(data), chunk_size):
        chunk = data.iloc[start_row:start_row + chunk_size]
        if chunk.empty:
            break

        sorted_chunk = chunk.sort_values(by=3, ascending=True)
        min_row = sorted_chunk.iloc[0]
        selected_rows.append(min_row.tolist())

    result_df = pd.DataFrame(selected_rows)
    result_df.to_csv(output_csv, index=False, header=False)
    print(f"min_K.csv が生成されました: {output_csv}")

    # グラフ作成
    result_df = result_df.iloc[:-1]
    x = plate_thickness - result_df.iloc[:, 3]
    y = result_df.iloc[:, 5]

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='green')
    plt.xlabel("Crack Depth [mm]", fontsize=12)
    plt.ylabel("SIF [MPa*m^1/2]", fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_svg, format='svg')
    print(f"グラフがSVG形式で保存されました: {output_svg}")

# GUIアプリケーション
def run_script(mode, base_path, max_number=None, chunk_size=None, diff_threshold=None, plate_thickness=None):
    """処理モードに応じた関数を実行"""
    try:
        if mode == "merge":
            merge_files(base_path, max_number)
        elif mode == "max_K":
            process_max_K(base_path, chunk_size, diff_threshold, plate_thickness)
        elif mode == "min_K":
            process_min_K(base_path, chunk_size, plate_thickness)
        output_log.insert(tk.END, f"{mode} 処理が完了しました。\n")
    except Exception as e:
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}")

def select_folder():
    """フォルダ選択ダイアログを表示"""
    folder_path = filedialog.askdirectory()
    if folder_path:
        base_path_entry.delete(0, tk.END)
        base_path_entry.insert(0, folder_path)

# メインウィンドウの作成
root = tk.Tk()
root.title("データ処理GUIアプリ")

# フォルダのベースパス
tk.Label(root, text="フォルダのベースパス:").grid(row=0, column=0, sticky=tk.W)
base_path_entry = tk.Entry(root, width=50)
base_path_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="参照", command=select_folder).grid(row=0, column=2, padx=5, pady=5)

# 最大フォルダ番号
tk.Label(root, text="最大フォルダ番号 (merge):").grid(row=1, column=0, sticky=tk.W)
max_number_spinbox = tk.Spinbox(root, from_=1, to=100, width=10)
max_number_spinbox.grid(row=1, column=1, padx=5, pady=5)

# chunk_size
tk.Label(root, text="chunk_size (max/min):").grid(row=2, column=0, sticky=tk.W)
chunk_size_spinbox = tk.Spinbox(root, from_=1, to=1000, width=10)
chunk_size_spinbox.grid(row=2, column=1, padx=5, pady=5)

# 3列目の差の閾値
tk.Label(root, text="3列目の差の閾値 (max):").grid(row=3, column=0, sticky=tk.W)
diff_threshold_spinbox = tk.Spinbox(root, from_=0, to=100, increment=0.1, width=10)
diff_threshold_spinbox.grid(row=3, column=1, padx=5, pady=5)

# 板厚
tk.Label(root, text="板厚 [mm] (min):").grid(row=4, column=0, sticky=tk.W)
plate_thickness_spinbox = tk.Spinbox(root, from_=1, to=100, width=10)
plate_thickness_spinbox.grid(row=4, column=1, padx=5, pady=5)

# 実行ボタン
tk.Button(root, text="merge 実行", command=lambda: run_script(
    "merge",
    base_path_entry.get(),
    int(max_number_spinbox.get()),
    None,  # chunk_sizeは不要
    None,  # diff_thresholdは不要
    None   # plate_thicknessは不要
)).grid(row=5, column=0, padx=5, pady=5)

tk.Button(root, text="max_K 実行", command=lambda: run_script(
    "max_K",
    base_path_entry.get(),
    None,  # max_numberは不要
    int(chunk_size_spinbox.get()),
    float(diff_threshold_spinbox.get()),
    int(plate_thickness_spinbox.get())
)).grid(row=5, column=1, padx=5, pady=5)

tk.Button(root, text="min_K 実行", command=lambda: run_script(
    "min_K",
    base_path_entry.get(),
    None,  # max_numberは不要
    int(chunk_size_spinbox.get()),
    None,  # diff_thresholdは不要
    int(plate_thickness_spinbox.get())
)).grid(row=5, column=2, padx=5, pady=5)

# 実行結果の表示
output_log = tk.Text(root, height=10, width=80)
output_log.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# メインループ
root.mainloop()






