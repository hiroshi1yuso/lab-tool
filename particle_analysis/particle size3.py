import cv2
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# GUIアプリケーションを作成
class ParticleAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("粒子解析ツール")

        # 初期パラメータ
        self.params = {
            "sharp_strength": tk.DoubleVar(value=8.3),
            "clip_limit": tk.DoubleVar(value=3.0),
            "binary_threshold": tk.IntVar(value=121),
            "kernel_width": tk.IntVar(value=3),
            "kernel_height": tk.IntVar(value=4),
            "scale_bar_length_pixels": tk.IntVar(value=167),
            "circularity_threshold": tk.DoubleVar(value=0.74)
        }

        # GUIウィジェットの作成
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # ファイル選択
        self.image_path = tk.StringVar()
        ttk.Label(frame, text="画像ファイル").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.image_path, width=40).grid(row=0, column=1)
        ttk.Button(frame, text="参照", command=self.select_file).grid(row=0, column=2)

        # パラメータ入力
        row_offset = 1
        for idx, (param, var) in enumerate(self.params.items()):
            ttk.Label(frame, text=param).grid(row=idx + row_offset, column=0, sticky=tk.W)
            ttk.Entry(frame, textvariable=var).grid(row=idx + row_offset, column=1, sticky=(tk.W, tk.E))

        # 実行ボタン
        ttk.Button(frame, text="解析を開始", command=self.run_analysis).grid(row=len(self.params) + row_offset, column=0, columnspan=3)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="画像ファイルを選択")
        if file_path:
            self.image_path.set(file_path)

    def run_analysis(self):
        image_path = self.image_path.get()
        if not image_path:
            print("画像ファイルを選択してください。")
            return

        # パラメータを取得
        sharp_strength = self.params["sharp_strength"].get()
        clip_limit = self.params["clip_limit"].get()
        binary_threshold = self.params["binary_threshold"].get()
        kernel_width = self.params["kernel_width"].get()
        kernel_height = self.params["kernel_height"].get()
        scale_bar_length_pixels = self.params["scale_bar_length_pixels"].get()
        circularity_threshold = self.params["circularity_threshold"].get()

        # 保存先ディレクトリを定義
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)

        # 画像の読み込み
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print("画像の読み込みに失敗しました。")
            return

        # コントラスト調整（シャープ化）
        kernel = np.array([[-1, -1, -1], [-1, sharp_strength, -1], [-1, -1, -1]])
        sharp = cv2.filter2D(img, -1, kernel)

        # CLAHE（ローカルコントラスト強調）
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        clahe_img = clahe.apply(sharp)

        # 軽いガウシアンブラーを追加
        blurred_clahe = cv2.GaussianBlur(clahe_img, (3, 5), 0)

        # 二値化のしきい値を調整
        _, binary = cv2.threshold(blurred_clahe, binary_threshold, 255, cv2.THRESH_BINARY)

        # モルフォロジー処理によるノイズ除去
        kernel = np.ones((kernel_width, kernel_height), np.uint8)
        cleaned_binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

        # スケールバーからピクセルあたりのスケールを計算
        microns_per_pixel = 1 / scale_bar_length_pixels

        # ラベリング（ラベルを付ける）
        num_labels, labels = cv2.connectedComponents(cleaned_binary)

        # 粒子解析
        colored_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        valid_particle_count = 0
        radius_list = []
        with open(os.path.join(output_dir, "particle_data.csv"), "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["ID", "Radius (μm)"])
            for label in range(1, num_labels):
                mask = np.uint8(labels == label)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if len(contour) > 0:
                        (x, y), radius = cv2.minEnclosingCircle(contour)
                        area = cv2.contourArea(contour)
                        perimeter = cv2.arcLength(contour, True)
                        circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0
                        if circularity_threshold <= circularity <= 1.0:
                            valid_particle_count += 1
                            radius_in_microns = radius * microns_per_pixel
                            radius_list.append(radius_in_microns)
                            csvwriter.writerow([valid_particle_count, radius_in_microns])
                            center = (int(x), int(y))
                            cv2.circle(colored_img, center, int(radius), (0, 255, 0), 2)

        # 平均半径を計算
        if radius_list:
            average_radius = np.mean(radius_list)
            print(f"平均半径 (μm): {average_radius:.2f}")

            # 粒子半径の分布をプロット
            plt.hist(radius_list, bins=20, range=(0, max(radius_list)), weights=np.ones(len(radius_list)) / len(radius_list) * 100, edgecolor="black")
            plt.xlabel("Radius (μm)")
            plt.ylabel("Frequency (%)")
            plt.title("Radius Distribution")
            plt.grid(True)
            plt.savefig(os.path.join(output_dir, "radius_distribution.png"))
            plt.show()
        else:
            print("粒子が検出されませんでした。")

        # 結果を保存
        cv2.imwrite(os.path.join(output_dir, "result_with_circles.jpg"), colored_img)
        print("解析が完了しました。結果はoutputフォルダに保存されました。")

# GUIアプリケーションの起動
if __name__ == "__main__":
    root = tk.Tk()
    app = ParticleAnalyzerApp(root)
    root.mainloop()



















