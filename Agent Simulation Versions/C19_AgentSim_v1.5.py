import pygame, sys, random
from pygame.locals import *
import numpy as np

# Room Size in Meters
Room_WIDTH = 2.7
Room_LENGTH = 5

WIDTH = int((Room_WIDTH*100) / 2)
HEIGHT = int((Room_LENGTH*100) / 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
agentSize = 15
breathWidth = 50
breathLength = 50
numAgents = 2

class Image: 
    # Draws Agent

    def __init__(self):
        self.drawAgent = self.drawAgent()
    
    def drawAgent(self):
        surface = pygame.Surface((agentSize*2, agentSize*2), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        surface.fill("orange")
        pygame.draw.circle(surface, "black", (agentSize,agentSize), agentSize)
        pygame.draw.line(surface, "green", (agentSize, agentSize), (agentSize*2, agentSize))
        return surface

    def updateAgent(self):
        surface = pygame.Surface((agentSize*2, agentSize*2), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        surface.fill("orange")
        pygame.draw.circle(surface, "red", (agentSize,agentSize), agentSize)
        pygame.draw.line(surface, "green", (agentSize, agentSize), (agentSize*2, agentSize))
        return surface
    

class Agent:

    # Contains information about Agent

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
        self.angle = 0

        self.breathedIn = False
        self.breathWidth = breathWidth
        self.breathLength = breathLength

        # Agent Infected
        self.infected = bool(np.random.choice([0,1],1,p=[0.50,0.50]))


    def collisionCheck(self, coneCenter):
        cX = coneCenter[0]
        cY = coneCenter[1]
        if (cX) > WIDTH or (cX) < 0 or (cY) > HEIGHT or (cY) < 0:
            self.angle += random.randint(45, 180)
            return True

    def randRotate(self, rotate):
        if(np.random.choice([0,1],1,p=[0.50,0.50]) == 0):
            return rotate-5
        else:
            return rotate+5

    def rotateImage(self, delta, rotate):
        if rotate != 0:
            self.angle += delta * self.turnSpeed * rotate
            self.image = pygame.transform.rotate(self.oimage, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.vector.from_polar((1, self.angle))
    
    def moveForward(self, delta, forward):
        if(np.random.choice([0,1],1,p=[0.90,0.10]) == 0):
            forward = 5
        
        if forward != 0:
            self.center += forward * self.vector * delta * self.speed
            self.rect.center = self.center

        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

        
    def move(self, delta, coneCenter):
        forward = 0
        rotate = 0

        if self.collisionCheck(coneCenter) == True:
            self.rotateImage(delta, rotate)
        else:
            rotate += self.randRotate(rotate)
            self.rotateImage(delta, rotate)
            self.moveForward(delta, forward)
    
    # def collisionCheck(self):
    #     if (self.x + 10) > WIDTH or (self.x - 10) < 0 or (self.y + 10) > HEIGHT or (self.y - 10) < 0:
    #         self.angle += 180

    #     # if self.x < 10 or self.x > WIDTH - 10 or self.y < 10 or self.y > HEIGHT - 10:
    #     #     if self.x - (agentSize + 5) > 10:
    #     #         self.angle += 180
    #     #     elif self.x + (agentSize + 5) < WIDTH -10:
    #     #         self.angle -= 180
    #     #     elif self.y  + (agentSize + 5) > 10:
    #     #         self.angle += 180
    #     #     elif self.y  + (agentSize + 5) < HEIGHT -10:
    #     #         self.angle -= 180

    # def rotateAgent(self,rotate):
    #     if(np.random.choice([0,1],1,p=[0.50,0.50]) == 0):
    #         return rotate - 5
    #     else:
    #         return rotate + 5
    
    # def rotateImage(self, rotate, delta):
    #     if rotate != 0:
    #         self.angle += delta * self.turnSpeed * rotate
    #         self.image = pygame.transform.rotate(self.oimage, -self.angle)
    #         self.rect = self.image.get_rect(center=self.rect.center)
    #         self.vector.from_polar((1, self.angle))
         
    # def move(self, delta):
    #     forward = 0
    #     rotate = 0

    #     self.collisionCheck()
    #     rotate = self.rotateAgent(rotate)
        
    #     if(np.random.choice([0,1],1,p=[0.90,0.10]) == 0):
    #         forward = 5

    #     self.rotateImage(rotate, delta)
        
    #     if forward != 0:
    #         self.center += forward * self.vector * delta * self.speed
    #         self.rect.center = self.center

    #     self.x = self.rect.center[0]
    #     self.y = self.rect.center[1]

    def breathFallOff(self):
        self.breathedIn = True
        self.breathWidth = self.breathWidth- 5
        self.breathLength = self.breathLength- 5

    def breatheOut(self):
        self.breathedIn = False
        self.breathWidth = 55
        self.breathLength = 55

    def agentCough(self):
        self.breathedIn = False
        self.breathWidth = 110
        self.breathLength = 110

    def agentSneeze(self):
        self.breathedIn = False
        self.breathWidth = 330  
        self.breathLength = 330

    def infectProbability(self):
        # Agent chance of infection

        infects = bool(np.random.choice([0,1],1,p=[0.99,0.01]))
        return infects

class Cone:

    # Contains cone information, draws cone and rotates cone with agent

    def __init__(self, idx):
        self.idx = idx
        self.image = self.init_DrawCone()
        self.ocone = self.init_DrawCone()
        
        self.viewSize = 50
        self.view = self.viewCone(self.viewSize,self.viewSize)
        self.vCenter = pygame.Vector2(self.view.get_rect().center)

        self.rect = self.image.get_rect()
        self.center = pygame.Vector2(self.rect.center)
        self.angle = 90
        self.vector = pygame.Vector2()
        self.vector.from_polar((1, 0))


    def init_DrawCone(self):
        # Draws surface and then draws cone within surface.
        # Surface size is Width x Height 

        surface = pygame.Surface(((breathWidth), breathLength ), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.polygon(surface, "blue", ((0,breathWidth/2), (breathWidth,0), (breathWidth,breathLength)))
        return surface

    def reDrawCone(self, agentBreathWidth, agentBreathLength):
        surface = pygame.Surface(((agentBreathWidth), agentBreathLength ), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.polygon(surface, "blue", ((0,agentBreathWidth/2), (agentBreathWidth,0), (agentBreathWidth,agentBreathLength)))
        return surface
    
    def viewCone(self, viewWidth, viewLength):
        surface = pygame.Surface(((viewWidth), viewLength ), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.line(surface, "green", (surface.get_rect().center), (viewWidth, viewLength/2))
        return surface

    
    # Previous Trials
    
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

    # Working Rotation Code
    def rotate4(self, image, origin, pivot, angle):
        # Rotate cone using 

        image_rect = image.get_rect(center = (origin[0] + pivot[0], origin[1] + pivot[1]))
        offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
        return rotated_image, rotated_image_rect

class Simulation:

    # Main simulation class

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

        for i in range(numAgents):
            uAgent = Agent(self.images.drawAgent, [random.randrange(10, WIDTH -10), random.randrange(10, HEIGHT -10)])
            self.agents.append(uAgent)

        for idx, i in enumerate(self.agents):
            uCones = Cone(idx)
            self.cones.append(uCones)

    def simLoop(self):   
        tick = 0 
        while True:
            tick = tick + 1
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
                
                rI, rect = c.rotate4(c.image, a.center,(agentSize + (a.breathWidth/2),0), -a.angle)
                self.surface.blit(rI, rect)
                c.rect = rect
                agentRect = a.rect

                vRI, vRect = c.rotate4(c.view, a.center,(agentSize + (c.viewSize/2),0), -a.angle)
                self.surface.blit(vRI, vRect)
                c.vCenter = pygame.Vector2(vRect.center)

                if (tick % 10 == 0):
                    if(a.breathedIn == True):
                        a.breatheOut()
                else: 
                    a.breathFallOff()

                if(bool(np.random.choice([0,1],1,p=[0.99,0.01]))):
                    a.agentCough()

                if(bool(np.random.choice([0,1],1,p=[0.999,0.001]))):
                    a.agentSneeze()

                c.image = c.reDrawCone(a.breathWidth, a.breathLength)

                for n, xc in enumerate(self.cones):
                    # Collision Check
                
                    if(agentRect.colliderect(xc.rect) and idx != xc.idx):
                        coneMask = pygame.mask.from_surface(xc.image)

                        offsetX = xc.rect.x - a.rect.x
                        offsetY = xc.rect.y - a.rect.y

                        overlap = agentMask.overlap_mask(coneMask, (offsetX, offsetY))
                        if overlap:
                            if(self.agents[xc.idx].infected == True):
                                a.infected = a.infectProbability()
                            #print(n, 'The two masks overlap!', overlap)
                        
                a.move(self.delta, c.vCenter)
            
            pygame.display.update() 
            pygame.time.Clock().tick(FPS)
            pygame.display.flip()
            # Smooth Movement
            self.delta = self.clock.tick(self.fps) * 0.001

sim = Simulation("Covid 19 Agent Simulation", 60, (WIDTH,HEIGHT), 0)
sim.simLoop()
