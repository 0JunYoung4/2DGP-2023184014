"""Drill #8: 크기가 다른 프레임과 동작별 프레임 수를 지원하는 Pico2D 뷰어."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Frame:
    # PNG 왼쪽 위 기준 영역과, 영역 내부의 발 기준점.
    x: int
    y: int
    width: int
    height: int
    anchor_x: int
    anchor_y: int


@dataclass(frozen=True)
class Animation:
    name: str
    fps: float
    frames: tuple[Frame, ...]


SPRITE_PATH = Path(__file__).resolve().with_name("adventurer_bonus_sheet.png")
SHEET_WIDTH, SHEET_HEIGHT = 1536, 1024

# 각 Frame: x, y, width, height, anchor_x, anchor_y.
# 프레임 크기와 프레임 수를 고정된 격자로 가정하지 않는다.
ANIMATIONS = (
    Animation("Idle", 6, (
        Frame(92, 41, 70, 186, 35, 184),
        Frame(270, 39, 71, 188, 35, 186),
        Frame(442, 41, 72, 186, 36, 184),
        Frame(621, 40, 71, 187, 35, 185),
    )),
    Animation("Walk", 9, (
        Frame(60, 277, 115, 188, 57, 186),
        Frame(238, 274, 109, 191, 54, 189),
        Frame(415, 274, 103, 191, 51, 189),
        Frame(583, 276, 115, 189, 57, 187),
        Frame(763, 275, 118, 190, 59, 188),
        Frame(945, 276, 116, 189, 58, 187),
    )),
    Animation("Run", 12, (
        Frame(30, 515, 166, 188, 83, 192),
        Frame(228, 514, 160, 183, 80, 193),
        Frame(413, 515, 165, 188, 82, 192),
        Frame(595, 510, 167, 193, 83, 197),
        Frame(778, 513, 168, 187, 84, 194),
        Frame(965, 517, 161, 192, 80, 190),
        Frame(1148, 507, 176, 198, 88, 200),
        Frame(1355, 511, 145, 197, 72, 196),
    )),
    Animation("Jump", 7, (
        Frame(109, 860, 135, 129, 67, 127),
        Frame(302, 779, 141, 210, 70, 208),
        Frame(487, 741, 130, 171, 65, 246),
        Frame(665, 770, 111, 200, 55, 217),
        Frame(845, 838, 142, 151, 71, 149),
    )),
)


CANVAS_WIDTH, CANVAS_HEIGHT = 900, 700


def draw_frame(sprite, frame):
    # Pico2D는 왼쪽 아래 기준이므로 PNG의 위쪽 좌표를 변환한다.
    bottom = SHEET_HEIGHT - frame.y - frame.height
    sprite.clip_draw(frame.x, bottom, frame.width, frame.height,
                     CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2,
                     frame.width, frame.height)


def main():
    import pico2d as p2

    p2.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        p2.hide_lattice()
        sprite = p2.load_image(str(SPRITE_PATH))
        while True:
            if any(event.type == p2.SDL_QUIT for event in p2.get_events()):
                break
            p2.clear_canvas()
            draw_frame(sprite, ANIMATIONS[0].frames[0])
            p2.update_canvas()
            p2.delay(0.01)
    finally:
        p2.close_canvas()


if __name__ == "__main__":
    main()
