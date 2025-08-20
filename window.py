import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from math import floor
from files import *
from drawing import Drawing, Color, AVAILABLE_COLORS, BACKGROUND_PIXEL
from macro import execute_drawing_macro

WINDOW_WIDTH: int = 1300
WINDOW_HEIGHT: int = 750


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wplace Macro Bot")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.iconbitmap("images/wplace_logo.ico")

        self.current_drawing: Drawing = Drawing(0, 0)

        container: tk.Frame = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames: dict[type[tk.Frame], tk.Frame] = {}
        screen_classes: tuple[type[tk.Frame], ...] = (StartScreen, DrawingScreen,
                                                      CompletedDrawingsScreen)

        for ScreenClass in screen_classes:
            screen_frame = ScreenClass(parent=container, controller=self)
            self.frames[ScreenClass] = screen_frame
            screen_frame.grid(row=0, column=0, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.set_screen(StartScreen)

    
    def set_screen(self, screen_class: type[tk.Frame]) -> None:
        screen: tk.Frame = self.frames[screen_class]
        screen.tkraise()


class StartScreen(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: App):
        super().__init__(parent)

        tk.Button(self, text="View Saved Drawings",
                  command=lambda:controller.set_screen(CompletedDrawingsScreen)).pack(pady=10)

        tk.Label(self, text="new drawing width").pack()
        self.width_entry: tk.Entry = tk.Entry(self)
        self.width_entry.pack()

        tk.Label(self, text="new drawing height").pack()
        self.height_entry: tk.Entry = tk.Entry(self)
        self.height_entry.pack()

        tk.Button(self, text="Start New Blank Drawing",
                  command=lambda: self.start_drawing_blank(controller)).pack(pady=10)
        
        tk.Button(self, text="Start From Image File",
                  command=lambda: self.start_drawing_image(controller)).pack(pady=10)
        

    def start_drawing_image(self, controller: App) -> None:
        drawing_width = int(self.width_entry.get())
        drawing_height = int(self.height_entry.get())

        image_path: str = filedialog.askopenfilename(
            title="Select an Image to Start From",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        controller.current_drawing = Drawing(drawing_width, drawing_height,
                                             image_path=image_path)
        controller.set_screen(DrawingScreen)


    def start_drawing_blank(self, controller: App) -> None:
        drawing_width = int(self.width_entry.get())
        drawing_height = int(self.height_entry.get())
        controller.current_drawing = Drawing(drawing_width, drawing_height)
        controller.set_screen(DrawingScreen)


class DrawingScreen(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: App):
        super().__init__(parent)

        self.controller: App = controller
        self.drawing: Drawing = controller.current_drawing
        self.holding_left_click: bool = False
        self.holding_right_click: bool = False
        self.grid_drawn: bool = True
        self.brush_size: int = 1

        top_row_frame: tk.Frame = tk.Frame(self)
        top_row_frame.pack(side="top", fill="x")

        tk.Button(top_row_frame, text="Exit Without Saving",
                command=lambda: controller.set_screen(StartScreen)).pack(
                side="left", padx=(0, 20))
        tk.Label(top_row_frame, text="drawing name:").pack(side="left")
        self.name_entry: tk.Entry = tk.Entry(top_row_frame)
        self.name_entry.pack(side="left")
        tk.Button(top_row_frame, text="Save Drawing",
                command=self.finish_drawing).pack(side="left")
        
        tk.Button(top_row_frame, text="Toggle Grid",
                command=self.toggle_grid).pack(side="left", padx=20)
        
        tk.Label(top_row_frame, text="brush size:").pack(side="left")
        self.brushshize_scale: tk.Scale = tk.Scale(top_row_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                length=100, command=lambda value: setattr(self, "brush_size", int(value)))
        self.brushshize_scale.pack(side="left")

        self.paint_mode: tk.BooleanVar = tk.BooleanVar(value=False)
        tk.Label(top_row_frame, text="paint bucket mode:").pack(side="left",padx=(10,0))
        tk.Checkbutton(top_row_frame, variable=self.paint_mode).pack(side="left")
        
        self.color_row_frame: tk.Frame = self.create_color_row_frame()
        
        self.canvas: tk.Canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Motion>", self.update_clicked_pixel)
        self.canvas.bind("<ButtonPress-1>",
                lambda event: self.update_mouse_state(True, True, event))
        self.canvas.bind("<ButtonRelease-1>",
                lambda event: self.update_mouse_state(True, False, event))
        self.canvas.bind("<ButtonPress-3>",
                lambda event: self.update_mouse_state(False, True, event))
        self.canvas.bind("<ButtonRelease-3>",
                lambda event: self.update_mouse_state(False, False, event))
        self.canvas.bind("<Button-2>", self.pick_color)
        
    
    def tkraise(self, aboveThis=None) -> None:
        self.create_pixels()
        self.update_selected_color(self.color_row_frame.winfo_children()[0])
        self.brush_size = 1
        self.brushshize_scale.set(self.brush_size)
        self.paint_mode.set(False)
        return super().tkraise(aboveThis)
    

    def pick_color(self, event: tk.Event) -> None:
        picked_pixel_ids: tuple[int, ...] = self.canvas.find_overlapping(
                event.x, event.y, event.x, event.y)
        
        if picked_pixel_ids == ():
            return
        
        picked_pixel_id: int = picked_pixel_ids[0]
        picked_color_string: str = self.canvas.itemcget(picked_pixel_id, "fill")
        
        for button in self.color_row_frame.winfo_children():
            if button.cget("bg") == picked_color_string:
                self.update_selected_color(button)
                return
        
        # select eraser button if no colors match
        self.update_selected_color(button)  # type: ignore
        

    def toggle_grid(self) -> None:
        self.grid_drawn = not self.grid_drawn

        self.create_pixels()


    def update_mouse_state(self, left_click: bool, press: bool, event: tk.Event):
        if left_click:
            self.holding_left_click = press
        else:
            self.holding_right_click = press

        self.update_clicked_pixel(event)

    
    def create_color_row_frame(self) -> tk.Frame:
        color_row_frame: tk.Frame = tk.Frame(self)
        color_row_frame.pack(side="top", fill="x")
        
        button_sidelength: int = floor(WINDOW_WIDTH / (len(AVAILABLE_COLORS)))

        color_row_frame.config(height=button_sidelength)
        color_row_frame.pack_propagate(False)

        for color_index in range(len(AVAILABLE_COLORS)):
            self.create_color_button(color_row_frame, color_index)
        
        return color_row_frame


    def create_color_button(self, frame: tk.Frame, color_index: int) -> None:
        button_sidelength: int = floor(WINDOW_WIDTH / (len(AVAILABLE_COLORS)))
        x_position: int = button_sidelength * color_index
        color: Color = AVAILABLE_COLORS[color_index]

        button: tk.Button = tk.Button(frame, bg=self.drawing.get_color_as_string(color))
        button.config(command=lambda clicked=button: self.update_selected_color(clicked),
                    width=button_sidelength, height=button_sidelength, borderwidth=1)
        button.place(width=button_sidelength, height=button_sidelength, x=x_position, y=0)

        is_eraser_button: bool = color is BACKGROUND_PIXEL
        if is_eraser_button:
            eraser_image = Image.open("images/eraser.jpg")
            eraser_image = eraser_image.resize((button_sidelength, button_sidelength),
                                               Image.Resampling.LANCZOS)
            eraser_image_tk = ImageTk.PhotoImage(eraser_image)
            button.config(image=eraser_image_tk)
            button.image = eraser_image_tk # type: ignore


    def update_selected_color(self, button: tk.Widget) -> None:
        if not isinstance(button, tk.Button):
            return
        color_red: int = int(button["bg"][1:3], base=16)
        color_green: int = int(button["bg"][3:5], base=16)
        color_blue: int = int(button["bg"][5:7], base=16)

        color: Color = (color_red, color_green, color_blue)

        color_buttons: list[tk.Widget] = self.color_row_frame.winfo_children()
        eraser_button: tk.Widget = color_buttons[-1]

        if button is eraser_button:
            color = BACKGROUND_PIXEL

        self.drawing.selected_color = color

        for color_button in color_buttons:
            if not isinstance(color_button, tk.Button):
                continue

            color_button.config(borderwidth=1)

        button_sidelength: int = floor(WINDOW_WIDTH / len(color_buttons))
        button.config(borderwidth= floor(button_sidelength * .15))


    def finish_drawing(self) -> None:
        save_new_drawing(self.drawing, self.name_entry.get())
        self.name_entry.delete(0, tk.END)
        self.controller.set_screen(CompletedDrawingsScreen)


    def get_pixel_sidelength(self) -> int:
        available_width: int = self.canvas.winfo_width()
        available_height: int = self.canvas.winfo_height()

        maximum_pixel_width: int = floor(available_width / self.drawing.width)
        maximum_pixel_height: int = floor(available_height / self.drawing.height)

        return min(maximum_pixel_width, maximum_pixel_height)

    
    def create_pixels(self) -> None:
        self.drawing = self.controller.current_drawing
        self.canvas.delete("all")

        pixel_sidelength: int = self.get_pixel_sidelength()

        current_x: int = 0
        current_y: int = 0

        for row_index, pixel_row in enumerate(self.drawing.pixel_rows):
            for column_index, pixel in enumerate(pixel_row):
                color_as_string = self.drawing.get_color_as_string(pixel)
                self.canvas.create_rectangle(current_x, current_y,
                        current_x+pixel_sidelength, current_y+pixel_sidelength,
                        fill=color_as_string, tags=f"{row_index},{column_index}",
                        width=int(self.grid_drawn))
                
                current_x += pixel_sidelength
            current_x = 0
            current_y += pixel_sidelength


    def update_pixels_normal(self, event: tk.Event, new_color: Color) -> None:
        pixel_size: int = self.get_pixel_sidelength()
        brush_size_pixels: float = ((self.brush_size - 1) * pixel_size) / 2
        new_color_as_string: str = self.drawing.get_color_as_string(new_color)

        affected_pixel_ids: tuple[int, ...] = self.canvas.find_overlapping(
                event.x - brush_size_pixels, event.y - brush_size_pixels,
                event.x + brush_size_pixels, event.y + brush_size_pixels)
            
        for pixel_id in affected_pixel_ids:
            self.canvas.itemconfig(pixel_id, fill=new_color_as_string)
            pixel_row, pixel_column = map(int, self.canvas.gettags(pixel_id)[0].split(","))
            self.drawing.pixel_rows[pixel_row][pixel_column] = new_color


    def update_pixels_paint_mode(self, event: tk.Event, new_color: Color) -> None:
        clicked_pixel_ids: tuple[int, ...] = self.canvas.find_overlapping(
                event.x, event.y, event.x, event.y)
        
        if clicked_pixel_ids == ():
            return
        
        clicked_pixel_id = clicked_pixel_ids[0]
        pixel_row, pixel_column = map(int, self.canvas.gettags(clicked_pixel_id)[0].split(","))
        self.drawing.paint_fill(pixel_row, pixel_column, new_color)
        self.create_pixels()
            
    
    def update_clicked_pixel(self, event: tk.Event) -> None:
        is_drawing: bool = self.holding_left_click
        is_erasing: bool = self.holding_right_click

        if not is_drawing and not is_erasing:
            return

        new_color: Color = self.drawing.selected_color if is_drawing else BACKGROUND_PIXEL

        if self.paint_mode.get():
            self.update_pixels_paint_mode(event, new_color)
        else:
            self.update_pixels_normal(event, new_color)


class CompletedDrawingsScreen(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: App):
        super().__init__(parent)

        self.controller: App = controller

        tk.Button(self, text="Create New Drawing",
                  command=lambda: self.exit_screen()).grid(row=0, column=0)
        tk.Label(self, text="starting charges: ").grid(row=0, column=1, padx=(7,3))
        self.starting_charges_entry = tk.Entry(self, width=6)
        self.starting_charges_entry.grid(row=0, column=2)
    

    def tkraise(self, aboveThis=None) -> None:
        self.create_options()
        return super().tkraise(aboveThis)

        
    def create_options(self) -> None:
        self.remove_options()

        drawing_names: list[str] = get_list_drawing_names()
        for drawing_index, drawing_name in enumerate(drawing_names, start=1):
            tk.Label(self, text=drawing_name).grid(row=drawing_index, column=0)
            tk.Button(self, text="Run Macro",
                      command=lambda name=drawing_name:
                      self.run_drawing_macro(name, int(self.starting_charges_entry.get()))).grid(
                          row=drawing_index, column=1, padx=5, pady=5)
            tk.Button(self, text="Load",
                      command=lambda name=drawing_name: self.load_drawing(name)).grid(
                          row=drawing_index, column=2, padx=5, pady=5)
            tk.Button(self, text="Delete",
                      command=lambda name=drawing_name: self.remove_drawing(name)).grid(
                          row=drawing_index, column=3, padx=5, pady=5)
            

    def run_drawing_macro(self, drawing_name: str, starting_charges: int) -> None:
        self.controller.iconify()
        drawing: Drawing = load_drawing_from_name(drawing_name)
        execute_drawing_macro(drawing, starting_charges)


    def load_drawing(self, drawing_name: str) -> None:
        self.controller.current_drawing = load_drawing_from_name(drawing_name)
        self.controller.set_screen(DrawingScreen)


    def remove_drawing(self, drawing_name) -> None:
        delete_drawing(drawing_name)
        self.create_options()


    def remove_options(self) -> None:
        for widget in self.winfo_children():
            if widget.grid_info()["row"] != 0:
                widget.destroy()


    def exit_screen(self) -> None:
        self.remove_options()
        self.controller.set_screen(StartScreen)


if __name__ == "__main__":
    app: App = App()
    app.mainloop()