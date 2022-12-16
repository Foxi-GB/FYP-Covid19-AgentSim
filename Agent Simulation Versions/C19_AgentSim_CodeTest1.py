import pygame, sys, random
from pygame.locals import *
import numpy as np

class Images:
    def __init__(self):
        self.player = self.create_player()

    def create_player(self):
        surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        surface.fill("black")
        pygame.draw.line(surface, "green", (10, 10), (20, 10))
        return surface

class Agent(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.oimage = image
        self.image = image
        self.rect = image.get_rect(center=position)
        self.center = pygame.Vector2(self.rect.center)
        self.vector = pygame.Vector2()
        self.vector.from_polar((1, 0))
        self.turn_speed = 40
        self.speed = 50
        self.angle = 0
    
    def move(self, keys, delta):
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
            self.image = pygame.transform.rotate(self.oimage, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.vector.from_polar((1, self.angle))

        if forward != 0:
            self.center += forward * self.vector * delta * self.speed
            self.rect.center = self.center


class Sim:
    def __init__ (self, caption, size, fps = 60, flags = 0):

        # Pygame Setup

        pygame.display.set_caption(caption)
        self.surface = pygame.display.set_mode(size, flags)
        self.rect = self.surface.get_rect()
        self.clock = pygame.time.Clock()
        self.running = False
        self.delta = 0
        self.fps = fps

        # Variables

        self.images = Images()
        self.agent = Agent(self.images.player, self.rect.center)

        self.agents = []
        for i in range(3):
            Agents = Agent(self.images.player, self.rect.center)
            self.agents.append(Agents)

    def on_draw(self):
        self.surface.fill('white')
        self.surface.blit(self.agent.image, self.agent.rect)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def on_update(self):
        keys = pygame.key.get_pressed()
        self.agent.move(keys, self.delta)

    def main_loop(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.on_event(event)

            for idx, i in enumerate(self.agents):
                self.on_draw()
                self.on_update()
                
            pygame.display.flip()
            # Smooth Movement
            self.delta = self.clock.tick(self.fps) * 0.001

if __name__ == "__main__":
    pygame.init()
    window = Sim("Monster Drops", (800, 600))
    window.main_loop()
    pygame.quit()


