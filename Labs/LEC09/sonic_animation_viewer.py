"""Sonic 스프라이트 애니메이션 뷰어.

실행: python Labs/LEC09/sonic_animation_viewer.py
"""


from pathlib import Path


CANVAS_WIDTH, CANVAS_HEIGHT = 1280, 720
SPRITE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")


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
