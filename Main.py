import os
import shutil
import uuid
import tkinter as tk
from plyer import notification
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import messagebox
import json
import re 

root = tk.Tk()

root.title("Productivity Toolkit") 
root.geometry("600x400")
main_menu = tk.Frame(root)
screenshot_vault_frame = tk.Frame(root)
focus_timer_frame = tk.Frame(root)
main_menu.pack(fill="both", expand=True)
time_left = 1500  #Time for the timer
timer_running = False #A way to stop a cumulative timer
current_mode = "focus"
timer_job = None
#vault loaders
vault_folder = "vault"
os.makedirs(vault_folder, exist_ok=True)

title_label = tk.Label(main_menu, text="⚒️Productivity Toolkit", font=("Helvetica", 18))
title_label.pack(pady=20)

# metadata stuff
metadata_file = "metadata.json"

# Load metadata from file or create an empty dictionary
if os.path.exists(metadata_file):
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
else:
    metadata = {}

# Pomodoro timer

def send_notification(title,message):
    notification.notify(
        title=title,
        message=message,
        timeout=5
    )

def focus_timer_clicked():
    main_menu.pack_forget()
    focus_timer_frame.pack(fill="both", expand=True)
    print("Focus timer clicked!")

def start_timer():
    global time_left, timer_running

    if not timer_running:
        try:
            minutes = int(custom_time_entry.get())
            time_left = minutes * 60
            timer_running = True
            countdown()
        except ValueError:
            timer_label.config(text="Invalid time")

def start_break():
    global time_left, timer_running, timer_job

    time_left = 5 * 60
    timer_running = True
    start_break_button.pack_forget() 
    countdown()

def start_focus():
    global time_left, timer_running, timer_job

    try:
        minutes = int(custom_time_entry.get())
        time_left = minutes * 60
        timer_running = True
        start_focus_button.pack_forget()
        countdown()
    except ValueError:
        timer_label.config(text="Invalid time")

def reset_timer():
   global time_left, timer_running, timer_job

   timer_running = False
   if timer_job is not None:
       root.after_cancel(timer_job)
       timer_job = None
   try:
        minutes = int(custom_time_entry.get())
        time_left = minutes * 60
        timer_label.config(text=f"{minutes:02d}:00")    
   except ValueError:
        timer_label.config(text="Invalid time")

def countdown():
    global time_left, timer_running, timer_job, current_mode
    if time_left > 0:
        minutes = time_left // 60
        seconds = time_left % 60
        timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        time_left -= 1
        timer_job = root.after(1000, countdown)

    else:
        timer_running = False

        if current_mode == "focus":
           current_mode = "break"
           timer_label.config(text="Break time! Press Start Break")
           send_notification("Focus session complete!", "Time for a break.")
           start_break_button.pack(pady=10)


        elif current_mode == "break":
            current_mode = "focus"
            timer_label.config(text="Break over! Ready to work?")
            send_notification("break over!", "Time to get back to work.")
            start_focus_button.pack(pady=10)

def go_back_to_menu(): 
    focus_timer_frame.pack_forget()
    screenshot_vault_frame.pack_forget()
    main_menu.pack(fill="both", expand=True)

# Screenshot vault

def show_screenshot_vault():
    main_menu.pack_forget()
    screenshot_vault_frame.pack(fill="both", expand=True)
    load_vault_gallery()

def upload_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
    )

    if file_path:
        ext = os.path.splitext(file_path)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(vault_folder, unique_name)
        shutil.copy(file_path, save_path)
        load_vault_gallery()  # Refresh the gallery after uploading

def load_vault_gallery():
    for widget in screenshot_vault_frame.winfo_children():
        widget.destroy()

    heading = tk.Label(screenshot_vault_frame, text="Screenshot Vault", font=("Helvetica", 16))
    heading.pack(pady=10)

    filter_label = tk.Label(screenshot_vault_frame, text="Filter by tag:")
    filter_label.pack()

    tag_filter_entry = tk.Entry(screenshot_vault_frame, width=30)
    tag_filter_entry.pack(pady=5)

    def apply_tag_filter():
        tag = tag_filter_entry.get().strip().lower()
        show_thumbnails(tag)

    filter_btn = tk.Button(screenshot_vault_frame, text="Apply Filter", command=apply_tag_filter)
    filter_btn.pack(pady=(0, 10))

    show_thumbnails()

def show_thumbnails(tag_filter=None):
    for filename in os.listdir(vault_folder):
        path = os.path.join(vault_folder, filename)

        # Check if file is an image
        if not os.path.isfile(path):
            continue

        # If filtering, check tags
        if tag_filter:
            info = metadata.get(filename, {})
            tags = info.get("tags", [])
            tags_lower = [t.lower() for t in tags]
            if tag_filter not in tags_lower:
                continue

        # Create thumbnail
        img = Image.open(path)
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)

        thumb_btn = tk.Button(
            screenshot_vault_frame,
            image=img_tk,
            command=lambda p=path: open_full_image(p)
        )
        thumb_btn.image = img_tk
        thumb_btn.pack(pady=5)

    # Upload button
    upload_button = tk.Button(screenshot_vault_frame, text="Upload New Image", command=upload_image)
    upload_button.pack(pady=10)

    # Back to menu
    back_btn = tk.Button(screenshot_vault_frame, text="← Back to Menu", command=go_back_to_menu)
    back_btn.pack(pady=10)

def open_full_image(image_path):
    for widget in screenshot_vault_frame.winfo_children():
        widget.destroy()

    img = Image.open(image_path)
    filename = os.path.basename(image_path)
    info = metadata.get(filename, {"title": "", "notes": ""})
    # Editable tags
    tags_label = tk.Label(screenshot_vault_frame, text="Tags (comma-separated):", font=("Helvetica", 12))
    tags_label.pack(pady=(10, 0))

    tags_entry = tk.Entry(screenshot_vault_frame, width=40)
    existing_tags = ", ".join(info.get("tags", []))
    tags_entry.insert(0, existing_tags)
    tags_entry.pack()

    img.thumbnail((500, 500))
    img_tk = ImageTk.PhotoImage(img)

    # Display image
    label = tk.Label(screenshot_vault_frame, image=img_tk)
    label.image = img_tk
    label.pack(pady=10)

    # Editable title
    title_label = tk.Label(screenshot_vault_frame, text="Title:", font=("Helvetica", 12))
    title_label.pack(pady=(10, 0))
    title_entry = tk.Entry(screenshot_vault_frame, width=40)
    title_entry.insert(0, info["title"])  # Pre-fill if already exists
    title_entry.pack()

    # Editable notes
    notes_label = tk.Label(screenshot_vault_frame, text="Notes:", font=("Helvetica", 12))
    notes_label.pack(pady=(10, 0))
    notes_box = tk.Text(screenshot_vault_frame, height=4, wrap="word")
    notes_box.insert("1.0", info["notes"])
    notes_box.pack(padx=20, pady=5, fill="both")

    # Saving information
    def save_info():
        tags_raw = tags_entry.get()
        tags_list = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

        metadata[filename] = {
            "title": title_entry.get(),
            "notes": notes_box.get("1.0", "end").strip(),
            "tags": tags_list 
            }
        
        save_metadata()
        messagebox.showinfo("Saved", "Image info saved successfully!")

    save_btn = tk.Button(screenshot_vault_frame, text="Save Info", command=save_info)
    save_btn.pack(pady=5)

    # Extract text with OCR
    extracted_text = pytesseract.image_to_string(img)

    # Display extracted text
    text_label = tk.Label(screenshot_vault_frame, text="Extracted Text:", font=("Helvetica", 12, "bold"))
    text_label.pack(pady=(10, 0))

    text_box = tk.Text(screenshot_vault_frame, height=10, wrap="word")
    text_box.insert("1.0", extracted_text.strip())
    text_box.config(state="disabled")  # Make the pasted text read only! "don't touch"
    text_box.pack(padx=20, pady=5, fill="both", expand=False)

    # Copy to clipboard button
    def copy_text():
        root.clipboard_clear()
        root.clipboard_append(extracted_text)
        root.update()

    copy_btn = tk.Button(screenshot_vault_frame, text="Copy Text", command=copy_text)
    copy_btn.pack(pady=5)

    # Delete Button
    def delete_image():
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this image?")
        if confirm:
            os.remove(image_path)
            load_vault_gallery()

    delete_btn = tk.Button(screenshot_vault_frame, text="🗑️ Delete Image", fg="red", command=delete_image)
    delete_btn.pack(pady=5)

    # Back Button
    back_btn = tk.Button(screenshot_vault_frame, text="← Back to Vault", command=load_vault_gallery)
    back_btn.pack(pady=10)

def save_metadata():
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

#Email Extractor 

def extract_email(text):
    #regex to find emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found_emails = re.findall(email_pattern, text)
    return list(set(found_emails))  # Remove duplicates

def show_email_extractor():
    main_menu.pack_forget()
    email_extractor_frame.pack(fill="both", expand=True)

def extract_from_input():
    raw_text = input_box.get("1.0", "end")
    emails = extract_email(raw_text)

    result_box.config(state="normal")  # Allow writing
    result_box.delete("1.0", "end")  # Clear previous
    if emails:
        result_box.insert("1.0", "\n".join(emails))
    else:
        result_box.insert("1.0", "No valid emails found.")
    result_box.config(state="disabled")  # Lock again

# Focus timer frame

focus_timer_btn = tk.Button(main_menu, text="Focus timer", command=focus_timer_clicked)
focus_timer_btn.pack(pady=5)

timer_label = tk.Label(focus_timer_frame, text="25:00", font=("Helvetica",36))
timer_label.pack(pady=20)

custom_time_entry = tk.Entry(focus_timer_frame, width=10,justify="center")
custom_time_entry.insert(0,25) #Default value
custom_time_entry.pack(pady=5)

start_button = tk.Button(focus_timer_frame, text="Start", command=start_timer)
start_button.pack(pady=10)

start_break_button = tk.Button(focus_timer_frame, text="Start Break", command=start_break)
start_break_button.pack_forget()

start_focus_button = tk.Button(focus_timer_frame, text="Start Focus", command=start_focus)
start_focus_button.pack_forget()

back_button = tk.Button(focus_timer_frame, text="← Back", command=go_back_to_menu)
back_button.pack()

reset_button = tk.Button(focus_timer_frame, text="Reset", command=reset_timer)
reset_button.pack(pady=5)

# Screenshot vault frame
screenshot_vault_btn = tk.Button(main_menu, text="Screenshot Vault", command=show_screenshot_vault)
screenshot_vault_btn.pack(pady=5)

uploaded_image_label = tk.Label(screenshot_vault_frame)
uploaded_image_label.pack(pady=10)

upload_button = tk.Button(screenshot_vault_frame, text="Upload Image", command=upload_image)
upload_button.pack(pady=5)

heading = tk.Label(screenshot_vault_frame, text="Screenshot Vault", font=("Helvetica", 16))
heading.pack(pady=10)

# Email extractor frames

email_extractor_frame = tk.Frame(root)
email_extractor_btn = tk.Button(main_menu, text="Email Extractor", command=lambda: show_email_extractor())
email_extractor_btn.pack(pady=5)

# Email Extractor UI
heading = tk.Label(email_extractor_frame, text="Email Extractor", font=("Helvetica", 16))
heading.pack(pady=10)

# Text area for input
input_box = tk.Text(email_extractor_frame, height=10, wrap="word")
input_box.pack(padx=20, pady=5, fill="both", expand=True)

# Extracted results
result_label = tk.Label(email_extractor_frame, text="Found Emails:", font=("Helvetica", 12, "bold"))
result_label.pack(pady=(10, 0))

result_box = tk.Text(email_extractor_frame, height=8, wrap="word", state="disabled")
result_box.pack(padx=20, pady=5, fill="both", expand=True)

# Back button
back_btn = tk.Button(email_extractor_frame, text="← Back to Menu", command=go_back_to_menu)
back_btn.pack(pady=10)

# Extraction button
extract_btn = tk.Button(email_extractor_frame, text="Extract Emails", command=extract_from_input)
extract_btn.pack(pady=5)

root.mainloop()