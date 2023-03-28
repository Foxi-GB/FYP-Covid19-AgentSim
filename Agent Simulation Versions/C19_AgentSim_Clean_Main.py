import pygame, sys, random, csv, math
from pygame.locals import *
import numpy as np
import cProfile, pstats 



## Simulation Variables  
gradientMap = True # Toggle the colour-coding method
# subMicrometer = False
# tenMicrometer = True
# hundMicrometer = True
# thouMicrometer = True
# Agent Variables
agentSize = 10 # Agent Radius
cmPerPxl = 39 / (agentSize*2) # Average human width (cm) divided by agent size in pixels
breathLength = 1 # In meters
breathAngle = 25 # In degrees
# Environment Variables
numAgents = 5
numInfAgents = 1
blockSize = 20
# Room Size in Meters
Room_WIDTH = 10
Room_LENGTH = 10

FPS = 60
HEIGHT = int((Room_WIDTH*100) / cmPerPxl)
WIDTH = int((Room_LENGTH*100) / cmPerPxl)
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
        return random.randrange(-12,12)


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
        elif(level > 300 and level <= 1000):
            rand = bool(np.random.choice([0,1],1,p=[0.99995, 0.00005]))
        elif(level > 2000 and level <= 5000):
            rand = bool(np.random.choice([0,1],1,p=[0.99993, 0.00007]))
        else:
            rand = bool(np.random.choice([0,1],1,p=[0.99991, 0.00009]))
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
        rows = int(round((Room_WIDTH*100)/ blockSize))
        cols = int(round((Room_LENGTH*100)/ blockSize))
        grid = [[GridSquare((j * blockSize), (i * blockSize)) for j in range(cols)] for i in range(rows)]
        return grid


class GridSquare:
    def __init__(self, x, y):
        self.pL = 0
        self.age = 0
        self.posX = x
        self.posY = y

        self.subMM = 0
        self.tenMM = 0
        self.hundMM = 0
        self.thouMM = 0
    
    def sumDL(self):
        total = self.subMM + self.tenMM + self.hundMM + self.thouMM
        return total
    
    def setDL(self, subMM, tenMM, hundMM, thouMM):
        if(subMM != 0):
            self.subMM = subMM 
        if(tenMM != 0):
            self.tenMM = tenMM
        if(hundMM != 0):
            self.hundMM = hundMM
        if(thouMM != 0):
            self.thouMM = thouMM

    def addDL(self, subMM, tenMM, hundMM, thouMM):
        self.subMM += subMM 
        self.tenMM += tenMM
        self.hundMM += hundMM
        self.thouMM += thouMM
    
    def addPL(self, level, age):
        self.pL += level
        self.age = age

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
    def __init__(self, title, fps, flags):
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(title)
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT), flags)

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
            if numInfAgents <= len(agents):
                for i in range ((numInfAgents)):
                    agents[i-1].infectious = True
            else:
                print("Request number of infected agents is greater than the total number of agents.")
        return agents
    
    def calcDropletsProduced(self, dist, status):
        level = 0
        subMM = 0
        tenMM = 0
        hunMM = 0 
        # dist *= cmPerPxl
        dist /= 10
        if(status == "breathingIn"):
            return level
        elif(status == "breathingOut"):
            level = 100
            subMM = (level * 0.75) / (dist/2)
            tenMM = (level * 0.25) / (dist/2)
            hunMM = (level * 0) / dist
            thouMM = (level * 0) / dist
        elif(status == "coughing"):
            level = 3000
            subMM = (level * 0) / (dist/2)
            tenMM = (level * 0.0) / (dist/2)
            hunMM = (level * 0.20) / dist
            thouMM = (level * 0.80) / dist
        elif(status == "sneezing"):
            level = 40000
            subMM = (level * 0.0) / (dist/2)
            tenMM = (level * 0.5) / (dist/2)
            hunMM = (level * 0.15) / dist
            thouMM = (level * 0.8) / dist

        p = float(10**2)
        subMM = int(subMM * p + 0.5)/p
        tenMM = int(tenMM * p + 0.5)/p
        hunMM = int(hunMM * p + 0.5)/p
        thouMM = int(thouMM * p + 0.5)/p
        return subMM , tenMM , hunMM,thouMM


    def calcColour(self, pL):
        if(gradientMap == True):
            if(pL > 1000):
                pL = 1000
            if(pL <= 10):
                if(pL < 1): pL = 0
                pLgrnDiff = 1.0 - (pL/10)
                greenCol0 = min(255, pLgrnDiff*2 * 255)
                col = (greenCol0, 255, greenCol0) # R, G, B 
                return col
            elif(10 < pL <= 100):
                pL = pL/100
                pLDiff = 1.0 - pL
                redCol = min(255, pL*2 * 255)
                greenCol = min(255, pLDiff*2 * 255)
                col = (redCol, 255, 0)
            else:
                pL = pL/1000
                pLDiff = 1.0 - pL
                redCol = min(255, pL*2 * 255)
                greenCol = min(255, pLDiff*2 * 255)
                col = (greenCol, 255 - redCol, 0)
            return col
        else:
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
                    color = self.calcColour(self.grid[x][y].sumDL())
                    gridImages = []
                    gridImages.append(pygame.draw.rect(self.surface, color, (self.grid[x][y].getPosX(), self.grid[x][y].getPosY(), self.grid[x][y].getPosX() + blockSize, self.grid[x][y].getPosY() + blockSize)))
            
            for idx, (a, c) in enumerate(zip(self.agents, self.cones)):

                if(a.infectious == True):
                    a.oimage = self.images.updateAgent("infectious")
                if(a.infected == True):
                    a.oimage = self.images.updateAgent("infected")

                self.surface.blit(a.image, a.rect)

                if(bool(np.random.choice([0,1],1,p=[0.99,0.01]))):
                    a.agentCough()
                if(bool(np.random.choice([0,1],1,p=[0.999,0.001]))):
                    a.agentSneeze()

                c.image = c.reDrawCone(a.breathWidth, a.breathLength)
                
                rI, rect = c.rotate4(c.image, a.center,(agentSize + (a.breathLength/2),0), -a.angle)
                self.surface.blit(rI, rect)
                c.image = rI
                c.rect = rect
                agentRect = a.rect

                vRI, vRect = c.rotate4(c.view, a.center,(agentSize + (c.viewSize/2),0), -a.angle)
                self.surface.blit(vRI, vRect)
                c.vCenter = pygame.Vector2(vRect.center)

                if (tick % 3 == 0):
                    if(a.status != "breathingIn"):
                        a.breatheIn()
                    elif(a.status == "breathingIn"):
                        a.breatheOut()

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
                                    agentDist = np.sqrt((c.rect.centerx - self.gridRect[x][y].centerx)**2 + (c.rect.centery - self.gridRect[x][y].centery)**2 )
                                    if(agentDist < 1): agentDist = 1
                                    #agentDist = a.center.distance_to(self.gridRect[x][y].center)
                                    subMM, tenMM, hunMM, thouMM = self.calcDropletsProduced((agentDist), a.status)
                                    self.grid[x][y].addDL(subMM, tenMM, hunMM, thouMM)

                elif(a.infectious == False and a.status == "breathingIn"):
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
                # if(tick %200 == 0):
                for x in range(numRows):
                        for y in range(numCols):
                            subMM = self.grid[x][y].subMM
                            tenMM = self.grid[x][y].tenMM
                            hundMM = self.grid[x][y].hundMM
                            thouMM = self.grid[x][y].thouMM

                            adj = 0.001875
                            dia = 0.000625
                            age = 0
                            evapRate = 0.99
                            fallRate = 0.99
                            
                            self.grid[x][y].subMM = subMM * 0.99
                            self.grid[x][y].tenMM * 0.99
                            self.grid[x][y].hundMM * evapRate
                            self.grid[x][y].thouMM * fallRate

                            subMMDiffADJ = subMM * adj
                            subMMDiffDIA = subMM * dia
                            self.grid[x+1][y].subMM *= subMMDiffADJ
                            self.grid[x-1][y].subMM *= subMMDiffADJ
                            self.grid[x][y+1].subMM *= subMMDiffADJ
                            self.grid[x][y-1].subMM *= subMMDiffADJ
                            self.grid[x+1][y+1].subMM *= subMMDiffDIA
                            self.grid[x-1][y+1].subMM *= subMMDiffDIA
                            self.grid[x+1][y-1].subMM *= subMMDiffDIA
                            self.grid[x-1][y-1].subMM *= subMMDiffDIA
                            

                """
                Agent checks all the cones that it current interacts with, and if one of them is infected whilst
                the agent is breathing in, then the infectProbability() method is called.
                """                        
                for n, xc in enumerate(self.cones):
                    if(agentRect.colliderect(xc.rect) and idx != xc.idx):
                        coneMask = pygame.mask.from_surface(xc.image)
                        agentMask = pygame.mask.from_surface(c.image)

                        offset = (xc.rect.x - a.rect.x, xc.rect.y - a.rect.y)

                        overlap = agentMask.overlap(coneMask, offset)
                        if overlap:
                            if(self.agents[xc.idx].infectious == True and a.infectious == False and a.status == "breathingIn"):
                                if(a.infected == False):
                                    a.infected = a.infectProbability()

                if(a.stop != 0):
                    a.stop -= 1
                else:
                    a.move(self.delta, c.vCenter, (70/cmPerPxl))


            if (tick % 60) == 0:
                binaryArray = self.createBinaryArray()
                self.writeToCSV(binaryArray)

            if tick == 500:
                binaryArray = self.createBinaryArray()
                self.writeToCSV(binaryArray)
                pygame.quit()
                sys.exit()

            
            pygame.display.update() 

            pygame.display.flip()
            self.delta = 17 * 0.001


sim = Simulation("Covid 19 Agent Simulation", 120, 0)
cProfile.run('sim.simLoop()')


"""
Trial diffusion code. 
"""
# if(0 < self.grid[x][y].getPL() <= 0.001 ):
                            #     self.grid[x][y].setPL(0.001)
                            # if(self.grid[x][y].age < 5):
                            #     self.grid[x][y].setPL(pL)
                            # if(self.grid[x][y].age == 5):
                            #     self.grid[x][y].setPL(pL * 0.54) # falling to an average of 54% within 5 s of generation
                            # elif(5 < self.grid[x][y].age < 300):
                            #     self.grid[x][y].setPL(pL * 0.933) # decrease on average by 20% (19%) over the next 5 mins
                            # elif(self.grid[x][y].age > 300):
                            #     self.grid[x][y].setPL(pL * 0.995)

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

"""
Diffusion Grid 2
"""
# pL = self.grid[x][y].getPL()
#                             adj = 0
#                             dia = 0
#                             age = 0
#                             eMP = 1.7
#                             if(pL > 0.0):
#                                 # if(self.grid[x][y].age <= 5):
#                                 #     self.grid[x][y].setPL(pL * 0.892)
#                                 #     adj = 0.02025
#                                 #     dia = 0.00675
#                                 # elif(5 < self.grid[x][y].age <= 300):
#                                 #     self.grid[x][y].setPL(pL * 0.933) # decrease on average by 20% (19%) over the next 5 mins
#                                 #     adj = 0.0125625
#                                 #     dia = 0.0041875
#                                 # elif(self.grid[x][y].age > 300):
#                                 #     self.grid[x][y].setPL(pL * 0.995)
#                                 #     adj = 0.0009375
#                                 #     dia = 0.0003125

#                                 if(self.grid[x][y].age < 600):
#                                     self.grid[x][y].setPL(pL * 0.870)
#                                     adj = 0.024375
#                                     dia = 0.008125
#                                 elif(self.grid[x][y].age >600):
#                                     self.grid[x][y].setPL(pL * 0.995)
#                                     adj = 0.0009375
#                                     dia = 0.0003125
                                
#                                 # # self.grid[x][y].setPL(pL * 0.8)
#                                 # self.grid[x+1][y].addPL(pL * adj, age)
#                                 # self.grid[x-1][y].addPL(pL * adj, age)
#                                 # self.grid[x][y+1].addPL(pL * adj, age)
#                                 # self.grid[x][y-1].addPL(pL * adj, age)

#                                 # self.grid[x+1][y+1].addPL(pL * dia, age)
#                                 # self.grid[x-1][y+1].addPL(pL * dia, age)
#                                 # self.grid[x+1][y-1].addPL(pL * dia, age)
#                                 # self.grid[x-1][y-1].addPL(pL * dia, age)
#                                 self.grid[x][y].age += 1
#                             if (x == 0):
#                                 self.grid[x-1][y].addPL(pL * adj, age) #down
#                                 self.grid[x][y+1].addPL(pL * (adj * eMP), age) #right
#                                 self.grid[x][y-1].addPL(pL * (adj * eMP), age) #left

#                                 self.grid[x+1][y+1].addPL(pL * dia, age) #SE
#                                 self.grid[x+1][y-1].addPL(pL * dia, age) #SW
#                             elif (y == 0):
                                
#                                 self.grid[x-1][y].addPL(pL * (adj * eMP), age) #down
#                                 self.grid[x+1][y].addPL(pL * (adj * eMP), age) #up
#                                 self.grid[x][y+1].addPL(pL * adj, age) #right

#                                 self.grid[x-1][y+1].addPL(pL * dia, age) #NE
#                                 self.grid[x+1][y+1].addPL(pL * dia, age) #SE
#                             elif (x == numRows):
                                
#                                 self.grid[x+1][y].addPL(pL * adj, age) #up
#                                 self.grid[x][y+1].addPL(pL * (adj * eMP), age) #right
#                                 self.grid[x][y-1].addPL(pL * (adj * eMP), age) #left

#                                 self.grid[x-1][y+1].addPL(pL * dia, age) #NE
#                                 self.grid[x-1][y-1].addPL(pL * dia, age) #NW
#                             elif (y == numCols):
                                
#                                 self.grid[x-1][y].addPL(pL * adj, age) #down
#                                 self.grid[x+1][y].addPL(pL * (adj * eMP), age) #up
#                                 self.grid[x][y-1].addPL(pL * (adj * eMP), age) #left

#                                 self.grid[x-1][y-1].addPL(pL * dia, age) #NW
#                                 self.grid[x+1][y-1].addPL(pL * dia, age) #SW
#                             else:
                                
#                                 self.grid[x+1][y].addPL(pL * adj, age)
#                                 self.grid[x-1][y].addPL(pL * adj, age)
#                                 self.grid[x][y+1].addPL(pL * adj, age)
#                                 self.grid[x][y-1].addPL(pL * adj, age)

#                                 self.grid[x+1][y+1].addPL(pL * dia, age)
#                                 self.grid[x-1][y+1].addPL(pL * dia, age)
#                                 self.grid[x+1][y-1].addPL(pL * dia, age)
#                                 self.grid[x-1][y-1].addPL(pL * dia, age)