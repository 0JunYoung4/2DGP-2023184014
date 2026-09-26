import math
from pico2d import* 

WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH//2
CENTER_Y = HEIGHT//2
RADIUS = 200

RECT_LEFT = 50
RECT_RIGHT = 750
RECT_BOTTOM = 50
RECT_TOP = 550

TRI_A = (100, 100)
TRI_B = (700, 100)
TRI_C = (400, 500)

TEST_MODE = 'triangle'

def circle_position(degree):
    theta = math.radians(degree)
    x = CENTER_X + RADIUS * math.cos(theta)
    y = CENTER_Y + RADIUS * math.sin(theta)
    return x, y

def draw_boy(x, y):
    clear_canvas()
    boy.draw(x, y)
    update_canvas()
    delay(0.01)

def move_circle():
    for degree in range(361):
        x, y = circle_position(degree)
        draw_boy(x, y)

def move_top():
    for x in range(RECT_LEFT, RECT_RIGHT + 1, 5):
        draw_boy(x, RECT_TOP)


def move_right():
    for y in range(RECT_TOP, RECT_BOTTOM - 1, -5):
        draw_boy(RECT_RIGHT, y)


def move_bottom():
    for x in range(RECT_RIGHT, RECT_LEFT - 1, -5):
        draw_boy(x, RECT_BOTTOM)


def move_left():
    for y in range(RECT_BOTTOM, RECT_TOP + 1, 5):
        draw_boy(RECT_LEFT, y)

def move_rectangle():
    move_top()
    move_right()
    move_bottom()
    move_left()

def move_ab():
    print('A -> B')


def move_bc():
    print('B -> C')


def move_ca():
    print('C -> A')


def move_triangle():
    move_ab()
    move_bc()
    move_ca()

open_canvas(WIDTH, HEIGHT)

boy = load_image('character.png')



if TEST_MODE == 'circle':
    move_circle()
elif TEST_MODE == 'rectangle':
    move_rectangle()
elif TEST_MODE == 'triangle':
    move_triangle()
else:
    move_circle()
    move_rectangle()
    move_triangle()

delay(1)
close_canvas()