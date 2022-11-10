##### UPDATE TRACKER #####
# Implemented a radius check to calcDistance for objects too far away from the agent.

import math
import pygame, sys
from pygame.locals import *
import time
import numpy as np
import random

##### Variables #####

WIDTH = 600
HEIGHT = 600
FPS = 60
pxlSize = 5
screen = pygame.display.set_mode((WIDTH,HEIGHT))

##### Define Agent #####

class Agent: 
    def __init__(self):
        self.x = random.randrange(10,WIDTH-10) # rand pos x
        self.y = random.randrange(10,HEIGHT-10) # rand pos y
        self.speed = random.randrange(2,5) #cell speed
        self.move = [None, None] #realtive x and y coordinates to move to
        self.direction = None #movement direction

    def draw(self):
        pygame.draw.circle(screen, (32, 32, 0), (self.x,self.y), pxlSize) #draw the cell

# keep code wander algorithm, and create a way to switch between.

    def wander(self):
        directions = {"S":((-1,2),(1,self.speed)),"SW":((-self.speed,-1),(1,self.speed)),"W":((-self.speed,-1),(-1,2)),"NW":((-self.speed,-1),(-self.speed,-1)),"N":((-1,2),(-self.speed,-1)),"NE":((1,self.speed),(-self.speed,-1)),"E":((1,self.speed),(-1,2)),"SE":((1,self.speed),(1,self.speed))} #((min x, max x)(min y, max y))
        directionsName = ("S","SW","W","NW","N","NE","E","SE") #possible directions
        if random.randrange(0,5) == 2: #move about once every 5 frames
            if self.direction == None: #if no direction is set, set a random one
                self.direction = random.choice(directionsName)
            else:
                a = directionsName.index(self.direction) #get the index of direction in directions list
                b = random.randrange(a-1,a+2) #set the direction to be the same, or one next to the current direction
                if b > len(directionsName)-1: #if direction index is outside the list, move back to the start
                    b = 0
                self.direction = directionsName[b]
            self.move[0] = random.randrange(directions[self.direction][0][0],directions[self.direction][0][1]) #change relative x to a random number between min x and max x
            self.move[1] = random.randrange(directions[self.direction][1][0],directions[self.direction][1][1]) #change relative y to a random number between min y and max y
        if self.x < 5 or self.x > WIDTH - 5 or self.y < 5 or self.y > HEIGHT - 5: #if cell is near the border of the screen, change direction
            if self.x < 5:
                self.direction = "E"
            elif self.x > WIDTH - 5:
                self.direction = "W"
            elif self.y < 5:
                self.direction = "S"
            elif self.y > HEIGHT - 5:
                self.direction = "N"
            self.move[0] = random.randrange(directions[self.direction][0][0],directions[self.direction][0][1]) #change relative x to a random number between min x and max x
            self.move[1] = random.randrange(directions[self.direction][1][0],directions[self.direction][1][1]) #change relative x to a random number between min x and max x
        if self.move[0] != None: #add the relative coordinates to the cells coordinates
            self.x += self.move[0]
            self.y += self.move[1]
    
    def calcDistance(self): # Calculate distance to other Agents within a set area
        for idx, obj in enumerate(agents):
            if(obj.x > self.x+10 or obj.x < self.x-10 and obj.y > self.x+10 or obj.y < self.x-10):
                print("too far")
            else: 
                if (self.x == obj.x and self.y == obj.y):
                    print("self")
                else: 
                    print(idx, math.sqrt((self.x - obj.x)**2 + (self.y - obj.y)**2)) # Calculates distance between self and other agents.
                    #pygame.draw.line(screen, (32,32,0), (self.x, self.y), (obj.x, obj.y))
        

agents = []
for i in range(10):
    Agents = Agent()
    agents.append(Agents)

##### Game Loop #####

def gameLoop(): 
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))
        
        for i in agents:
            i.wander()  # agent random walk
            i.draw()    # draw agent with update position
            i.calcDistance()
            print("##################")

        pygame.display.update() 
        pygame.time.Clock().tick(FPS)

gameLoop()
        
