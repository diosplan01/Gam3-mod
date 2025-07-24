import pygame
import time
import random
import math
from config import *
from note import Note
from animations import Explosion, Miss

class Game:
    """
    This class manages the game state and the main game loop.
    """
    def __init__(self):
        self.notas = []
        self.animations = []
        self.vidas = INITIAL_LIVES
        self.puntaje = INITIAL_SCORE
        self.fallos_seguidos = 0
        self.juego_activo = True
        self.combo = 0
        self.max_combo = 0
        self.nivel = 1
        self.tiempo_juego = 0
        self.tiempo_ultima_nota = 0
        self.ultima_penalizacion = 0
        self.pulsaciones_innecesarias = 0
        self.tiempo_inicio = time.time()
        self.last_hit_evaluation = None
        self.pattern_index = 0
        self.columns = [{"x": i * COLUMN_WIDTH, "angle": 0} for i in range(4)]
        self.patterns = [
            [0, 1, 2, 3], [0, 2, 1, 3], [3, 2, 1, 0], [0, 1, 0, 1], [2, 3, 2, 3], [0, 3, 1, 2],
            # Nuevos patrones más complejos
            [0, 1, 2, 1], [3, 2, 1, 2], [0, 2, 0, 3], [1, 3, 1, 2],
            [0, 1, 3, 2], [0, 3, 2, 1], [1, 2, 0, 3], [1, 3, 0, 2],
            [2, 0, 1, 3], [2, 1, 3, 0], [3, 0, 2, 1], [3, 1, 0, 2]
        ]

    def reset_timer(self):
        """
        Resets the game timer.
        """
        self.tiempo_inicio = time.time()

    def reiniciar_juego(self):
        """
        Resets the game to its initial state.
        """
        self.notas = []
        self.animations = []
        self.vidas = INITIAL_LIVES
        self.puntaje = INITIAL_SCORE
        self.fallos_seguidos = 0
        self.juego_activo = True
        self.combo = 0
        self.max_combo = 0
        self.nivel = 1
        self.tiempo_juego = 0
        self.tiempo_inicio = time.time()
        self.last_hit_evaluation = None
        self.pattern_index = 0

    def generate_note(self):
        """
        Generates a new note with a random column.
        """
        notes_to_generate = []
        if self.nivel > 15:
            num_notes = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1], k=1)[0]
        elif self.nivel > 10:
            num_notes = random.choices([1, 2], weights=[0.8, 0.2], k=1)[0]
        else:
            num_notes = 1

        available_columns = [0, 1, 2, 3]
        for _ in range(num_notes):
            if not available_columns:
                break
            columna = random.choice(available_columns)
            available_columns.remove(columna)
            notes_to_generate.append(Note(columna))

        return notes_to_generate

    def evaluate_hit(self, nota):
        """
        Evaluates the timing of a hit and returns the corresponding grade and score.
        """
        diff = abs(nota.y - HIT_ZONE_Y)
        for category, values in EVALUATION_CATEGORIES.items():
            if diff <= values["window"]:
                return category, values["score"]
        return "bad", 0

    def update(self, key_presses, dt):
        """
        Updates the game state on each frame.
        """
        if not self.juego_activo:
            return

        ahora = time.time()
        self.tiempo_juego = ahora - self.tiempo_inicio
        self.nivel = max(1, min(MAX_LEVEL, int(self.tiempo_juego // DIFFICULTY_INCREASE_INTERVAL + 1)))

        intervalo_notas = max(0.2, NOTE_INTERVAL - self.nivel * NOTE_INTERVAL_DECREASE_RATE)
        velocidad_base = min(12, NOTE_SPEED + self.nivel * NOTE_SPEED_INCREASE_RATE)

        if ahora - self.tiempo_ultima_nota > intervalo_notas:
            new_notes = self.generate_note()
            for note in new_notes:
                self.notas.append(note)
            self.tiempo_ultima_nota = ahora

        for nota in self.notas[:]:
            nota.velocidad = velocidad_base
            nota.update(dt, key_presses)

            if not nota.activa:
                self.notas.remove(nota)
                continue

            if nota.is_hittable() and nota.columna in key_presses:
                self.handle_hit(nota)

            elif nota.is_offscreen():
                self.handle_miss(nota)
                self.notas.remove(nota)

        for i in key_presses:
            nota_cercana = False
            for nota in self.notas:
                if nota.columna == i and abs(nota.y - HIT_ZONE_Y) < 150:
                    nota_cercana = True
                    break

            if not nota_cercana and ahora - self.ultima_penalizacion > 0.1:
                self.puntaje -= WRONG_HIT_PENALTY
                self.pulsaciones_innecesarias += 1
                self.ultima_penalizacion = ahora

        for anim in self.animations[:]:
            anim.update(dt)
            if anim.completed:
                self.animations.remove(anim)

        self.update_columns()

    def update_columns(self):
        if self.nivel > 10:
            for i, col in enumerate(self.columns):
                angle_factor = (self.nivel - 10) / 10.0
                col["angle"] = math.sin(self.tiempo_juego * 2 + i) * 5 * angle_factor

                offset_factor = (self.nivel - 10) / 5.0
                col["x"] = i * COLUMN_WIDTH + math.sin(self.tiempo_juego + i) * 20 * offset_factor

    def handle_hit(self, nota):
        """
        Handles a successful hit.
        """
        nota.activa = False
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.fallos_seguidos = 0

        evaluation, score = self.evaluate_hit(nota)
        self.puntaje += score * self.combo
        self.last_hit_evaluation = evaluation

        self.animations.append(Explosion(
            nota.columna * COLUMN_WIDTH + COLUMN_WIDTH // 2,
            nota.y,
            nota.color
        ))

        if nota in self.notas:
            self.notas.remove(nota)

    def handle_miss(self, nota):
        """
        Handles a missed note.
        """
        self.combo = 0
        self.puntaje -= MISS_PENALTY
        self.vidas -= 1
        self.last_hit_evaluation = "miss"
        self.animations.append(Miss(
            nota.columna * COLUMN_WIDTH + COLUMN_WIDTH // 2,
            nota.y
        ))
        if self.vidas <= 0:
            self.juego_activo = False