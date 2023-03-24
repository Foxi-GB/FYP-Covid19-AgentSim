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
    def __init__(self, image, position):
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

    """
    Cone Rotation code, works by rotating the cone surface around a fixed point defined by the pivot.
    """
    def rotate4(self, image, origin, pivot, angle):
        image_rect = image.get_rect(center = (origin[0] + pivot[0], origin[1] + pivot[1]))
        offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
        return rotated_image, rotated_image_rect

class DiffusionGrid:
    def createGrid():
        rows = int(np.ceil(WIDTH / blockSize))
        cols = int(np.ceil(HEIGHT / blockSize))
        grid = [[GridSquare((j * blockSize), (i * blockSize)) for j in range(cols)] for i in range(rows)]
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
        self.diffusedGrid = DiffusionGrid.createGrid()

        numRows = len(self.grid)
        numCols = len(self.grid[0])

        self.gridRect = [[Rect(self.grid[x][y].getPosX(), self.grid[x][y].getPosY(), self.grid[x][y].getPosX() + blockSize, self.grid[x][y].getPosY() + blockSize) for y in range(numCols)] for x in range(numRows)]

        self.diffGridRect = []
        for x in range(numRows):
            for y in range(numCols):
                rect = Rect(self.grid[x][y].getPosX(), self.grid[x][y].getPosY(), self.grid[x][y].getPosX() + blockSize, self.grid[x][y].getPosY() + blockSize)
                self.diffGridRect.append(rect)

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
        if (pL == 0): return (255,255,255)
        elif (pL > 0 and pL <= 1): return (255,255,0)
        elif(pL > 1 and pL <= 2): return (255,150,0)
        elif(pL > 2 and pL <= 3): return (255,100,0)
        else: return (220,0,0)


    def simLoop(self):   
        tick = 0
        numRows = len(self.grid)
        numCols = len(self.grid[0])

        while True:
            tick = tick + 1
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
            self.surface.fill('white')

            for x in range(numRows):
                for y in range(numCols):
                    color = self.calcColour(self.grid[x][y].getPL())
                    gridImages = []
                    gridImages.append(pygame.draw.rect(self.surface, color, (self.grid[x][y].getPosX(), self.grid[x][y].getPosY(), self.grid[x][y].getPosX() + blockSize, self.grid[x][y].getPosY() + blockSize)))
            
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

                if(bool(np.random.choice([0,1],1,p=[0.99,0.01]))):
                    a.agentCough()
                if(bool(np.random.choice([0,1],1,p=[0.999,0.001]))):
                    a.agentSneeze()

                c.image = c.reDrawCone(a.breathWidth, a.breathLength)
                coneRect = c.rect

                """
                Diffusion grid colouring and infection ability.
                First if statement deals with infected agents breathing into the grid.
                Second if statement handles susceptible agents getting infected. 
                """
                if(a.infectious == True and a.breathedIn == True):
                    for x in range(numRows):
                        for y in range(numCols):
                            if(coneRect.colliderect(self.gridRect[x][y])):
                                coneMask = pygame.mask.from_surface(c.image)
                                sqrMask = pygame.mask.Mask((blockSize, blockSize))
                                sqrMask.fill()

                                offset = (self.gridRect[x][y].x - c.rect.x, self.gridRect[x][y].y - c.rect.y)

                                overlap = coneMask.overlap(sqrMask, offset)

                                if overlap:
                                    agentDist = a.center.distance_to(self.gridRect[x][y].center)
                                    pLevel = (self.grid[x][y].getPL()) + self.calcParticleLevel(agentDist)
                                    self.grid[x][y].setPL(pLevel)

                elif(a.infectious == False):
                    for x in range(numRows):
                        for y in range(numCols):
                            if(coneRect.colliderect(self.gridRect[x][y])):
                                if(coneRect.colliderect(self.gridRect[x][y])):
                                    sqrMask = pygame.mask.Mask((blockSize, blockSize))
                                    sqrMask.fill()

                                    offset = (self.gridRect[x][y].x - a.rect.x, self.gridRect[x][y].y - a.rect.y)

                                    overlap = agentMask.overlap(sqrMask, offset)
                                    if (overlap and a.breathedIn == False) :
                                        a.infected = a.infectRoomProbability()
    
                """
                Agent checks all the cones that it current interacts with, and if one of them is infected whilst
                the agent is breathing in, then the infectProbability() method is called.
                """                        
                for n, xc in enumerate(self.cones):
                    if(agentRect.colliderect(xc.rect) and idx != xc.idx):
                        coneMask = pygame.mask.from_surface(xc.image)

                        offsetX = xc.rect.x - a.rect.x
                        offsetY = xc.rect.y - a.rect.y

                        overlap = agentMask.overlap(coneMask, (offsetX, offsetY))
                        if overlap:
                            if(self.agents[xc.idx].infectious == True and a.infectious == False and a.breathedIn == False):
                                if(a.infected == False):
                                    a.infected = a.infectProbability()

                
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
            self.delta = 17 * 0.001


sim = Simulation("Covid 19 Agent Simulation", 120, (WIDTH,HEIGHT), 0)
sim.simLoop()
#cProfile.run('sim.simLoop()')
