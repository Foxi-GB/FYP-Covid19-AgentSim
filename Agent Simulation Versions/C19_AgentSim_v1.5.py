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
        self.angle = -90

        # Agent Infected
        self.infected = bool(np.random.choice([0,1],1,p=[0.90,0.10]))

    def move(self, delta):
        rotate = 0
        forward = 0

        if(np.random.choice([0,1],1,p=[0.50,0.50]) == 0):
            rotate -= 5
        else:
            rotate += 5

        if(np.random.choice([0,1],1,p=[0.90,0.10]) == 0):
            forward += 5

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

    def infectProbability(self):
        return True

class Cone:
    def __init__(self, idx):
        self.idx = idx
        self.image = self.drawCone()
        self.ocone = self.drawCone()

        self.rect = self.image.get_rect()
        self.center = pygame.Vector2(self.rect.center)
        self.angle = 90
        self.vector = pygame.Vector2()
        self.vector.from_polar((1, 0))


    def drawCone(self):
        surface = pygame.Surface(((agentSize * 2), agentSize ), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.polygon(surface, "blue", ((0,5), (20,0), (20,10)))
        pygame.draw.circle(surface, "red", (0,0), 1)
        return surface
    
    def rotate(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.ocone, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.vector.from_polar((1, self.angle))
    
    def rotate2(self, surface, angle, pivot, offset):
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
        rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        rect = rotated_image.get_rect(center=pivot+rotated_offset)
        return rotated_image, rect  # Return the rotated image and shifted rect.
    
    def rotate3(self, im, angle, pivot):
        image = pygame.transform.rotate(im, -angle)
        rect = image.get_rect()
        rect.center = pivot
        return image, rect

    def rotate4(self, surf, image, origin, pivot, angle):
        image_rect = image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
        offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
        self.rect = rotated_image_rect
        return rotated_image, rotated_image_rect
    

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
        
        self.cones = []
        self.agents = []

        for i in range(25):
            uAgent = Agent(self.images.drawAgent, [random.randrange(10, WIDTH -10), random.randrange(10, HEIGHT -10)])
            self.agents.append(uAgent)

        for idx, i in enumerate(self.agents):
            uCones = Cone(idx)
            self.cones.append(uCones)

    def simLoop(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.surface.fill('white')

            for idx, (a, c) in enumerate(zip(self.agents, self.cones)):

                if(a.infected == True):
                    a.oimage = self.images.updateAgent()
                self.surface.blit(a.image, a.rect)
                agentMask = pygame.mask.from_surface(a.image)
                
                rI, rect = c.rotate4(self.surface, c.image, a.center, (0,4), -a.angle)
                self.surface.blit(rI, rect)
                agentRect = a.rect

                #print("main", idx, c.cIdx)

                for n, xc in enumerate(self.cones):
                    #print("sub", n, xc.cIdx, c.cIdx)
                
                    if(agentRect.colliderect(xc.rect) and idx != xc.idx):
                        print("collision")
                        coneMask = pygame.mask.from_surface(xc.image)

                        offsetX = xc.rect.x - a.rect.x
                        offsetY = xc.rect.y - a.rect.y

                        overlap = agentMask.overlap_mask(coneMask, (offsetX, offsetY))
                        if overlap:
                            if(self.agents[xc.idx].infected == True):
                                a.infected = a.infectProbability()
                            #print(n, 'The two masks overlap!', overlap)
                        
                a.move(self.delta)
            
            pygame.display.update() 
            pygame.time.Clock().tick(FPS)
            pygame.display.flip()
            # Smooth Movement
            self.delta = self.clock.tick(self.fps) * 0.001

sim = Simulation("Covid 19 Agent Simulation", 60, (WIDTH,HEIGHT), 0)
sim.simLoop()
