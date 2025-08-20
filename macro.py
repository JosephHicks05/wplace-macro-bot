from time import sleep
from macro_utils import *
from typing import Literal
from drawing import BACKGROUND_PIXEL, Drawing, Color, PickableColor, get_pickable_from_color
from datetime import datetime, timedelta
from math import floor

PAINT_BUTTON_LOCATION: tuple[int, int] = (740, 783)


class MouseState:
    def __init__(self, position: tuple[int, int] | None = None, clicked: bool | None = None):
        position = get_mouse_position() if position is None else position
        self.positon: tuple[int, int] = position

        clicked = is_key_pressed("leftclick") if clicked is None else clicked
        self.clicked: bool = clicked


class Macro:
    def __init__(self, name: str, mouse_states: list[MouseState] | None = None, poll_rate_hertz: int = 30):
        self.name: str = name
        self.mouse_states: list[MouseState] = [] if mouse_states is None else mouse_states
        self.poll_rate_hertz: int = poll_rate_hertz


    def record(self, stop_button: Literal["space", "leftclick", "rightclick"] = "space",
                 poll_rate_hertz: int = 30) -> None:
        from files import write_macro

        while is_key_pressed(stop_button):  # do not immediately stop
            sleep(1/30)

        self.poll_rate_hertz = poll_rate_hertz
        self.mouse_states = []

        while not is_key_pressed(stop_button):
            self.mouse_states.append(MouseState())
            sleep(1/poll_rate_hertz)

        write_macro(self)

    
    def playback(self, kill_button: Literal["space", "leftclick", "rightclick"] = "space") -> None:
        while is_key_pressed(kill_button):  # do not immediatly stop
            sleep(1/30)
        
        clicking_current: bool = False
        clicking_last: bool = False
        for mouse_state in self.mouse_states:
            if is_key_pressed(kill_button):
                return
            
            move_mouse(mouse_state.positon)

            clicking_current = mouse_state.clicked
            if clicking_current and not clicking_last:
                click_mouse()
            if clicking_last and not clicking_current:
                release_mouse()
            clicking_last = clicking_current

            sleep(1/self.poll_rate_hertz)
            

def edit_macros() -> None:
    from files import read_macro, delete_macro  # local import to avoid circular import
    COMMANDS_STRING = "commands:\nrecord <macro name> <poll rate>\n\
play <macro name>\ndelete <macro name>\nexit"
    print(COMMANDS_STRING)
    
    while True:
        input_tokens: list[str] = input("enter command: ").split(" ")
        command: str = input_tokens[0]

        if command in ("exit", "quit"):
            return
        
        if command == "record":
            name: str = input_tokens[1]
            poll_rate: int = int(input_tokens[2])
            print("macro recording. press space to stop")
            Macro(name).record(poll_rate_hertz=poll_rate)

        elif command == "play":
            name: str = input_tokens[1]
            print("macro playing. press space to stop")
            macro: Macro = read_macro(name)
            macro.playback()

        elif command == "delete":
            name: str = input_tokens[1]
            delete_macro(name)
            print("deleted.") 

        else:
            print(f"unrecognized command.\n{COMMANDS_STRING}")


def attempt_reload_login() -> None:
    RELOAD_BUTTON_POSITION = (93, 58)
    LOGIN_BUTTON_POSITION = (1470, 150)
    WITH_GOOGLE_BUTTON_POSITION = (762, 413)
    ACCOUNT_BUTTON_POSITION = (841, 364)

    click_location(RELOAD_BUTTON_POSITION, .4, 3)
    click_location(LOGIN_BUTTON_POSITION, 0, 7)
    click_location(WITH_GOOGLE_BUTTON_POSITION, 0, 2)
    click_location(ACCOUNT_BUTTON_POSITION, 0, 3)
    


def submit_pixels(end: bool = False) -> None:
    CLOSE_PIXEL_INFO_POSITION = (990, 691)

    if end:
        click_location(PAINT_BUTTON_LOCATION, .04)
        return
    
    click_location(PAINT_BUTTON_LOCATION, 1, 4)  # click captcha if there was captcha, submit pixels if not
    click_location(PAINT_BUTTON_LOCATION, 0, 2)  # submit pixels if there was captcha, nothing if not

    attempt_reload_login()
    click_location(PAINT_BUTTON_LOCATION, 1, 3)
    click_location(PAINT_BUTTON_LOCATION, 0, 2)  # open paint mode if logged out, nothing if not
    click_location(CLOSE_PIXEL_INFO_POSITION, 0, 1)  # nothing if logged out, unselect random pixel if not
    click_location(PAINT_BUTTON_LOCATION, 0, 4)  # nothing if logged out, open paint mode if not
    click_location(PAINT_BUTTON_LOCATION, 0, 1)  # in case captcha again


def place_pixel(color: PickableColor, charges_used: int) -> bool:
    DRAWN_PIXEL_POSITION: tuple[int, int] = (260, 480)

    if color.color == BACKGROUND_PIXEL:
        return False

    click_location(color.screen_position, 0, .02)
    click_location(DRAWN_PIXEL_POSITION, 0, .02)

    ready_to_submit: bool = charges_used > 0 and charges_used % 10 == 0
    if ready_to_submit:
        submit_pixels()
    return True


def has_charge(starting_time: datetime, starting_charges: int, charges_used: int) -> bool:
    CHARGE_ADD_PERIOD: timedelta = timedelta(seconds=30)

    current_time: datetime = datetime.now()
    time_elapsed: timedelta = current_time - starting_time
    charges_added: int = floor(time_elapsed / CHARGE_ADD_PERIOD)

    current_charges: int = starting_charges - charges_used + charges_added
    return current_charges > 4  # safety buffer


def next_two_rows_empty(position: list[int], drawing: Drawing) -> bool:
    current_row: int = position[0]
    next_two_rows: list[list[Color]] = drawing.pixel_rows[current_row:current_row+2]
    
    for row in next_two_rows:
        for color in row:
            if color != BACKGROUND_PIXEL:
                return False
            
    return True


def update_position(position: list[int], drawing: Drawing) -> None:
    row: int = position[0]
    column: int = position[1]

    even_row: bool = row % 2 == 0
    row_end_left: bool = column == 0
    row_end_right: bool = column == drawing.width - 1

    
    if column == 0 and next_two_rows_empty(position, drawing):
        row += 2  # skip empty rows, move down twice
        move_pixel("down")
        move_pixel("down")

    elif (even_row and row_end_right) or ((not even_row) and row_end_left):
        row += 1  # end of row, move down
        move_pixel("down")

    elif even_row:
        column += 1  # even row, move right
        move_pixel("right")

    else:
        column -= 1  # odd row, move left
        move_pixel("left")

    position[0] = row
    position[1] = column


def execute_drawing_macro(drawing: Drawing, starting_charges: int) -> None:
    sleep(.1)

    current_position: list[int] = [0, 0]

    starting_time: datetime = datetime.now()
    charges_used: int = 0

    while current_position[0] < drawing.height:
        current_row = current_position[0]
        current_column = current_position[1]

        if is_key_pressed("space"):
            return
        
        if not has_charge(starting_time, starting_charges, charges_used):
            sleep(1)
            if is_key_pressed("space"):
                return
            
            continue

        color: Color = drawing.pixel_rows[current_row][current_column]
        color_pickable: PickableColor = get_pickable_from_color(color)
        if place_pixel(color_pickable, charges_used):
            charges_used += 1

        update_position(current_position, drawing)

    submit_pixels(end=True)


def test_pixel_movement() -> None: 
    print("testing pixel movement. press WASD to move around, space to stop.")

    PIXEL_MOVEMENT_HERTZ = 30
    while not is_key_pressed("space"):
        for direction in ("down", "left", "right"):
            if is_key_pressed(direction):
                move_pixel(direction)
            
        sleep(1/PIXEL_MOVEMENT_HERTZ)

    print(f"stopped with mouse at: {get_mouse_position()}")


def get_pixel_positions() -> None:
    print("grabbing pixel values. Press space to print mouse's location")

    space_pressed: bool = False
    space_pressed_last: bool = False

    while True:
        space_pressed = is_key_pressed("space")
        space_just_pressed: bool = space_pressed and not space_pressed_last

        if space_just_pressed:
            print(get_mouse_position())
        
        space_pressed_last = space_pressed
        sleep(1/30)


if __name__ == "__main__":
    from files import read_macro

    get_pixel_positions()

    while True:
        if is_key_pressed("space"):
            read_macro("login").playback()

        sleep(.1)