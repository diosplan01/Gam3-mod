import time
import random
from config import COLORES, HIT_ZONE_Y, NOTE_SPEED

class Note:
    def __init__(self, columna):
        self.columna = columna
        self.y = -100
        self.velocidad = NOTE_SPEED
        self.activa = True
        self.color = COLORES[columna]
        self.alpha = 255
        self.creado = time.time()

    def move(self, dt):
        self.y += self.velocidad * dt * 60

    def update(self, dt, key_presses):
        self.move(dt)
        if self.y > HIT_ZONE_Y + 100:
            self.alpha = max(0, self.alpha - 5)
            if self.alpha <= 0:
                self.activa = False

    def is_hittable(self):
        return abs(self.y - HIT_ZONE_Y) < 50

    def is_offscreen(self):
        return self.y > HIT_ZONE_Y + 100
