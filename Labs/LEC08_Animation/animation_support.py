"""프레임 정보와 재생 상태. Pico2D 없이도 검증할 수 있다."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Frame:
    # PNG 왼쪽 위 기준의 영역. anchor는 영역 안의 발 기준점이다.
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
