import os
import tkinter as tk
from tkinter import messagebox, filedialog
from ftplib import FTP

ftp = None

def login():
    global ftp
    host = host_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    try:
        ftp = FTP(host)
        ftp.login(username, password)
        update_file_list()
        login_frame.pack_forget()
        main_frame.pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_file_list():
    files_listbox.delete(0, tk.END)
    files = ftp.nlst()
    files.sort()
    for file in files:
        files_listbox.insert(tk.END, file)

def download_selected():
    selection = files_listbox.curselection()
    if not selection:
        messagebox.showinfo("Info", "Please select a file or directory to download.")
        return
    selected_item = files_listbox.get(selection)
    if "." in selected_item:  # If it's a file
        download_file(selected_item)
    else:  # If it's a directory
        download_directory(selected_item)

def download_file(filename):
    confirm = messagebox.askyesno("Confirm", f"Do you want to download {filename}?")
    if confirm:
        try:
            with open(filename, 'wb') as file:
                ftp.retrbinary('RETR ' + filename, file.write)
            messagebox.showinfo("Success", f"File '{filename}' downloaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def download_directory(dirname):
    local_path = filedialog.askdirectory(title="Select Directory to Save")
    if not local_path:
        return
    try:
        os.makedirs(os.path.join(local_path, dirname), exist_ok=True)
        ftp.cwd(dirname)
        files = ftp.nlst()
        for file in files:
            if "." in file:  # If it's a file
                with open(os.path.join(local_path, dirname, file), 'wb') as local_file:
                    ftp.retrbinary('RETR ' + file, local_file.write)
            else:  # If it's a directory
                download_directory_recursive(os.path.join(local_path, dirname), file)
        ftp.cwd('..')  # Return to parent directory
        messagebox.showinfo("Success", f"Directory '{dirname}' downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def download_directory_recursive(local_path, dirname):
    try:
        os.makedirs(os.path.join(local_path, dirname), exist_ok=True)
        ftp.cwd(dirname)
        files = ftp.nlst()
        for file in files:
            if "." in file:  # If it's a file
                with open(os.path.join(local_path, dirname, file), 'wb') as local_file:
                    ftp.retrbinary('RETR ' + file, local_file.write)
            else:  # If it's a directory
                download_directory_recursive(os.path.join(local_path, dirname), file)
        ftp.cwd('..')  # Return to parent directory
    except Exception as e:
        messagebox.showerror("Error", str(e))

def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                ftp.storbinary('STOR ' + filename, file)
            messagebox.showinfo("Success", f"File '{filename}' uploaded successfully.")
            update_file_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def upload_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        try:
            dirname = os.path.basename(directory_path)
            ftp.mkd(dirname)
            ftp.cwd(dirname)
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    with open(local_file_path, 'rb') as local_file:
                        ftp.storbinary('STOR ' + file, local_file)
                for directory in dirs:
                    ftp.mkd(directory)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        ftp.cwd('..')
        messagebox.showinfo("Success", f"Directory '{dirname}' uploaded successfully.")
        update_file_list()

# Create main window
root = tk.Tk()
root.title("FTP Client")

# Create login frame
login_frame = tk.Frame(root)
login_frame.pack(padx=20, pady=20)

tk.Label(login_frame, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
host_entry = tk.Entry(login_frame)
host_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(login_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
username_entry = tk.Entry(login_frame)
username_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(login_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=2, column=1, padx=5, pady=5)

login_button = tk.Button(login_frame, text="Login", command=login)
login_button.grid(row=3, columnspan=2, pady=10)

# Create main frame
main_frame = tk.Frame(root)

files_listbox = tk.Listbox(main_frame, width=50, height=20)
files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

files_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=files_listbox.yview)

download_button = tk.Button(main_frame, text="Download", command=download_selected)
download_button.pack(pady=10)

upload_file_button = tk.Button(main_frame, text="Upload File", command=upload_file)
upload_file_button.pack(pady=5)

upload_dir_button = tk.Button(main_frame, text="Upload Directory", command=upload_directory)
upload_dir_button.pack(pady=5)

# Start the GUI
root.mainloop()