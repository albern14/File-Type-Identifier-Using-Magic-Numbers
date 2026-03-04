import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
from scanner import load_signatures, scan_file, scan_folder

class FileTypeIdentifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Type Identification Tool (Magic Numbers)")
        self.root.geometry("900x450")

        self.db = load_signatures()
        self.results = []

        # Top buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Select File", width=20, command=self.select_file).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Scan Folder", width=20, command=self.select_folder).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Export CSV", width=20, command=self.export_csv).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear Results", width=20, command=self.clear_results).grid(row=0, column=3, padx=5)

        # Results table
        columns = ("file", "extension", "detected", "confidence", "note")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")

        for col, title, width in [
            ("file", "File", 260),
            ("extension", "Extension", 90),
            ("detected", "Detected Type", 120),
            ("confidence", "Confidence", 100),
            ("note", "Note / Warning", 320),
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width)

        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Footer label
        self.status = tk.StringVar()
        self.status.set("Ready.")
        tk.Label(root, textvariable=self.status, anchor="w").pack(fill="x", padx=10, pady=(0, 10))

    def add_result(self, result):
        self.results.append(result)
        self.tree.insert("", tk.END, values=(
            result["file"],
            result["extension"],
            result["detected"],
            result["confidence"],
            result["note"]
        ))

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        result = scan_file(file_path, self.db)
        self.add_result(result)
        self.status.set(f"Scanned 1 file: {result['file']}")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        results = scan_folder(folder_path, self.db)
        for r in results:
            self.add_result(r)

        self.status.set(f"Scanned folder. Files scanned: {len(results)}")
        messagebox.showinfo("Scan Complete", f"Scanned {len(results)} files.")

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "Nothing to export yet.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not save_path:
            return

        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["file", "path", "extension", "detected", "confidence", "note"])
            writer.writeheader()
            writer.writerows(self.results)

        messagebox.showinfo("Exported", "CSV export completed successfully.")
        self.status.set("Exported results to CSV.")

    def clear_results(self):
        self.results = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status.set("Cleared results.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTypeIdentifierApp(root)
    root.mainloop()

