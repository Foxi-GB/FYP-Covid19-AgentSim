import pygame, sys, random
from pygame.locals import *
import numpy as np

WIDTH = 800
HEIGHT = 600
FPS = 60
agentSize = 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Agent:
    def __init__(self):
        # Agent Coordinates
        self.x = random.randrange(10, WIDTH -10)
        self.y = random.randrange(10, HEIGHT -10)
        self.pos = [self.x, self.y]

        # Agent Rotation
        self.rotation = 0 

        # Agent Infected
        self.infected = bool(np.random.choice([0,1],1,p=[0.90,0.10]))

    def draw(self):
        if(self.infected):
            pygame.draw.circle(screen, (255, 0, 0), (self.x,self.y), agentSize) 
        else:
            pygame.draw.circle(screen, (32, 32, 32), (self.x,self.y), agentSize)
        
        Agent.drawCone(self.x, self.y, self.rotation)
    
    def drawCone(agentX, agentY, agentRotation):
        # First Attempt - Vector Circles to Draw XY coordinates
        # Rotation point for polygon X
        vecX = pygame.math.Vector2(0, 0).rotate(agentRotation)
        ptX_x, ptX_y = agentX + vecX.x, agentY + vecX.y

        # Rotation point for polygon Y
        vecY = pygame.math.Vector2(0, 25).rotate(agentRotation - 10)
        ptY_x, ptY_y = ptX_x + vecY.x, ptX_y + vecY.y

        # Rotation point for polygon Y
        vecZ = pygame.math.Vector2(0, 25).rotate(agentRotation + 10)
        ptZ_x, ptZ_y = ptX_x + vecZ.x, ptX_y + vecZ.y

        pygame.draw.polygon(screen, (255,0,0), ((ptX_x, ptX_y), (ptY_x, ptY_y), (ptZ_x, ptZ_y))) # Draw Cone

class Simulation:

    def __init__(self, title, fps):
        pygame.display.set_caption(title)
        self.width = WIDTH
        self.height = HEIGHT
        self.screen = screen
        self.fps = fps

        self.agents = []
        for i in range(3):
            Agents = Agent()
            self.agents.append(Agents)

    def simLoop(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((255,255,255))

            for idx, i in enumerate(self.agents):
                i.draw()
            pygame.display.update() 
            pygame.time.Clock().tick(FPS)

sim = Simulation("Covid 19 Agent Simulation", 60)
sim.simLoop()
