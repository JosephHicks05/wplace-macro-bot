from PIL import Image
from macro_utils import move_mouse, click_mouse

Color = tuple[int, int, int]


class PickableColor:
    def __init__(self, name: str, color: Color, screen_position: tuple[int, int]):
        self.name: str = name
        self.color: Color = color
        self.screen_position: tuple[int, int] = screen_position

    
    def select_color(self):
        move_mouse(self.screen_position, .02)
        click_mouse(.02)


PICKABLE_COLORS: tuple[PickableColor, ...] = (
        PickableColor("Black", (0, 0, 0), (33, 664)),
        PickableColor("Dark Gray", (60, 60, 60), (81, 666)),
        PickableColor("Gray", (120, 120, 120), (130, 665)),
        PickableColor("Light Gray", (210, 210, 210), (222, 666)),
        PickableColor("White", (255, 255, 255), (271, 665)),
        PickableColor("Deep Red", (96, 0, 24), (322, 664)),
        PickableColor("Red", (237, 28, 36), (410, 666)),
        PickableColor("Orange", (255, 127, 39), (553, 669)),
        PickableColor("Gold", (246, 170, 9), (604, 665)),
        PickableColor("Yellow", (249, 221, 59), (650, 668)),
        PickableColor("Light Yellow", (255, 250, 188), (698, 667)),
        PickableColor("Dark Olive", (74, 107, 58), (887, 665)),
        PickableColor("Olive", (90,148,74), (932, 663)),
        PickableColor("Light Olive", (132, 197, 115), (982, 668)),
        PickableColor("Dark Green", (14, 185, 104), (1028, 667)),
        PickableColor("Green", (19, 230, 123), (1079, 665)),
        PickableColor("Light Green", (135, 255, 94), (1123, 666)),
        PickableColor("Dark Teal", (12, 129, 110), (1174, 664)),
        PickableColor("Teal", (16, 174, 166), (1220, 662)),
        PickableColor("Light Teal", (19, 225, 190), (1271, 664)),
        PickableColor("Dark Cyan", (15, 121, 159), (1312, 666)),
        PickableColor("Cyan", (96, 247, 242), (1359, 666)),
        PickableColor("Light Cyan", (187, 250, 242), (1408, 669)),
        PickableColor("Dark Blue", (40, 80, 158), (1454, 667)),
        PickableColor("Blue", (64, 147, 228), (1503, 667)),
        PickableColor("Light Blue", (125, 199, 255), (32, 710)),
        PickableColor("Dark Indigo", (77, 49, 184), (82, 711)),
        PickableColor("Indigo", (107, 80, 246), (128, 706)),
        PickableColor("Light Indigo", (153, 177, 251), (176, 711)),
        PickableColor("Dark Slate Blue", (74, 66, 132), (226, 713)),
        PickableColor("Dark Purple", (120, 12, 153), (368, 710)),
        PickableColor("Purple", (170, 56, 185), (414, 710)),
        PickableColor("Light Purple", (224, 159, 249), (460, 708)),
        PickableColor("Dark Pink", (203, 0, 122), (504, 707)),
        PickableColor("Pink", (236, 31, 128), (556, 710)),
        PickableColor("Light Pink", (243, 141, 169), (602, 712)),
        PickableColor("Dark Brown", (104, 70, 52), (792, 710)),
        PickableColor("Brown", (149, 104, 42), (840, 708)),
        PickableColor("Beige", (248, 178, 119), (1125, 710)),
        PickableColor("Dark Slate", (51 ,57, 65), (1360, 710)),
        PickableColor("Slate", (109, 117, 141), (1408, 710))
)

BACKGROUND_PIXEL: Color = (-1, -1, -1)

AVAILABLE_COLORS: tuple[Color, ...] = tuple([color.color for color in PICKABLE_COLORS]) +\
                                      (BACKGROUND_PIXEL,)

class Drawing:
    def __init__(self, width: int, height: int,
                 pixel_rows: list[list[Color]]=[], image_path: str | None = None):
        if pixel_rows == []:
            pixel_rows = []
        
        self.width: int = width
        self.height: int = height
        self.pixel_rows: list[list[Color]] = pixel_rows

        self.resampling: Image.Resampling = Image.Resampling.LANCZOS
        self.dither: Image.Dither = Image.Dither.FLOYDSTEINBERG

        if image_path != None:
            self.set_pixels_from_image(image_path)

        self.selected_color: Color = AVAILABLE_COLORS[0]  # black
        self.background_color: Color = (0, 0, 100)

        if self.pixel_rows != []:
            return
        
        for _ in range(self.height):
            self.pixel_rows.append([BACKGROUND_PIXEL] * self.width)


    def set_pixels_from_image(self, image_path: str) -> None:
        image = Image.open(image_path)
        image = image.convert("RGB")
        image = image.resize((self.width, self.height), self.resampling)
        image = self.color_image(image)
        image = image.convert("RGB")

        finished_pixels = list(image.getdata()) # type: ignore
        finished_pixel_rows: list[list[Color]] = [finished_pixels[i * self.width:(i + 1) * self.width]
                                             for i in range(self.height)]
        
        self.pixel_rows = finished_pixel_rows


    def color_image(self, image: Image.Image) -> Image.Image:
        palette_image: Image.Image = Image.new("P", (1, 1))

        palette: list[int] = []
        for color in AVAILABLE_COLORS:
            palette.extend(color)
        palette = palette[:-3]  # remove background color
        palette += [0, 0, 0] * (256 - len(palette) // 3)

        palette_image.putpalette(palette)

        return image.quantize(palette=palette_image, dither=self.dither)
    
    
    def update_pixel(self, row: int, column: int, erase: bool = False) -> None:
        self.pixel_rows[row][column] = BACKGROUND_PIXEL if erase else self.selected_color
    

    def num_nonbackground_pixels(self) -> int:
        num_nonbackground_pixels: int = 0

        for pixel_row in self.pixel_rows:
            for pixel in pixel_row:
                if pixel != BACKGROUND_PIXEL:
                    num_nonbackground_pixels += 1

        return num_nonbackground_pixels
    

    def get_same_color_neighbors(self, coords: tuple[int, int]) -> list[tuple[int, int]]:
        neighbors: list[tuple[int, int]] = []

        row: int = coords[0]
        column: int = coords[1]
        color: Color = self.pixel_rows[row][column]
        for potential_neighbor in (row, column+1), (row+1, column), (row, column-1), (row-1, column):
            is_valid_neighor = 0 <= potential_neighbor[0] < self.height\
                    and 0 <= potential_neighbor[1] < self.width
            
            if is_valid_neighor and self.pixel_rows[potential_neighbor[0]][potential_neighbor[1]] == color:
                neighbors.append(potential_neighbor)

        return neighbors
    

    def paint_fill(self, row: int, column: int, color: Color) -> None:
        to_fill: set[tuple[int, int]] = {(row, column)}
        to_check_neighbors: list[tuple[int, int]] = [(row, column)]

        while to_check_neighbors != []:
            pixel_neighbors: list[tuple[int, int]] = self.get_same_color_neighbors(to_check_neighbors.pop(0))

            for neighbor in pixel_neighbors:
                if neighbor not in to_fill:
                    to_fill.add(neighbor)
                    to_check_neighbors.append(neighbor)

        for row, column in to_fill:
            self.pixel_rows[row][column] = color


    def get_color_as_string(self, color: Color) -> str:
        if color == BACKGROUND_PIXEL:
            color = self.background_color

        rgb_number: int = color[0] * (2**16) + color[1] * (2**8) + color[2]
        return f"#{rgb_number:06x}"
    

def get_pickable_from_color(color: Color) -> PickableColor:
    if color == BACKGROUND_PIXEL:
        return PickableColor("background", BACKGROUND_PIXEL, (0, 0))
    
    for pickable in PICKABLE_COLORS:
        if pickable.color == color:
            return pickable
    
    print(f"could not find color: {color}")
    return PickableColor("background", BACKGROUND_PIXEL, (0, 0))


def get_string_as_color(string: str):
    return (int(string[1:3], base=16), int(string[3:5], base=16), int(string[5:7], base=16))