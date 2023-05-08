import pygame, math, random

from pygame.locals import *

pygame.init()

S_WIDTH, S_HEIGHT = 600, 760
BACKGROUND = (135, 206, 255)

CLOCK = pygame.time.Clock()

screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
pygame.display.set_caption("AI learns Flappy Bird")


