import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from run import run_as_module
from core.url_parser import parse_booking_url
import threading
import logging
import sys
import os
from datetime import datetime

class ModernTheme:
    """Modern theme colors and styles"""
    BG_COLOR = "#f0f0f0"
    ACCENT_COLOR = "#2196F3"  # Material Design Blue
    TEXT_COLOR = "#212121"
    SECONDARY_COLOR = "#757575"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#f44336"

def setup_styles():
    """Configure ttk styles for a modern look"""
    style = ttk.Style()
    
    # Configure main styles
    style.configure("Modern.TFrame", background=ModernTheme.BG_COLOR)
    style.configure("Modern.TLabel", 
                   background=ModernTheme.BG_COLOR, 
                   foreground=ModernTheme.TEXT_COLOR,
                   font=("Segoe UI", 9))
    style.configure("Header.TLabel",
                   background=ModernTheme.BG_COLOR,
                   foreground=ModernTheme.ACCENT_COLOR,
                   font=("Segoe UI", 11, "bold"))
    style.configure("Status.TLabel",
                   background=ModernTheme.BG_COLOR,
                   foreground=ModernTheme.SECONDARY_COLOR,
                   font=("Segoe UI", 9))
    
    # Configure button styles
    style.configure("Modern.TButton",
                   background=ModernTheme.ACCENT_COLOR,
                   foreground="white",
                   padding=(20, 10),
                   font=("Segoe UI", 9, "bold"))
    style.map("Modern.TButton",
             background=[("active", ModernTheme.ACCENT_COLOR),
                        ("disabled", ModernTheme.SECONDARY_COLOR)])

    # Configure entry and combobox
    style.configure("Modern.TEntry", padding=5)
    style.configure("Modern.TCombobox", padding=5)

def setup_logger():
    """Set up a logger for the GUI version"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    logger = logging.getLogger('GUI_Logger')
    logger.setLevel(logging.INFO)
    
    # Generate a unique log file name
    log_file = f"logs/{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    def show_tooltip(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = ttk.Label(tooltip, text=text, background="#ffffe0", 
                         relief="solid", borderwidth=1)
        label.pack()
        
        def hide_tooltip():
            tooltip.destroy()
        
        widget.tooltip = tooltip
        widget.bind('<Leave>', lambda e: hide_tooltip())
        
    widget.bind('<Enter>', show_tooltip)

def start_scraping():
    def show_messagebox(kind, title, message):
        if kind == "error":
            messagebox.showerror(title, message)
        elif kind == "info":
            messagebox.showinfo(title, message)

    def process_urls():
        # Get URLs from text area
        urls = url_text.get("1.0", tk.END).strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            root.after(0, lambda: show_messagebox("error", "Input Error", "Please enter at least one Booking.com URL"))
            root.after(0, lambda: start_btn.config(state=tk.NORMAL))
            return

        total_reviews = 0
        failed_urls = []
        
        try:
            n_reviews = int(n_reviews_var.get())
        except ValueError:
            n_reviews = -1
            
        sort = sort_var.get()
        save = save_var.get()
        download_photos = download_photos_var.get()
        stop_user = stop_user_var.get().strip()
        stop_title = stop_title_var.get().strip()
        
        # Create a custom logger for this scraping session
        logger = setup_logger()
        
        # Process each URL
        for i, url in enumerate(urls, 1):
            try:
                # Update status
                status_var.set(f"Processing property {i}/{len(urls)}...")
                
                # Parse URL to get hotel name and country
                hotel_name, country = parse_booking_url(url)
                
                # Set the job_id environment variable for this run
                os.environ["job_id"] = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                
                reviews = run_as_module(
                    hotel_name=hotel_name,
                    country=country,
                    sort_by=sort,
                    n_reviews=n_reviews,
                    save_to_disk=save,
                    stop_cri_user=stop_user,
                    stop_cri_title=stop_title,
                    download_photos=download_photos,
                    logger=logger,
                    is_gui=True
                )
                total_reviews += len(reviews)
                
            except Exception as e:
                failed_urls.append((url, str(e)))
                logger.error(f"Failed to process URL: {url}\nError: {str(e)}")
                continue
        
        # Show final results
        status_message = f"Scraping complete!\nTotal reviews scraped: {total_reviews}"
        if failed_urls:
            status_message += f"\n\nFailed URLs ({len(failed_urls)}):"
            for url, error in failed_urls:
                status_message += f"\n{url}\nError: {error}\n"
        
        root.after(0, lambda: show_messagebox("info", "Complete", status_message))
        root.after(0, lambda: start_btn.config(state=tk.NORMAL))
        root.after(0, lambda: status_var.set("Ready"))

    start_btn.config(state=tk.DISABLED)
    status_var.set("Starting...")
    threading.Thread(target=process_urls, daemon=True).start()

def create_gui():
    root = tk.Tk()
    root.title("Booking.com Reviews Scraper")
    root.configure(bg=ModernTheme.BG_COLOR)
    
    # Set up modern styles
    setup_styles()
    
    # Create main container
    main_container = ttk.Frame(root, style="Modern.TFrame", padding="20")
    main_container.grid(row=0, column=0, sticky="nsew")
    
    # Configure grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_container.columnconfigure(1, weight=1)
    
    # Header
    header_label = ttk.Label(main_container, 
                            text="Booking.com Reviews Scraper",
                            style="Header.TLabel")
    header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # URL input section
    url_frame = ttk.LabelFrame(main_container, text="URLs", padding="10", style="Modern.TFrame")
    url_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
    
    url_label = ttk.Label(url_frame, 
                         text="Enter Booking.com URLs (one per line):",
                         style="Modern.TLabel")
    url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
    
    global url_text
    url_text = scrolledtext.ScrolledText(url_frame, width=50, height=5, 
                                       font=("Segoe UI", 9))
    url_text.grid(row=1, column=0, sticky="ew")
    create_tooltip(url_text, "Paste your Booking.com property URLs here")
    
    # Options frame
    options_frame = ttk.LabelFrame(main_container, text="Scraping Options", 
                                 padding="10", style="Modern.TFrame")
    options_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 20))
    
    # Sort options
    ttk.Label(options_frame, text="Sort By:", 
              style="Modern.TLabel").grid(row=0, column=0, sticky="w")
    global sort_var
    sort_var = tk.StringVar(value="most_relevant")
    sort_combo = ttk.Combobox(options_frame, textvariable=sort_var,
                             values=["most_relevant", "newest_first", 
                                    "oldest_first", "highest_scores", 
                                    "lowest_scores"],
                             state="readonly", style="Modern.TCombobox")
    sort_combo.grid(row=0, column=1, sticky="w", padx=(10, 0))
    
    # Number of reviews
    ttk.Label(options_frame, text="Number of Reviews:",
              style="Modern.TLabel").grid(row=1, column=0, sticky="w", pady=10)
    global n_reviews_var
    n_reviews_var = tk.StringVar(value="-1")
    reviews_entry = ttk.Entry(options_frame, textvariable=n_reviews_var,
                            width=10, style="Modern.TEntry")
    reviews_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=10)
    create_tooltip(reviews_entry, "Enter -1 to scrape all reviews")
    
    # Checkboxes frame
    checks_frame = ttk.Frame(options_frame, style="Modern.TFrame")
    checks_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    
    global save_var, download_photos_var
    save_var = tk.BooleanVar(value=True)
    download_photos_var = tk.BooleanVar(value=True)
    
    ttk.Checkbutton(checks_frame, text="Save to disk",
                    variable=save_var).grid(row=0, column=0, padx=5)
    ttk.Checkbutton(checks_frame, text="Download photos",
                    variable=download_photos_var).grid(row=0, column=1, padx=5)
    
    # Stop criteria frame
    stop_frame = ttk.LabelFrame(main_container, text="Stop Criteria (Optional)",
                               padding="10", style="Modern.TFrame")
    stop_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20))
    
    global stop_user_var, stop_title_var
    stop_user_var = tk.StringVar()
    stop_title_var = tk.StringVar()
    
    ttk.Label(stop_frame, text="Username:",
              style="Modern.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Entry(stop_frame, textvariable=stop_user_var,
              width=20, style="Modern.TEntry").grid(row=0, column=1, padx=(10, 0))
    
    ttk.Label(stop_frame, text="Review Title:",
              style="Modern.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
    ttk.Entry(stop_frame, textvariable=stop_title_var,
              width=20, style="Modern.TEntry").grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
    
    # Status and button frame
    status_frame = ttk.Frame(main_container, style="Modern.TFrame")
    status_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
    
    global status_var, start_btn
    status_var = tk.StringVar(value="Ready")
    status_label = ttk.Label(status_frame, textvariable=status_var,
                            style="Status.TLabel")
    status_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
    
    start_btn = ttk.Button(status_frame, text="Start Scraping",
                          command=start_scraping, style="Modern.TButton")
    start_btn.grid(row=1, column=0, sticky="ew")
    
    return root

if __name__ == "__main__":
    root = create_gui()
    root.mainloop()
