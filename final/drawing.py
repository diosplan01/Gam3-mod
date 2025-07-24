import pygame
import config as cfg

# Fonts
pygame.font.init()
titulo_font = pygame.font.SysFont(cfg.FONT_NAME, cfg.TITLE_FONT_SIZE, bold=True)
fuente_grande = pygame.font.SysFont(cfg.FONT_NAME, cfg.LARGE_FONT_SIZE, bold=True)
fuente = pygame.font.SysFont(cfg.FONT_NAME, cfg.DEFAULT_FONT_SIZE)

def draw_button(win, x, y, ancho, alto, color, presionado, columna):
    if presionado:
        brillo_color = (min(color[0]+100, 255), min(color[1]+100, 255), min(color[2]+100, 255))
    else:
        brillo_color = (min(color[0]+50, 255), min(color[1]+50, 255), min(color[2]+50, 255))

    pygame.draw.rect(win, brillo_color, (x, y, ancho, alto), border_radius=cfg.BUTTON_BORDER_RADIUS)
    pygame.draw.rect(win, color, (x+5, y+5, ancho-10, alto-10), border_radius=cfg.BUTTON_INNER_BORDER_RADIUS)
    pygame.draw.rect(win, cfg.BUTTON_BORDER_COLOR, (x, y, ancho, alto), cfg.BUTTON_BORDER_WIDTH, border_radius=cfg.BUTTON_BORDER_RADIUS)

    icono = fuente_grande.render(cfg.BUTTON_ICONS[columna], True, cfg.BUTTON_ICON_COLOR)
    win.blit(icono, (x + ancho//2 - icono.get_width()//2, y + alto//2 - icono.get_height()//2))

def draw_note(win, x, y, color, alpha=255):
    note_surface = pygame.Surface((cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), pygame.SRCALPHA)
    note_surface.set_alpha(alpha)
    pygame.draw.rect(note_surface, color, (0, 0, cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), border_radius=cfg.NOTE_BORDER_RADIUS)
    pygame.draw.rect(note_surface, (255, 255, 255), (0, 0, cfg.NOTE_WIDTH, cfg.NOTE_HEIGHT), cfg.NOTE_BORDER_WIDTH, border_radius=cfg.NOTE_BORDER_RADIUS)
    win.blit(note_surface, (x, y))

def draw_hit_evaluation(win, evaluation):
    if evaluation:
        color = cfg.HIT_EVALUATION_COLORS.get(evaluation, (255, 255, 255))
        text = fuente_grande.render(evaluation.upper(), True, color)
        win.blit(text, (cfg.WIDTH//2 - text.get_width()//2, cfg.HIT_EVALUATION_Y))

column_surfaces = []
for i in range(4):
    columna_surface = pygame.Surface((cfg.COLUMN_WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    columna_surface.fill((0, 0, 0, 0))
    pygame.draw.line(columna_surface, cfg.LINE_COLOR, (0, 0), (0, cfg.HEIGHT), cfg.LINE_WIDTH)
    pygame.draw.line(columna_surface, cfg.LINE_COLOR, (cfg.COLUMN_WIDTH, 0), (cfg.COLUMN_WIDTH, cfg.HEIGHT), cfg.LINE_WIDTH)
    column_surfaces.append(columna_surface)

def draw_game(win, game, teclas, glow_surface):
    win.fill(cfg.BACKGROUND_COLOR)

    for i in range(4):
        rotated_surface = pygame.transform.rotate(column_surfaces[i], game.columns[i]["angle"])
        win.blit(rotated_surface, (game.columns[i]["x"] - rotated_surface.get_width() / 2 + cfg.COLUMN_WIDTH / 2, cfg.HEIGHT / 2 - rotated_surface.get_height() / 2))


    for nota in game.notas:
        if nota.activa:
            columna = game.columns[nota.columna]
            nota.x = columna["x"] + (cfg.COLUMN_WIDTH - cfg.NOTE_WIDTH) / 2
            draw_note(win, nota.x, nota.y, nota.color, nota.alpha)

    pygame.draw.line(win, cfg.HIT_ZONE_COLOR, (0, cfg.HIT_ZONE_Y), (cfg.WIDTH, cfg.HIT_ZONE_Y), cfg.HIT_ZONE_LINE_WIDTH)

    for i in range(4):
        draw_button(
            win,
            i * cfg.COLUMN_WIDTH + (cfg.COLUMN_WIDTH - cfg.BUTTON_WIDTH) // 2,
            cfg.HIT_ZONE_Y - cfg.BUTTON_Y_OFFSET,
            cfg.BUTTON_WIDTH,
            cfg.BUTTON_HEIGHT,
            cfg.COLORES[i],
            teclas[i],
            i
        )

    for anim in game.animations:
        anim.draw(win)

    pygame.draw.rect(win, cfg.PANEL_COLOR, (0, 0, cfg.WIDTH, cfg.PANEL_HEIGHT))
    pygame.draw.line(win, cfg.PANEL_LINE_COLOR, (0, cfg.PANEL_HEIGHT), (cfg.WIDTH, cfg.PANEL_HEIGHT), cfg.LINE_WIDTH)

    titulo = titulo_font.render(cfg.GAME_TITLE, True, cfg.TITLE_COLOR)
    win.blit(titulo, (cfg.WIDTH//2 - titulo.get_width()//2, 20))

    score_text_surface = fuente.render(f"Puntaje: {game.puntaje}", True, cfg.SCORE_TEXT_COLOR)
    win.blit(score_text_surface, (cfg.SCORE_X_OFFSET, 100))

    level_text_surface = fuente.render(f"Nivel: {game.nivel}", True, cfg.LEVEL_TEXT_COLOR)
    win.blit(level_text_surface, (cfg.WIDTH - cfg.LEVEL_X_OFFSET, 100))

    if game.combo > 0:
        combo_color = cfg.COMBO_TEXT_COLOR_1
        combo_text_surface = fuente_grande.render(f"{game.combo}x COMBO!", True, combo_color)
        win.blit(combo_text_surface, (cfg.WIDTH//2 - combo_text_surface.get_width()//2, 100))

    vida_text = fuente.render(cfg.LIFE_TEXT, True, cfg.LIFE_COLOR)
    win.blit(vida_text, (cfg.WIDTH - cfg.LIFE_X_OFFSET, 100))
    for i in range(game.vidas):
        pygame.draw.circle(win, cfg.LIFE_COLOR, (cfg.WIDTH - 250 + i * cfg.LIFE_SPACING, cfg.LIFE_Y_OFFSET), 15)

    if game.last_hit_evaluation:
        draw_hit_evaluation(win, game.last_hit_evaluation)

    if not game.juego_activo:
        overlay = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        overlay.fill(cfg.GAME_OVER_BG_COLOR)
        win.blit(overlay, (0, 0))

        fin_text = titulo_font.render(cfg.GAME_OVER_MESSAGE, True, cfg.GAME_OVER_TEXT_COLOR)
        win.blit(fin_text, (cfg.WIDTH//2 - fin_text.get_width()//2, cfg.HEIGHT//2 - cfg.GAME_OVER_Y_OFFSET))

        puntaje_final = fuente_grande.render(f"Puntaje final: {game.puntaje}", True, cfg.FINAL_SCORE_COLOR)
        win.blit(puntaje_final, (cfg.WIDTH//2 - puntaje_final.get_width()//2, cfg.HEIGHT//2 + cfg.FINAL_SCORE_Y_OFFSET))

        max_combo_text = fuente_grande.render(f"Combo máximo: {game.max_combo}x", True, cfg.MAX_COMBO_COLOR)
        win.blit(max_combo_text, (cfg.WIDTH//2 - max_combo_text.get_width()//2, cfg.HEIGHT//2 + cfg.MAX_COMBO_Y_OFFSET))

        reiniciar_text = fuente.render(cfg.RESTART_MESSAGE, True, cfg.RESTART_TEXT_COLOR)
        win.blit(reiniciar_text, (cfg.WIDTH//2 - reiniciar_text.get_width()//2, cfg.HEIGHT//2 + cfg.RESTART_Y_OFFSET))

    pygame.display.flip()