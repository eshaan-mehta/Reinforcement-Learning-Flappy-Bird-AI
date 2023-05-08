from player import PlayerManager
from poles import PoleManager
from model import *

class Game:
    bold_font = pygame.font.Font("fonts/SourceSansPro-Bold.ttf", 104)
    outline_font = pygame.font.Font("fonts/SourceSansPro-Bold.ttf", 110)
    light_font = pygame.font.Font("fonts/SourceSansPro-Light.ttf", 20)

    game_speed = 0.1
    score_pos = (S_WIDTH/2, 50)

    ground_height = 60
    ground_color = (158, 95, 12)
    ground_image = pygame.transform.scale(pygame.image.load("sprites/world/ground.png"), (S_WIDTH, ground_height))

    def __init__(self):
        self.players = PlayerManager()
        self.poles = PoleManager(self.ground_height)
        
        self.reset()
        
    def reset(self, et_diff = 0, generation = 1, initial_round = True):
        self.game_started = False
        self.elapsed_time = 0
        self.elapsed_time_difference = et_diff
        self.elapsed_time_intermediate = et_diff
        self.generation = generation

        self.speed_is_increasing = False

        self.score = 0
        self.score_has_increased = False

        self.players.reset(initial_round)
        self.poles.reset(self.game_speed)

    def round_over(self):
        self.poles.clear()
        #self.players.models.check_mutation_rate()

        self.reset(pygame.time.get_ticks(), self.generation + 1, initial_round = False)

    def text_update(self):
        self.fps_text = self.light_font.render("FPS: " + str(int(CLOCK.get_fps())), True, (0,0,0))
        self.gen_text = self.light_font.render("Generation: " + str(self.generation), True, (0,0,0))
        self.num_players_text = self.light_font.render("Players Alive: " + str(len(self.players.players)), True, (0,0,0))
        
        self.score_text = self.bold_font.render(str(self.score), True, (255,255,255))
        self.outline_font.set_bold(True)
        self.outline_text = self.outline_font.render(str(self.score), True, (0,0,0))
        self.score_text_rect = self.score_text.get_rect()
        self.outline_text_rect = self.outline_text.get_rect()
        self.score_text_rect.center = self.outline_text_rect.center = self.score_pos

    def update(self, dt):
        pressed = pygame.key.get_pressed()[K_SPACE] or pygame.mouse.get_pressed()[0]
        time_passed = self.elapsed_time_difference - self. elapsed_time_intermediate

        #manually or autostarting each round 
        if pressed or time_passed > 1700:
            self.game_started = True

        #updating all the UI text elements
        self.text_update()

        if self.game_started:
            #calculating elapsed time (in deciseconds), since each round begins
            #elapsed_time_difference used to compensate for time difference since pygame.init()
            self.elapsed_time = (pygame.time.get_ticks() - self.elapsed_time_difference) // 100
            self.elapsed_time /= 10

            #if no players alive, end round
            if not self.players.check_num_players():
                self.round_over()
                return
            
            #score incrementation, once first bird hasc crossed the center of the pole
            if self.poles.poles[0].center[0] < self.players.players[0].hitbox.centerx and not self.score_has_increased:
                self.score += 1
                self.score_has_increased = True
            if self.poles.poles[0].tophor.left > self.players.players[0].hitbox.right and self.score_has_increased:
                self.score_has_increased = False
            
            #updating player and pole variables
            self.players.update(dt, S_HEIGHT - self.ground_height, self.poles.poles, self.elapsed_time, self.score)
            self.poles.update(dt, self.game_speed)
        else:
            self.elapsed_time_difference = pygame.time.get_ticks()

        
    def draw(self, screen):
        #drawing all elements to screen
        screen.blit(self.ground_image, (0, S_HEIGHT - self.ground_height))
        self.poles.draw(screen)
        self.players.draw(screen)

        screen.blit(self.fps_text, (5, 5))
        screen.blit(self.gen_text, (5, 38))
        screen.blit(self.num_players_text, (5, 71))

        screen.blit(self.outline_text, self.outline_text_rect.topleft)
        screen.blit(self.score_text, self.score_text_rect.topleft)
