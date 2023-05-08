from setup import *
from model import *

class Player:
    gravity = 0.002
    jump_power = 0.6

    width, height = 60, 40

    index_font = pygame.font.Font("fonts/SourceSansPro-Regular.ttf", 30)

    #images for the animation
    frames_per_animation = 100
    images = (pygame.image.load("sprites/player/bird1.png"),
              pygame.image.load("sprites/player/bird2.png"),
              pygame.image.load("sprites/player/bird3.png"),
              pygame.image.load("sprites/player/bird4.png"),
              pygame.image.load("sprites/player/bird3.png"),
              pygame.image.load("sprites/player/bird2.png"))
    
    def __init__(self, spawn_x, spawn_y, i):
        self.d = pygame.Vector2(spawn_x, spawn_y)
        self.v = pygame.Vector2(0, 0)
        self.a = pygame.Vector2(0, self.gravity)

        self.hitbox = pygame.Rect(self.d.x, self.d.y, self.width, self.height)
        self.hitbox.center = self.d

        self.is_jumping = False
        self.time_alive = 0
        self.fitness = 0

        #player number is shown on their body
        self.index = i
        self.index_object = self.index_font.render(str(self.index), True, (0,0,0))
        self.index_object_rect = self.index_object.get_rect()
        self.index_object_rect.center = self.d

        self.image_index = 0
        self.cur_image = self.images[0]

        self.brain = NN()#creating a model for the player

    def jump(self):
        self.v.y = -self.jump_power

    def is_colliding(self, ground, poles):
        #ground collision
        if self.hitbox.bottom > ground:
            return True
        
        #goes off top of screen
        if self.hitbox.top < 0:
            return True

        #pole collision
        for pole in poles:
            #only checking the upcoming pole to reduce computation times
            if pole.tophor.left < S_WIDTH/2 and pole.tophor.right > 0:
                for piece in pole.pieces: 
                    if self.hitbox.colliderect(piece):
                        return True
                    
        return False

    def update(self, dt):
        #updating all variables each frame
        self.d += self.v * dt
        self.v += self.a * dt

        self.is_jumping = True if self.v.y < 0 else False

        self.image_index += 1 / self.frames_per_animation * dt 
        self.cur_image = self.images[int(self.image_index) % len(self.images)]

        self.hitbox.center = self.d
        self.index_object = self.index_font.render(str(self.index), True, (0,0,0))
        self.index_object_rect = self.index_object.get_rect()
        self.index_object_rect.center = self.d

    def draw(self, screen):
        screen.blit(self.cur_image, self.hitbox.topleft)
        screen.blit(self.index_object, self.index_object_rect.topleft)



class PlayerManager:
    num_players = 50
    max_pole_dist = 500

    spawn_x, spawn_y = S_WIDTH/5, S_HEIGHT * 5/12
    
    def __init__(self):
        self.players = []
        self.models = NNManager()
        self.crossover_weights = []

    def reset(self, initial):
        #creating all the players
        for i in range(self.num_players):
            self.add_new_player(i, initial)

    def add_new_player(self, i, initial_round):
        p = Player(self.spawn_x, self.spawn_y, i)

        #after first generation, adding the new weights for the player brain
        if not initial_round:
            if i < 2:
                weights = self.models.best_fit_stats[i][1]
            else:
                if i % 2 == 0:
                    self.crossover_weights = self.models.sibling_crossover()
                weights = self.models.mutate(self.crossover_weights[i%2])

            # weights = self.models.single_crossover()
            # weights = self.models.mutate(weights)
            p.brain.model.set_weights(weights)
        self.players.append(p)

    def del_player(self, player):
        #deleting player from memory
        self.players.remove(player)
        
        for entry in self.models.best_fit_stats:
            print('fitness:', entry[0], "\t\tIndex:", entry[2])
        print('\n')

        #del player

    def check_num_players(self):
        #see if any players are alive
        return len(self.players) != 0

    def update(self, dt, ground_level, poles, et, game_score):
        for player in self.players:
            #calculating next pole, for model inputs
            if poles[0].bottomhor.left > player.hitbox.right:
                next_pole = poles[0]
            else:
                next_pole = poles[1]

            #update player variables only if alive, else pass it player stats to NNManager
            if not player.is_colliding(ground_level, poles): #can't use next_pole here as need to check with current pole as well
                player.update(dt)

                y_range = ground_level - player.hitbox.height - 2*next_pole.tophor.height
                x_range = S_WIDTH - player.hitbox.right

                x_dist = (next_pole.tophor.left - player.hitbox.right) / x_range
                top_dist = abs(player.hitbox.bottom - next_pole.tophor.bottom) / y_range
                bottom_dist = abs(next_pole.bottomhor.top - player.hitbox.bottom) / y_range
                
                player_y = (ground_level - player.hitbox.bottom) / ground_level 
                pole_y = (ground_level - next_pole.bottomhor.top) / ground_level
                dist = math.dist(player.hitbox.center, next_pole.center) / self.max_pole_dist

                #if player.brain.predict_action2(x_dist, player.v.y, top_dist, bottom_dist):
                if player.brain.predict_action1(player_y - 0.5, player.v.y - 0.5, pole_y - 0.5, dist - 0.5):
                    player.jump()
            else:
                player.time_alive = et
                player.fitness = self.models.update_best_weights(player, next_pole.center, game_score)
                self.del_player(player)

    def draw(self, screen):
        for player in self.players:
            player.draw(screen)