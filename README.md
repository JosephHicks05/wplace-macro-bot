## wplace-macro-bot
Pixel art creator and macro creator/runner made using the Tkinter Python library. This program is intended for use creating drawings on the wplace.live website. At a high level, the job of this program is to create 2D pixel art using a graphical interface, then execute a series of inputs that automatically draws that pixel art creation on wplace.live.

# to use
Run window.py to open. Enter your preferred drawing dimensions, then either select an image from your computer
as a base or start a blank drawing. Note that selecting an image will automatically result in the resizing of said image to your specified dimensions and recoloring of said image into the 31 colors available on wplace by default, though the rest of the 63 total colors can be added by opening the drawing.py file and un-commenting the lines of code adding the purchasable colors.

## drawing creation menu instructions
Use the row of buttons at the top to select a color. Left-click and drag on the grid squares to color those squares
the selected color.
Right-click and drag to erase those squares (dark blue represents a background square and will not be colored in when the drawing's macro is run.)
Middle-click while hovering over a square to select its color.
Once your drawing is done, enter a name in the text field and click save drawing. It can then be loaded later from the "view saved drawings" screen.

## executing the macro
To execute a drawing's macro, start by loading into wplace.live and zooming in as far as possible. Then, hit the "-" zoom button once to zoom out a bit. Then align the pixel grid on the website such that there is one pixel whose left side runs along the left side of your screen, and whose top side runs along the bottom of your browser's bookmarks bar/search bar. In other words, one pixel should be "as top left" as it can get while still seeing the whole thing. Then open the paint menu and enter the "view saved drawings" screen of the app. From there, enter your current number of available paint charges and click the "run macro" button for the drawing that you would like to be drawn. Space can be pressed and held at any time to cancel the macro.

## creating your own macros
Running macro.py will launch a CLI that allows you to record and playback your own macros that support only mouse movement and clicking at a specified polling rate. Available commands are displayed when launched.

