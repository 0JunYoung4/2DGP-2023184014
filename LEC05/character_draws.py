import math
from pico2d import* 

WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH//2
CENTER_Y = HEIGHT//2
RADIUS = 200

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
    for x in range(50,751,5):
        draw_boy(x,550)

def move_right():
    for y in range(550, 49, -5):
        draw_boy(750, y)

def move_bottom():
    print('bottom')

def move_left():
    print('left')

def move_rectangle():
    move_top()
    move_right()
    move_bottom()
    move_left()

def move_triangle():
    print('triangle')

open_canvas(WIDTH, HEIGHT)

boy = load_image('character.png')



while True:
    move_circle()
    move_rectangle()
    move_triangle()
    break

delay(1)
close_canvas()