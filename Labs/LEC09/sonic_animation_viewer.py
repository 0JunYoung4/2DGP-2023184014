"""Sonic 스프라이트 애니메이션 뷰어.

실행: python Labs/LEC09/sonic_animation_viewer.py
"""


from pathlib import Path


CANVAS_WIDTH, CANVAS_HEIGHT = 1280, 720
SPRITE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")
SHEET_WIDTH, SHEET_HEIGHT = 399, 525
# 시트 조사: 제목(상단)과 크레딧/장식(470행 이후)은 동작에서 제외한다.
# 시트 순서: 대기 9, 웅크리기 2, 걷기 12, 달리기 6, 회전 9,
# 회전 공 6, 질주 6, 회전 질주 6, 뒤돌기 6, 넘어짐 2,
# 균형잡기 8, 놀라기 2, 둘러보기 2. 총 13개 동작, 86개 프레임.
# 동작 이름은 뷰어에서 식별하기 위한 이름이며 원작의 공식 명칭은 아니다.


def main():
    import pico2d as p2

    p2.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        try:
            sprite = p2.load_image(str(SPRITE_PATH))
        except Exception as error:
            raise RuntimeError(f"스프라이트 로딩 실패: {SPRITE_PATH}: {error}") from error
        running = True
        while running:
            for event in p2.get_events():
                if event.type == p2.SDL_QUIT:
                    running = False
                elif event.type == p2.SDL_KEYDOWN and event.key == p2.SDLK_ESCAPE:
                    running = False
            p2.clear_canvas()
            p2.update_canvas()
            p2.delay(0.01)
    finally:
        p2.close_canvas()


if __name__ == "__main__":
    main()
