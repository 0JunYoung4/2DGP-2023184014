"""Sonic 스프라이트 애니메이션 뷰어.

실행: python Labs/LEC09/sonic_animation_viewer.py
"""


from dataclasses import dataclass
from pathlib import Path
from time import perf_counter


CANVAS_WIDTH, CANVAS_HEIGHT = 1280, 720
SPRITE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")
FRAME_SECONDS = 1.0 / 10
REPEAT_COUNT = 5
SHEET_WIDTH, SHEET_HEIGHT = 399, 525
# 시트 조사: 제목(상단)과 크레딧/장식(470행 이후)은 동작에서 제외한다.
# 시트 순서: 대기 9, 웅크리기 2, 걷기 12, 달리기 6, 회전 9,
# 회전 공 6, 질주 6, 회전 질주 6, 뒤돌기 6, 넘어짐 2,
# 균형잡기 8, 놀라기 2, 둘러보기 2. 총 13개 동작, 86개 프레임.
# 동작 이름은 뷰어에서 식별하기 위한 이름이며 원작의 공식 명칭은 아니다.


@dataclass(frozen=True)
class Frame:
    # 원본 PNG의 왼쪽 위 기준 영역. 기준점은 잘라낸 영역의 아래쪽 중앙.
    x: int
    y: int
    width: int
    height: int

    @property
    def clip_rect(self):
        return self.x, SHEET_HEIGHT - self.y - self.height, self.width, self.height


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]


ANIMATIONS = (
    Animation("대기", tuple(Frame(*box) for box in (
        (1, 39, 29, 39), (31, 40, 26, 38), (58, 39, 29, 39),
        (87, 40, 29, 38), (118, 40, 30, 38), (150, 40, 30, 38),
        (182, 40, 31, 38), (213, 39, 30, 38), (243, 39, 26, 38),
    ))),
)


ALL_FRAMES = tuple(frame for animation in ANIMATIONS for frame in animation.frames)
DISPLAY_SCALE = min((CANVAS_WIDTH - 160) / max(f.width for f in ALL_FRAMES),
                    (CANVAS_HEIGHT - 160) / max(f.height for f in ALL_FRAMES))
GROUND_Y = (CANVAS_HEIGHT - max(f.height for f in ALL_FRAMES) * DISPLAY_SCALE) / 2


class AnimationPlayer:
    def __init__(self, animations=ANIMATIONS):
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.elapsed = 0.0
        self.completed_cycles = 0
        self.state = "PLAYING"

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, dt):
        if self.state == "WAITING":
            return
        self.elapsed += max(0.0, dt)
        while self.elapsed + 1e-9 >= FRAME_SECONDS:
            self.elapsed = max(0.0, self.elapsed - FRAME_SECONDS)
            self.frame_index = (self.frame_index + 1) % len(self.animation.frames)
            if self.frame_index == 0:
                self.completed_cycles += 1
                if self.completed_cycles == REPEAT_COUNT:
                    self.frame_index = len(self.animation.frames) - 1
                    self.state = "WAITING"
                    break


def destination_rect(frame):
    return (CANVAS_WIDTH / 2, GROUND_Y + frame.height * DISPLAY_SCALE / 2,
            frame.width * DISPLAY_SCALE, frame.height * DISPLAY_SCALE)


def draw_frame(sprite, frame):
    sprite.clip_draw(*frame.clip_rect, *destination_rect(frame))


def main():
    import pico2d as p2

    p2.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        try:
            sprite = p2.load_image(str(SPRITE_PATH))
        except Exception as error:
            raise RuntimeError(f"스프라이트 로딩 실패: {SPRITE_PATH}: {error}") from error
        running = True
        player = AnimationPlayer()
        previous_time = perf_counter()
        while running:
            for event in p2.get_events():
                if event.type == p2.SDL_QUIT:
                    running = False
                elif event.type == p2.SDL_KEYDOWN and event.key == p2.SDLK_ESCAPE:
                    running = False
            now = perf_counter()
            dt = now - previous_time
            previous_time = now
            player.update(dt)
            p2.clear_canvas()
            draw_frame(sprite, player.frame)
            p2.update_canvas()
            p2.delay(0.01)
    finally:
        p2.close_canvas()


if __name__ == "__main__":
    main()
