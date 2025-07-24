import pygame
from pygame import gfxdraw
from config import *

class Animation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.progress = 0.0
        self.completed = False

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError

class Explosion(Animation):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.color = color
        self.radius = 5
        self.max_radius = EXPLOSION_RADIUS
        self.duration = ANIMATION_DURATION / 2 # Faster animation

    def update(self, dt):
        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            self.completed = True

    def draw(self, surface):
        radius = self.radius + (self.max_radius - self.radius) * self.progress
        alpha = max(0, 255 - 255 * self.progress)

        if alpha > 0:
            gfxdraw.filled_circle(
                surface,
                int(self.x),
                int(self.y),
                int(radius),
                (*self.color, int(alpha)))

class Miss(Animation):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.duration = ANIMATION_DURATION
        self.color = (255, 0, 0)

    def update(self, dt):
        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            self.completed = True

    def draw(self, surface):
        alpha = max(0, 255 - 255 * self.progress)
        if alpha > 0:
            font = pygame.font.SysFont(FONT_NAME, LARGE_FONT_SIZE, bold=True)
            text = font.render("MISS", True, (*self.color, int(alpha)))
            surface.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))