import pygame, sys, random, csv
from pygame.locals import *
import numpy as np
import cProfile, pstats 

# Room Size in Meters
Room_WIDTH = 10
Room_LENGTH = 10

WIDTH = int((Room_WIDTH*100) / 2)
HEIGHT = int((Room_LENGTH*100) / 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
agentSize = 10
breathWidth = 50
breathLength = 50
numAgents = 20
blockSize = 20

class Image: 
    # Draws Agent

    def __init__(self):
        self.drawAgent = self.drawAgent()
    
    def drawAgent(self):
        surface = pygame.Surface((agentSize*2, agentSize*2), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.circle(surface, "black", (agentSize,agentSize), agentSize)
        pygame.draw.line(surface, "green", (agentSize, agentSize), (agentSize*2, agentSize))
        return surface

    def updateAgent(self, type):
        surface = pygame.Surface((agentSize*2, agentSize*2), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()

        if (type == "infected"):
            pygame.draw.circle(surface, "orange", (agentSize,agentSize), agentSize)
        if (type == "infectious"):
            pygame.draw.circle(surface, "cyan", (agentSize,agentSize), agentSize)

        pygame.draw.line(surface, "green", (agentSize, agentSize), (agentSize*2, agentSize))
        return surface

    def drawSquare(blockSize,colour):
        surface = pygame.Surface((blockSize, blockSize), 0)
        surface.fill(colour)
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

        # Agent Infected#
        self.infected = False
        self.infectious = bool(np.random.choice([0,1],1,p=[0.60,0.40])) 

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

    def breatheIn(self):
        self.breathWidth = 25
        self.breathLength = 25
        self.breathedIn = True

    def breatheOut(self):
        self.breathWidth = 55
        self.breathLength = 55
        self.breathedIn = False

    def agentCough(self):
        self.breathedIn = False
        self.breathWidth = 110
        self.breathLength = 110

    def agentSneeze(self):
        self.breathedIn = False
        self.breathWidth = 330  
        self.breathLength = 330

    def infectProbability(self):
        rand = bool(np.random.choice([0,1],1,p=[0.99995, 0.00005]))
        if(rand == 1):
            print("Agent Infection")
        return rand
    
    def infectRoomProbability(self):
        rand = bool(np.random.choice([0,1],1,p=[0.99995, 0.00005]))
        if(rand == 1):
            print("Room Infection")
        return rand
        

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
    
    # def rotate(self, angle):
    #     self.angle = angle
    #     self.image = pygame.transform.rotate(self.ocone, -self.angle)
    #     self.rect = self.image.get_rect(center=self.rect.center)
    #     self.vector.from_polar((1, self.angle))   
    # def rotate2(self, surface, angle, pivot, offset):
    #     rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    #     rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    #     # Add the offset vector to the center/pivot point to shift the rect.
    #     rect = rotated_image.get_rect(center=pivot+rotated_offset)
    #     return rotated_image, rect  # Return the rotated image and shifted rect.
    # def rotate3(self, im, angle, pivot):
    #     image = pygame.transform.rotate(im, -angle)
    #     rect = image.get_rect()
    #     rect.center = pivot
    #     return image, rect

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

class DiffusionGrid:
    def createGrid():
        grid = []
        for x in range(0, WIDTH, blockSize):
            for y in range(0, HEIGHT, blockSize):
                square = GridSquare(x, y)
                grid.append(square)
        return grid

class GridSquare:
    def __init__(self, x, y):
        self.pL = 0
        self.opac = 0
        self.posX = x
        self.posY = y
    
    def setPL(self, level):
        self.pL = level
    
    def getPL(self):
        return self.pL
    
    def setPosX(self, x):
        self.posX = x
    
    def getPosX(self):
        return self.posX
    
    def setPosY(self, y):
        self.posY = y
    
    def getPosY(self):
        return self.posY


    # Main simulation class
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
        self.grid = DiffusionGrid.createGrid()
        self.gridRect = []
        for idx,sqr in enumerate(self.grid):
            rect = Rect(sqr.getPosX(), sqr.getPosY(), sqr.getPosX() + blockSize, sqr.getPosY() + blockSize)
            self.gridRect.append(rect)

        for i in range(numAgents):
            uAgent = Agent(self.images.drawAgent, [random.randrange(10, WIDTH -10), random.randrange(10, HEIGHT -10)])
            self.agents.append(uAgent)

        for idx, i in enumerate(self.agents):
            uCones = Cone(idx)
            self.cones.append(uCones)

        self.agents = self.infectiousTestGen(self.agents)

    def writeToCSV(self, binaryArray):
        f = open('results.csv','a+', newline='')
        writer = csv.writer(f)
        writer.writerow(binaryArray)
        f.close

    def createBinaryArray(self):
        binaryArray = []
        for idx, x in enumerate(self.agents):
            if (x.infected == True or x.infectious == True):
                binaryArray.append(1)
            elif (x.infected == False or x.infectious == False):
                binaryArray.append(0)
        return binaryArray
    
    def infectiousTestGen(self, agents):
        for idx, x in enumerate (agents):
            if(idx == 0 or idx == 1):
                x.infectious = True
            else:
                x.infectious = False
        return agents
    
    def calcParticleLevel(self, dist):
        if dist >= 0 and dist <= 100:
            return 1
        if dist >100 and dist <= 200:
            return 0.5
        else:
            return 0.25

    def calcColour(self, pL):
        if (pL == 0):
            return (255,255,255)
        elif (pL > 0 and pL <= 1):
            return (255,255,0)
        elif(pL > 1 and pL <= 2):
            return (255,150,0)
        elif(pL > 2 and pL <= 3):
            return (255,100,0)
        else:
            return (220,0,0)


    def simLoop(self):   
        tick = 0

        while True:
            tick = tick + 1
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.surface.fill('white')

            for idx, sqr in enumerate(self.grid):
                color = (255,255,255)
                if(sqr.getPL() > 0 ):
                    color = self.calcColour(sqr.getPL())
                gridImages = []
                gridImages.append(pygame.draw.rect(self.surface, color, (sqr.getPosX(), sqr.getPosY(), sqr.getPosX() + blockSize, sqr.getPosY() + blockSize)))
            
            for idx, (a, c) in enumerate(zip(self.agents, self.cones)):

                if(a.infectious == True):
                    a.oimage = self.images.updateAgent("infectious")

                if(a.infected == True):
                    a.oimage = self.images.updateAgent("infected")

                self.surface.blit(a.image, a.rect)
                agentMask = pygame.mask.from_surface(a.image)
                
                rI, rect = c.rotate4(c.image, a.center,(agentSize + (a.breathWidth/2),0), -a.angle)
                self.surface.blit(rI, rect)
                c.rect = rect
                agentRect = a.rect

                vRI, vRect = c.rotate4(c.view, a.center,(agentSize + (c.viewSize/2),0), -a.angle)
                self.surface.blit(vRI, vRect)
                c.vCenter = pygame.Vector2(vRect.center)

                if (tick % 3 == 0):
                    if(a.breathedIn == False):
                        a.breatheIn()
                    elif(a.breathedIn == True):
                        a.breatheOut()


                # if(bool(np.random.choice([0,1],1,p=[0.99,0.01]))):
                #     a.agentCough()

                # if(bool(np.random.choice([0,1],1,p=[0.999,0.001]))):
                #     a.agentSneeze()

                c.image = c.reDrawCone(a.breathWidth, a.breathLength)
                coneRect = c.rect

                if(a.infectious == True and a.breathedIn == True):
                    for idx, gridSqr in enumerate(self.gridRect):
                        if(coneRect.colliderect(gridSqr)):
                            coneMask = pygame.mask.from_surface(c.image)
                            sqrMask = pygame.mask.Mask((blockSize, blockSize))
                            sqrMask.fill()

                            offset = (gridSqr.x - c.rect.x, gridSqr.y - c.rect.y)

                            overlap = coneMask.overlap(sqrMask, offset)
                            if overlap:
                                # Addition of pLevel should be based on distance to mouth, and then colour of square is dictated by total level.
                                agentDist = a.center.distance_to(gridSqr.center)
                                pLevel = (self.grid[idx].getPL()) + self.calcParticleLevel(agentDist)
                                pLevel = (self.grid[idx].getPL()) + 1
                                self.grid[idx].setPL(pLevel)
                elif(a.infectious == False):
                    for idx, gridSqr in enumerate(self.gridRect):
                        if(coneRect.colliderect(gridSqr)):
                            sqrMask = pygame.mask.Mask((blockSize, blockSize))
                            sqrMask.fill()

                            offset = (gridSqr.x - a.rect.x, gridSqr.y - a.rect.y)

                            overlap = agentMask.overlap(sqrMask, offset)
                            if (overlap and a.breathedIn == False) :
                                # Addition of pLevel should be based on distance to mouth, and then colour of square is dictated by total level.
                                a.infected = a.infectRoomProbability()
                        
                # Loop through the cones and check to see if any of them are colliding with agents.
                for n, xc in enumerate(self.cones):
                    # If agent collides with cone.
                    if(agentRect.colliderect(xc.rect) and idx != xc.idx):
                        coneMask = pygame.mask.from_surface(xc.image)

                        offsetX = xc.rect.x - a.rect.x
                        offsetY = xc.rect.y - a.rect.y

                        overlap = agentMask.overlap(coneMask, (offsetX, offsetY))
                        if overlap:
                            if(self.agents[xc.idx].infectious == True and a.infectious == False and a.breathedIn == False):
                                if(a.infected == False):
                                    a.infected = a.infectProbability()
                            # a is being set to false so once its set to TRUE
                            # we need to make sure once its set true it cannot be changed.
                            #print(n, 'The two masks overlap!', overlap)
                
                a.move(self.delta, c.vCenter)


            if (tick % 60) == 0:
                binaryArray = self.createBinaryArray()
                self.writeToCSV(binaryArray)

            if tick == 5000:
                binaryArray = self.createBinaryArray()
                self.writeToCSV(binaryArray)
                pygame.quit()
                sys.exit()

            
            pygame.display.update() 

            pygame.display.flip()
            # Value of 17 was taken from printing out self.clock.tick(60).
            self.delta = 17 * 0.001


sim = Simulation("Covid 19 Agent Simulation", 120, (WIDTH,HEIGHT), 0)
sim.simLoop()
#cProfile.run('sim.simLoop()')
