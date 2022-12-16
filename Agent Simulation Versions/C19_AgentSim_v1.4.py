import pygame, sys, random
from pygame.locals import *
import numpy as np

WIDTH = 1000
HEIGHT = 700
FPS = 5
pxlSize = 10
screen = pygame.display.set_mode((WIDTH,HEIGHT))

class Agent:

    def __init__(self):
        self.x = random.randrange(10,WIDTH-10) # rand pos x
        self.y = random.randrange(10,HEIGHT-10) # rand pos y
        self.center = pygame.Vector2(self.x, self.y)
        self.vector = pygame.Vector2()
        self.vector.from_polar((1, 0))
        self.turn_speed = 40
        self.speed = 50
        self.angle = 0

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
    
    def move(self,delta):
        rotate = 0
        forward = 0

        if(np.random.choice([0,1],1,p=[0.50,0.50]) == 0):
            rotate -= 1
        else:
            rotate += 1

        if(np.random.choice([0,1],1,p=[0.90,0.10]) == 0):
            forward += 1
        else:
            forward -= 1

        if rotate != 0:
            self.angle += delta * self.turn_speed * rotate
            #self.image = pygame.transform.rotate(self.oimage, -self.angle)
            #self.rect = self.image.get_rect(center=self.rect.center)
            self.vector.from_polar((1, self.angle))

        if forward != 0:
            self.center += forward * self.vector * delta * self.speed
            #self.rect.center = self.center

agents = []
for i in range(3):
    Agents = Agent()
    agents.append(Agents)

class Sim:
    def __init__(self):
        self.delta = 0

    def mainLoop():
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((255, 255, 255))
        
            for idx, i in enumerate(agents):
                # draw agent with update position
                i.move(0)
                i.draw()
                # print("##################")

            pygame.display.update() 
            pygame.time.Clock().tick(FPS)

Sim.mainLoop()
        