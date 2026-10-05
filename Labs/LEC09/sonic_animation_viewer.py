"""Sonic 스프라이트 애니메이션 뷰어.

실행: python Labs/LEC09/sonic_animation_viewer.py
"""


CANVAS_WIDTH, CANVAS_HEIGHT = 1280, 720


def main():
    import pico2d as p2

    p2.open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        p2.clear_canvas()
        p2.update_canvas()
    finally:
        p2.close_canvas()


if __name__ == "__main__":
    main()
