import pygame
import sys
import threading
from config import *
from game import Game
from drawing import draw_game
from serial_reader import SerialReader

def game_logic_thread(game, serial_reader, running_event, reloj):
    while running_event.is_set():
        dt = reloj.tick(60) / 1000.0
        key_presses = serial_reader.get_key_presses()
        game.update(key_presses, dt)

def main():
    print("El juego comenzo :)")
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sublime")
    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    reloj = pygame.time.Clock()

    game = Game()
    serial_reader = SerialReader()
    serial_reader.start()

    running_event = threading.Event()
    running_event.set()

    logic_thread = threading.Thread(target=game_logic_thread, args=(game, serial_reader, running_event, reloj))
    logic_thread.daemon = True  # Hacer demonio para cerrar automáticamente
    logic_thread.start()

    corriendo = True
    while corriendo:
        reloj.tick(40)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    game.reiniciar_juego()
                    game.reset_timer()
                elif evento.key == pygame.K_ESCAPE:
                    corriendo = False

        # Verificar reinicio desde ESP32 (prioridad alta)
        if serial_reader.get_reset_request():
            game.reiniciar_juego()
            game.reset_timer()

        key_states = serial_reader.get_key_states()
        draw_game(win, game, key_states, glow_surface)

    running_event.clear()
    serial_reader.stop()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
