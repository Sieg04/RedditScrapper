import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
import tkinter.font as tkFont
import praw
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import webbrowser
import json

# A subclass of ttk.Combobox to always return a valid string
class SafeCombobox(ttk.Combobox):
    def get(self):
        value = super().get()
        try:
            s = str(value).strip()
            if not s or s.lower() == "_notset":
                return "Title"
            return s
        except Exception:
            return "Title"

# Configuration file for storing credentials
CONFIG_FILE = "credentials_config.json"

# =======================
# Credential-related functions
# =======================

def load_credentials():
    """Loads credentials from the config file, if it exists."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load credentials: {e}")
    return {}

def save_credentials(credentials):
    """Saves credentials to the config file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(credentials, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save credentials: {e}")

# =======================
# Data extraction and export
# =======================

def get_reddit_posts(limit, client_id, client_secret, user_agent):
    """
    Extracts posts from the r/simpleloans subreddit using the given Reddit configuration.
    Each post includes: Title, URL, Author, and Date (without the time).
    """
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    subreddit = reddit.subreddit('simpleloans')
    posts = []
    for submission in subreddit.new(limit=limit):
        post_date = datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%d")
        posts.append({
            'Title': submission.title,
            'URL': submission.url,
            'Author': submission.author.name if submission.author else 'N/A',
            'Date': post_date
        })
    return posts

def export_to_csv(posts, file_path):
    """
    Exports a list of posts to a local CSV file.
    The posts are sorted by Title before exporting.
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'URL', 'Author', 'Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            posts_sorted = sorted(posts, key=lambda x: x['Title'])
            for post in posts_sorted:
                writer.writerow(post)
    except Exception as e:
        raise Exception(f"Error writing to CSV file: {e}")
    return f"Data successfully exported to {file_path}"

def load_csv_data(file_path):
    """
    Loads data from a CSV file and returns it as a list of dictionaries.
    """
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except Exception as e:
        raise Exception(f"Error reading CSV file: {e}")
    return data

def plot_post_frequency(csv_path):
    """
    Generates a bar chart showing post frequency by user.
    """
    data = load_csv_data(csv_path)
    freq = {}
    for row in data:
        user = row.get('Author', 'N/A')
        freq[user] = freq.get(user, 0) + 1
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    if not sorted_freq:
        messagebox.showinfo("Information", "No data to plot.")
        return
    users, counts = zip(*sorted_freq)
    plt.figure(figsize=(10, 6))
    plt.bar(users, counts, color="#a3c1da")
    plt.xlabel("Users")
    plt.ylabel("Number of Posts")
    plt.title("Posting Frequency by User")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# =======================
# Function to auto-adjust Treeview columns
# =======================

def adjust_columns(tree, data, columns):
    default_font = tkFont.nametofont("TkDefaultFont")
    for col in columns:
        max_width = default_font.measure(col)
        for row in data:
            text = row.get(col, "")
            width = default_font.measure(text)
            if width > max_width:
                max_width = width
        tree.column(col, width=max_width + 10)

# =======================
# GUI (UI)
# =======================

class RedditTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Reddit Tracker")

        # Modern pastel-style configuration
        self.style = ttk.Style(master)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f8ff")
        self.style.configure("TLabel", background="#f0f8ff", foreground="#333333", font=("Helvetica", 10))
        self.style.configure("TButton", background="#e6f7ff", foreground="#333333", font=("Helvetica", 10, "bold"))
        self.style.configure("TEntry", fieldbackground="#ffffff", foreground="#333333", font=("Helvetica", 10))
        self.style.configure("Treeview", font=("Helvetica", 10))

        # Divide the window into two panels: controls (top) and viewer (bottom)
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))

        self.viewer_frame = ttk.Frame(self.main_frame)
        self.viewer_frame.pack(fill=tk.BOTH, expand=True)

        # --- Top panel controls ---
        ttk.Label(
            self.control_frame,
            text="Reddit Configuration",
            font=("Helvetica", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        ttk.Label(self.control_frame, text="Client ID:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.client_id_entry = ttk.Entry(self.control_frame, width=50)
        self.client_id_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self.control_frame, text="Client Secret:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.client_secret_entry = ttk.Entry(self.control_frame, width=50, show="*")
        self.client_secret_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self.control_frame, text="User Agent:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.user_agent_entry = ttk.Entry(self.control_frame, width=50)
        self.user_agent_entry.grid(row=3, column=1, padx=5, pady=2)

        self.save_button = ttk.Button(
            self.control_frame,
            text="Save Credentials",
            command=self.save_credentials_ui
        )
        self.save_button.grid(row=1, column=2, rowspan=3, padx=5, pady=2)

        # Load existing credentials (if any)
        creds = load_credentials()
        self.client_id_entry.insert(0, creds.get("client_id", ""))
        self.client_secret_entry.insert(0, creds.get("client_secret", ""))
        self.user_agent_entry.insert(0, creds.get("user_agent", ""))

        # Extraction parameters
        ttk.Label(
            self.control_frame,
            text="Extraction Parameters",
            font=("Helvetica", 10, "bold")
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        ttk.Label(self.control_frame, text="Number of Posts:").grid(
            row=5, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.limit_entry = ttk.Entry(self.control_frame, width=10)
        self.limit_entry.insert(0, "100")
        self.limit_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        # CSV file configuration
        ttk.Label(
            self.control_frame,
            text="CSV File Path:",
            font=("Helvetica", 10, "bold")
        ).grid(row=6, column=0, sticky=tk.W, padx=5, pady=(10, 2))
        self.csv_path_entry = ttk.Entry(self.control_frame, width=50)
        self.csv_path_entry.insert(0, "RedditPosts.csv")
        self.csv_path_entry.grid(row=6, column=1, padx=5, pady=(10, 2))

        self.browse_button = ttk.Button(
            self.control_frame,
            text="Browse...",
            command=self.browse_csv_path
        )
        self.browse_button.grid(row=6, column=2, padx=5, pady=(10, 2))

        # Action buttons
        self.run_button = ttk.Button(
            self.control_frame,
            text="Run Extraction",
            command=self.run_extraction
        )
        self.run_button.grid(row=7, column=0, columnspan=3, pady=(10, 2))

        self.view_button = ttk.Button(
            self.control_frame,
            text="View CSV",
            command=self.open_csv_viewer
        )
        self.view_button.grid(row=8, column=0, columnspan=3, pady=(2, 2))

        self.graph_button = ttk.Button(
            self.control_frame,
            text="Show Graphs",
            command=self.show_graphs
        )
        self.graph_button.grid(row=9, column=0, columnspan=3, pady=(2, 2))

        # Status label in the control panel
        self.status_var = tk.StringVar()
        status_label = ttk.Label(self.control_frame, textvariable=self.status_var)
        status_label.grid(row=10, column=0, columnspan=3, sticky="w", padx=5, pady=(10, 0))

    def save_credentials_ui(self):
        credentials = {
            "client_id": self.client_id_entry.get().strip(),
            "client_secret": self.client_secret_entry.get().strip(),
            "user_agent": self.user_agent_entry.get().strip()
        }
        save_credentials(credentials)
        messagebox.showinfo("Information", "Credentials saved successfully.")

    def browse_csv_path(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV File"
        )
        if file_path:
            self.csv_path_entry.delete(0, tk.END)
            self.csv_path_entry.insert(0, file_path)

    def run_extraction(self):
        try:
            limit = int(self.limit_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for the limit.")
            return

        client_id = self.client_id_entry.get().strip()
        client_secret = self.client_secret_entry.get().strip()
        user_agent = self.user_agent_entry.get().strip()

        if not client_id or not client_secret or not user_agent:
            messagebox.showerror("Error", "Please complete the Reddit configuration.")
            return

        csv_path = self.csv_path_entry.get().strip()
        if not csv_path:
            messagebox.showerror("Error", "Please provide a valid CSV file path.")
            return

        self.run_button.config(state=tk.DISABLED)
        self.status_message("Extracting posts from Reddit...")
        self.master.update_idletasks()

        try:
            posts = get_reddit_posts(limit, client_id, client_secret, user_agent)
        except Exception as e:
            messagebox.showerror("Error", f"Error extracting posts: {e}")
            self.run_button.config(state=tk.NORMAL)
            return

        self.status_message(f"{len(posts)} posts extracted. Exporting to CSV...")
        self.master.update_idletasks()
        try:
            result = export_to_csv(posts, csv_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to CSV: {e}")
            self.run_button.config(state=tk.NORMAL)
            return

        self.status_message(result)
        messagebox.showinfo("Information", result)
        self.run_button.config(state=tk.NORMAL)

    def status_message(self, message):
        self.status_var.set(message)

    def open_csv_viewer(self):
        csv_path = self.csv_path_entry.get().strip()
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "CSV file does not exist. Please run extraction first.")
            return

        # Clear the viewer panel
        for widget in self.viewer_frame.winfo_children():
            widget.destroy()

        # Create the frame for filters and table in the same panel
        filter_frame = ttk.Frame(self.viewer_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=(0, 5))
        field_options = ["Title", "URL", "Author", "Date"]
        self.filter_field_var = tk.StringVar()
        # Use SafeCombobox to ensure a valid return value
        self.filter_field = SafeCombobox(
            filter_frame,
            textvariable=self.filter_field_var,
            values=field_options,
            state="readonly"
        )
        self.filter_field.current(0)
        self.filter_field_var.set(field_options[0])
        self.filter_field.pack(side=tk.LEFT, padx=(0, 5))

        filter_entry = ttk.Entry(filter_frame)
        filter_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        filter_button = ttk.Button(filter_frame, text="Apply Filter")
        filter_button.pack(side=tk.LEFT)

        # Treeview to display data
        columns = ("Title", "URL", "Author", "Date")
        tree = ttk.Treeview(self.viewer_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        def load_data(filter_field_value="", filter_text=""):
            # Use SafeCombobox to get a valid field name
            selected_field = self.filter_field.get()
            if not isinstance(selected_field, str) or not selected_field.strip() or selected_field.lower() == "_notset":
                selected_field = "Title"

            for row in tree.get_children():
                tree.delete(row)
            try:
                data = load_csv_data(csv_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading CSV: {e}")
                return
            data = sorted(data, key=lambda x: x['Title'])
            if filter_text:
                text_filter = filter_text.strip().lower()
                data = [
                    row for row in data
                    if text_filter in str(row.get(selected_field, "")).strip().lower()
                ]
            for row in data:
                tree.insert("", tk.END, values=(row['Title'], row['URL'], row['Author'], row['Date']))
            adjust_columns(tree, data, columns)

        load_data(self.filter_field.get(), "")
        filter_button.config(
            command=lambda: load_data(self.filter_field.get(), filter_entry.get().strip())
        )
        filter_entry.bind(
            "<Return>",
            lambda event: load_data(self.filter_field.get(), filter_entry.get().strip())
        )

        def on_double_click(event):
            item = tree.identify_row(event.y)
            if item:
                values = tree.item(item, "values")
                if len(values) >= 2:
                    webbrowser.open(values[1])
        tree.bind("<Double-1>", on_double_click)

    def show_graphs(self):
        csv_path = self.csv_path_entry.get().strip()
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "CSV file does not exist. Please run extraction first.")
            return
        try:
            plot_post_frequency(csv_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating graph: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RedditTrackerApp(root)
    root.mainloop()
