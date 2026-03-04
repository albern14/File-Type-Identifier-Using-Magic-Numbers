# Import the main tkinter library for building the GUI
import tkinter as tk

# Import specific tkinter modules:
# filedialog -> lets user choose files/folders
# messagebox -> popup messages (info, warning, etc.)
# ttk -> themed widgets (like modern table/treeview)
from tkinter import filedialog, messagebox, ttk

# Import required functions from your scanner module
# load_signatures -> loads known file "magic numbers"
# scan_file -> scans one file
# scan_folder -> scans all files inside a folder
import csv
from scanner import load_signatures, scan_file, scan_folder


class FileTypeIdentifierApp:
    def __init__(self, root):
        # Store the main window
        self.root = root
        
        # Set window title
        self.root.title("File Type Identification Tool (Magic Numbers)")
        
        # Set window size
        self.root.geometry("900x450")

        # Load file signature database at startup
        self.db = load_signatures()
        
        # Store scan results in a list
        self.results = []

        # -------------------------
        # TOP BUTTON SECTION
        # -------------------------

        # Create a frame (container) to hold buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)  # Add vertical spacing

        # Button to scan a single file
        tk.Button(btn_frame, text="Select File", width=20,
                  command=self.select_file).grid(row=0, column=0, padx=5)

        # Button to scan an entire folder
        tk.Button(btn_frame, text="Scan Folder", width=20,
                  command=self.select_folder).grid(row=0, column=1, padx=5)

        # Button to export results to CSV
        tk.Button(btn_frame, text="Export CSV", width=20,
                  command=self.export_csv).grid(row=0, column=2, padx=5)

        # Button to clear all results
        tk.Button(btn_frame, text="Clear Results", width=20,
                  command=self.clear_results).grid(row=0, column=3, padx=5)

        # -------------------------
        # RESULTS TABLE SECTION
        # -------------------------

        # Define table columns
        columns = ("file", "extension", "detected", "confidence", "note")

        # Create a Treeview (table)
        self.tree = ttk.Treeview(root, columns=columns, show="headings")

        # Configure each column (id, display title, width)
        for col, title, width in [
            ("file", "File", 260),
            ("extension", "Extension", 90),
            ("detected", "Detected Type", 120),
            ("confidence", "Confidence", 100),
            ("note", "Note / Warning", 320),
        ]:
            self.tree.heading(col, text=title)  # Set column header text
            self.tree.column(col, width=width)  # Set column width

        # Make table expand to fill window
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # -------------------------
        # STATUS BAR (FOOTER)
        # -------------------------

        # Create a text variable to update status dynamically
        self.status = tk.StringVar()
        self.status.set("Ready.")

        # Display status label at bottom of window
        tk.Label(root, textvariable=self.status,
                 anchor="w").pack(fill="x", padx=10, pady=(0, 10))

    # -------------------------
    # ADD RESULT TO TABLE
    # -------------------------
    def add_result(self, result):
        # Save result to internal list
        self.results.append(result)

        # Insert result into the GUI table
        self.tree.insert("", tk.END, values=(
            result["file"],
            result["extension"],
            result["detected"],
            result["confidence"],
            result["note"]
        ))

    # -------------------------
    # SELECT AND SCAN SINGLE FILE
    # -------------------------
    def select_file(self):
        # Open file selection dialog
        file_path = filedialog.askopenfilename()

        # If user cancels, do nothing
        if not file_path:
            return

        # Scan selected file
        result = scan_file(file_path, self.db)

        # Add result to table
        self.add_result(result)

        # Update status bar
        self.status.set(f"Scanned 1 file: {result['file']}")

    # -------------------------
    # SELECT AND SCAN FOLDER
    # -------------------------
    def select_folder(self):
        # Open folder selection dialog
        folder_path = filedialog.askdirectory()

        # If user cancels, do nothing
        if not folder_path:
            return

        # Scan all files in folder
        results = scan_folder(folder_path, self.db)

        # Add each result to table
        for r in results:
            self.add_result(r)

        # Update status bar
        self.status.set(f"Scanned folder. Files scanned: {len(results)}")

        # Show popup message
        messagebox.showinfo("Scan Complete",
                            f"Scanned {len(results)} files.")

    # -------------------------
    # EXPORT RESULTS TO CSV
    # -------------------------
    def export_csv(self):
        # If no results exist, show warning
        if not self.results:
            messagebox.showwarning("No Data",
                                   "Nothing to export yet.")
            return

        # Ask user where to save file
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        # If user cancels, do nothing
        if not save_path:
            return

        # Open CSV file for writing
        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["file", "path", "extension",
                            "detected", "confidence", "note"]
            )

            # Write header row
            writer.writeheader()

            # Write all results
            writer.writerows(self.results)

        # Show confirmation popup
        messagebox.showinfo("Exported",
                            "CSV export completed successfully.")

        # Update status
        self.status.set("Exported results to CSV.")

    # -------------------------
    # CLEAR TABLE RESULTS
    # -------------------------
    def clear_results(self):
        # Reset stored results list
        self.results = []

        # Remove all rows from table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Update status
        self.status.set("Cleared results.")


# -------------------------
# PROGRAM ENTRY POINT
# -------------------------
if __name__ == "__main__":
    # Create main tkinter window
    root = tk.Tk()

    # Create app instance
    app = FileTypeIdentifierApp(root)

    # Start GUI event loop (keeps window running)
    root.mainloop()
