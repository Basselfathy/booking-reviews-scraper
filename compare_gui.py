import tkinter as tk
from tkinter import filedialog, messagebox
import os
import datetime
import pandas as pd
from compare_properties import compare_properties

try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Error", "tkcalendar is not installed. Please install it with 'pip install tkcalendar'.")
    raise

def run_comparison(selected_files, start_date, end_date, output_path):
    try:
        df = compare_properties(selected_files, start_date, end_date)
        df.to_csv(output_path, index=False)
        messagebox.showinfo("Success", f"Comparison complete!\nSaved to: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_output(entry):
    file = filedialog.asksaveasfilename(
        title="Save summary as...",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialdir=os.getcwd(),
        initialfile="comparison_summary.csv"
    )
    if file:
        entry.delete(0, tk.END)
        entry.insert(0, file)

def main():
    root = tk.Tk()
    root.title("Compare Booking.com Properties")
    root.geometry("600x400")

    tk.Label(root, text="Select review CSV files (from output/):").pack(anchor="w", padx=10, pady=(10,0))

    files_frame = tk.Frame(root)
    files_frame.pack(padx=10, pady=2, fill="x")
    file_entries = []

    def add_file_field():
        entry = tk.Entry(files_frame, width=60)
        entry.pack(pady=2, anchor="w")
        file_entries.append(entry)
        def browse():
            file = filedialog.askopenfilename(
                title="Select CSV file",
                filetypes=[("CSV Files", "*.csv")],
                initialdir=os.path.join(os.getcwd(), 'output')
            )
            if file:
                output_dir = os.path.join(os.getcwd(), 'output')
                if file.startswith(output_dir):
                    rel_file = os.path.relpath(file, output_dir)
                else:
                    rel_file = file
                entry.delete(0, tk.END)
                entry.insert(0, rel_file)
        tk.Button(files_frame, text="Browse", command=browse).pack(pady=2, anchor="w")

    def add_another_file():
        add_file_field()

    add_file_field()  # Add the first file field by default
    tk.Button(root, text="Add Another File", command=add_another_file).pack(padx=10, pady=2)

    tk.Label(root, text="Start date (YYYY-MM-DD):").pack(anchor="w", padx=10, pady=(10,0))
    start_entry = DateEntry(root, width=20, date_pattern='yyyy-mm-dd')
    start_entry.pack(padx=10)
    start_entry.set_date(datetime.date.today().replace(year=datetime.date.today().year-1))

    tk.Label(root, text="End date (YYYY-MM-DD):").pack(anchor="w", padx=10, pady=(10,0))
    end_entry = DateEntry(root, width=20, date_pattern='yyyy-mm-dd')
    end_entry.pack(padx=10)
    end_entry.set_date(datetime.date.today())

    tk.Label(root, text="Output file:").pack(anchor="w", padx=10, pady=(10,0))
    out_entry = tk.Entry(root, width=60)
    out_entry.pack(padx=10)
    tk.Button(root, text="Choose Output", command=lambda: select_output(out_entry)).pack(padx=10, pady=2)

    def on_run():
        files = [e.get().strip() for e in file_entries if e.get().strip()]
        start = start_entry.get_date().isoformat()
        end = end_entry.get_date().isoformat()
        out = out_entry.get().strip()
        if not files or not start or not end or not out:
            messagebox.showerror("Error", "Please fill in all fields and select files.")
            return
        run_comparison(files, start, end, out)

    tk.Button(root, text="Run Comparison", command=on_run, bg="#4CAF50", fg="white").pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    main()
