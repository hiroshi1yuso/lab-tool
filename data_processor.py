import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

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
                   # print(f"読み込み成功: {file_path}")
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

# メイン処理
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data processing script for merge, max_K, and min_K operations.")
    parser.add_argument("mode", choices=["merge", "max_K", "min_K"], help="Operation mode")
    parser.add_argument("--base_path", required=True, help="Base directory path")
    parser.add_argument("--max_number", type=int, required=False, help="Maximum folder number (for merge)")
    parser.add_argument("--chunk_size", type=int, required=False, help="Chunk size for processing (for max_K and min_K)")
    parser.add_argument("--diff_threshold", type=float, required=False, help="Threshold for 3rd column difference (for max_K)")
    parser.add_argument("--plate_thickness", type=float, required=False, help="Plate thickness value (for min_K)")
    args = parser.parse_args()

    if args.mode == "merge":
        merge_files(args.base_path, args.max_number)
    elif args.mode == "max_K":
        process_max_K(args.base_path, args.chunk_size, args.diff_threshold, args.plate_thickness)
    elif args.mode == "min_K":
        process_min_K(args.base_path, args.chunk_size, args.plate_thickness)




