from setup import *
from keras.models import Sequential
from keras.layers import Dense
import numpy as np


class NN:
    input_size = 4
    hidden_size = 8
    output_size = 1

    def __init__(self):
        #creating the model
        self.model = Sequential()

        self.model.add(Dense(self.input_size, activation = 'relu', input_shape = (self.input_size, )))
        self.model.add(Dense(self.hidden_size, activation = 'relu', input_shape = (self.input_size, )))
        self.model.add(Dense(self.output_size, activation = 'sigmoid', input_shape = (self.hidden_size, )))

        self.model.compile(optimizer = 'adam', loss = 'mse')
        self.print = False

    def predict_action1(self, player_y, player_v, pole_height, dist):
        #formatting the input into a matrix
        input = np.asarray([player_y, player_v, pole_height, dist])
        input = np.atleast_2d(input)

        #if model returns value less than 0.5, jump
        return self.copy_predict(input) < 0.5
    
    def predict_action2(self, x_dist, player_v, top_dist, bottom_dist):
        #formatting the input into a matrix
        input = np.asarray([x_dist, player_v, top_dist, bottom_dist])
        input = np.atleast_2d(input)

        #if model returns value less than 0.5, jump
        return self.copy_predict(input) < 0.5
    
    def copy_predict(self, x):
        w = self.model.get_weights()

        #actions are hardcoded based on model initialization 
        #hardcoding it provides a massive performance increase
        #this function is accurate to model.predict() up to 5 decimal places
        x = x @ w[0] + w[1]             #dense
        x[x<0] = 0                      #relu
        x = x @ w[2] + w[3]             #dense
        x[x<0] = 0                      #relu
        x = x @ w[4] + w[5]             #dense
        x = 1 / (1 + np.exp(-x))        #sigmoid

        return x[0][0]


class NNManager:
    num_parents = 2
    time_scalar = 50
    score_scalar = 500
    distance_scalar = 0.25

    base_mutation_chance = 0.05
    max_same_fitness_rounds = 10

    def __init__(self):
        self.best_fit_stats = []
        self.next_gen_weights = []
        self.prev_best_fitness = []
        
        self.mutation_chance = self.base_mutation_chance
        self.num_rounds_with_same_fitness = 0

    def update_best_weights(self, player, next_pole_center, game_score):
        #distance from player center to pole center
        dist = math.dist(player.hitbox.center, next_pole_center)

        #player fitness calculation
        fitness = self.time_scalar*player.time_alive + self.score_scalar*game_score - self.distance_scalar*dist

        #each entry contains the weights and the fitness of the bird
        new_entry = [fitness, player.brain.model.get_weights(), player.index]

        #first two birds
        if len(self.best_fit_stats) < self.num_parents:
            self.best_fit_stats.append(new_entry)
            self.best_fit_stats.sort(key = lambda entry: entry[0], reverse = True)  #sorts the list in decreasing order depending on fitness
            
            for entry in self.best_fit_stats:
                self.prev_best_fitness.append(entry[0])
            return fitness
        
        #all other birds, checking if they are fitter than the current birds
        for i in range(len(self.best_fit_stats)):
            if fitness > self.best_fit_stats[i][0]:
                self.best_fit_stats.insert(i, new_entry)
                self.best_fit_stats.pop(-1)

                #self.prev_best_fitness = [self.best_fit_stats[0][0], self.best_fit_stats[1][0]]
                return fitness
            
    def sibling_crossover(self):
        child1_weights = self.best_fit_stats[0][1] #best bird
        child2_weights = self.best_fit_stats[1][1] #second best bird

        gene = random.randint(0, len(child1_weights) - 1)

        #swapping random genes to create a mix of parents genetics in the children
        temp = child1_weights[gene]
        child1_weights[gene] = child2_weights[gene]
        child2_weights[gene] = temp

        return [child1_weights, child2_weights]

    def single_crossover(self):
        parent1_weights = self.best_fit_stats[0][1] #best bird
        parent2_weights = self.best_fit_stats[1][1] #second best bird
        child = []

        parent1_fitness = self.best_fit_stats[0][0]
        parent2_fitness = self.best_fit_stats[1][0]

        #percent_diff = (parent1_fitness - parent2_fitness)/parent1_fitness + 0.5
        

        for i in range(len(parent1_weights)):
            if random.uniform(0, 1) < 0.5:
                child.append(parent1_weights[i]) 
            else:
                child.append(parent2_weights[i])
        
        return np.asarray(child, dtype= list)

    def check_mutation_rate(self):
        if self.num_rounds_with_same_fitness >= self.max_same_fitness_rounds:
            self.mutation_chance += 0.02
            self.num_rounds_with_same_fitness = 0
        
        if self.prev_best_fitness[0] == self.best_fit_stats[0][0] and self.prev_best_fitness[1] == self.best_fit_stats[1][0]:
            self.num_rounds_with_same_fitness += 1
        else:
            self.num_rounds_with_same_fitness = 0
            self.mutation_chance = self.base_mutation_chance

        print(self.mutation_chance, self.num_rounds_with_same_fitness)

        
    def mutate(self, child_weights):
        #adding mutation to the brains of the children
        #randomly changing an individual weight of a child to simulate mutation
        for weight in child_weights:
            for w in weight:
                if random.uniform(0, 1) <= self.mutation_chance:
                    delta_change = random.uniform(-0.5, 0.5)
                    w += delta_change

        return child_weights

