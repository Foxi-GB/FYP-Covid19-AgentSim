import pygame, sys, random
from pygame.locals import *
import numpy as np

WIDTH = 800
HEIGHT = 600
FPS = 60
agentSize = 10
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Image: 
    def __init__(self):
        self.drawAgent = self.drawAgent()
    
    def drawAgent(self):
        surface = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.circle(surface, "black", (10,10), 10)
        pygame.draw.line(surface, "green", (10, 10), (20, 10))
        return surface

    def updateAgent(self):
        surface = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.circle(surface, "red", (10,10), 10)
        pygame.draw.line(surface, "green", (10, 10), (20, 10))
        return surface
    

class Agent:
    def __init__(self, image, position):

        # Agent Coordinates
        self.oimage = image
        self.image = image
        self.rect = image.get_rect(center=position)
        self.center = pygame.Vector2(self.rect.center)
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]
        self.vector = pygame.Vector2()
        self.vector.from_polar((1, 0))
        self.turnSpeed = 40
        self.speed = 30
        self.angle = 90

        # Agent Infected
        self.infected = bool(np.random.choice([0,1],1,p=[0.90,0.10]))

    # def draw(self):
        
    #     # if(self.infected):
    #     #     pygame.draw.circle(screen, (255, 0, 0), (self.x,self.y), agentSize) 
    #     # else:
    #     #     pygame.draw.circle(screen, (32, 32, 32), (self.x,self.y), agentSize)
        
    #     Agent.drawCone(self.x, self.y)
    

    def move(self, delta):
        rotate = 0
        forward = 0

        if(np.random.choice([0,1],1,p=[0.50,0.50]) == 0):
            rotate -= 5
        else:
            rotate += 5

        if(np.random.choice([0,1],1,p=[0.90,0.10]) == 0):
            forward += 5
        else:
            forward -= 5

        if rotate != 0:
            self.angle += delta * self.turnSpeed * rotate
            self.image = pygame.transform.rotate(self.oimage, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.vector.from_polar((1, self.angle))
        
        if forward != 0:
            self.center += forward * self.vector * delta * self.speed
            self.rect.center = self.center

        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

        if self.x < 10 or self.x > WIDTH - 10 or self.y < 10 or self.y > HEIGHT - 10:
            if self.x < 10:
                self.angle += 90
            elif self.x > WIDTH -10:
                self.angle -= 90
            elif self.y < 10:
                self.angle += 90
            elif self.y > HEIGHT -10: 
                self.angle -= 90

    def drawCone(self, agentX, agentY, agentRotation):
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

    def __init__(self, title, fps, size, flags):
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(title)
        self.surface = pygame.display.set_mode(size, flags)

        self.width = WIDTH
        self.height = HEIGHT
        self.screen = screen
        self.fps = fps
        self.delta = 0
        
        self.rect = self.surface.get_rect()

        self.images = Image()
        
        self.agents = []
        for i in range(100):
            uAgent = Agent(self.images.drawAgent, [random.randrange(10, WIDTH -10), random.randrange(10, HEIGHT -10)])
            self.agents.append(uAgent)

    def simLoop(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.surface.fill('white')

            for idx, i in enumerate(self.agents):

                if(i.infected == True):
                    i.oimage = self.images.updateAgent()
                self.surface.blit(i.image, i.rect)
                i.drawCone(i.x, i.y, i.angle - 90)

                i.move(self.delta)
            
            
            pygame.display.update() 
            pygame.time.Clock().tick(FPS)
            pygame.display.flip()
            # Smooth Movement
            self.delta = self.clock.tick(self.fps) * 0.001

sim = Simulation("Covid 19 Agent Simulation", 60, (WIDTH,HEIGHT), 0)
sim.simLoop()
