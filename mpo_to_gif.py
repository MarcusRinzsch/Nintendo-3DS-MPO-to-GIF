import os
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk
from typing import Callable
from PIL import Image, ImageSequence, ImageTk
from tkinter import filedialog
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg.exe"

VERSION = "0.1.0"
COLORS = {
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


# === SPLASH SCREEN ===
def launch_splash() -> tuple[Path, Path] | None:
    splash = tk.Tk()
    splash.title("MPO to GIF")
    splash.geometry("500x400")
    splash.configure(bg=COLORS["bg_main"])
    #splash.iconbitmap("MPOtoGIFicon.ico")  # ← Use your candy-blue star icon here

    # Title
    title = tk.Label(splash, text="MPO to GIF", font=("Segoe UI", 20, "bold"), bg=COLORS["bg_main"], fg=COLORS["fg_title"])
    title.pack(pady=(30, 0))

    version_text = tk.Label(splash, text=f"v{VERSION}", font=("Segoe UI", 10), bg=COLORS["bg_main"], fg=COLORS["fg_label"])
    version_text.pack(pady=(0, 5))

    subtitle = tk.Label(splash, text="by Marcus Rinzsch and some AI", font=("Segoe UI", 12), bg=COLORS["bg_main"], fg=COLORS["fg_label"])
    subtitle.pack(pady=(0, 20))

    # MPO Location
    mpo_label = tk.Label(splash, text="MPO Location", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_main"], fg=COLORS["fg_label"])
    mpo_label.pack(anchor="w", padx=40)
    mpo_entry = tk.Entry(splash, width=50, bg=COLORS["bg_entry"], fg=COLORS["fg_entry"])
    mpo_entry.pack(padx=40, pady=(0, 10))

    def browse_mpo():
        folder = filedialog.askdirectory()
        if folder:
            mpo_entry.delete(0, tk.END)
            mpo_entry.insert(0, folder)

    ttk.Button(splash, text="Browse", command=browse_mpo).pack(padx=40, pady=(0, 10))

    # GIF Output Location
    gif_label = tk.Label(splash, text="GIF Output Location", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_main"], fg=COLORS["fg_label"])
    gif_label.pack(anchor="w", padx=40)
    gif_entry = tk.Entry(splash, width=50, bg=COLORS["bg_entry"], fg=COLORS["fg_entry"])
    gif_entry.pack(padx=40, pady=(0, 10))

    def browse_gif():
        folder = filedialog.askdirectory()
        if folder:
            gif_entry.delete(0, tk.END)
            gif_entry.insert(0, folder)

    ttk.Button(splash, text="Browse", command=browse_gif).pack(padx=40, pady=(0, 20))

    # Submit Button
    paths: list[Path] = []
    def submit():
        paths.append(Path(mpo_entry.get()))
        paths.append(Path(gif_entry.get()))
        splash.destroy()

    ttk.Button(splash, text="Start", command=submit).pack(pady=10)

    splash.mainloop()

    if len(paths) < 2:
        return None

    return paths[0], paths[1]


def create_slider(
    label_text: str,
    slider_range: tuple[float, float],
    grid_frame: tk.Frame,
    grid_coordinates: tuple[int, int],
    command: Callable[[int], None] | tuple[Callable[[str, int], None], str],
    initial: float
) -> tk.Scale:
    frame = tk.Frame(grid_frame, bg=COLORS["bg_controls"])
    frame.grid(row=grid_coordinates[0], column=grid_coordinates[1], padx=10, pady=5, sticky="w")

    # Title above slider
    title = ttk.Label(frame, text=label_text)
    title.configure(background=COLORS["bg_controls"], foreground=COLORS["fg_label"])
    title.pack(anchor="w")

    # Horizontal container for live value + slider
    slider_row = tk.Frame(frame, bg=COLORS["bg_controls"])
    slider_row.pack()

    # Live value label to the left of slider
    value_label = ttk.Label(slider_row, text=str(initial), width=5)
    value_label.configure(background=COLORS["bg_controls"], foreground=COLORS["fg_value"])
    value_label.pack(side="left")

    if isinstance(command, Callable):
        def slider_command(val: str) -> None:
            value = int(val)
            value_label.config(text=str(value))
            command(value)
    else:
        def slider_command(val: str) -> None:
            value = int(val)
            value_label.config(text=str(value))
            command[0](command[1], value)

    # Slider
    scale = tk.Scale(
        slider_row,
        from_=slider_range[0],
        to=slider_range[1],
        orient=tk.HORIZONTAL,
        length=250,
        sliderlength=10,
        width=8,
        highlightthickness=0,
        showvalue=False,
        troughcolor=COLORS["bg_slider"],
        bg=COLORS["bg_controls"],
        fg=COLORS["fg_value"],
        activebackground=COLORS["bg_slider_knob"],
        highlightbackground=COLORS["bg_controls"],
        command=slider_command
    )
    scale.set(initial)
    scale.pack(side="left")
    return scale


def create_button(
    text: str,
    command: Callable[[], None],
    grid_frame: tk.Frame,
    grid_coords: tuple[int, int],
) -> None:
    if text == "Exit":
        btn = ttk.Button(grid_frame, text=text, command=command)
    else:
        btn = ttk.Button(grid_frame, text=text, command=command)
    
    btn.grid(row=grid_coords[0], column=grid_coords[1], padx=10, pady=5, sticky="ew")


class App:
    def __init__(self, input_folder: Path, output_folder: Path) -> None:
        self._input_folder = input_folder
        self._output_folder = output_folder
        self._mpo_files = sorted([f for f in input_folder.iterdir() if f.suffix.lower() == ".mpo"])

        # === State tracking
        self._current_index = 0
        self._current_file_name = ""
        self._overlap = 0
        self._frame_duration = 175
        self._preview_interval = 0.05
        self._crop = {"l": 0, "t": 0, "r": 0, "b": 0}
        self._toggle = True
        self._left_img: Image.Image | None = None
        self._right_img: Image.Image | None = None
        self._photo = None

        # === GUI SETUP ===
        self._window = tk.Tk()
        self._window.title("3DS MPO Batch Editor")
        self._window.geometry("640x900")  # Default window size

        default_font = ("Segoe UI", 10)
        self._window.option_add("*Font", default_font)
        self._window.configure(bg=COLORS["bg_main"])  # black
        #window.iconbitmap("MPOtoGIFicon.ico")

        self._canvas = tk.Canvas(self._window, bg=COLORS["bg_main"], highlightthickness=0)
        self._canvas.pack()

        self._window.bind("<Key>", self._handle_key)
            
        # === APPLY COLORS TO WINDOW AND WIDGETS ===
        self._window.configure(bg=COLORS["bg_main"])
        self._canvas.configure(bg=COLORS["bg_canvas"], highlightthickness=0)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", background=COLORS["bg_controls"], foreground=COLORS["fg_label"])
        style.configure("TButton", background=COLORS["bg_button"], foreground=COLORS["fg_button"])
        style.configure("TEntry", fieldbackground=COLORS["bg_entry"], foreground=COLORS["fg_button"])

        self._image_container = self._canvas.create_image(0, 0, anchor=tk.NW)

        self._status_label = ttk.Label(self._window, text="Ready")
        self._status_label.configure(background=COLORS["bg_main"], foreground=COLORS["fg_title"])
        self._status_label.pack(pady=5)

        # === SLIDERS ===
        controls = tk.Frame(self._window, bg=COLORS["bg_controls"])
        controls.pack(pady=5)
        grid = tk.Frame(controls, bg=COLORS["bg_controls"])
        grid.pack()

        self._overlap_slider = create_slider(
            "Overlap",
            (-100, 100),
            grid,
            (0, 0),
            self._update_overlap,
            self._overlap
        )
        self._crop_left_slider = create_slider(
            "Crop Left",
            (0, 200),
            grid,
            (0, 1),
            (self._update_crop, "l"),
            self._crop["l"],
        )
        self._crop_top_slider = create_slider(
            "Crop Top",
            (0, 200),
            grid,
            (1, 0),
            (self._update_crop, "t"),
            self._crop["t"]
        )
        self._crop_right_slider = create_slider(
            "Crop Right",
            (0, 200),
            grid,
            (1, 1),
            (self._update_crop, "r"),
            self._crop["r"]
        )
        self._crop_bottom_slider = create_slider(
            "Crop Bottom",
            (0, 200),
            grid,
            (2, 0),
            (self._update_crop, "b"),
            self._crop["b"]
        )
        self._duration_slider = create_slider(
            "Frame Duration (ms)",
            (50, 1000),
            grid,
            (2, 1),
            self._update_duration,
            self._frame_duration,
        )

        # === BUTTONS ===
        self._export_button = create_button("Export", self._export_current, grid, (3, 0))
        self._export_button = create_button("Skip", self._skip_current, grid, (3, 1))

        skip_label = ttk.Label(grid, text="Skip X Files")
        skip_label.configure(background=COLORS["bg_controls"], foreground=COLORS["fg_label"])
        skip_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self._skip_entry = ttk.Entry(grid, width=10)
        self._skip_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self._go_button = create_button("Go", self._skip_ahead, grid, (5, 0))
        self._exit_button = create_button("Exit", self._exit_script, grid, (5, 1))
        self._reset_button = create_button("Reset", self._reset_defaults, grid, (6, 0))

    def run(self) -> None:
        if not self._load_file(self._current_index):
            return

        self._update_preview()
        print("Main pre main loop")
        self._window.mainloop()
        print("Main loop done")

    def _reset_defaults(self) -> None:
        self._overlap = 0
        self._frame_duration = 175
        self._preview_interval = self._frame_duration / 1000.0
        self._crop = {"l": 0, "t": 0, "r": 0, "b": 0}

        # Reset sliders visually
        self._overlap_slider.set(self._overlap)
        self._crop_left_slider.set(self._crop["l"])
        self._crop_top_slider.set(self._crop["t"])
        self._crop_right_slider.set(self._crop["r"])
        self._crop_bottom_slider.set(self._crop["b"])
        self._duration_slider.set(self._frame_duration)

    def _handle_key(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key == "s":
            self._skip_current()
        elif key == "e":
            self._export_current()
        elif key.startswith("kp_") or key.isdigit():
            self._skip_entry.focus_set()

    def _process_images(self) -> tuple[Image.Image, Image.Image]:
        mpo = Image.open(self._mpo_files[self._current_index])
        frames = [frame.copy() for frame in ImageSequence.Iterator(mpo)]
        if len(frames) < 2:
            raise ValueError("MPO file must contain at least two frames.")

        width, height = frames[0].size
        left_start = -self._overlap
        right_start = self._overlap

        left_box = (left_start, 0, width + left_start, height)
        right_box = (right_start, 0, width + right_start, height)

        left_image = frames[0].crop(left_box)
        right_image = frames[1].crop(right_box)

        crop_l, crop_t, crop_r, crop_b = self._crop["l"], self._crop["t"], self._crop["r"], self._crop["b"]
        new_width = left_image.width - crop_l - crop_r
        new_height = left_image.height - crop_t - crop_b

        left_image = left_image.crop((crop_l, crop_t, crop_l + new_width, crop_t + new_height))
        right_image = right_image.crop((crop_l, crop_t, crop_l + new_width, crop_t + new_height))

        return left_image, right_image

    def _update_preview(self) -> None:
        assert self._left_img is not None and self._right_img is not None

        img = self._left_img if self._toggle else self._right_img
        photo = ImageTk.PhotoImage(img)
        self._canvas.image = photo
        self._canvas.itemconfig(self._image_container, image=photo)
        self._toggle = not self._toggle
        self._window.after(int(self._preview_interval * 1000), self._update_preview)

    def _load_file(self, index: int) -> bool:
        if index >= len(self._mpo_files):
            print("✅ All files processed.")
            self._window.destroy()
            return False

        self._current_index = index
        self._toggle = True
        mpo_path = self._mpo_files[index]
        self._current_file_name = mpo_path.stem  # ← use original filename

        self._left_img, self._right_img = self._process_images()
        self._canvas.config(width=self._left_img.width, height=self._left_img.height)
        self._status_label.config(text=f"Editing {mpo_path.name}")

        return True

    # === CONTROL ACTIONS ===
    def _update_overlap(self, val: int) -> None:
        self._overlap = val
        self._left_img, self._right_img = self._process_images()

    def _update_crop(self, side: str, val: int) -> None:
        self._crop[side] = val
        self._left_img, self._right_img = self._process_images()

    def _update_duration(self, val: int) -> None:
        self._frame_duration = val
        self._preview_interval = self._frame_duration / 1000.0

    def _export_current(self) -> None:
        assert self._left_img is not None and self._right_img is not None

        self._output_folder.mkdir(exist_ok=True)

        self._left_img.save(self._output_folder / f"{self._current_file_name}_left.jpg")
        self._right_img.save(self._output_folder / f"{self._current_file_name}_right.jpg")

        gif_path = self._output_folder / f"{self._current_file_name}.gif"
        create_gif([self._left_img, self._right_img], gif_path, self._frame_duration)
        
        mp4_path = self._output_folder / f"{self._current_file_name}.mp4"
        create_mp4([self._left_img, self._right_img], mp4_path, self._frame_duration)
        
        print(f"✅ Exported {self._current_file_name}")
        self._load_file(self._current_index + 1)

    def _skip_current(self) -> None:
        print("⏭️ Skipped current file.")
        self._load_file(self._current_index + 1)

    def _skip_ahead(self) -> None:
        try:
            x = int(self._skip_entry.get())
        except ValueError:
            print("⚠️ Invalid skip value.")
            return

        remaining = len(self._mpo_files) - self._current_index - 1
        if x > remaining:
            print(f"❌ Cannot skip {x} files — only {remaining} remain.")
        else:
            print(f"⏭️ Skipping ahead {x} files...")
            self._load_file(self._current_index + x)

    def _exit_script(self) -> None:
        print("🛑 Exiting script.")
        if self._window:
            self._window.destroy()


# === GIF CREATION ===
def create_gif(images: list[Image.Image], output_path: Path, duration: float) -> None:
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0
    )
    print(f"🎞️ GIF saved to: {output_path}")


# === MP4 CREATION ===
def create_mp4(images: list[Image.Image], output_path: Path, duration: float) -> None:
    try:
        fps = round(1000 / duration)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_paths: list[str] = []
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


# === START ===
def main() -> None:
    paths = launch_splash()
    if paths is not None:
        App(paths[0], paths[1]).run()


if __name__ == "__main__":
    main()
