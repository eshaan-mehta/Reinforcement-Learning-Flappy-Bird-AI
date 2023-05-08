from setup import *

#room to work with is 600 pixels

class Pole:
    border_thickness = 2
    gap_size = 190

    color = (50, 135, 25)

    ver_width = 90
    hor_width, hor_height = 100, 20
    diff = (hor_width - ver_width)/2

    score_dim = 50

    def __init__(self, level, spawn_x, speed, sky_range):
        #all four rectangles in each pole
        self.topvert = pygame.Rect(spawn_x, 0, self.ver_width, level)
        self.tophor = pygame.Rect(self.topvert.left - self.diff, self.topvert.bottom - self.border_thickness, self.hor_width, self.hor_height)
        self.bottomhor = pygame.Rect(self.tophor.left, self.tophor.bottom + self.gap_size, self.hor_width, self.hor_height)
        self.bottomvert = pygame.Rect(spawn_x, self.bottomhor.bottom - self.border_thickness, self.ver_width, sky_range - self.bottomhor.bottom + self.border_thickness)

        self.d = pygame.Vector2(spawn_x, 0)
        self.v = pygame.Vector2(-speed, 0)

        self.center = (self.tophor.centerx, self.tophor.bottom + self.gap_size/2)

        #creating a list with those four pieces
        self.pieces = [self.topvert, self.tophor, self.bottomhor, self.bottomvert]  



    def update(self, dt, speed):
        #updating all variables
        self.d += self.v * dt
        self.v.x = -speed

        self.topvert.topleft = self.d
        self.tophor.left = self.topvert.left - self.diff
        self.bottomhor.left = self.tophor.left
        self.bottomvert.left = self.topvert.left

        self.center = (self.tophor.centerx, self.tophor.bottom + self.gap_size/2)


    def is_on_screen(self):
        #checking if pole is visible on screen
        return self.tophor.left < S_WIDTH and self.tophor.right > 0

    def draw(self, screen):
        #drawing the pole if on screen
        if self.is_on_screen():
            for piece in self.pieces:
                pygame.draw.rect(screen, self.color, piece) #rectangle
                pygame.draw.rect(screen, (0,0,0), piece, self.border_thickness) #outline


class PoleManager:
    interval = 200 #distance between adjacent poles

    init_pole_dist = S_WIDTH + 100
    min_pole_height = 40
    num_pole_heights = 6
    num_total_poles = S_WIDTH // (interval + Pole.ver_width) + 1


    def __init__(self, ground_height):
        self.poles = []
        self.sky_range = S_HEIGHT - ground_height

        #all possible heights where gaps can spawn
        self.levels = self.calculate_levels()

    def reset(self, speed):
        #adding all initial poles
        for i in range(self.num_total_poles):
            self.add_new_pole(speed)
            

    def calculate_levels(self):
        l = []

        #interval between each hole height difference
        difference = (self.sky_range - 2*self.min_pole_height - 2*Pole.hor_height - Pole.gap_size) /  (self.num_pole_heights - 1)
        
        for i in range(self.num_pole_heights):
            l.append(self.min_pole_height + i*difference)
        
        return l  
        
    def add_new_pole(self, speed):
        if len(self.poles) == 0: #pole starting x upon reset
            spawn_x = self.init_pole_dist 
            prev_index = -1
            level_index = random.randint(2, 3)
        else:   #pole starting x when adding new pole
            spawn_x = self.poles[-1].topvert.right + self.interval
            prev_index = self.levels.index(self.poles[-1].topvert.height)
            level_index = random.randint(0, self.num_pole_heights - 1)

        #level_index and prev_index are used to make sure to consectutive poles aren't at the same height
        while level_index == prev_index:
            level_index = random.randint(0, self.num_pole_heights - 1)

        #adding new pole to list
        self.poles.append(Pole(self.levels[level_index], spawn_x, speed, self.sky_range))

    def clear(self):
        #emptying poles list
        self.poles.clear()

    def del_pole(self, pole):
        self.poles.remove(pole)
        del pole

    def update(self, dt, speed):
        #updating variables of all poles
        for pole in self.poles:
            pole.update(dt, speed)

            #deleting front pole in list once past left of screen
            if not pole.is_on_screen() and pole.d.x < S_WIDTH:
                self.del_pole(pole)
                self.add_new_pole(speed)

    def draw(self, screen):
        #drawing poles to screen
        for pole in self.poles:
            pole.draw(screen)
