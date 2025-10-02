# MPO to GIF

This script is to allow batch editing of all your amazing Nintendo 3DS images.
The Nintendo 3DS outputs two files per image (when seen on the PC), a .JPG and .MPO. I had no idea what an MPO was but I really wanted a gif showing both images (left and right camera) at the same time!
Honourable mention that fully inspired me to work on this editor is: [MPO-to-JPEG-Stereo](https://donatstudios.com/MPO-to-JPEG-Stereo)
Cheers to Jesse Donat in 2011 for solving this issue for us! However, I got picky. His editor only creates stereoscopic images or anaglyphs, no gifs... it also is slow since it only edits one image at a time.

This editor will take your MPO files, decompose them into a stereoscopic image, tear that in two, produce two images. The left and right image are now saved locally and displayed in a pop-up window. Each image is shown for 50 miliseconds before switching to the next image.
The editor will accept a list of commands (shown below) to allow YOU to edit YOUR images to your heart's content. Now you just have to specify input paths (where your MPO images are) and output paths (where the GIF and JPGs should go) and spend some time fiddling around till it looks sick as fuck!

Full disclosure this is my first time working with python. I am a MATLAB enthusiast and can make really good calculators. I have no idea what I am doing with python or image processing. This is your invitation to work on this code and make it actually good. The idea is there it just isnt efficient.
Sometimes it will crash... I know that sucks... But that's why I have the skip function. I am trying to fix the crashing but just note that when it does crash the symptoms are:

- The terminal does not accept any more commands.
- closing the pop-up opens a new pop-up with the next image and then immediately closes and stops the script.
- The image where it crashed on will NOT export your edited GIF entirely. It creates a corrupt file (but don't worry your .MPO is still in tact!)

## Installation

Windows builds can be downloaded from the [releases page](https://github.com/MarcusRinzsch/Nintendo-3DS-MPO-to-GIF/releases).

MPO to GIF can also be installed with pip of run directly as a script.

### Using pip

```shell
# Clone the repository
git clone https://github.com/MarcusRinzsch/Nintendo-3DS-MPO-to-GIF.git
cd Nintendo-3DS-MPO-to-GIF

# Install mpo-to-git and it's dependencies
pip install .

# mpo-to-git is now available on the command line
mpo-to-gif
```

### Running directly

```shell
# Clone the repository
git clone https://github.com/MarcusRinzsch/Nintendo-3DS-MPO-to-GIF.git
cd Nintendo-3DS-MPO-to-GIF

# Install the requirements
pip install -r requirements.txt

# Run the script with python
# Use 'python3' for linux
python mpo_to_gif.py
```

## Usage

The editor requires a file path for input and output destinations.
From your terminal in VS Code you can modify various parameters of the gif.

- command "o" followed by a number will modify the overlap value of the two (left and right) images. ex: o45
- command "c" followed by a modifier "l", "t", "r", "b" (for left, top, right, bottom) and a number will crop the gif by the value. example showing 45 pixel crop from the right: c r45
- command "s" skips to next image
- command "e" exports whatever gif is being previewed
- command "exit" exits the script.
- command "f" followed by a value will edit the time either image is shown. ex: f50 will change the default time per image of 175 ms to 50 ms

When exporting it will export the left, right images and the GIF created. Have fun and play with the overlap value to change the focal point of your flickering gif!
