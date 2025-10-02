import os
import tempfile
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageSequence, ImageTk
from tkinter import filedialog
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg.exe"

VERSION = "0.1.0"

# === SPLASH SCREEN ===
def launch_splash(on_submit):
    splash = tk.Tk()
    splash.title("MPO to GIF")
    splash.geometry("500x400")
    splash.configure(bg=colors["bg_main"])
    #splash.iconbitmap("MPOtoGIFicon.ico")  # ← Use your candy-blue star icon here

    # Title
    title = tk.Label(splash, text="MPO to GIF", font=("Segoe UI", 20, "bold"), bg=colors["bg_main"], fg=colors["fg_title"])
    title.pack(pady=(30, 0))

    version_text = tk.Label(splash, text=f"v{VERSION}", font=("Segoe UI", 10), bg=colors["bg_main"], fg=colors["fg_label"])
    version_text.pack(pady=(0, 5))

    subtitle = tk.Label(splash, text="by Marcus Rinzsch and some AI", font=("Segoe UI", 12), bg=colors["bg_main"], fg=colors["fg_label"])
    subtitle.pack(pady=(0, 20))

    # MPO Location
    mpo_label = tk.Label(splash, text="MPO Location", font=("Segoe UI", 10, "bold"), bg=colors["bg_main"], fg=colors["fg_label"])
    mpo_label.pack(anchor="w", padx=40)
    mpo_entry = tk.Entry(splash, width=50, bg=colors["bg_entry"], fg=colors["fg_entry"])
    mpo_entry.pack(padx=40, pady=(0, 10))

    def browse_mpo():
        folder = filedialog.askdirectory()
        if folder:
            mpo_entry.delete(0, tk.END)
            mpo_entry.insert(0, folder)

    ttk.Button(splash, text="Browse", command=browse_mpo).pack(padx=40, pady=(0, 10))

    # GIF Output Location
    gif_label = tk.Label(splash, text="GIF Output Location", font=("Segoe UI", 10, "bold"), bg=colors["bg_main"], fg=colors["fg_label"])
    gif_label.pack(anchor="w", padx=40)
    gif_entry = tk.Entry(splash, width=50, bg=colors["bg_entry"], fg=colors["fg_entry"])
    gif_entry.pack(padx=40, pady=(0, 10))

    def browse_gif():
        folder = filedialog.askdirectory()
        if folder:
            gif_entry.delete(0, tk.END)
            gif_entry.insert(0, folder)

    ttk.Button(splash, text="Browse", command=browse_gif).pack(padx=40, pady=(0, 20))

    # Submit Button
    def submit():
        input_folder = mpo_entry.get()
        output_folder = gif_entry.get()
        splash.destroy()
        on_submit(input_folder, output_folder)

    ttk.Button(splash, text="Start", command=submit).pack(pady=10)
    
    splash.mainloop()

def start_main_app(input_path, output_path):
    global input_folder, output_folder, mpo_files, window, canvas, image_container, status_label, skip_entry


    input_folder = input_path
    output_folder = output_path

    mpo_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(".mpo")])
    current_index = 0

    # === GUI SETUP ===
    window = tk.Tk()
    window.title("3DS MPO Batch Editor")
    window.geometry("640x900")  # Default window size
    default_font = ("Segoe UI", 10)
    window.option_add("*Font", default_font)
    window.configure(bg=colors["bg_main"])  # black
    #window.iconbitmap("MPOtoGIFicon.ico")
    
    canvas = tk.Canvas(window, bg=colors["bg_main"], highlightthickness=0)
    canvas.pack()

    def handle_key(event):
        key = event.keysym.lower()
        if key == "s":
            skip_current()
        elif key == "e":
            export_current()
        elif key.startswith("kp_") or key.isdigit():
            skip_entry.focus_set()

    window.bind("<Key>", handle_key)

    # === APPLY COLORS TO WINDOW AND WIDGETS ===
    window.configure(bg=colors["bg_main"])
    canvas.configure(bg=colors["bg_canvas"], highlightthickness=0)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TLabel", background=colors["bg_controls"], foreground=colors["fg_label"])
    style.configure("TButton", background=colors["bg_button"], foreground=colors["fg_button"])
    style.configure("TEntry", fieldbackground=colors["bg_entry"], foreground=colors["fg_button"])

    # === SLIDER CREATOR FUNCTION ===
    slider_grid = {"row": 0}
    slider_widgets = {}

    def create_slider(label_text, from_, to, command, initial, side_key=None):
        row = slider_grid["row"]
        col = slider_grid["col"]

        frame = tk.Frame(grid_frame, bg=colors["bg_controls"])
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")

        # Title above slider
        title = ttk.Label(frame, text=label_text)
        title.configure(background=colors["bg_controls"], foreground=colors["fg_label"])
        title.pack(anchor="w")

        # Horizontal container for live value + slider
        slider_row = tk.Frame(frame, bg=colors["bg_controls"])
        slider_row.pack()

        # Live value label to the left of slider
        value_label = ttk.Label(slider_row, text=str(initial), width=5)
        value_label.configure(background=colors["bg_controls"], foreground=colors["fg_value"])
        value_label.pack(side="left")

        # Slider
        scale = tk.Scale(
            slider_row,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            length=250,
            sliderlength=10,
            width=8,
            highlightthickness=0,
            showvalue=False,
            troughcolor=colors["bg_slider"],
            bg=colors["bg_controls"],
            fg=colors["fg_value"],
            activebackground=colors["bg_slider_knob"],
            highlightbackground=colors["bg_controls"],
            command=lambda val: (
                value_label.config(text=str(int(float(val)))),
                command(side_key, val) if side_key else command(val)
            )
        )
        scale.set(initial)
        scale.pack(side="left")

        slider_widgets[label_text] = scale

        if slider_grid["col"] == 0:
            slider_grid["col"] = 1
        else:
            slider_grid["col"] = 0
            slider_grid["row"] += 1

    image_container = canvas.create_image(0, 0, anchor=tk.NW)

    status_label = ttk.Label(window, text="Ready")
    status_label.configure(background=colors["bg_main"], foreground=colors["fg_title"])
    status_label.pack(pady=5)

    controls = tk.Frame(window, bg=colors["bg_controls"])
    controls.pack(pady=5)
    grid_frame = tk.Frame(controls, bg=colors["bg_controls"])
    grid_frame.pack()
    slider_grid = {"row": 0, "col": 0}

    # === SLIDERS ===
    create_slider("Overlap", -100, 100, update_overlap, overlap)
    create_slider("Crop Left", 0, 200, update_crop, crop["l"], "l")
    create_slider("Crop Top", 0, 200, update_crop, crop["t"], "t")
    create_slider("Crop Right", 0, 200, update_crop, crop["r"], "r")
    create_slider("Crop Bottom", 0, 200, update_crop, crop["b"], "b")
    create_slider("Frame Duration (ms)", 50, 1000, update_duration, frame_duration)

    # === BUTTONS ===
    def add_button(text, command):
        row = slider_grid["row"]
        col = slider_grid["col"]

        if text == "Exit":
            btn = ttk.Button(grid_frame, text=text, command=command)
        else:
            btn = ttk.Button(grid_frame, text=text, command=command)
        
        btn.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

        if slider_grid["col"] == 0:
            slider_grid["col"] = 1
        else:
            slider_grid["col"] = 0
            slider_grid["row"] += 1

    def reset_defaults():
        global overlap, frame_duration, crop, preview_interval
        overlap = 0
        frame_duration = 175
        preview_interval = frame_duration / 1000.0
        crop = {"l": 0, "t": 0, "r": 0, "b": 0}

        # Reset sliders visually
        slider_widgets["Overlap"].set(overlap)
        slider_widgets["Crop Left"].set(crop["l"])
        slider_widgets["Crop Top"].set(crop["t"])
        slider_widgets["Crop Right"].set(crop["r"])
        slider_widgets["Crop Bottom"].set(crop["b"])
        slider_widgets["Frame Duration (ms)"].set(frame_duration)

    add_button("Export", export_current)
    add_button("Skip", skip_current)

    skip_label = ttk.Label(grid_frame, text="Skip X Files")
    skip_label.configure(background=colors["bg_controls"], foreground=colors["fg_label"])
    skip_label.grid(row=slider_grid["row"], column=slider_grid["col"], padx=10, pady=5, sticky="w")

    slider_grid["col"] = 1
    skip_entry = ttk.Entry(grid_frame, width=10)
    skip_entry.grid(row=slider_grid["row"], column=slider_grid["col"], padx=10, pady=5, sticky="w")

    slider_grid["row"] += 1
    slider_grid["col"] = 0
    add_button("Go", skip_ahead)
    add_button("Exit", exit_script)
    add_button("Reset", reset_defaults)

    pass

    load_file(current_index)
    update_preview()
    window.mainloop()

# === GLOBAL STATE ===
overlap = 0
frame_duration = 175
preview_interval = 0.05
crop = {"l": 0, "t": 0, "r": 0, "b": 0}
toggle = True
left_img = None
right_img = None
window = None
canvas = None
image_container = None
photo = None
base_filename = ""

# === COLOR PALETTE ===
colors = {
    # Backgrounds
    "bg_main": "#e8e6df",        # light beige for overall background
    "bg_canvas": "#f4f2ec",      # slightly lighter beige for image area
    "bg_controls": "#d0d8d8",    # soft teal for control panel
    "bg_slider": "#a0bfcf",      # dull teal for slider trough
    "bg_slider_knob": "#7fc7ff", # candy blue for slider knob
    "bg_button": "#c0c0c0",      # silver for buttons
    "bg_entry": "#d8e6f0",       # pale blue for entry fields
    "bg_box": "#b0b0b0",         # medium silver for bounding box

    "star_blue": "#7fc7ff",

    # Fonts
    "fg_title": "#1e1e1e",       # black for file renaming title
    "fg_label": "#2c2c2c",       # dark grey for slider titles
    "fg_value": "#003366",       # deep blue for live value display
    "fg_button": "#1e1e1e",      # black for button text
    "fg_entry": "#003366",
    "fg_box": "#ffffff",         # white for bounding box text (if any)
}

# === IMAGE PROCESSING ===
def process_images(mpo_path, overlap):
    mpo = Image.open(mpo_path)
    frames = [frame.copy() for frame in ImageSequence.Iterator(mpo)]
    if len(frames) < 2:
        raise ValueError("MPO file must contain at least two frames.")

    width, height = frames[0].size
    left_start = -overlap
    right_start = overlap

    left_box = (left_start, 0, width + left_start, height)
    right_box = (right_start, 0, width + right_start, height)

    left_image = frames[0].crop(left_box)
    right_image = frames[1].crop(right_box)

    crop_l, crop_t, crop_r, crop_b = crop["l"], crop["t"], crop["r"], crop["b"]
    new_width = left_image.width - crop_l - crop_r
    new_height = left_image.height - crop_t - crop_b

    left_image = left_image.crop((crop_l, crop_t, crop_l + new_width, crop_t + new_height))
    right_image = right_image.crop((crop_l, crop_t, crop_l + new_width, crop_t + new_height))

    return left_image, right_image

# === GIF CREATION ===
def create_gif(images, output_path, duration):
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0
    )
    print(f"🎞️ GIF saved to: {output_path}")

# === MP4 CREATION ===
def create_mp4(images, output_path, duration):
    try:
        fps = round(1000 / duration)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_paths = []
            for i, img in enumerate(images):
                temp_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
                img.save(temp_path)
                temp_paths.append(temp_path)

            clip = ImageSequenceClip(temp_paths, fps=fps)
            clip.write_videofile(
                output_path,
                codec="libx264",
                audio=False,
                preset="medium",
                ffmpeg_params=["-movflags", "faststart"]
            )
            clip.close()


        print(f"🎥 MP4 saved to: {output_path}")
    except Exception as e:
        print(f"❌ MP4 export failed: {e}")

# === PREVIEW UPDATE ===
def update_preview():
    global toggle, photo
    img = left_img if toggle else right_img
    photo = ImageTk.PhotoImage(img)
    canvas.image = photo
    canvas.itemconfig(image_container, image=photo)
    toggle = not toggle
    window.after(int(preview_interval * 1000), update_preview)

# === LOAD NEXT FILE ===
def load_file(index):
    global left_img, right_img, canvas, image_container, photo, base_filename, current_index, toggle

    if index >= len(mpo_files):
        print("✅ All files processed.")
        window.destroy()
        return

    current_index = index
    toggle = True
    mpo_path = os.path.join(input_folder, mpo_files[index])
    base_filename = os.path.splitext(mpo_files[index])[0]  # ← use original filename

    left_img, right_img = process_images(mpo_path, overlap)
    canvas.config(width=left_img.width, height=left_img.height)
    photo = ImageTk.PhotoImage(left_img)
    canvas.image = photo
    canvas.itemconfig(image_container, image=photo)
    status_label.config(text=f"Editing {mpo_files[index]}")

# === CONTROL ACTIONS ===
def update_overlap(val):
    global overlap, left_img, right_img
    overlap = int(val)
    left_img, right_img = process_images(os.path.join(input_folder, mpo_files[current_index]), overlap)

def update_crop(side, val):
    global crop, left_img, right_img
    crop[side] = int(val)
    left_img, right_img = process_images(os.path.join(input_folder, mpo_files[current_index]), overlap)

def update_duration(val):
    global frame_duration, preview_interval
    frame_duration = int(val)
    preview_interval = frame_duration / 1000.0

def export_current():
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    left_img.save(os.path.join(output_folder, f"{base_filename}_left.jpg"))
    right_img.save(os.path.join(output_folder, f"{base_filename}_right.jpg"))
    
    gif_path = os.path.join(output_folder, f"{base_filename}.gif")
    create_gif([left_img, right_img], gif_path, frame_duration)
    
    mp4_path = os.path.join(output_folder, f"{base_filename}.mp4")
    create_mp4([left_img, right_img], mp4_path, frame_duration)
    
    print(f"✅ Exported {base_filename}")
    load_file(current_index + 1)

def skip_current():
    print("⏭️ Skipped current file.")
    load_file(current_index + 1)

def skip_ahead():
    try:
        x = int(skip_entry.get())
    except ValueError:
        print("⚠️ Invalid skip value.")
        return

    remaining = len(mpo_files) - current_index - 1
    if x > remaining:
        print(f"❌ Cannot skip {x} files — only {remaining} remain.")
    else:
        print(f"⏭️ Skipping ahead {x} files...")
        load_file(current_index + x)

def exit_script():
    global window
    print("🛑 Exiting script.")
    if window:
        window.destroy()

def jump_to_click(event, scale):
    value = scale.cget("from") + (scale.cget("to") - scale.cget("from")) * event.x / scale.winfo_width()
    scale.set(int(value))


# === START ===
def main():
    launch_splash(start_main_app)


if __name__ == "__main__":
    main()
