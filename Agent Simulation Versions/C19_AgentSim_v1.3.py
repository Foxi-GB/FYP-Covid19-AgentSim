##### UPDATE TRACKER #####
# Implemented a radius check to calcDistance for objects too far away from the agent.

import math
from math import sin, cos
import pygame, sys
from pygame.locals import *
import time
import numpy as np
import random
from csv import writer

##### Variables #####

WIDTH = 1000
HEIGHT = 700
FPS = 5
pxlSize = 10
screen = pygame.display.set_mode((WIDTH,HEIGHT))

##### Define Agent #####

class Agent: 

    def __init__(self, id):
        self.id = id
        self.x = random.randrange(10,WIDTH-10) # rand pos x
        self.y = random.randrange(10,HEIGHT-10) # rand pos y
        self.pos = [self.x , self.y]
        self.rotation = 0
        # self.speed = random.randrange(2,5) #cell speed
        # self.move = [None, None] #realtive x and y coordinates to move to
        # self.direction = None #movement direction
        self.infected = bool(np.random.choice([0,1],1,p=[0.90,0.10]))

    def draw(self):

        pygame.draw.circle(screen, (32, 32, 32), (self.x,self.y), pxlSize)
        
        # First Attempt - Vector Circles to Draw XY coordinates
        # Rotation point for polygon X
        vecX = pygame.math.Vector2(0, 0).rotate(self.rotation)
        ptX_x, ptX_y = self.x + vecX.x, self.y + vecX.y

        # Rotation point for polygon Y
        vecY = pygame.math.Vector2(0, 25).rotate(self.rotation - 10)
        ptY_x, ptY_y = ptX_x + vecY.x, ptX_y + vecY.y

        # Rotation point for polygon Y
        vecZ = pygame.math.Vector2(0, 25).rotate(self.rotation + 10)
        ptZ_x, ptZ_y = ptX_x + vecZ.x, ptX_y + vecZ.y


        pygame.draw.polygon(screen, (255,0,0), ((ptX_x, ptX_y), (ptY_x, ptY_y), (ptZ_x, ptZ_y))) # Draw Cone

        # # Second Attempt - Draw Line from Centre of Circle
        # angle_rad = math.radians(self.rotation)
        # ptX_x = self.x + (pxlSize/2) * math.sin(angle_rad)
        # ptX_y = self.y - (pxlSize/2) * math.cos(angle_rad)  

        # line = pygame.draw.line(screen, (255, 0, 0), (self.x, self.y),(ptX_x, ptX_y), width = 5) 

        # # Rotation point for polygon X
        # vecX = pygame.math.Vector2(0, -pxlSize)
        # ptX_x, ptX_y = self.x + vecX.x, self.y + vecX.y

        # pygame.draw.polygon(screen, (255,0,0), ((ptX_x, ptX_y), (ptX_x + 50, ptX_y + 20), (ptX_x + 20, ptX_y + 50)))


    def move(self):
        self.rotation += random.randrange(-90,90)


agents = []
for i in range(3):
    Agents = Agent(id = i)
    agents.append(Agents)

##### Game Loop #####

def gameLoop(): 
    tStep = 0  
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))
        
        for idx, i in enumerate(agents):
            # draw agent with update position
            i.move()
            i.draw()
            # print("##################")

        pygame.display.update() 
        pygame.time.Clock().tick(FPS)

gameLoop()
        
