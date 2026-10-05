"""Sonic 스프라이트 애니메이션 뷰어.

실행: python Labs/LEC09/sonic_animation_viewer.py
검증: python Labs/LEC09/sonic_animation_viewer.py --self-test
종료: ESC 또는 창 닫기. Python과 pico2d가 필요하다.
같은 폴더의 sonic-sprite.png에서 13개 동작, 76개 프레임을 재생한다.
각 동작을 5회 반복하고 마지막 자세에서 1초 쉰 뒤 다음 동작으로 넘어간다.
이동 동작은 화면 가장자리에서 방향을 바꾸며, 회전 동작은 가볍게 튀어 오른다.
"""


from dataclasses import dataclass
import math
import struct
from pathlib import Path
from time import perf_counter


CANVAS_WIDTH, CANVAS_HEIGHT = 1280, 720
SPRITE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")
FRAME_SECONDS = 1.0 / 10
REPEAT_COUNT = 5
PAUSE_SECONDS = 1.0
SHEET_WIDTH, SHEET_HEIGHT = 399, 525
# 시트 조사: 제목(상단)과 크레딧/장식(470행 이후)은 동작에서 제외한다.
# 시트 순서: 대기 9, 웅크리기 2, 걷기 12, 달리기 6, 회전 9,
# 회전 공 6, 질주 6, 회전 질주 6, 뒤돌기 6, 넘어짐 2,
# 균형잡기 8, 놀라기 2, 둘러보기 2. 총 13개 동작, 76개 프레임.
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
    Animation("웅크리기", (Frame(270, 45, 24, 32), Frame(302, 51, 29, 26))),
    Animation("걷기", tuple(Frame(*box) for box in (
        (8, 80, 26, 37), (37, 80, 27, 37), (65, 80, 31, 38),
        (97, 80, 37, 37), (135, 80, 32, 35), (170, 79, 32, 38),
        (206, 79, 26, 38), (238, 80, 24, 37), (263, 80, 30, 37),
        (295, 80, 36, 37), (334, 80, 32, 36), (370, 79, 29, 38),
    ))),
    Animation("달리기", tuple(Frame(*box) for box in (
        (1, 124, 33, 40), (39, 124, 35, 39), (89, 125, 35, 38),
        (130, 121, 34, 42), (181, 122, 34, 41), (228, 122, 33, 40),
    ))),
    Animation("회전", tuple(Frame(*box) for box in (
        (1, 169, 29, 30), (35, 167, 29, 31), (67, 169, 30, 29),
        (98, 169, 31, 29), (131, 168, 29, 30), (162, 168, 29, 31),
        (193, 170, 30, 29), (230, 170, 31, 29), (268, 170, 30, 30),
    ))),
    Animation("회전 공", tuple(Frame(*box) for box in (
        (1, 206, 30, 27), (36, 206, 29, 27), (70, 206, 29, 27),
        (105, 206, 29, 27), (139, 206, 29, 27), (174, 206, 29, 27),
    ))),
    Animation("질주", tuple(Frame(*box) for box in (
        (1, 239, 29, 35), (36, 239, 30, 35), (74, 239, 31, 35),
        (111, 238, 31, 36), (149, 239, 30, 35), (186, 238, 31, 36),
    ))),
    Animation("회전 질주", tuple(Frame(*box) for box in (
        (1, 283, 29, 35), (36, 283, 30, 35), (72, 286, 39, 31),
        (123, 285, 39, 32), (172, 286, 39, 31), (218, 285, 38, 32),
    ))),
    Animation("뒤돌기", tuple(Frame(*box) for box in (
        (1, 326, 24, 45), (31, 327, 29, 44), (65, 327, 20, 44),
        (90, 327, 25, 43), (119, 327, 25, 43), (149, 327, 20, 44),
    ))),
    Animation("넘어짐", (Frame(184, 341, 40, 28), Frame(232, 341, 39, 27))),
    Animation("균형잡기", tuple(Frame(*box) for box in (
        (1, 379, 27, 38), (31, 379, 31, 36), (64, 379, 31, 36),
        (99, 377, 33, 38), (136, 379, 32, 36), (176, 379, 33, 36),
        (217, 379, 33, 36), (254, 378, 33, 36),
    ))),
    Animation("놀라기", (Frame(6, 429, 34, 40), Frame(49, 426, 34, 43))),
    Animation("둘러보기", (Frame(96, 427, 23, 39), Frame(125, 427, 23, 39))),
)


ALL_FRAMES = tuple(frame for animation in ANIMATIONS for frame in animation.frames)
DISPLAY_SCALE = 4.0  # 가장 큰 자세의 높이 180픽셀 (기존 576픽셀).
GROUND_Y = 260
EDGE_MARGIN = max(f.width for f in ALL_FRAMES) * DISPLAY_SCALE / 2 + 24
TRAVEL_SPAN = CANVAS_WIDTH - 2 * EDGE_MARGIN
# 초당 이동 거리와 프레임 사이클당 튀어 오르는 높이.
MOTION_SPEEDS = {"걷기": 130, "달리기": 280, "회전": 180,
                 "회전 공": 220, "질주": 420, "회전 질주": 360}
HOP_HEIGHTS = {"회전": 45, "회전 공": 70, "넘어짐": 35, "놀라기": 20}


class AnimationPlayer:
    """대기 중에도 이벤트 처리를 유지하고, 남은 시간을 다음 상태로 넘긴다."""

    def __init__(self, animations=ANIMATIONS):
        if not animations or any(not animation.frames for animation in animations):
            raise ValueError("동작 목록과 프레임은 비어 있을 수 없습니다.")
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.elapsed = 0.0
        self.completed_cycles = 0
        self.state = "PLAYING"
        self.travel = TRAVEL_SPAN / 2
        self.motion_time = 0.0

    @property
    def x(self):
        phase = self.travel % (2 * TRAVEL_SPAN)
        return EDGE_MARGIN + (phase if phase <= TRAVEL_SPAN else 2 * TRAVEL_SPAN - phase)

    @property
    def direction(self):
        return 1 if self.travel % (2 * TRAVEL_SPAN) < TRAVEL_SPAN else -1

    @property
    def hop(self):
        duration = len(self.animation.frames) * FRAME_SECONDS
        phase = (self.motion_time % duration) / duration
        return HOP_HEIGHTS.get(self.animation.name, 0) * max(0.0, math.sin(2 * math.pi * phase))

    @property
    def animation(self):
        return self.animations[self.animation_index]

    @property
    def frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, dt):
        if not math.isfinite(dt):
            raise ValueError("경과 시간은 유한한 수여야 합니다.")
        remaining = max(0.0, dt)
        while remaining > 0:
            duration = PAUSE_SECONDS if self.state == "WAITING" else FRAME_SECONDS
            consumed = min(remaining, max(0.0, duration - self.elapsed))
            if self.state == "PLAYING":
                self.travel = (self.travel + MOTION_SPEEDS.get(self.animation.name, 0) * consumed) % (2 * TRAVEL_SPAN)
                self.motion_time += consumed
            self.elapsed += consumed
            remaining = max(0.0, remaining - consumed)
            if self.elapsed + 1e-9 < duration:
                break
            self.elapsed = max(0.0, self.elapsed - duration)
            if self.state == "WAITING":
                self.animation_index = (self.animation_index + 1) % len(self.animations)
                self.state = "PLAYING"
                self.completed_cycles = 0
                self.frame_index = 0
                self.motion_time = 0.0
                continue
            self.frame_index = (self.frame_index + 1) % len(self.animation.frames)
            if self.frame_index == 0:
                self.completed_cycles += 1
                if self.completed_cycles == REPEAT_COUNT:
                    self.frame_index = len(self.animation.frames) - 1
                    self.state = "WAITING"


def destination_rect(frame, player=None):
    x = player.x if player is not None else CANVAS_WIDTH / 2
    hop = player.hop if player is not None else 0
    return (x, GROUND_Y + hop + frame.height * DISPLAY_SCALE / 2,
            frame.width * DISPLAY_SCALE, frame.height * DISPLAY_SCALE)


def draw_frame(sprite, frame, player=None):
    flip = "h" if player is not None and player.direction < 0 else ""
    sprite.clip_composite_draw(*frame.clip_rect, 0, flip, *destination_rect(frame, player))


def validate_assets(path=SPRITE_PATH):
    try:
        with path.open("rb") as source:
            header = source.read(24)
    except OSError as error:
        raise ValueError(f"스프라이트를 읽을 수 없습니다: {path}: {error}") from error
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"올바른 PNG 파일이 아닙니다: {path}")
    if struct.unpack(">II", header[16:24]) != (SHEET_WIDTH, SHEET_HEIGHT):
        raise ValueError("스프라이트 크기가 프레임 좌표와 일치하지 않습니다.")
    for animation in ANIMATIONS:
        if not animation.frames:
            raise ValueError(f"빈 동작: {animation.name}")
        for frame in animation.frames:
            if not (frame.x >= 0 and frame.y >= 0 and frame.width > 0 and frame.height > 0
                    and frame.x + frame.width <= SHEET_WIDTH
                    and frame.y + frame.height <= SHEET_HEIGHT):
                raise ValueError(f"프레임 영역 오류: {animation.name}: {frame}")


def run_self_tests():
    """창 없이 실제 동작 데이터의 재생 경계와 표시 영역을 검사한다."""
    import unittest

    class ViewerTests(unittest.TestCase):
        def test_every_motion_five_cycles_and_one_second_pause(self):
            player = AnimationPlayer()
            for _ in range(2):
                for index, animation in enumerate(ANIMATIONS):
                    self.assertEqual(player.animation_index, index)
                    self.assertEqual(player.frame_index, 0)
                    self.assertEqual(player.completed_cycles, 0)
                    for cycle in range(REPEAT_COUNT):
                        player.update(len(animation.frames) * FRAME_SECONDS - 0.0001)
                        self.assertEqual(player.completed_cycles, cycle)
                        self.assertEqual(player.state, "PLAYING")
                        self.assertEqual(player.frame_index, len(animation.frames) - 1)
                        player.update(0.0001)
                        self.assertEqual(player.completed_cycles, cycle + 1)
                    self.assertEqual(player.state, "WAITING")
                    final_frame = player.frame
                    player.update(0.999)
                    self.assertEqual(player.state, "WAITING")
                    self.assertEqual(player.frame, final_frame)
                    player.update(0.001)
                    self.assertEqual(player.state, "PLAYING")
            self.assertEqual(player.animation_index, 0)

        def test_delayed_update_preserves_time_across_states(self):
            total = sum(len(a.frames) * FRAME_SECONDS * REPEAT_COUNT + PAUSE_SECONDS
                        for a in ANIMATIONS)
            player = AnimationPlayer()
            player.update(total * 100 + 0.25)
            self.assertEqual((player.animation_index, player.frame_index,
                              player.completed_cycles, player.state), (0, 2, 0, "PLAYING"))
            self.assertAlmostEqual(player.elapsed, 0.05, places=6)
            slow, fast = AnimationPlayer(), AnimationPlayer()
            for _ in range(10000):
                slow.update(0.01)
            fast.update(100)
            self.assertEqual((slow.animation_index, slow.frame_index, slow.state,
                              slow.completed_cycles),
                             (fast.animation_index, fast.frame_index, fast.state,
                              fast.completed_cycles))
            self.assertAlmostEqual(slow.elapsed, fast.elapsed)
            self.assertAlmostEqual(slow.x, fast.x, places=6)
            self.assertAlmostEqual(slow.hop, fast.hop, places=6)
            self.assertEqual(slow.direction, fast.direction)

        def test_motion_speed_and_stationary_poses(self):
            for name, distance in (("대기", 0), ("걷기", 65),
                                   ("달리기", 140), ("질주", 210)):
                animation = next(a for a in ANIMATIONS if a.name == name)
                player = AnimationPlayer((animation,))
                start = player.x
                player.update(0.5)
                self.assertAlmostEqual(player.x - start, distance)

        def test_bounce_and_pause_freeze(self):
            walk = next(a for a in ANIMATIONS if a.name == "걷기")
            player = AnimationPlayer((walk,))
            player.travel = TRAVEL_SPAN - 10
            player.update(0.2)
            self.assertEqual(player.direction, -1)
            self.assertAlmostEqual(player.x, CANVAS_WIDTH - EDGE_MARGIN - 16)
            player.update(len(walk.frames) * FRAME_SECONDS * REPEAT_COUNT - 0.2)
            frozen = (player.x, player.hop, player.direction)
            self.assertEqual(player.state, "WAITING")
            player.update(0.999)
            self.assertEqual((player.x, player.hop, player.direction), frozen)

        def test_moving_frames_stay_inside_canvas(self):
            player = AnimationPlayer()
            saw_hop = False
            for _ in range(6000):
                player.update(0.02)
                x, y, width, height = destination_rect(player.frame, player)
                self.assertGreaterEqual(x - width / 2, 0)
                self.assertLessEqual(x + width / 2, CANVAS_WIDTH)
                self.assertGreaterEqual(y - height / 2, 0)
                self.assertLessEqual(y + height / 2, CANVAS_HEIGHT)
                saw_hop |= player.hop > 0
            self.assertTrue(saw_hop)

        def test_single_frame_motion(self):
            player = AnimationPlayer((Animation("한 프레임", (ALL_FRAMES[0],)),))
            player.update(5 * FRAME_SECONDS)
            self.assertEqual((player.state, player.completed_cycles), ("WAITING", 5))
            player.update(PAUSE_SECONDS)
            self.assertEqual((player.state, player.completed_cycles, player.frame_index),
                             ("PLAYING", 0, 0))

        def test_assets_and_visible_bounds(self):
            validate_assets()
            self.assertEqual(len(ANIMATIONS), 13)
            self.assertEqual(len(ALL_FRAMES), 76)
            self.assertEqual([len(a.frames) for a in ANIMATIONS],
                             [9, 2, 12, 6, 9, 6, 6, 6, 6, 2, 8, 2, 2])
            for frame in ALL_FRAMES:
                x, y, width, height = destination_rect(frame)
                self.assertGreaterEqual(x - width / 2, 0)
                self.assertLessEqual(x + width / 2, CANVAS_WIDTH)
                self.assertGreaterEqual(y - height / 2, 0)
                self.assertLessEqual(y + height / 2, CANVAS_HEIGHT)
                self.assertAlmostEqual(width / height, frame.width / frame.height)
                self.assertGreaterEqual(height, 100)
                self.assertLessEqual(height, 180)

        def test_invalid_inputs(self):
            for animations in ((), (Animation("빈 동작", ()),)):
                with self.assertRaises(ValueError):
                    AnimationPlayer(animations)
            player = AnimationPlayer()
            player.update(-1)
            self.assertEqual(player.frame_index, 0)
            for dt in (float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    player.update(dt)
            with self.assertRaises(ValueError):
                validate_assets(SPRITE_PATH.with_name("__missing_sprite__.png"))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ViewerTests)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)


def main():
    validate_assets()
    import pico2d as p2

    p2.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        p2.hide_lattice()
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
            draw_frame(sprite, player.frame, player)
            p2.update_canvas()
            p2.delay(0.01)
    finally:
        p2.close_canvas()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="창 없이 재생 규칙 검증")
    args = parser.parse_args()
    if args.self_test:
        run_self_tests()
    else:
        try:
            main()
        except (ValueError, RuntimeError) as error:
            parser.exit(1, f"오류: {error}\n")
