import pygame as pg
import sys
import os
import math
import random

# -------------------- INITIALIZATION --------------------
pg.init()
pg.mixer.init()

# -------------------- CONFIGURATION --------------------
ASSETS_FOLDER = "Assets folder" 
ENEMY_SIZE = 25 
FPS = 60
SPAWN_PROTECTION_RADIUS = 5
HIGH_SCORE_FILE = "highscore.txt"

# Colors
GREEN_HIGHLIGHT = (0, 255, 0)
RED_HIGHLIGHT = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SIDEBAR_COLOR = (40, 40, 50) 
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
ICE_BLUE = (135, 206, 250)
LIME_GREEN = (50, 205, 50) 
INPUT_BG = (30, 30, 30)
INPUT_ACTIVE_COLOR = (100, 200, 255)
INPUT_INACTIVE_COLOR = (100, 100, 100)

# Towers
TOWER_DATA = {
    1: {'name': 'Archer', 'cost': 50, 'color': (0, 255, 0)},
    2: {'name': 'Mage', 'cost': 100, 'color': (0, 100, 255)},
    3: {'name': 'Cannon', 'cost': 200, 'color': (255, 0, 0)},
    4: {'name': 'Sniper', 'cost': 300, 'color': (128, 0, 128)}
}

# Theme Variables
IS_DARK_MODE = True
UI_BG_COLOR = (40, 40, 50)       
UI_TEXT_COLOR = (255, 255, 255)  
GAME_BG_COLOR = (50, 80, 50)     
MENU_BG_COLOR = (30, 30, 45)     

def update_theme():
    global UI_BG_COLOR, UI_TEXT_COLOR, GAME_BG_COLOR, MENU_BG_COLOR, IS_DARK_MODE
    if IS_DARK_MODE:
        UI_BG_COLOR = (40, 40, 50)
        UI_TEXT_COLOR = (255, 255, 255)
        GAME_BG_COLOR = (50, 80, 50)
        MENU_BG_COLOR = (30, 30, 45)
    else: 
        UI_BG_COLOR = (220, 220, 220)
        UI_TEXT_COLOR = (255, 255, 255) 
        GAME_BG_COLOR = (100, 200, 100)
        MENU_BG_COLOR = (240, 240, 245)

# Power-ups
POWERUP_CONFIG = {
    'damage': {'name': 'Damage x2', 'cost': 500, 'duration': 10000, 'cooldown': 30000, 'color': ORANGE},
    'freeze': {'name': 'Freeze', 'cost': 300, 'duration': 5000, 'cooldown': 20000, 'color': ICE_BLUE},
    'nuke': {'name': 'Nuke', 'cost': 800, 'duration': 0, 'cooldown': 60000, 'color': (255, 50, 50)},
    'heal': {'name': 'Heal +5', 'cost': 600, 'duration': 0, 'cooldown': 45000, 'color': LIME_GREEN}
}

# Screen & Resolution
info = pg.display.Info()
MAX_W = info.current_w
MAX_H = info.current_h

current_scale_idx = 1 
SCALES = [0.5, 0.7, 0.9]
SCALE_NAMES = ["Small (50%)", "Medium (70%)", "Large (90%)"]

SCREEN_W = 0
SCREEN_H = 0
SIDEBAR_WIDTH = 0
MAP_WIDTH = 0
screen = None

player_name = "Player"
high_score = 0

def set_resolution(scale_idx):
    global SCREEN_W, SCREEN_H, SIDEBAR_WIDTH, MAP_WIDTH, screen
    scale = SCALES[scale_idx]
    SCREEN_W = int(MAX_W * scale)
    SCREEN_H = int(MAX_H * scale)
    SIDEBAR_WIDTH = int(SCREEN_W * 0.30)
    MAP_WIDTH = SCREEN_W - SIDEBAR_WIDTH
    screen = pg.display.set_mode((SCREEN_W, SCREEN_H))
    pg.display.set_caption(f"Tower Defense - THE FINAL BATTLE")

set_resolution(current_scale_idx)
clock = pg.time.Clock()

# -------------------- DATA HANDLING --------------------
def load_high_score():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                high_score = int(f.read())
        except:
            high_score = 0

def save_high_score(new_score):
    global high_score
    if new_score > high_score:
        high_score = new_score
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                f.write(str(high_score))
        except: pass

load_high_score()

# -------------------- ASSET LOADING --------------------
class DummySound:
    def play(self): pass
    def set_volume(self, v): pass

ENEMY_IMGS = {}
TOWER_IMGS = {} 
MENU_BG_IMG = None
SPAWN_IMG = None
GOAL_IMG = None
ENEMY_IMGS_RAW = {}

try:
    pg.mixer.music.load(os.path.join(ASSETS_FOLDER, "main_menu sound.wav"))
except: pass

try:
    click_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "click_sound_1.wav"))
    hover_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "Menu Selection Click.wav"))
    shoot_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "gunshot12.wav")) 
    die_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "die.wav"))     
    wave_clear_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "wave_clear.wav"))
    
    # --- أضف هذين السطرين هنا ---
    game_over_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "game_over.wav")) # تأكد أن الملف موجود
    game_over_sound.set_volume(0.5)
    # ---------------------------

    click_sound.set_volume(0.4); hover_sound.set_volume(0.3)
    shoot_sound.set_volume(0.2); die_sound.set_volume(0.3); wave_clear_sound.set_volume(0.4)
except:
    # --- وعدل هذا السطر أيضاً ليمنع الكراش إذا الملف غير موجود ---
    click_sound = hover_sound = shoot_sound = die_sound = wave_clear_sound = game_over_sound = DummySound()
try:
    archer_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "gunshot12.wav"))
    mage_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "mega_tower.wav"))
    cannon_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "tower_strong.wav"))
    sniper_sound = pg.mixer.Sound(os.path.join(ASSETS_FOLDER, "tower_strong.wav"))
    
    archer_sound.set_volume(0.2); mage_sound.set_volume(0.2)
    cannon_sound.set_volume(0.4); sniper_sound.set_volume(0.3)
except:
    archer_sound = mage_sound = cannon_sound = sniper_sound = DummySound()

try:
    base_enemy_path = os.path.join(ASSETS_FOLDER, "enemy.png")
    base_img_raw = pg.image.load(base_enemy_path).convert_alpha() if os.path.exists(base_enemy_path) else None
    
    if base_img_raw: ENEMY_IMGS_RAW['base'] = base_img_raw

    for e_type in ["normal", "strong", "shooter"]:
        path = os.path.join(ASSETS_FOLDER, f"enemy_{e_type}.png")
        if os.path.exists(path):
            ENEMY_IMGS_RAW[e_type] = pg.image.load(path).convert_alpha()
        elif base_img_raw:
            ENEMY_IMGS_RAW[e_type] = base_img_raw
except: pass

try:
    tower_map = {1: "archer", 2: "mage", 3: "cannon", 4: "sniper"}
    for t_id, t_name in tower_map.items():
        path = os.path.join(ASSETS_FOLDER, f"tower_{t_name}.png")
        if os.path.exists(path):
            TOWER_IMGS[t_id] = pg.image.load(path).convert_alpha()
        else:
            TOWER_IMGS[t_id] = None
except: pass

try:
    s_path = os.path.join(ASSETS_FOLDER, "spawn.png")
    if os.path.exists(s_path): SPAWN_IMG = pg.image.load(s_path).convert_alpha()
    
    g_path = os.path.join(ASSETS_FOLDER, "goal.png")
    if os.path.exists(g_path): GOAL_IMG = pg.image.load(g_path).convert_alpha()

    mbg_path = os.path.join(ASSETS_FOLDER, "menu_bg.png")
    if not os.path.exists(mbg_path): mbg_path = os.path.join(ASSETS_FOLDER, "menu_bg.jpg")
    if os.path.exists(mbg_path):
        MENU_BG_IMG = pg.image.load(mbg_path).convert()
except: pass

# -------------------- CLASSES --------------------
class Bullet:
    __slots__ = ['x', 'y', 'target', 'damage', 'color', 'speed', 'active']
    def __init__(self, x, y, target, damage, color, speed=15):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.color = color
        self.speed = speed
        self.active = True

    def move(self):
        if not self.target.alive:
            self.active = False
            return

        dir_x = self.target.x - self.x
        dir_y = self.target.y - self.y
        dist = math.hypot(dir_x, dir_y)

        if dist <= self.speed:
            self.x, self.y = self.target.x, self.target.y
            self.target.take_damage(self.damage)
            self.active = False 
        else:
            factor = self.speed / dist
            self.x += dir_x * factor
            self.y += dir_y * factor

    def draw(self, surface):
        pg.draw.circle(surface, self.color, (int(self.x), int(self.y)), 7)

class Enemy:
    def __init__(self, path, wave_difficulty, e_type="normal"):
        self.path = path
        self.path_index = 0
        self.type = e_type
        self.x, self.y = path[0] if path else (0, 0)
            
        self.speed = 2 + (wave_difficulty * 0.2)
        base_hp = 60 + (wave_difficulty * 35)
        self.reward = 10 + (wave_difficulty * 2)
        self.color = (200, 50, 50)
        self.shoot_range = 0
        self.damage = 0
        self.cooldown = 0
        self.last_shot = 0
        self.bullets = []
        
        self.raw_image = ENEMY_IMGS_RAW.get(self.type, ENEMY_IMGS_RAW.get('base'))

        if self.type == "strong":
            self.max_health = base_hp * 2.5; self.speed *= 0.6; self.color = (0, 255, 255)
            self.reward *= 2
        elif self.type == "shooter":
            self.max_health = base_hp * 0.8; self.color = (255, 215, 0)
            self.shoot_range = 250; self.damage = 45; self.cooldown = 1500
            self.reward *= 1.5
        else:
            self.max_health = base_hp; self.color = (255, 0, 255)

        self.health = self.max_health
        self.alive = True
        self.reached_end = False

    def move(self, speed_multiplier=1):
        if not self.path: return
        cur_speed = self.speed * speed_multiplier

        if self.path_index < len(self.path) - 1:
            tx, ty = self.path[self.path_index + 1]
            dist = math.hypot(tx - self.x, ty - self.y)
            
            if dist <= cur_speed:
                self.x, self.y = tx, ty
                self.path_index += 1
            else:
                factor = cur_speed / dist
                self.x += (tx - self.x) * factor
                self.y += (ty - self.y) * factor
        else:
            self.reached_end = True; self.alive = False

    def update(self, towers):
        for b in self.bullets[:]:
            b.move()
            if not b.active: self.bullets.remove(b)

        if self.type == "shooter" and self.alive:
            now = pg.time.get_ticks()
            if now - self.last_shot >= self.cooldown:
                target, min_d = None, self.shoot_range
                for t in towers:
                    d = math.hypot(t.x - self.x, t.y - self.y)
                    if d <= min_d: min_d = d; target = t
                if target:
                    self.bullets.append(Bullet(self.x, self.y, target, self.damage, BLACK, speed=8))
                    self.last_shot = now
                    shoot_sound.play() 

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            die_sound.play() 

    def draw(self, surface, tile_w, tile_h):
        draw_size = min(tile_w, tile_h)
        radius = int(draw_size * 0.9) // 2
        
        if self.raw_image: 
            scaled_img = pg.transform.scale(self.raw_image, (int(draw_size*0.9), int(draw_size*0.9)))
            rect = scaled_img.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(scaled_img, rect)
        else:
            pg.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)
            if self.type == "shooter": pg.draw.circle(surface, BLACK, (int(self.x), int(self.y)), radius//2)

        if self.health < self.max_health:
            bar_w = int(draw_size * 0.8)
            ratio = max(0, min(1, self.health / self.max_health))
            bx = self.x - bar_w // 2
            by = self.y + radius + 5 
            pg.draw.rect(surface, (100, 0, 0), (bx, by, bar_w, 4)) 
            pg.draw.rect(surface, (0, 255, 0), (bx, by, bar_w * ratio, 4))
        
        for b in self.bullets: b.draw(surface)

class Tower:
    def __init__(self, x, y, type_id):
        self.x, self.y = x, y
        self.type_id = type_id
        self.level = 1 
        self.size = 40
        self.bullets = []
        self.max_health = 200
        self.health = self.max_health
        self.alive = True
        
        self.base_cost = TOWER_DATA[type_id]['cost']
        self.total_spent = self.base_cost 
        self.last_upgrade_cost = 0 

        orig = TOWER_IMGS.get(type_id)
        self.image = pg.transform.scale(orig, (40, 40)) if orig else None

        if type_id == 1: # Archer
            self.range = 250; self.damage = 15; self.cooldown = 600; self.color = (0, 255, 0)
            self.bullet_color = (255, 255, 0); self.shoot_sfx = archer_sound 
        elif type_id == 2: # Mage
            self.range = 220; self.damage = 35; self.cooldown = 1100; self.color = (0, 100, 255)
            self.bullet_color = (0, 255, 255); self.shoot_sfx = mage_sound   
        elif type_id == 3: # Cannon
            self.range = 220; self.damage = 60; self.cooldown = 1500; self.color = (255, 0, 0)
            self.bullet_color = (0, 0, 0); self.max_health = 400; self.health = 400
            self.shoot_sfx = cannon_sound 
        elif type_id == 4: # Sniper
            self.range = 450; self.damage = 120; self.cooldown = 3500; self.color = (128, 0, 128)
            self.bullet_color = (255, 0, 255); self.shoot_sfx = sniper_sound 
            
        self.last_shot = pg.time.get_ticks()

    def get_upgrade_cost(self):
        if self.level == 1:
            return self.base_cost
        else:
            return self.base_cost + self.last_upgrade_cost

    def upgrade(self):
        cost = self.get_upgrade_cost()
        self.last_upgrade_cost = cost 
        self.total_spent += cost 
        self.level += 1
        self.damage = int(self.damage * 1.3)
        self.range = int(self.range * 1.1)   
        return cost

    def update(self, enemies, dmg_mult=1):
        if not self.alive: return
        now = pg.time.get_ticks()
        for b in self.bullets[:]:
            b.move()
            if not b.active: self.bullets.remove(b)

        if now - self.last_shot >= self.cooldown:
            target = None
            range_sq = self.range * self.range
            max_index = -1
            min_dist_next = float('inf')

            for e in enemies:
                d_sq = (e.x - self.x)**2 + (e.y - self.y)**2
                if d_sq <= range_sq:
                    dist_next = 0
                    if e.path_index < len(e.path) - 1:
                        nx, ny = e.path[e.path_index + 1]
                        dist_next = (nx - e.x)**2 + (ny - e.y)**2
                    
                    if target is None:
                        target = e
                        max_index = e.path_index
                        min_dist_next = dist_next
                    else:
                        if e.path_index > max_index:
                            target = e
                            max_index = e.path_index
                            min_dist_next = dist_next
                        elif e.path_index == max_index:
                            if dist_next < min_dist_next:
                                target = e
                                min_dist_next = dist_next
            
            if target:
                self.bullets.append(Bullet(self.x, self.y, target, self.damage * dmg_mult, self.bullet_color))
                self.last_shot = now
                self.shoot_sfx.play()

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0: self.alive = False

    def draw(self, surface, tile_w, tile_h):
        draw_size = min(tile_w, tile_h)
        
        if self.image:
            scaled_t = pg.transform.scale(self.image, (draw_size, draw_size))
            surface.blit(scaled_t, scaled_t.get_rect(center=(self.x, self.y)))
        else:
            r = pg.Rect(self.x - draw_size//2, self.y - draw_size//2, draw_size, draw_size)
            pg.draw.rect(surface, self.color, r, border_radius=5)
            pg.draw.rect(surface, BLACK, r, 2, border_radius=5)

        font = pg.font.Font(None, int(draw_size*0.5))
        lvl_txt = font.render(str(self.level), True, GOLD)
        surface.blit(lvl_txt, (self.x, self.y - draw_size//2))

        if self.health < self.max_health:
            ratio = self.health / self.max_health
            bw = int(draw_size * 0.8)
            # Bar below tower
            pg.draw.rect(surface, (100,0,0), (self.x - bw//2, self.y + draw_size//2 + 5, bw, 4))
            pg.draw.rect(surface, (0,255,0), (self.x - bw//2, self.y + draw_size//2 + 5, bw*ratio, 4))
        
        for b in self.bullets: b.draw(surface)

# -------------------- HELPERS --------------------
def calculate_path(matrix):
    rows, cols = len(matrix), len(matrix[0])
    tile_w, tile_h = MAP_WIDTH // cols, SCREEN_H // rows
    start = next(((c, r) for r in range(rows) for c in range(cols) if matrix[r][c] == 3), None)
    if not start: return []

    path = []
    curr = start
    visited = set()
    
    while True:
        c, r = curr
        path.append((c * tile_w + tile_w // 2, r * tile_h + tile_h // 2))
        visited.add(curr)
        if matrix[r][c] == 2: break
        
        ordered_neighbors = [(c+1, r), (c-1, r), (c, r+1), (c, r-1)]
        next_step = None
        
        for nc, nr in ordered_neighbors:
            if 0 <= nr < rows and 0 <= nc < cols:
                if (nc, nr) not in visited and matrix[nr][nc] in [1, 2]:
                    next_step = (nc, nr)
                    break
        
        if not next_step:
            for nc, nr in ordered_neighbors:
                if 0 <= nr < rows and 0 <= nc < cols:
                    if (nc, nr) not in visited and matrix[nr][nc] == 3:
                        next_step = (nc, nr)
                        break
        
        if next_step: curr = next_step
        else: break
            
    return path

def draw_Button(rect, text, mouse_pos, hover_text=None, color_override=None):
    if not hasattr(draw_Button, "hover_states"):
        draw_Button.hover_states = {}

    rect_tuple = (rect.x, rect.y, rect.w, rect.h)
    was_hovered = draw_Button.hover_states.get(rect_tuple, False)

    color = color_override if color_override else (240, 160, 30)
    hover_c = (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30))
    is_hovered = rect.collidepoint(mouse_pos)
    
    if is_hovered:
        pg.draw.rect(screen, hover_c, rect, border_radius=10)
        if not was_hovered: 
            hover_sound.play()
            draw_Button.hover_states[rect_tuple] = True
    else:
        pg.draw.rect(screen, color, rect, border_radius=10)
        draw_Button.hover_states[rect_tuple] = False

    if text:
        txt = hover_text if (is_hovered and hover_text) else text
        font = pg.font.Font(None, int(rect.height * 0.5)) 
        text_col = BLACK if color == GOLD or color == (240,160,30) or color == LIME_GREEN else BLACK 
        if color == (200, 50, 50): text_col = WHITE 
        lbl = font.render(txt, True, text_col)
        screen.blit(lbl, lbl.get_rect(center=rect.center))
    return is_hovered

def pre_render_map(map_matrix):
    rows, cols = len(map_matrix), len(map_matrix[0])
    tw, th = MAP_WIDTH // cols, SCREEN_H // rows
    map_surf = pg.Surface((MAP_WIDTH, SCREEN_H))
    
    for r in range(rows):
        for c in range(cols):
            val = map_matrix[r][c]
            x, y = c * tw, r * th
            if val == 0: col = GAME_BG_COLOR 
            elif val == 1: col = (139, 69, 19)
            elif val == 2: col = (139, 19, 29)
            elif val == 3: col = (19, 89, 139)
            else: col = (0,0,0)

            pg.draw.rect(map_surf, col, (x, y, tw, th))
            if val == 0: 
                border_col = (10, 80, 40) if IS_DARK_MODE else (150, 255, 150)
                pg.draw.rect(map_surf, border_col, (x, y, tw, th), 1)

            if val == 2 and GOAL_IMG: 
                map_surf.blit(pg.transform.scale(GOAL_IMG, (tw, th)), (x, y))
            elif val == 3 and SPAWN_IMG: 
                map_surf.blit(pg.transform.scale(SPAWN_IMG, (tw, th)), (x, y))
    return map_surf.convert()

def check_placement(matrix, towers, c, r, tw):
    rows, cols = len(matrix), len(matrix[0])
    if not (0 <= c < cols and 0 <= r < rows) or matrix[r][c] != 0: return False
    for t in towers:
        if abs(c - int(t.x / tw)) == 0 and abs(r - int(t.y / (SCREEN_H // rows))) == 0: return False
    return True

def draw_highlight(matrix, towers, spawn, sel_t, sel_on_map):
    if sel_on_map: return 

    mx, my = pg.mouse.get_pos()
    if mx > MAP_WIDTH: return
    rows, cols = len(matrix), len(matrix[0])
    tw, th = MAP_WIDTH // cols, SCREEN_H // rows
    c, r = mx // tw, my // th
    
    if 0 <= r < rows and 0 <= c < cols:
        valid = False
        if sel_t: 
            valid = check_placement(matrix, towers, c, r, tw)
            if spawn and math.hypot(c-spawn[0], r-spawn[1]) < SPAWN_PROTECTION_RADIUS: 
                valid = False
            pg.draw.rect(screen, GREEN_HIGHLIGHT if valid else RED_HIGHLIGHT, (c*tw, r*th, tw, th), 3)
        else: 
            for t in towers:
                t_c, t_r = int(t.x / tw), int(t.y / (SCREEN_H // rows))
                if c == t_c and r == t_r:
                    pg.draw.rect(screen, CYAN, (c*tw, r*th, tw, th), 3)

# [DYNAMIC SIDEBAR] Compact Layout
def draw_sidebar(lives, money, score, t_count, wave, sel_type, p_states, now, selected_tower_obj, dev_mode):
    pg.draw.rect(screen, UI_BG_COLOR, (MAP_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_H))
    pg.draw.line(screen, UI_TEXT_COLOR, (MAP_WIDTH, 0), (MAP_WIDTH, SCREEN_H), 3)

    panel_x = MAP_WIDTH
    
    f1 = pg.font.Font(None, int(SCREEN_H * 0.04)) 
    f2 = pg.font.Font(None, int(SCREEN_H * 0.025)) 
    f_pwr = pg.font.Font(None, int(SCREEN_H * 0.035))

    # 1. Stats
    stat_y = SCREEN_H * 0.01
    stat_gap = SCREEN_H * 0.028
    
    screen.blit(f1.render(f"Lives: {lives}", True, (255, 100, 100)), (panel_x + 10, stat_y))
    screen.blit(f1.render(f"Money: ${money}", True, GOLD), (panel_x + 10, stat_y + stat_gap))
    screen.blit(f1.render(f"Wave: {wave}", True, UI_TEXT_COLOR), (panel_x + 10, stat_y + stat_gap*2))
    screen.blit(f2.render(f"Best: {high_score}", True, ICE_BLUE), (panel_x + 10, stat_y + stat_gap*3))
    screen.blit(f1.render(f"Score: {score}", True, WHITE), (panel_x + SIDEBAR_WIDTH//2 + 5, stat_y))

    # Dev Mode Indicator - [DELETED]

    tower_y_start = stat_y + stat_gap * 4.0
    
    btn_size = int(SIDEBAR_WIDTH * 0.30)
    gap_x = int(SIDEBAR_WIDTH * 0.1)
    c1 = panel_x + gap_x
    c2 = c1 + btn_size + gap_x
    
    t1, t2, t3, t4 = None, None, None, None
    upgrade_rect, sell_rect = None, None
    
    if selected_tower_obj:
        screen.blit(f1.render("- SELECTED -", True, CYAN), (panel_x + 10, tower_y_start))
        
        type_name = TOWER_DATA[selected_tower_obj.type_id]['name']
        screen.blit(f2.render(f"{type_name} Lvl {selected_tower_obj.level}", True, WHITE), (panel_x + 20, tower_y_start + 30))
        screen.blit(f2.render(f"Dmg: {selected_tower_obj.damage}", True, WHITE), (panel_x + 20, tower_y_start + 55))
        
        up_cost = selected_tower_obj.get_upgrade_cost()
        upgrade_rect = pg.Rect(c1, tower_y_start + 90, SIDEBAR_WIDTH - 2*gap_x, 50)
        
        col = GREEN_HIGHLIGHT if money >= up_cost else (100, 100, 100)
        draw_Button(upgrade_rect, "", pg.mouse.get_pos(), color_override=col)
        
        ulbl = f2.render(f"UPGRADE ${up_cost}", True, BLACK)
        screen.blit(ulbl, ulbl.get_rect(center=upgrade_rect.center))
        
        sell_val = selected_tower_obj.total_spent // 2 
        sell_rect = pg.Rect(c1, tower_y_start + 150, SIDEBAR_WIDTH - 2*gap_x, 40)
        draw_Button(sell_rect, f"SELL +${sell_val}", pg.mouse.get_pos(), color_override=(200, 50, 50))
        
        power_y_start = tower_y_start + 200
        
    else:
        screen.blit(f1.render("- TOWERS -", True, WHITE), (panel_x + 10, tower_y_start))
        
        # --- التعديل هنا: قمنا بزيادة القيم لعمل مسافة أكبر ---
        # كانت 0.04 وزدناها قليلاً لتناسب العنوان
        t_row1 = tower_y_start + int(SCREEN_H * 0.06) 
        
        # كانت 0.02 وهذه هي المشكلة الرئيسية، جعلناها 0.08 لترك مسافة للسعر والاسم
        t_row2 = t_row1 + btn_size + int(SCREEN_H * 0.09) 

        def draw_t(x, y, col, name, pr, tid):
            # تحسين بسيط: توسيط الاسم فوق الزر بدلاً من x+5
            name_surf = f2.render(name, True, WHITE)
            screen.blit(name_surf, (x + (btn_size - name_surf.get_width())//2, y - 20))
            
            r = pg.Rect(x, y, btn_size, btn_size)
            pg.draw.rect(screen, col, r, border_radius=5)
            if TOWER_IMGS.get(tid): 
                screen.blit(pg.transform.scale(TOWER_IMGS[tid], (btn_size-4, btn_size-4)), (x+2, y+2))
            pg.draw.rect(screen, BLACK, r, 2, border_radius=5)
            if sel_type == tid: pg.draw.rect(screen, (255, 255, 0), r, 3, border_radius=5)
            
            # تحسين بسيط: توسيط السعر تحت الزر
            price_surf = f2.render(pr, True, WHITE)
            screen.blit(price_surf, (x + (btn_size - price_surf.get_width())//2, y + btn_size + 5))
            return r

        t1 = draw_t(c1, t_row1, (0, 255, 0), "Archer", "$50", 1)
        t2 = draw_t(c2, t_row1, (0, 100, 255), "Mage", "$100", 2)
        t3 = draw_t(c1, t_row2, (255, 0, 0), "Cannon", "$200", 3)
        t4 = draw_t(c2, t_row2, (128, 0, 128), "Sniper", "$300", 4)
        
        # تعديل مكان قسم الـ Powers ليكون بعيداً عن الأبراج السفلية
        power_y_start = t_row2 + btn_size + int(SCREEN_H * 0.08)

    screen.blit(f1.render("- POWERS -", True, WHITE), (panel_x + 10, power_y_start))
    
    p_rects = {}
    curr_py = power_y_start + int(SCREEN_H * 0.04)
    p_h = int(SCREEN_H * 0.05) 
    p_gap = int(SCREEN_H * 0.005)
    
    for pk in ['damage', 'freeze', 'nuke', 'heal']:
        cfg = POWERUP_CONFIG[pk]
        r = pg.Rect(panel_x + 10, curr_py, SIDEBAR_WIDTH - 20, p_h)
        
        act = now < p_states['active_until'][pk]
        cd = now < p_states['next_available'][pk]
        col = (255, 255, 255) if act else ((100, 100, 100) if cd else cfg['color'])
        
        draw_Button(r, "", pg.mouse.get_pos(), color_override=col)
        
        nm = f_pwr.render(cfg['name'], True, BLACK)
        screen.blit(nm, nm.get_rect(center=(r.centerx, r.centery - 8)))
        
        st = "ACTIVE!" if act else (f"Wait {(p_states['next_available'][pk] - now)//1000}s" if cd else f"${cfg['cost']}")
        cs = f_pwr.render(st, True, BLACK)
        screen.blit(cs, cs.get_rect(center=(r.centerx, r.centery + 10)))
        
        p_rects[pk] = r
        curr_py += p_h + p_gap

    res_h = int(SCREEN_H * 0.05)
    rr = pg.Rect(panel_x + 10, SCREEN_H - res_h - 10, SIDEBAR_WIDTH - 20, res_h)
    return rr, t1, t2, t3, t4, p_rects, upgrade_rect, sell_rect

# -------------------- MENUS --------------------
def main_menu():
    global current_scale_idx, IS_DARK_MODE, high_score, player_name 
    f = pg.font.Font(None, int(SCREEN_W*0.08))
    cf = pg.font.Font(None, int(SCREEN_W*0.035)) 
    bf = pg.font.Font(None, int(SCREEN_W*0.05)) 
    
    try: pg.mixer.music.load(os.path.join(ASSETS_FOLDER, "main_menu sound.wav")); pg.mixer.music.play(-1)
    except: pass
    
    mus = True
    clines = ["Game By:", "Abdulrahman Mohammed - Mohammed Elsawy", "Mennallah Mohamed - Mariam Saleh"]
    
    menu_state = "MAIN" 

    # Input Box setup (Dynamic)
    input_text = ""
    input_active = False

    while True:
        bw, bh = int(SCREEN_W*0.4), int(SCREEN_H*0.09)
        spacing = int(SCREEN_H * 0.11)
        start_y = int(SCREEN_H*0.45) 

        # [تعديل]: نقل مربع الإدخال ليكون فوق الأزرار مباشرة
        input_h = int(SCREEN_H*0.09) 
        total_w = int(SCREEN_W*0.4)
        field_w = int(total_w * 0.75)
        btn_w = total_w - field_w - 5 
        
        # تحديد الموقع الجديد بناءً على موقع أول زر
        input_y_pos = start_y - input_h - int(SCREEN_H*0.02) 
        input_rect = pg.Rect(SCREEN_W//2 - total_w//2, input_y_pos, field_w, input_h)
        set_btn_rect = pg.Rect(input_rect.right + 5, input_y_pos, btn_w, input_h)

        if MENU_BG_IMG:
            bg_scaled = pg.transform.scale(MENU_BG_IMG, (SCREEN_W, SCREEN_H))
            screen.blit(bg_scaled, (0, 0))
            overlay = pg.Surface((SCREEN_W, SCREEN_H))
            overlay.set_alpha(100)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
        else:
            screen.fill(MENU_BG_COLOR)

        mx, my = pg.mouse.get_pos()
        
        t = f.render("Tower Defense", True, UI_TEXT_COLOR)
        sub_t = cf.render("THE FINAL BATTLE", True, WHITE) 
        # [تعديل]: زيادة المسافة بين العنوان الرئيسي والفرعي
        screen.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H*0.08))
        screen.blit(sub_t, (SCREEN_W//2 - sub_t.get_width()//2, SCREEN_H*0.18))

        player_info = cf.render(f"Welcome, {player_name} | High Score: {high_score}", True, GOLD)
        screen.blit(player_info, (SCREEN_W//2 - player_info.get_width()//2, SCREEN_H*0.23))

        # رسم مربع إدخال الاسم
        box_col = (240, 160, 30) 
        pg.draw.rect(screen, box_col, input_rect, border_radius=10)
        
        border_c = WHITE if input_active else BLACK
        pg.draw.rect(screen, border_c, input_rect, 3, border_radius=10)
        
        txt_surf = bf.render(input_text, True, BLACK)
        screen.blit(txt_surf, txt_surf.get_rect(center=input_rect.center))
        
        if not input_text and not input_active:
            ph_surf = bf.render("Enter Name...", True, (80, 80, 80))
            screen.blit(ph_surf, ph_surf.get_rect(center=input_rect.center))

        if draw_Button(set_btn_rect, "Set", (mx, my)):
            if pg.mouse.get_pressed()[0] and input_text.strip():
                click_sound.play()
                player_name = input_text
                pg.time.wait(200)

        if menu_state == "MAIN":
            b1 = pg.Rect(SCREEN_W//2 - bw//2, start_y, bw, bh)
            b2 = pg.Rect(SCREEN_W//2 - bw//2, start_y + spacing, bw, bh)
            b3 = pg.Rect(SCREEN_W//2 - bw//2, start_y + spacing*2, bw, bh)

            reset_score_rect = pg.Rect(SCREEN_W - int(SCREEN_W*0.18), SCREEN_H - int(SCREEN_H*0.08), int(SCREEN_W*0.16), int(SCREEN_H*0.06))

            if draw_Button(b1, "PLAY", (mx, my)): 
                if pg.mouse.get_pressed()[0]: 
                    click_sound.play(); pg.time.wait(150); return "map"
            
            if draw_Button(b2, "SETTINGS", (mx, my)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play(); pg.time.wait(150); menu_state = "SETTINGS"
            
            if draw_Button(b3, "QUIT", (mx, my)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play(); pg.quit(); sys.exit()

            if draw_Button(reset_score_rect, "Reset Score", (mx, my), color_override=(200, 50, 50)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play(); high_score = 0; save_high_score(0); pg.time.wait(150)

        elif menu_state == "SETTINGS":
            b1 = pg.Rect(SCREEN_W//2 - bw//2, start_y, bw, bh)
            b2 = pg.Rect(SCREEN_W//2 - bw//2, start_y + spacing, bw, bh)
            b3 = pg.Rect(SCREEN_W//2 - bw//2, start_y + spacing*2, bw, bh)
            b4 = pg.Rect(SCREEN_W//2 - bw//2, start_y + spacing*3, bw, bh)

            txt_mus = "Music: ON" if mus else "Music: OFF"
            if draw_Button(b1, txt_mus, (mx, my)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play(); pg.time.wait(150)
                    mus = not mus
                    if mus: pg.mixer.music.unpause() 
                    else: pg.mixer.music.pause()

            if draw_Button(b2, f"Screen: {SCALE_NAMES[current_scale_idx]}", (mx, my)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play()
                    current_scale_idx = (current_scale_idx + 1) % len(SCALES)
                    set_resolution(current_scale_idx)
                    f = pg.font.Font(None, int(SCREEN_W*0.08))
                    cf = pg.font.Font(None, int(SCREEN_W*0.035))
                    bf = pg.font.Font(None, int(SCREEN_W*0.05)) # Re-calc font
                    pg.time.wait(200)

            txt_theme = "Theme: Dark" if IS_DARK_MODE else "Theme: Light"
            if draw_Button(b3, txt_theme, (mx, my)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play(); pg.time.wait(150)
                    IS_DARK_MODE = not IS_DARK_MODE
                    update_theme()

            if draw_Button(b4, "BACK", (mx, my), color_override=(200, 50, 50)):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play(); pg.time.wait(150); menu_state = "MAIN"

        for e in pg.event.get():
            if e.type == pg.QUIT: pg.quit(); sys.exit()
            if e.type == pg.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(e.pos):
                    input_active = True
                else:
                    input_active = False
            if e.type == pg.KEYDOWN:
                if input_active:
                    if e.key == pg.K_RETURN:
                        if input_text.strip():
                            player_name = input_text
                            click_sound.play()
                    elif e.key == pg.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 15:
                            input_text += e.unicode

        pg.display.update(); clock.tick(FPS)

def map_sel():
    sel_m, sel_d = 0, 1
    diffs = ["Easy", "Medium", "Hard"]
    while True:
        if MENU_BG_IMG:
            bg_scaled = pg.transform.scale(MENU_BG_IMG, (SCREEN_W, SCREEN_H))
            screen.blit(bg_scaled, (0, 0))
            overlay = pg.Surface((SCREEN_W, SCREEN_H))
            overlay.set_alpha(100)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
        else:
            screen.fill(MENU_BG_COLOR)
        
        mp = pg.mouse.get_pos()
        
        back_rect = pg.Rect(20, 20, int(SCREEN_W*0.12), int(SCREEN_H*0.06))
        if draw_Button(back_rect, "Back", mp, color_override=(200, 50, 50)):
             if pg.mouse.get_pressed()[0]:
                 click_sound.play(); pg.time.wait(150); return None, None

        for i in range(4):
            b = pg.Rect(SCREEN_W*0.05 + i*SCREEN_W*0.23, SCREEN_H*0.3, int(SCREEN_W*0.2), int(SCREEN_H*0.1))
            
            if i < 3:
                txt = f"Map {i+1}"
                is_selected = (sel_m == i)
            else:
                txt = "Random"
                is_selected = False 
            
            if draw_Button(b, txt, mp):
                if pg.mouse.get_pressed()[0]:
                    click_sound.play()
                    if i < 3:
                        sel_m = i
                    else:
                        sel_m = random.randint(0, 2)
                    pg.time.wait(150)
            
            if i < 3 and sel_m == i:
                pg.draw.rect(screen, (255,255,0), b, 4, border_radius=10)

        for i, d in enumerate(diffs):
            b = pg.Rect(SCREEN_W*0.2 + i*SCREEN_W*0.2, SCREEN_H*0.55, int(SCREEN_W*0.15), int(SCREEN_H*0.08))
            h = draw_Button(b, d, mp)
            if h and pg.mouse.get_pressed()[0]: click_sound.play(); sel_d = i; pg.time.wait(150)
            if sel_d == i: pg.draw.rect(screen, (255,255,0), b, 4, border_radius=10)

        pb = pg.Rect(SCREEN_W//2 - int(SCREEN_W*0.15), SCREEN_H*0.75, int(SCREEN_W*0.3), int(SCREEN_H*0.1))
        ph = draw_Button(pb, "Start Game", mp)
        if ph and pg.mouse.get_pressed()[0]:
            click_sound.play(); pg.time.wait(150); pg.mixer.music.stop(); return sel_m, sel_d

        for e in pg.event.get():
            if e.type == pg.QUIT: pg.quit(); sys.exit()
        pg.display.update(); clock.tick(FPS)

def credits_scr():
    try:
        mp = os.path.join(ASSETS_FOLDER, "credits.wav")
        if not os.path.exists(mp): mp = os.path.join(ASSETS_FOLDER, "credits.mp3")
        if os.path.exists(mp): pg.mixer.music.load(mp); pg.mixer.music.set_volume(0.5); pg.mixer.music.play(-1)
        else: pg.mixer.music.stop()
    except: pg.mixer.music.stop()

    bg = None
    if MENU_BG_IMG:
        bg = pg.transform.scale(MENU_BG_IMG, (SCREEN_W, SCREEN_H))
        ov = pg.Surface((SCREEN_W, SCREEN_H)); ov.set_alpha(150); ov.fill((0,0,0))
    else:
        try:
            bp = os.path.join(ASSETS_FOLDER, "credits_bg.png")
            if not os.path.exists(bp): bp = os.path.join(ASSETS_FOLDER, "credits_bg.jpg")
            if os.path.exists(bp):
                bg = pg.transform.scale(pg.image.load(bp).convert(), (SCREEN_W, SCREEN_H))
                ov = pg.Surface((SCREEN_W, SCREEN_H)); ov.set_alpha(150); ov.fill((0,0,0))
        except: bg = None

    tf = pg.font.Font(None, int(SCREEN_W*0.08))
    nf = pg.font.Font(None, int(SCREEN_W*0.05))
    rf = pg.font.Font(None, int(SCREEN_W*0.06))
    
    cdata = [
        ("TOWER DEFENSE", GOLD), ("THE FINAL BATTLE", WHITE), ("", WHITE),
        ("--- DEVELOPMENT TEAM ---", CYAN), ("Sound & Music by Abdulrahman Mohammed", WHITE),
        ("Map Design by Abdulrahman Mohammed", WHITE), ("UI/UX by Abdulrahman Mohammed", WHITE), 
        ("Game Desing by Abdulrahman Mohammed", WHITE), 
        ("Level Design byAbdulrahman Mohammed", WHITE), ("", WHITE),
        ("Game Graphics & Art by Mohammed Elsawy", WHITE), ("Tower & Enemies by Mohammed Elsawy", WHITE), 
        ("Game Logic by Mohammed Elsawy", WHITE), ("", WHITE),
        ("Level Design by Mennallah Mohamed", WHITE), ("Economy System by Mariam Saleh", WHITE),
        ("Testing by Mariam Saleh & Mennallah Mohamed", WHITE), ("", WHITE),
        ("--- POWERED BY ---", CYAN), ("Python & Pygame", WHITE),
        ("Audacity for sound", WHITE), ("MAIN IDLE [VS CODE]", WHITE), ("", WHITE),
        ("--- SPECIAL THANKS ---", GOLD), ("To Our Professors & Mentors", WHITE),
        ("Open Source Community", WHITE), ("And To You, The Player!", WHITE), ("", WHITE),
        ("--- PRODUCTION ---", CYAN), ("Version 5.0 - Final Release", WHITE),
        ("Made with Passion & Code", WHITE), ("", WHITE),
        ("© 2025 All Rights Reserved", WHITE), ("", WHITE), ("CLICK TO RETURN", GOLD)
    ]
    
    sy, run = SCREEN_H, True
    while run:
        if bg: screen.blit(bg, (0,0)); screen.blit(ov, (0,0))
        else: screen.fill(BLACK)
        
        for e in pg.event.get():
            if e.type == pg.QUIT: pg.quit(); sys.exit()
            if e.type in [pg.KEYDOWN, pg.MOUSEBUTTONDOWN]: run = False
        
        sy -= 1.5
        for i, (t, c) in enumerate(cdata):
            f = rf if c == CYAN else (tf if c == GOLD else nf)
            s = f.render(t, True, c)
            screen.blit(s, s.get_rect(center=(SCREEN_W//2, sy + i * 80)))
            
        if sy + len(cdata) * 80 < -50: run = False
        pg.display.update(); clock.tick(60)

# -------------------- GAME LOGIC --------------------
def run_game(s_map, s_diff):
    global high_score
    cmap = MAPS[s_map]
    path = calculate_path(cmap)
    rows, cols = len(cmap), len(cmap[0])
    tw, th = MAP_WIDTH // cols, SCREEN_H // rows
    
    sp = next(((c,r) for r in range(rows) for c in range(cols) if cmap[r][c] == 3), None)

    map_surface = pre_render_map(cmap)

    try: pg.mixer.music.load(os.path.join(ASSETS_FOLDER, "game play m.wav")); pg.mixer.music.set_volume(0.1); pg.mixer.music.play(-1)
    except: pass
    
    gof = pg.font.Font(None, int(SCREEN_W * 0.15))
    wvf = pg.font.Font(None, int(SCREEN_W * 0.1))
    alertf = pg.font.Font(None, int(SCREEN_W * 0.05))

    lives = 20 if s_diff == 0 else (5 if s_diff == 2 else 10)
    money = 300 if s_diff == 0 else (150 if s_diff == 2 else 200)
    score, towers, enemies = 0, [], []
    
    p_states = {'active_until': {'damage': 0, 'freeze': 0, 'nuke': 0, 'heal': 0},
                'next_available': {'damage': 0, 'freeze': 0, 'nuke': 0, 'heal': 0}}
    wnum, winp, wcd = 1, False, 7000
    lwt, es, ets, lst, sdel = pg.time.get_ticks(), 0, 5, 0, 1000
    
    TOWER_COSTS = {1: 50, 2: 100, 3: 200, 4: 300}
    sel_t = None
    sel_tower_on_map = None 
    dev_mode = False 

    wave_sound_played = False

    while True:
        mx, my = pg.mouse.get_pos()
        now = pg.time.get_ticks()
        
        dmg_mul = 2 if now < p_states['active_until']['damage'] else 1
        spd_mul = 0.5 if now < p_states['active_until']['freeze'] else 1
        freeze_active = now < p_states['active_until']['freeze']
        damage_active = now < p_states['active_until']['damage']

        screen.blit(map_surface, (0, 0))

        if damage_active:
            tint_surf = pg.Surface((MAP_WIDTH, SCREEN_H))
            tint_surf.fill(ORANGE); tint_surf.set_alpha(50); screen.blit(tint_surf, (0,0))
        elif freeze_active:
            tint_surf = pg.Surface((MAP_WIDTH, SCREEN_H))
            tint_surf.fill(ICE_BLUE); tint_surf.set_alpha(50); screen.blit(tint_surf, (0,0))

        draw_highlight(cmap, towers, sp, sel_t, sel_tower_on_map)
        
        alert_y = 20
        if damage_active:
            alert = alertf.render("DAMAGE BOOST ACTIVE!", True, ORANGE)
            screen.blit(alert, (MAP_WIDTH//2 - alert.get_width()//2, alert_y)); alert_y += 40
        if freeze_active:
            alert = alertf.render("FREEZE ACTIVE!", True, ICE_BLUE)
            screen.blit(alert, (MAP_WIDTH//2 - alert.get_width()//2, alert_y))
        
        for t in towers[:]:
            if not t.alive: towers.remove(t); continue
            t.update(enemies, dmg_mul)
            t.draw(screen, tw, th)

        if not winp:
            if not wave_sound_played:
                wave_clear_sound.play()
                wave_sound_played = True

            tl = wcd - (now - lwt)
            if tl > 0:
                txt = wvf.render(f"WAVE {wnum} IN {int(tl/1000)+1}", True, UI_TEXT_COLOR)
                br = txt.get_rect(center=(MAP_WIDTH//2, SCREEN_H//2))
                pg.draw.rect(screen, (0,0,0), br.inflate(20, 20)); screen.blit(txt, br)
            else:
                winp = True; es = 0
                ets = 5 + (wnum * 3) 
                wave_sound_played = False
        else:
            if es < ets and now - lst > sdel:
                if path:
                    typ = "normal"
                    if wnum >= 2 and random.random() < 0.3: typ = "strong"
                    if wnum >= 3 and random.random() < 0.2: typ = "shooter"
                    enemies.append(Enemy(path, wnum, typ)); es += 1; lst = now
            if es == ets and not enemies:
                winp = False; wnum += 1; lwt = now; money += 50

        for e in enemies[:]:
            e.move(spd_mul)
            e.update(towers) 
            e.draw(screen, tw, th) 
            if e.reached_end: 
                if not dev_mode: lives -= 1
                enemies.remove(e)
            elif not e.alive: money += e.reward; score += 10; enemies.remove(e)

        rst, t1, t2, t3, t4, prects, up_rect, sell_rect = draw_sidebar(lives, money, score, len(towers), wnum, sel_t, p_states, now, sel_tower_on_map, dev_mode)

        if lives <= 0:
            save_high_score(score)
            
            # 1. نوقف موسيقى اللعبة أولاً
            pg.mixer.music.stop()
            
            # 2. نشغل صوت الخسارة
            game_over_sound.play()
            
            screen.fill(BLACK) 
            go = gof.render("GAME OVER", True, (255, 0, 0))
            screen.blit(go, go.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
            pg.display.update()
            
            # الانتظار 3 ثواني حتى يسمع اللاعب الصوت ويستوعب الخسارة
            pg.time.wait(3000)
            
            credits_scr(); return "menu"

        rh = draw_Button(rst, "Restart", (mx, my))
        
        for e in pg.event.get():
            if e.type == pg.QUIT: pg.quit(); sys.exit()
            
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_d: dev_mode = not dev_mode
                if dev_mode:
                    if e.key == pg.K_m: money += 5000
                    if e.key == pg.K_l: lives = 100
                    if e.key == pg.K_k: 
                        for en in enemies: en.take_damage(9999)
            
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                # 1. Sidebar Interactions
                if rst.collidepoint((mx, my)): 
                    click_sound.play(); pg.time.wait(200); return "restart"
                
                # Check Powerups
                for k, r in prects.items():
                    if r.collidepoint((mx, my)):
                        cfg = POWERUP_CONFIG[k]
                        if now >= p_states['next_available'][k] and money >= cfg['cost']:
                            money -= cfg['cost']
                            p_states['next_available'][k] = now + cfg['cooldown']
                            click_sound.play()
                            if k == 'nuke':
                                for en in enemies: en.take_damage(en.max_health * 0.5)
                            elif k == 'heal':
                                lives += 5
                            else: p_states['active_until'][k] = now + cfg['duration']
                
                # Check Tower Selection / Upgrade
                if sel_tower_on_map:
                    if up_rect and up_rect.collidepoint((mx, my)):
                        up_cost = sel_tower_on_map.get_upgrade_cost()
                        if money >= up_cost:
                            money -= up_cost
                            sel_tower_on_map.upgrade()
                            click_sound.play()
                    elif sell_rect and sell_rect.collidepoint((mx, my)):
                        sell_val = sel_tower_on_map.total_spent // 2 
                        money += sell_val
                        sel_tower_on_map.alive = False 
                        sel_tower_on_map = None
                        click_sound.play()
                else:
                    if t1 and t1.collidepoint((mx, my)): sel_t = 1; click_sound.play()
                    elif t2 and t2.collidepoint((mx, my)): sel_t = 2; click_sound.play()
                    elif t3 and t3.collidepoint((mx, my)): sel_t = 3; click_sound.play()
                    elif t4 and t4.collidepoint((mx, my)): sel_t = 4; click_sound.play()

                # 2. Map Interactions
                if mx < MAP_WIDTH:
                    c, r = mx // tw, my // th
                    
                    clicked_tower = None
                    for t in towers:
                        t_c = int(t.x / tw); t_r = int(t.y / th)
                        if c == t_c and r == t_r: clicked_tower = t; break
                    
                    if clicked_tower:
                        if sel_tower_on_map == clicked_tower:
                             sel_tower_on_map = None
                        else:
                             sel_tower_on_map = clicked_tower
                        
                        sel_t = None
                        click_sound.play()
                    else:
                        if sel_t: 
                            if 0 <= r < rows and 0 <= c < cols:
                                safe = True
                                if sp and math.hypot(c - sp[0], r - sp[1]) < SPAWN_PROTECTION_RADIUS: safe = False
                                if check_placement(cmap, towers, c, r, tw) and safe:
                                    cost = TOWER_DATA[sel_t]['cost']
                                    if money >= cost:
                                        towers.append(Tower(c * tw + tw // 2, r * th + th // 2, sel_t))
                                        money -= cost 
                                        click_sound.play()
                                        sel_t = None
                        else:
                            sel_tower_on_map = None

        pg.display.update()
        clock.tick(FPS)

# -------------------- DATA --------------------
MAPS = [
    # Map 1: Spiral inward
    [[3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
     [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1],
     [1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1],
     [1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,0,0,0,0,0,0,1,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,0,1,1,1,1,0,1,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,0,1,2,2,1,0,1,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,0,1,2,2,0,0,1,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,0,1,1,1,1,1,1,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1],
     [1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1],
     [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1],
     [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
     [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
     [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], 
     
     # Map 2: Improved Spiral
     [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
      [2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
      [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3]],
      
      # Map 3
      [[2,2,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1],
      [2,2,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,1],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0],
      [0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
      [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
      [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,3,3,3]]
]

# -------------------- MAIN --------------------
if __name__ == "__main__":
    while True:
        m = main_menu()
        if m == "map":
            sm, sd = map_sel()
            if sm is None: continue 
            res = run_game(sm, sd)
            if res == "restart": continue