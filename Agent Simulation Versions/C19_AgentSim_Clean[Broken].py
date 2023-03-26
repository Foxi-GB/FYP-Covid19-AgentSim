import pygame, sys, random, csv, math
from pygame.locals import *
import numpy as np
import cProfile, pstats 



## Simulation Variables
# Agent Variables
agentSize = 10 # Agent Radius
cmPerPxl = 39 / (agentSize*2) # Average human width (cm) divided by agent size in pixels
breathLength = 1 # In meters
breathAngle = 25 # In degrees
# Environment Variables
numAgents = 2
numInfAgents = 1
blockSize = 10
# Room Size in Meters
Room_WIDTH = 5
Room_LENGTH = 5

FPS = 60
WIDTH = int((Room_WIDTH*100) / cmPerPxl)
HEIGHT = int((Room_LENGTH*100) / cmPerPxl)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

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
        self.statuses = ["breathingIn", "breathingOut", "coughing", "sneezing"]
        self.status = self.statuses[0]
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
        self.stop = 0

        self.breathedIn = False
        self.breathWidth = 0
        self.breathLength = 0

        self.infected = False
        self.infectious = False

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
        self.center += forward * self.vector * delta * self.speed
        self.rect.center = self.center
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

        
    def move(self, delta, coneCenter, forward):
        rotate = 0

        if self.collisionCheck(coneCenter) == True:
            self.rotateImage(delta, rotate)
        else:
            rotate += self.randRotate(rotate)
            self.rotateImage(delta, rotate)
            if(bool(np.random.choice([0,1],1,p=[0.997,0.003]))):
                self.moveForward(delta, 0)
                self.stop = random.randrange(1,2) * 60
            else:
                self.moveForward(delta, forward)


    def breatheIn(self):
        self.breathedIn = True
        self.status = self.statuses[0]
        self.breathWidth = 10
        self.breathLength = (breathLength * 100) / 10

    def breatheOut(self):
        self.breathedIn = False
        self.status = self.statuses[1]
        self.breathLength = (breathLength * 100) /cmPerPxl
        self.breathWidth = (np.tan(np.radians(breathAngle/2)) * self.breathLength) * 2
        
    def agentCough(self):
        self.breathedIn = False
        self.status = self.statuses[2]
        self.breathLength = (breathLength * 200) / cmPerPxl
        self.breathWidth = (np.tan(np.radians(breathAngle/2)) * self.breathLength) * 2

    def agentSneeze(self):
        self.breathedIn = False
        self.status = self.statuses[3]
        self.breathLength = (breathLength * 600) / cmPerPxl 
        self.breathWidth = (np.tan(np.radians(breathAngle/2)) * self.breathLength) * 2

    def infectProbability(self):
        rand = bool(np.random.choice([0,1],1,p=[0.99995, 0.00005]))
        return rand
    
    def infectRoomProbability(self, level):
        if(level <= 300):
            rand = False
        elif(level > 300 and level <= 2000):
            rand = bool(np.random.choice([0,1],1,p=[0.99995, 0.00005]))
        elif(level > 2000 and level <= 5000):
            rand = bool(np.random.choice([0,1],1,p=[0.99995, 0.00005]))
        else:
            rand = bool(np.random.choice([0,1],1,p=[0.999925, 0.000075]))
        return rand
        

class Cone:
    def __init__(self, idx):
        self.idx = idx
        self.image = self.init_DrawCone(1, 1)
        self.ocone = self.init_DrawCone(1, 1)
        
        self.viewSize = 50
        self.view = self.viewCone(self.viewSize,self.viewSize)
        self.vCenter = pygame.Vector2(self.view.get_rect().center)

        self.rect = self.image.get_rect()
        self.center = pygame.Vector2(self.rect.center)
        self.angle = 90
        self.vector = pygame.Vector2()
        self.vector.from_polar((1, 0))


    def init_DrawCone(self, breathWidth, breathLength):
        surface = pygame.Surface((breathWidth, breathLength ), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.polygon(surface, "blue", ((0,breathWidth/2), (breathWidth,0), (breathWidth,breathLength)))
        return surface

    def reDrawCone(self, agentBreathLength, agentBreathWidth):
        surface = pygame.Surface(((agentBreathWidth), agentBreathLength ), pygame.SRCALPHA, 32)
        surface = surface.convert_alpha()
        pygame.draw.polygon(surface, "blue", ((0,agentBreathLength/2), (agentBreathWidth,0), (agentBreathWidth,agentBreathLength)))
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
        rows = int(np.ceil(Room_WIDTH * 100 / blockSize))
        cols = int(np.ceil(Room_LENGTH * 100 / blockSize))
        grid = [[GridSquare((j * blockSize), (i * blockSize)) for j in range(cols)] for i in range(rows)]
        return grid

class GridSquare:
    def __init__(self, x, y):
        self.pL = 0
        self.age = 0
        self.posX = x
        self.posY = y
    
    def addPL(self, level):
        self.pL += level

    def subPL(self, level):
        self.pL -= level

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

        numRows = len(self.grid)
        numCols = len(self.grid[0])

        self.gridRect = [[Rect(self.grid[x][y].getPosX(), self.grid[x][y].getPosY(), self.grid[x][y].getPosX() + blockSize, self.grid[x][y].getPosY() + blockSize) for y in range(numCols)] for x in range(numRows)]


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
            if numInfAgents < len(agents):
                for i in range (0, numInfAgents):
                    agents[i].infectious = True
            else:
                print("Request number of infected agents is greater than the total number of agents.")
        return agents
    
    def calcParticleLevel(self, dist, status):
        level = 0
        dist *= cmPerPxl
        if(status == "breathingIn"):
            return level
        elif(status == "breathingOut"):
            level = 100 / dist
        elif(status == "coughing"):
            level = 123000 / dist
        elif(status == "sneezing"):
            level = 533000 / dist
        return level


    def calcColour(self, pL):
        # if(pL > 1000):
        #     pL = 1000
        # pL = pL/1000
        # pLDiff = 1.0 - pL
        # redCol = min(255, pL*2 * 255)
        # greenCol = min(255, pLDiff*2 * 255)
        # col = (redCol, greenCol, 0)
        # return col
        if (pL <= 100 ): return (255,255,255)
        elif (pL > 100 and pL <= 300): return (255,255,0)
        elif(pL > 300 and pL <= 1000): return (255,150,0)
        elif(pL > 1000 and pL <= 1000): return (255,100,0)
        else: return (220,0,0)


    def simLoop(self):   
        tick = 0
        numRows = len(self.grid) - 1
        numCols = len(self.grid[0]) - 1

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
                
                if (tick % 3 == 0):
                    if(a.status != "breathingIn"):
                        a.breatheIn()
                    elif(a.status == "breathingIn"):
                        a.breatheOut()

                if(bool(np.random.choice([0,1],1,p=[0.99,0.01]))):
                    a.agentCough()
                if(bool(np.random.choice([0,1],1,p=[0.999,0.001]))):
                    a.agentSneeze()

                c.image = c.reDrawCone(a.breathWidth, a.breathLength)

                rI, rect = c.rotate4(c.image, a.center,(agentSize + (a.breathLength/2),0), -a.angle)
                self.surface.blit(rI, rect)
                c.rect = rect
                agentRect = a.rect

                vRI, vRect = c.rotate4(c.view, a.center,(agentSize + (c.viewSize/2),0), -a.angle)
                self.surface.blit(vRI, vRect)
                c.vCenter = pygame.Vector2(vRect.center)

                coneRect = c.rect

                """
                Diffusion grid colouring and infection ability.
                First if statement deals with infected agents breathing into the grid.
                Second if statement handles susceptible agents getting infected. 
                """
                if(a.infectious == True and a.status != "breathingIn"):
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
                                    self.grid[x][y].addPL(self.calcParticleLevel(agentDist, a.status))
                                    self.grid[x][y].age = 0

                elif(a.infectious == False):
                    for x in range(numRows):
                        for y in range(numCols):
                            if(coneRect.colliderect(self.gridRect[x][y])):
                                if(coneRect.colliderect(self.gridRect[x][y])):
                                    sqrMask = pygame.mask.Mask((blockSize, blockSize))
                                    sqrMask.fill()
                                    agentMask = pygame.mask.from_surface(c.image)

                                    offset = (self.gridRect[x][y].x - a.rect.x, self.gridRect[x][y].y - a.rect.y)

                                    overlap = agentMask.overlap(sqrMask, offset)
                                    if (overlap and a.status == "breathingIn") :
                                        a.infected = a.infectRoomProbability(self.grid[x][y].getPL())

                """
                Diffusing the Diffusion Grid
                """
                if(tick %50 == 0):
                    for x in range(numRows):
                            for y in range(numCols):
                                    if(self.grid[x][y].age == 5):
                                        self.grid[x][y].setPL(self.grid[x][y].getPL() * 0.54) # falling to an average of 54% within 5 s of generation
                                    elif(5 < self.grid[x][y].age < 300):
                                        self.grid[x][y].setPL(self.grid[x][y].getPL() * 0.9994) # decrease on average by 20% (19%) over the next 5 mins
                                    elif(self.grid[x][y].age > 300):
                                        self.grid[x][y].setPL(self.grid[x][y].getPL() * 0.995)
                                    #self.grid[x][y].setPL(self.grid[x][y].getPL() * 0.9)
                                    self.grid[x+1][y].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x-1][y].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x][y+1].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x][y-1].addPL(self.grid[x][y].getPL() * 0.000625)

                                    self.grid[x+1][y+1].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x-1][y+1].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x+1][y-1].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x-1][y-1].addPL(self.grid[x][y].getPL() * 0.000625)
                                    self.grid[x][y].age += 1

                """
                Agent checks all the cones that it current interacts with, and if one of them is infected whilst
                the agent is breathing in, then the infectProbability() method is called.
                """                        
                for n, xc in enumerate(self.cones):
                    if(agentRect.colliderect(xc.rect) and idx != xc.idx):
                        coneMask = pygame.mask.from_surface(xc.image)

                        offset = (xc.rect.x - a.rect.x, xc.rect.y - a.rect.y)

                        overlap = agentMask.overlap(coneMask, offset)
                        if overlap:
                            if(self.agents[xc.idx].infectious == True and a.infectious == False and a.status == "breathingIn"):
                                if(a.infected == False):
                                    a.infected = a.infectProbability()

                if(a.stop != 0):
                    a.stop -= 1
                else:
                    a.move(self.delta, c.vCenter, 5)


            if (tick % 60) == 0:
                binaryArray = self.createBinaryArray()
                self.writeToCSV(binaryArray)

            if tick == 86400:
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


"""
Trial diffusion code. 
"""
 # for x in range(numRows):
                #     for y in range(numCols):
                #         if(self.grid[x][y].getPL() > 0.5):
                #             basePL = self.grid[x][y].getPL()

                #             sqrMain = basePL * 0.8
                #             print("aqr", sqrMain)
                #             sqrSides = basePL * 0.3
                #             sqrDiag = basePL * 0.2

                #             self.diffusedGrid[x][y].setPL(sqrMain) #self
                #             if (x == 0):
                                
                #                 self.diffusedGrid[x-1][y].setPL(sqrSides) #down
                #                 self.diffusedGrid[x][y+1].setPL(sqrSides) #right
                #                 self.diffusedGrid[x][y-1].setPL(sqrSides) #left

                #                 self.diffusedGrid[x+1][y+1].setPL(sqrDiag) #SE
                #                 self.diffusedGrid[x+1][y-1].setPL(sqrDiag) #SW
                #             elif (y == 0):
                                
                #                 self.diffusedGrid[x-1][y].setPL(sqrSides) #down
                #                 self.diffusedGrid[x+1][y].setPL(sqrSides) #up
                #                 self.diffusedGrid[x][y+1].setPL(sqrSides) #right

                #                 self.diffusedGrid[x-1][y+1].setPL(sqrDiag) #NE
                #                 self.diffusedGrid[x+1][y+1].setPL(sqrDiag) #SE
                #             elif (x == numRows):
                                
                #                 self.diffusedGrid[x+1][y].setPL(sqrSides) #up
                #                 self.diffusedGrid[x][y+1].setPL(sqrSides) #right
                #                 self.diffusedGrid[x][y-1].setPL(sqrSides) #left

                #                 self.diffusedGrid[x-1][y+1].setPL(sqrDiag) #NE
                #                 self.diffusedGrid[x-1][y-1].setPL(sqrDiag) #NW
                #             elif (y == numCols):
                                
                #                 self.diffusedGrid[x-1][y].setPL(sqrSides) #down
                #                 self.diffusedGrid[x+1][y].setPL(sqrSides) #up
                #                 self.diffusedGrid[x][y-1].setPL(sqrSides) #left

                #                 self.diffusedGrid[x-1][y-1].setPL(sqrDiag) #NW
                #                 self.diffusedGrid[x+1][y-1].setPL(sqrDiag) #SW
                #             else:
                                
                #                 self.diffusedGrid[x-1][y].setPL(sqrSides) #down
                #                 self.diffusedGrid[x+1][y].setPL(sqrSides) #up
                #                 self.diffusedGrid[x][y+1].setPL(sqrSides) #right
                #                 self.diffusedGrid[x][y-1].setPL(sqrSides) #left

                #                 self.diffusedGrid[x-1][y+1].setPL(sqrDiag) #NE
                #                 self.diffusedGrid[x+1][y+1].setPL(sqrDiag) #SE
                #                 self.diffusedGrid[x-1][y-1].setPL(sqrDiag) #NW
                #                 self.diffusedGrid[x+1][y-1].setPL(sqrDiag) #SW