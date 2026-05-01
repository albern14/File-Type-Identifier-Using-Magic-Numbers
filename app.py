# Import the main tkinter library for building the GUI
import tkinter as tk

# Import specific tkinter modules:
# filedialog -> lets user choose files/folders
# messagebox -> popup messages (info, warning, etc.)
# ttk -> themed widgets (modern table/treeview)
from tkinter import filedialog, messagebox, ttk

# Import CSV module for exporting results
import csv

# Import required functions from scanner module
# load_signatures -> loads known file magic numbers
# scan_file -> scans a single file
# scan_folder -> scans every file in a folder
from scanner import load_signatures, scan_file, scan_folder


class FileTypeIdentifierApp:
    def __init__(self, root):
        # Store the main application window
        self.root = root

        # Configure window title, size, and background styling
        self.root.title("File Type Identification Tool")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f4f6f8")

        # Load file signature database at startup
        self.db = load_signatures()

        # Store all scan results for export/summary
        self.results = []

        # -------------------------
        # TITLE SECTION
        # -------------------------

        # Frame to hold title labels
        title_frame = tk.Frame(root, bg="#f4f6f8")
        title_frame.pack(pady=(15, 5))

        # Main application heading
        tk.Label(
            title_frame,
            text="File Type Identification Tool",
            font=("Segoe UI", 20, "bold"),
            bg="#f4f6f8",
            fg="#1f3b5b"
        ).pack()

        # Subtitle/description
        tk.Label(
            title_frame,
            text="Detecting real file types using magic numbers",
            font=("Segoe UI", 11),
            bg="#f4f6f8",
            fg="#4f6475"
        ).pack()

        # -------------------------
        # BUTTON SECTION
        # -------------------------

        # Container for all top action buttons
        btn_frame = tk.Frame(root, bg="#f4f6f8")
        btn_frame.pack(pady=10)

        # Shared button styling dictionary
        button_style = {
            "font": ("Segoe UI", 10, "bold"),
            "width": 16,
            "padx": 8,
            "pady": 8
        }

        # Action buttons
        tk.Button(btn_frame, text="Select File",
                  command=self.select_file,
                  **button_style).grid(row=0, column=0, padx=6)

        tk.Button(btn_frame, text="Scan Folder",
                  command=self.select_folder,
                  **button_style).grid(row=0, column=1, padx=6)

        tk.Button(btn_frame, text="Export CSV",
                  command=self.export_csv,
                  **button_style).grid(row=0, column=2, padx=6)

        tk.Button(btn_frame, text="Clear Results",
                  command=self.clear_results,
                  **button_style).grid(row=0, column=3, padx=6)

        tk.Button(btn_frame, text="Supported Types",
                  command=self.show_supported_types,
                  **button_style).grid(row=0, column=4, padx=6)

        tk.Button(btn_frame, text="About",
                  command=self.show_about,
                  **button_style).grid(row=0, column=5, padx=6)

        # -------------------------
        # SUMMARY STATISTICS SECTION
        # -------------------------

        # Frame for summary counters
        summary_frame = tk.Frame(root, bg="#f4f6f8")
        summary_frame.pack(pady=(5, 10))

        # Dynamic summary values
        self.total_var = tk.StringVar(value="Total Scanned: 0")
        self.suspicious_var = tk.StringVar(value="Suspicious Files: 0")
        self.unknown_var = tk.StringVar(value="Unknown Files: 0")

        # Create summary cards
        self.make_summary_label(summary_frame, self.total_var, 0)
        self.make_summary_label(summary_frame, self.suspicious_var, 1)
        self.make_summary_label(summary_frame, self.unknown_var, 2)

        # -------------------------
        # RESULTS TABLE SECTION
        # -------------------------

        # Container for table and scrollbar
        table_frame = tk.Frame(root, bg="#f4f6f8")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Define table columns
        columns = ("file", "extension", "detected", "confidence", "note")

        # Create Treeview table
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=18
        )

        # Configure table headings
        self.tree.heading("file", text="File")
        self.tree.heading("extension", text="Extension")
        self.tree.heading("detected", text="Detected Type")
        self.tree.heading("confidence", text="Confidence")
        self.tree.heading("note", text="Note / Warning")

        # Configure column widths
        self.tree.column("file", width=280)
        self.tree.column("extension", width=100)
        self.tree.column("detected", width=130)
        self.tree.column("confidence", width=100)
        self.tree.column("note", width=420)

        # Add vertical scrollbar to table
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack table and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # -------------------------
        # ROW HIGHLIGHTING RULES
        # -------------------------

        # Suspicious files = red tint
        self.tree.tag_configure("suspicious", background="#ffe5e5")

        # Unknown files = yellow tint
        self.tree.tag_configure("unknown", background="#fff4cc")

        # -------------------------
        # STATUS BAR SECTION
        # -------------------------

        # Dynamic status text
        self.status = tk.StringVar()
        self.status.set("Ready.")

        # Bottom status bar
        status_bar = tk.Label(
            root,
            textvariable=self.status,
            anchor="w",
            bg="#d9e2ec",
            fg="#102a43",
            font=("Segoe UI", 10),
            padx=10,
            pady=6
        )
        status_bar.pack(fill="x", side="bottom")

    # -------------------------
    # CREATE SUMMARY CARD LABEL
    # -------------------------
    def make_summary_label(self, parent, variable, col):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        frame.grid(row=0, column=col, padx=10)

        tk.Label(
            frame,
            textvariable=variable,
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#1f3b5b",
            width=22,
            pady=10
        ).pack()

    # -------------------------
    # ADD RESULT TO TABLE
    # -------------------------
    def add_result(self, result):
        # Save result internally
        self.results.append(result)

        # Determine row highlighting tag
        tag = ""

        if result["detected"] == "Unknown":
            tag = "unknown"

        elif result["note"]:
            tag = "suspicious"

        # Insert row into table
        self.tree.insert(
            "",
            tk.END,
            values=(
                result["file"],
                result["extension"],
                result["detected"],
                result["confidence"],
                result["note"]
            ),
            tags=(tag,)
        )

        # Refresh summary counters
        self.update_summary()

    # -------------------------
    # UPDATE SUMMARY COUNTERS
    # -------------------------
    def update_summary(self):
        total = len(self.results)

        suspicious = sum(
            1 for r in self.results
            if r["note"]
        )

        unknown = sum(
            1 for r in self.results
            if r["detected"] == "Unknown"
        )

        self.total_var.set(f"Total Scanned: {total}")
        self.suspicious_var.set(f"Suspicious Files: {suspicious}")
        self.unknown_var.set(f"Unknown Files: {unknown}")

    # -------------------------
    # SELECT AND SCAN SINGLE FILE
    # -------------------------
    def select_file(self):
        file_path = filedialog.askopenfilename()

        if not file_path:
            return

        result = scan_file(file_path, self.db)

        self.add_result(result)

        self.status.set(f"Scanned file: {result['file']}")

    # -------------------------
    # SELECT AND SCAN FOLDER
    # -------------------------
    def select_folder(self):
        folder_path = filedialog.askdirectory()

        if not folder_path:
            return

        results = scan_folder(folder_path, self.db)

        for result in results:
            self.add_result(result)

        self.status.set(f"Folder scan completed. Files scanned: {len(results)}")

        messagebox.showinfo(
            "Scan Complete",
            f"Scanned {len(results)} files."
        )

    # -------------------------
    # EXPORT RESULTS TO CSV
    # -------------------------
    def export_csv(self):
        if not self.results:
            messagebox.showwarning(
                "No Data",
                "Nothing to export yet."
            )
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not save_path:
            return

        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "file",
                    "path",
                    "extension",
                    "detected",
                    "confidence",
                    "note"
                ]
            )

            writer.writeheader()
            writer.writerows(self.results)

        self.status.set("Results exported to CSV successfully.")

        messagebox.showinfo(
            "Export Complete",
            "Results exported successfully."
        )

    # -------------------------
    # CLEAR ALL RESULTS
    # -------------------------
    def clear_results(self):
        self.results = []

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.update_summary()

        self.status.set("Results cleared.")

    # -------------------------
    # SHOW SUPPORTED FILE TYPES
    # -------------------------
    def show_supported_types(self):
        supported = []

        for filetype, meta in self.db.items():
            supported.append(f"{filetype} ({meta['ext']})")

        message = "Currently supported file types:\n\n" + "\n".join(supported)

        messagebox.showinfo(
            "Supported File Types",
            message
        )

    # -------------------------
    # SHOW ABOUT DIALOG
    # -------------------------
    def show_about(self):
        message = (
            "File Type Identification Tool\n\n"
            "This application identifies the real type of a file "
            "by reading its magic number rather than trusting "
            "the file extension.\n\n"
            "Main features:\n"
            "- Scan individual files\n"
            "- Scan complete folders\n"
            "- Detect extension mismatches\n"
            "- Export results to CSV\n"
            "- Highlight suspicious and unknown files"
        )

        messagebox.showinfo("About", message)


# -------------------------
# PROGRAM ENTRY POINT
# -------------------------
if __name__ == "__main__":
    # Create main tkinter window
    root = tk.Tk()

    # Create application instance
    app = FileTypeIdentifierApp(root)

    # Start GUI event loop
    root.mainloop()
