from pathlib import Path
from drawing import Drawing
from drawing import Color
from macro import MouseState, Macro

SAVED_DRAWINGS_PATH: Path = Path(__file__).parent / "saved_drawings"
MACROS_PATH: Path = Path(__file__).parent / "macros"


def get_list_drawing_names() -> list[str]:
    drawing_names: list[str] = [drawing_file.stem for drawing_file in SAVED_DRAWINGS_PATH.iterdir()]
    return drawing_names


def get_valid_filename(name: str) -> str:
    existing_names: list[str] = get_list_drawing_names()

    if name == "":
        name = "unnamed_drawing"
    while name in existing_names:
        name += "_again"
    
    return f"{name}.txt"


def get_text_representation(drawing: Drawing) -> str:
    text: str = ""

    for row in drawing.pixel_rows:
        for index, pixel in enumerate(row):
            text += f"{pixel[0]} {pixel[1]} {pixel[2]}"

            if index != len(row) - 1:
                text += ","

        if row is not drawing.pixel_rows[-1]:
            text += "\n"

    return text


def save_new_drawing(drawing: Drawing, name: str) -> None:
    filename: str = get_valid_filename(name)
    new_drawing_path: Path = SAVED_DRAWINGS_PATH / filename

    with new_drawing_path.open("w", encoding="utf-8") as writer:
        writer.write(get_text_representation(drawing))


def delete_drawing(drawing_name: str) -> None:
    deletion_path: Path = SAVED_DRAWINGS_PATH / f"{drawing_name}.txt"
    deletion_path.unlink()


def load_drawing_from_name(drawing_name: str) -> Drawing:
    drawing_path: Path = SAVED_DRAWINGS_PATH / f"{drawing_name}.txt"

    with drawing_path.open("r", encoding="utf-8") as reader:
        raw_data: str = reader.read()

    
    pixel_rows: list[list[Color]] = []

    raw_data_rows: list[str] = raw_data.split("\n")
    for raw_data_row in raw_data_rows:
        row_data: list[Color] = []

        for raw_color_data in raw_data_row.split(","):
            color_data: list[str] = raw_color_data.split(" ")
            color: Color = tuple(map(int, color_data)) # type: ignore
            row_data.append(color)

        pixel_rows.append(row_data)

    return Drawing(len(pixel_rows[0]), len(pixel_rows), pixel_rows)


def write_macro(macro: Macro) -> None:
    new_macro_path: Path = MACROS_PATH / f"{macro.name}.txt"

    with new_macro_path.open("w", encoding="utf-8") as writer:
        writer.write(str(macro.poll_rate_hertz))

        for mouse_state in macro.mouse_states:
            mouse_x: int = mouse_state.positon[0]
            mouse_y: int = mouse_state.positon[1]
            is_clicked: int = int(mouse_state.clicked)
            writer.write(f"\n{mouse_x},{mouse_y},{is_clicked}")


def read_macro(name: str) -> Macro:
    macro_path: Path = MACROS_PATH / f"{name}.txt"

    with macro_path.open(encoding="utf-8") as reader:
        macro_lines: list[str] = reader.readlines()

    poll_rate_hertz: int = int(macro_lines[0])

    mouse_states: list[MouseState] = []
    for line in macro_lines[1:]:
        mouse_data: list[str] = line.split(",")
        mouse_x: int = int(mouse_data[0])
        mouse_y: int = int(mouse_data[1])
        clicked: bool = bool(int(mouse_data[2]))

        mouse_states.append(MouseState((mouse_x, mouse_y), clicked))

    return Macro(name, mouse_states, poll_rate_hertz)


def delete_macro(name: str) -> None:
    macro_path: Path = MACROS_PATH / f"{name}.txt"
    macro_path.unlink()