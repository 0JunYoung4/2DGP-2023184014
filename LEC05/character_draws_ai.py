"""캐릭터가 원, 사각형, 삼각형을 차례로 무한 반복한다."""

import math
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN, SDLK_ESCAPE, SDL_QUIT,
    clear_canvas, close_canvas, delay, get_events,
    load_image, open_canvas, update_canvas,
)


def circle_points():
    for degree in range(361):
        angle = math.radians(degree)
        yield 400 + 200 * math.cos(angle), 300 + 200 * math.sin(angle)


def polygon_points(vertices):
    for start, end in zip(vertices, vertices[1:] + vertices[:1]):
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        steps = max(1, math.ceil(distance / 5))
        for step in range(steps + 1):
            t = step / steps
            yield (
                start[0] + (end[0] - start[0]) * t,
                start[1] + (end[1] - start[1]) * t,
            )


def main():
    rectangle = [(50, 550), (750, 550), (750, 50), (50, 50)]
    triangle = [(100, 100), (700, 100), (400, 500)]
    open_canvas(800, 600)
    try:
        image_path = Path(__file__).resolve().parent / 'character.png'
        character = load_image(str(image_path))
        while True:
            for path in (circle_points(), polygon_points(rectangle), polygon_points(triangle)):
                for x, y in path:
                    for event in get_events():
                        if event.type == SDL_QUIT:
                            return
                        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                            return
                    clear_canvas()
                    character.draw(x, y)
                    update_canvas()
                    delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
