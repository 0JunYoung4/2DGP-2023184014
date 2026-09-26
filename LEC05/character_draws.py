from pico2d import* 

WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH//2
CENTER_Y = HEIGHT//2

def move_circle():
   print('circle')

def move_rectangle():
    print('rectangle')

def move_triangle():
    print('triangle')

open_canvas(WIDTH, HEIGHT)

boy = load_image('character.png')

clear_canvas()
boy.draw(CENTER_X, CENTER_Y)
update_canvas()

while True:
    move_circle()
    move_rectangle()
    move_triangle()
    break

delay(1)
close_canvas()