import pygame
import json
import os
from enum import Enum
from pygame.locals import *
from config import *

menu_music = pygame.mixer.Sound('resources/Music/menu0loop.mp3')
menu_music.set_volume(0.5)

level_music = pygame.mixer.Sound('resources/Music/lvl1.mp3')
level_music.set_volume(0.5)

try:
    level2_music = pygame.mixer.Sound('resources/Music/lvl2.wav')
    level2_music.set_volume(0.5)
except Exception:
    level2_music = None

defeat_music = pygame.mixer.Sound('resources/Music/defeatsg.mp3')

def load_settings():
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                data = json.load(f)
                if 'knowledge_points' not in data:
                    data['knowledge_points'] = 0
                    data['meta_upgrades'] = {'hp': 0, 'speed': 0, 'damage': 0}
                    data['unlocked_items'] = ['Pistol', 'Automatic Rifle', 'Speed Boots', 'Power Ring', 'Heart Crystal']
                return data
    except Exception:
        pass
    return {'music_volume': 0.5, 'sound_volume': 1.0, 'is_fullscreen': False, 'shake_intensity': 1.0, 'show_damage_numbers': True, 'knowledge_points': 0, 'meta_upgrades': {'hp': 0, 'speed': 0, 'damage': 0}, 'unlocked_items': ['Pistol', 'Automatic Rifle', 'Speed Boots', 'Power Ring', 'Heart Crystal']}

def save_settings(music_vol, sound_vol, is_full, shake_int=1.0,
                  show_dmg=True, kp=0, meta_ups=None,
                  unl_items=None):
    if meta_ups is None: meta_ups = {'hp': 0, 'speed': 0, 'damage': 0}
    if unl_items is None: unl_items = ['Pistol', 'Automatic Rifle', 'Speed Boots', 'Power Ring', 'Heart Crystal']
    try:
        with open('settings.json', 'w') as f:
            json.dump({'music_volume': music_vol, 'sound_volume': sound_vol, 'is_fullscreen': is_full,
                       'shake_intensity': shake_int, 'show_damage_numbers': show_dmg, 'knowledge_points': kp,
                       'meta_upgrades': meta_ups, 'unlocked_items': unl_items}, f)
    except Exception as e:
        print("Ошибка сохранения настроек:", e)
defeat_music.set_volume(0.5)

reload_sound = pygame.mixer.Sound('resources/Sounds/reload.mp3')
reload_sound.set_volume(0.5)

try:
    hurt_sound = pygame.mixer.Sound('resources/Sounds/hurt.wav')
    hurt_sound.set_volume(0.5)
except Exception:
    hurt_sound = None

try:
    dash_sound = pygame.mixer.Sound('resources/Sounds/dash.wav')
    dash_sound.set_volume(0.5)
except Exception:
    dash_sound = None

try:
    powerup_sound = pygame.mixer.Sound('resources/Sounds/powerUp.wav')
    powerup_sound.set_volume(0.5)
except Exception:
    powerup_sound = None

try:
    pickup_coin_sound = pygame.mixer.Sound('resources/Sounds/pickupCoin.wav')
    pickup_coin_sound.set_volume(0.3)
except Exception:
    pickup_coin_sound = None

try:
    equip_sound = pygame.mixer.Sound('resources/Sounds/equip.wav')
    equip_sound.set_volume(0.5)
except Exception:
    equip_sound = None

try:
    explosion_sound = pygame.mixer.Sound('resources/Sounds/explosion.wav')
    explosion_sound.set_volume(0.5)
except Exception:
    explosion_sound = None

try:
    portal_sound = pygame.mixer.Sound('resources/Sounds/portal.wav')
    portal_sound.set_volume(0.5)
except Exception:
    portal_sound = None

try:
    boss_spawn_snd = pygame.mixer.Sound('resources/Sounds/spawnBoss.wav')
    boss_spawn_snd.set_volume(0.6)
    boss_phase_snd = pygame.mixer.Sound('resources/Sounds/bossPhase.wav')
    boss_phase_snd.set_volume(0.6)
    spawn_enemies_snd = pygame.mixer.Sound('resources/Sounds/spawnEnemies.wav')
    boss_music = pygame.mixer.Sound('resources/Music/bosslvl1.mp3')
    boss_music.set_volume(0.5)
    boss_attack_snd = pygame.mixer.Sound('resources/Sounds/bossAttack.wav')
    boss_attack_snd.set_volume(0.7)
    wave_attack_snd = pygame.mixer.Sound('resources/Sounds/waveAttack.wav')
    wave_attack_snd.set_volume(0.6)
    boss_death_snd = pygame.mixer.Sound('resources/Sounds/bossDeath.wav')
    boss_death_snd.set_volume(0.8)
except Exception:
    boss_spawn_snd = boss_phase_snd = spawn_enemies_snd = boss_music = boss_attack_snd = wave_attack_snd = boss_death_snd = None

try:
    player_death_snd = pygame.mixer.Sound('resources/Sounds/playerDeath.wav')
    player_death_snd.set_volume(0.8)
except Exception:
    player_death_snd = None

try:
    select_sound = pygame.mixer.Sound('resources/Sounds/select.wav')
    select_sound.set_volume(0.5)
    shoot_sound = pygame.mixer.Sound('resources/Sounds/shoot.wav')
    shoot_sound.set_volume(0.5)
except Exception:
    select_sound = None
    shoot_sound = None

boss_attack_frames = []
try:
    b_atk_sheet = pygame.image.load('resources/tileset/bossAttack_sheet.png').convert_alpha()
    fw = b_atk_sheet.get_height()
    for i in range(b_atk_sheet.get_width() // fw):
        boss_attack_frames.append(pygame.transform.scale(b_atk_sheet.subsurface((i * fw, 0, fw, fw)), (120, 120)))
except Exception: pass

wave_frames = []
try:
    w_sheet = pygame.image.load('resources/tileset/waveAttack_sheet.png').convert_alpha()
    fw = w_sheet.get_height()
    for i in range(w_sheet.get_width() // fw):
        wave_frames.append(pygame.transform.scale(w_sheet.subsurface((i * fw, 0, fw, fw)), (140, 140)))
except Exception: pass

try:
    shopper_img = pygame.image.load('resources/tileset/shopper.png').convert_alpha()
    shopper_img = pygame.transform.scale(shopper_img, (40, 40))
except Exception:
    shopper_img = pygame.Surface((40, 40))

try:
    chest_img = pygame.image.load('resources/tileset/gold_chest.png').convert_alpha()
    chest_img = pygame.transform.scale(chest_img, (40, 40))
    chest_opened_img = pygame.image.load('resources/tileset/opened_gold_chest.png').convert_alpha()
    chest_opened_img = pygame.transform.scale(chest_opened_img, (40, 40))
    chest_open_sound = pygame.mixer.Sound('resources/Sounds/open.wav')
    chest_open_sound.set_volume(0.5)

    chest_sheet = pygame.image.load('resources/tileset/gold_chest_sheet.png').convert_alpha()
    chest_frames = []
    frame_w = chest_sheet.get_height()
    for i in range(chest_sheet.get_width() // frame_w):
        frame = chest_sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_w))
        chest_frames.append(pygame.transform.scale(frame, (40, 40)))
except Exception as e:
    chest_img = None
    chest_opened_img = None
    chest_frames = []
    chest_open_sound = None
    print("Chest load error:", e)

explosion_frames = []
try:
    exp_sheet = pygame.image.load('resources/tileset/explosion_sheet.png').convert_alpha()

    frame_size = exp_sheet.get_height()
    frames_count = exp_sheet.get_width() // frame_size

    for i in range(frames_count):
        rect = pygame.Rect(i * frame_size, 0, frame_size, frame_size)
        frame = exp_sheet.subsurface(rect)
        explosion_frames.append(pygame.transform.scale(frame, (120, 120)))
except Exception as e:
    print(f"Ошибка загрузки explosion_sheet.png: {e}")

logo_gif = pygame.image.load('resources/mathcrawl.png')
logo_frames = []
frame_count = 0
try:
    while True:
        logo_frames.append(pygame.image.load(f'BULKYS1.gif[{frame_count}]'))
        frame_count += 1
except Exception:
    pass
if not logo_frames:
    logo_frames = [logo_gif]

pygame.mouse.set_visible(False)
cursor = pygame.image.load('resources/tileset/cursor.png').convert_alpha()
cursor = pygame.transform.scale(cursor, (32, 32))
cursor_hand = pygame.image.load('resources/tileset/cursorhand.png').convert_alpha()
cursor_hand = pygame.transform.scale(cursor_hand, (32, 32))
current_cursor = cursor

coin_img = pygame.image.load('resources/tileset/gold_coin.png').convert_alpha()
coin_img = pygame.transform.scale(coin_img, (20, 20))

coin_frames = []
try:
    coin_sheet = pygame.image.load('resources/tileset/gold_coin_sheet.png').convert_alpha()
    frame_w = coin_sheet.get_height()
    for i in range(coin_sheet.get_width() // frame_w):
        frame = coin_sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_w))
        coin_frames.append(pygame.transform.scale(frame, (20, 20)))
except Exception as e:
    print("Ошибка загрузки gold_coin_sheet.png:", e)
    coin_frames = [coin_img]

enemy_frames = {'down': [], 'left': [], 'right': [], 'up': []}
try:
    sheet = pygame.image.load('resources/tileset/enemy_sheet.png').convert_alpha()
    directions = ['down', 'left', 'up', 'right']
    for col in range(4):
        for row in range(4):
            rect = pygame.Rect(col * 64, row * 64, 64, 64)
            frame = sheet.subsurface(rect)
            enemy_frames[directions[col]].append(frame)
except Exception as e:
    print("Не удалось загрузить enemy_sheet.png:", e)
    enemy_frames = None

boss_frames = {'down': [], 'left': [], 'right': [], 'up': []}
try:
    b_sheet = pygame.image.load('resources/tileset/boss_sheet.png').convert_alpha()
    directions = ['down', 'left', 'up', 'right']
    for col in range(4):
        for row in range(4):
            rect = pygame.Rect(col * 64, row * 64, 64, 64)
            frame = b_sheet.subsurface(rect)
            boss_frames[directions[col]].append(frame)
except Exception as e:
    print("Не удалось загрузить boss_sheet.png:", e)
    boss_frames = None

try:
    temp_heart = pygame.image.load('resources/tileset/heart1.png').convert_alpha()
    temp_halfheart = pygame.image.load('resources/tileset/halfheart1.png').convert_alpha()

    heart_size = (58, 58)

    heart_img = pygame.transform.smoothscale(temp_heart, heart_size)
    halfheart_img = pygame.transform.smoothscale(temp_halfheart, heart_size)
except Exception:
    heart_img = None
    halfheart_img = None

class RoomType(Enum):
    NORMAL = 1
    TREASURE = 2
    SHOP = 3
    BOSS = 4
    NEXT_FLOOR = 5

portal_frames = {RoomType.NORMAL: [], RoomType.TREASURE: [], RoomType.SHOP: [], RoomType.BOSS: [], RoomType.NEXT_FLOOR: []}
try:
    portal_sheet = pygame.image.load('resources/tileset/blue_portal_sheet.png').convert_alpha()
    frame_w = portal_sheet.get_height()

    # Цвета для автоматической перекраски портала
    portal_colors = {
        RoomType.NORMAL: None,
        RoomType.TREASURE: GOLD,
        RoomType.SHOP: GREEN,
        RoomType.BOSS: RED,
        RoomType.NEXT_FLOOR: PURPLE
    }

    for i in range(portal_sheet.get_width() // frame_w):
        frame = portal_sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_w))
        frame = pygame.transform.scale(frame, (40, 40))

        for p_type, color in portal_colors.items():
            if color is None:
                portal_frames[p_type].append(frame)
            else:
                colored_frame = pygame.transform.grayscale(frame)
                colored_frame.fill(color, special_flags=pygame.BLEND_RGB_MULT)
                portal_frames[p_type].append(colored_frame)
except Exception as e:
    print("Ошибка загрузки blue_portal_sheet.png:", e)

try:
    medkit_img = pygame.image.load('resources/tileset/medkit.png').convert_alpha()
    medkit_img = pygame.transform.scale(medkit_img, (30, 30))
except Exception:
    medkit_img = pygame.Surface((30, 30))
    medkit_img.fill((255, 100, 100))
    pygame.draw.rect(medkit_img, WHITE, (12, 5, 6, 20))
    pygame.draw.rect(medkit_img, WHITE, (5, 12, 20, 6))