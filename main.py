import pygame, random, math

pygame.init()

W = 600
screen = pygame.display.set_mode((W, W))
pygame.display.set_caption("Snake de Nekena")
clock = pygame.time.Clock()

# ── Couleurs ──────────────────────────────────────────────
BG          = (8,  12, 20)
GRID_COLOR  = (15, 25, 40)
GREEN_HEAD  = (0,  255, 120)
GREEN_BODY  = (0,  200, 90)
GREEN_DARK  = (0,  140, 60)
FOOD_COL    = (255, 80, 80)
FOOD_GLOW   = (255, 160, 100)
WHITE       = (220, 235, 255)
GRAY        = (80,  100, 130)
ACCENT      = (0,   255, 120)
RED         = (255, 60,  80)
YELLOW      = (255, 210, 0)

# ── Polices ───────────────────────────────────────────────
font_title  = pygame.font.SysFont("consolas", 52, bold=False)
font_medium = pygame.font.SysFont("consolas", 28, bold=False)
font_small  = pygame.font.SysFont("consolas", 20)
font_score  = pygame.font.SysFont("consolas", 22, bold=True)

CELL = 20

def random_food(snake, w):
    while True:
        pos = (random.randrange(0, w, CELL), random.randrange(0, w, CELL))
        if pos not in snake:
            return pos

# ── Helpers de dessin ─────────────────────────────────────
def draw_grid(surf, w):
    for x in range(0, w, CELL):
        pygame.draw.line(surf, GRID_COLOR, (x, 0), (x, w))
    for y in range(0, w, CELL):
        pygame.draw.line(surf, GRID_COLOR, (0, y), (w, y))

def draw_glow_rect(surf, color, rect, radius=6, alpha=60):
    glow = pygame.Surface((rect[2] + 16, rect[3] + 16), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*color, alpha), (0, 0, rect[2] + 16, rect[3] + 16), border_radius=radius + 4)
    surf.blit(glow, (rect[0] - 8, rect[1] - 8))

def draw_rounded_rect(surf, color, rect, radius=5):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_snake(surf, snake):
    for i, seg in enumerate(snake):
        x, y = seg
        r = pygame.Rect(x + 1, y + 1, CELL - 2, CELL - 2)

        if i == 0:
            draw_glow_rect(surf, GREEN_HEAD, r, alpha=80)
            draw_rounded_rect(surf, GREEN_HEAD, r, radius=6)
            pygame.draw.circle(surf, BG, (x + 5,  y + 7), 2)
            pygame.draw.circle(surf, BG, (x + 14, y + 7), 2)
        else:
            t = min(i / max(len(snake) - 1, 1), 1.0)
            r_col = int(GREEN_BODY[0] * (1 - t) + GREEN_DARK[0] * t)
            g_col = int(GREEN_BODY[1] * (1 - t) + GREEN_DARK[1] * t)
            b_col = int(GREEN_BODY[2] * (1 - t) + GREEN_DARK[2] * t)
            draw_rounded_rect(surf, (r_col, g_col, b_col), r, radius=4)

def draw_food(surf, food, tick):
    x, y = food
    pulse = abs(math.sin(tick * 0.08)) * 3
    r = pygame.Rect(x + 2 - pulse/2, y + 2 - pulse/2,
                    CELL - 4 + pulse, CELL - 4 + pulse)
    draw_glow_rect(surf, FOOD_COL, r, alpha=100)
    draw_rounded_rect(surf, FOOD_COL, r, radius=8)
    pygame.draw.circle(surf, FOOD_GLOW, (int(x + 7), int(y + 7)), 2)

def draw_hud(surf, score, w):
    bar = pygame.Surface((w//3, 36), pygame.SRCALPHA)   # ← un peu plus large
    bar.fill((10, 18, 30, 200))
    surf.blit(bar, (0, 0))
    pygame.draw.line(surf, GREEN_DARK, (0, 36), (w//3, 36), 1)

    sc_text = font_score.render(f"SCORE  {score:04d}", True, ACCENT)
    surf.blit(sc_text, (10, 8))

def draw_text_centered(surf, text, font, color, cy, w, glow=False):
    rendered = font.render(text, True, color)
    x = w // 2 - rendered.get_width() // 2
    if glow:
        g = font.render(text, True, (*color[:3], 60) if len(color) == 4 else color)
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            surf.blit(g, (x + dx, cy + dy))
    surf.blit(rendered, (x, cy))

def draw_panel(surf, w, h, title_lines, sub_lines, hint):
    panel_w, panel_h = 380, 280   # un peu plus haut pour le pause
    px = w // 2 - panel_w // 2
    py = h // 2 - panel_h // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((10, 20, 35, 220))
    surf.blit(panel, (px, py))

    pygame.draw.rect(surf, GREEN_DARK, (px, py, panel_w, panel_h), 2, border_radius=8)
    pygame.draw.rect(surf, ACCENT,     (px, py, panel_w, panel_h), 1, border_radius=8)

    y = py + 30
    for line, color, font in title_lines:
        draw_text_centered(surf, line, font, color, y, w, glow=True)
        y += font.get_height() + 8

    y += 20
    for line, color, font in sub_lines:
        draw_text_centered(surf, line, font, color, y, w)
        y += font.get_height() + 6

    # Hint clignotant
    tick = pygame.time.get_ticks()
    if (tick // 600) % 2 == 0:
        draw_text_centered(surf, hint, font_small, GRAY, py + panel_h - 50, w)

# ── État du jeu ───────────────────────────────────────────
def reset():
    # Option : on peut centrer le départ si tu veux
    # cx = (W // CELL // 2) * CELL
    # cy = (W // CELL // 2) * CELL
    # return [(cx, cy), (cx-CELL, cy), (cx-2*CELL, cy)], (CELL, 0), random_food([...], W), 0
    return [(200, 200)], (CELL, 0), random_food([(200, 200)], W), 0

snake, direction, food, score = reset()
state = "menu"
tick  = 0
hi_score = 0

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == "menu":
                if event.key == pygame.K_SPACE:
                    snake, direction, food, score = reset()
                    state = "game"

            elif state == "game":
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    state = "pause"
                if event.key == pygame.K_UP    and direction != (0, CELL):  direction = (0, -CELL)
                if event.key == pygame.K_DOWN  and direction != (0, -CELL): direction = (0,  CELL)
                if event.key == pygame.K_LEFT  and direction != (CELL, 0):  direction = (-CELL, 0)
                if event.key == pygame.K_RIGHT and direction != (-CELL, 0): direction = (CELL,  0)

            elif state == "pause":
                if event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_SPACE):
                    state = "game"
                if event.key == pygame.K_r:
                    snake, direction, food, score = reset()
                    state = "game"
                if event.key in (pygame.K_m, pygame.K_q):
                    state = "menu"

            elif state == "gameover":
                if event.key == pygame.K_r:
                    snake, direction, food, score = reset()
                    state = "game"
                if event.key == pygame.K_m:
                    state = "menu"

    # ── MISE À JOUR JEU ───────────────────────────────────
    if state == "game":
        clock.tick(10)
        tick += 1

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, head)

        if head == food:
            food = random_food(snake, W)
            score += 1
        else:
            snake.pop()

        if head[0] < 0 or head[0] >= W or head[1] < 0 or head[1] >= W or head in snake[1:]:
            hi_score = max(hi_score, score)
            state = "gameover"

    # ── AFFICHAGE ─────────────────────────────────────────
    screen.fill(BG)
    draw_grid(screen, W)

    if state in ("game", "pause"):
        draw_food(screen, food, tick)
        draw_snake(screen, snake)
        draw_hud(screen, score, W)

    if state == "menu":
        draw_panel(screen, W, W,
            title_lines=[("SNAKY", ACCENT, font_title), ("GAME", WHITE, font_medium)],
            sub_lines=[(f"MEILLEUR SCORE : {hi_score:04d}", YELLOW, font_small)],
            hint="[ ESPACE ]  pour jouer"
        )

    elif state == "pause":
        draw_panel(screen, W, W,
            title_lines=[("PAUSE", ACCENT, font_title)],
            sub_lines=[
                ("Jeu en pause", WHITE, font_medium),
            ],
            hint="[ P/Espace ]reprendre/[ R ]recommencer/[M/Q]menu"
        )

    elif state == "gameover":
        new_record = score == hi_score and score > 0
        draw_panel(screen, W, W,
            title_lines=[("GAME  OVER", RED, font_title)],
            sub_lines=[
                (f"SCORE         {score:04d}", WHITE,  font_medium),
                (f"MEILLEUR      {hi_score:04d}", YELLOW, font_small),
                ("NOUVEAU RECORD !" if new_record else "", ACCENT, font_small),
            ],
            hint="[ R ] recommencer   [ M ] menu"
        )

    pygame.display.flip()

pygame.quit()