import tkinter as tk
from tkinter import filedialog, messagebox
import cairosvg

def convert_svg_to_eps(input_svg_path, output_eps_path):
    """
    SVGファイルをEPSファイルに変換する関数
    """
    try:
        cairosvg.svg2eps(url=input_svg_path, write_to=output_eps_path)
        messagebox.showinfo("成功", f"変換完了: {output_eps_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"変換中にエラーが発生しました:\n{e}")

def browse_input_file():
    """SVGファイルを選択するダイアログを開く"""
    file_path = filedialog.askopenfilename(
        filetypes=[("SVGファイル", "*.svg"), ("すべてのファイル", "*.*")]
    )
    if file_path:
        input_path_var.set(file_path)

def convert_file():
    """選択されたSVGファイルをEPSに変換"""
    input_svg = input_path_var.get()
    if not input_svg:
        messagebox.showwarning("警告", "入力ファイルを選択してください。")
        return

    # 保存先を指定
    output_eps = filedialog.asksaveasfilename(
        defaultextension=".eps",
        filetypes=[("EPSファイル", "*.eps")],
        title="保存先を指定"
    )
    if output_eps:
        convert_svg_to_eps(input_svg, output_eps)

# GUIの作成
root = tk.Tk()
root.title("SVG -> EPS 変換ツール")

# 入力ファイル選択部分
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="SVGファイル:").grid(row=0, column=0, sticky=tk.W, pady=5)
input_path_var = tk.StringVar()
input_entry = tk.Entry(frame, textvariable=input_path_var, width=40)
input_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = tk.Button(frame, text="参照", command=browse_input_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# 実行ボタン
convert_button = tk.Button(root, text="変換実行", command=convert_file, padx=10, pady=5)
convert_button.pack(pady=10)

# GUI実行
root.mainloop()




