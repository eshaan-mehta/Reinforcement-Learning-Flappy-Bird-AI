from game import *

is_running = True

g = Game()
        
while is_running: 
    dt = CLOCK.tick()

    screen.fill(BACKGROUND)

    g.update(dt)
    g.draw(screen)

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False

    pygame.display.update()
pygame.quit()

