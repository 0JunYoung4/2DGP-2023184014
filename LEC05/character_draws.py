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

def move_circle():
  x,y=circle_position(0)
  clear_canvas()
  boy.draw(x, y)
  update_canvas()

def move_rectangle():
    print('rectangle')

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