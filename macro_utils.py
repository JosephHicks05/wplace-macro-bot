import ctypes
from time import sleep
from typing import Literal

SCREEN_WIDTH = 1530
SCREEN_HEIGHT = 860
PIXEL_WIDTH = 525


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]


def get_mouse_position() -> tuple[int, int]:
    point = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return (point.x, point.y)


def is_key_pressed(key: Literal["space", "leftclick", "rightclick",
                                "up", "down", "left", "right"]) -> bool:
    
    VK_MAPPING: dict[str, int] = {"space": 0x20, "leftclick": 0x01, "rightclick": 0x02,
                                  "up": 0x57, "down": 0x53, "left": 0x41, "right": 0x44}
    key_vk: int = VK_MAPPING[key]
    MAGIC_VOODOO_CONSTANT: int = 0x8000

    return bool(ctypes.windll.user32.GetAsyncKeyState(key_vk) & MAGIC_VOODOO_CONSTANT)


def move_mouse(position: tuple[int, int],
               pre_delay_seconds: float = 0, post_delay_seconds: float = 0) -> None:
    sleep(pre_delay_seconds)
    ctypes.windll.user32.SetCursorPos(position[0], position[1])
    sleep(post_delay_seconds)


def click_mouse(pre_delay_seconds: float = 0, post_delay_seconds: float = 0) -> None:
    sleep(pre_delay_seconds)
    CLICK_EVENT: int = 0x0002
    ctypes.windll.user32.mouse_event(CLICK_EVENT, 0, 0, 0, 0)
    sleep(post_delay_seconds)


def release_mouse(pre_delay_seconds: float = 0, post_delay_seconds: float = 0) -> None:
    sleep(pre_delay_seconds)
    RELEASE_EVENT: int = 0x0004
    ctypes.windll.user32.mouse_event(RELEASE_EVENT, 0, 0, 0, 0)
    sleep(post_delay_seconds)


def click_location(position: tuple[int, int],
               pre_delay_seconds: float = 0, post_delay_seconds: float = 0) -> None:
    sleep(pre_delay_seconds)
    move_mouse(position)
    sleep(.02)
    click_mouse()
    sleep(.02)
    release_mouse()
    sleep(post_delay_seconds)


def move_pixel(direction: Literal["right", "left", "down"]) -> None:
    DIRECTION_POSITION_MAPPING: dict[str, tuple[int, int, int, int]] = {
        "right": (PIXEL_WIDTH, 500, 0, 500),
        "left": (SCREEN_WIDTH - PIXEL_WIDTH + 1, 500, SCREEN_WIDTH, 500),
        #"up": (500, SCREEN_HEIGHT - PIXEL_WIDTH, 500, SCREEN_HEIGHT),
        "down": (500,  PIXEL_WIDTH, 500, 0)
    } # (starting x, starting y, ending x, ending y)

    starting_x: int = DIRECTION_POSITION_MAPPING[direction][0]
    starting_y: int = DIRECTION_POSITION_MAPPING[direction][1]
    ending_x: int = DIRECTION_POSITION_MAPPING[direction][2]
    ending_y: int = DIRECTION_POSITION_MAPPING[direction][3]

    move_mouse((starting_x, starting_y), .02, .08) 
    click_mouse(0, .08)
    move_mouse((ending_x, ending_y), 0, .08)
    release_mouse(0, .06)