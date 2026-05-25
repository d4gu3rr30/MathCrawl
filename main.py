import pygame
import random
import math
import time
import json
from enum import Enum
import os
from datetime import datetime
from pygame.locals import *

# Фикс для Windows, чтобы иконка отображалась на панели задач
if os.name == 'nt':
    try:
        import ctypes
        myappid = 'mathcrawl.game.1'
        # noinspection PyUnresolvedReferences
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

pygame.init()
pygame.mixer.init()
pygame.key.set_repeat(300, 50)
info = pygame.display.Info()
WINDOW_SIZE = (800, 600)
# флаг SCALED для автоматического сохранения пропорций при растягивании
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED)
is_fullscreen = False
pygame.display.set_caption('MATHCRAWL - Образовательный Roguelike')
clock = pygame.time.Clock()

menu_music = pygame.mixer.Sound('Music/menu0loop.mp3')
menu_music.set_volume(0.5)

level_music = pygame.mixer.Sound('Music/lvl1.mp3')
level_music.set_volume(0.5)

try:
    level2_music = pygame.mixer.Sound('Music/lvl2.wav')
    level2_music.set_volume(0.5)
except Exception:
    level2_music = None

defeat_music = pygame.mixer.Sound('Music/defeatsg.mp3')

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

reload_sound = pygame.mixer.Sound('Sounds/reload.mp3')
reload_sound.set_volume(0.5)

try:
    hurt_sound = pygame.mixer.Sound('Sounds/hurt.wav')
    hurt_sound.set_volume(0.5)
except Exception:
    hurt_sound = None

try:
    dash_sound = pygame.mixer.Sound('Sounds/dash.wav')
    dash_sound.set_volume(0.5)
except Exception:
    dash_sound = None

try:
    powerup_sound = pygame.mixer.Sound('Sounds/powerUp.wav')
    powerup_sound.set_volume(0.5)
except Exception:
    powerup_sound = None

try:
    pickup_coin_sound = pygame.mixer.Sound('Sounds/pickupCoin.wav')
    pickup_coin_sound.set_volume(0.3)
except Exception:
    pickup_coin_sound = None

try:
    equip_sound = pygame.mixer.Sound('Sounds/equip.wav')
    equip_sound.set_volume(0.5)
except Exception:
    equip_sound = None

try:
    explosion_sound = pygame.mixer.Sound('Sounds/explosion.wav')
    explosion_sound.set_volume(0.5)
except Exception:
    explosion_sound = None

try:
    portal_sound = pygame.mixer.Sound('Sounds/portal.wav')
    portal_sound.set_volume(0.5)
except Exception:
    portal_sound = None

try:
    boss_spawn_snd = pygame.mixer.Sound('Sounds/spawnBoss.wav')
    boss_spawn_snd.set_volume(0.6)
    boss_phase_snd = pygame.mixer.Sound('Sounds/bossPhase.wav')
    boss_phase_snd.set_volume(0.6)
    spawn_enemies_snd = pygame.mixer.Sound('Sounds/spawnEnemies.wav')
    boss_music = pygame.mixer.Sound('Music/bosslvl1.mp3')
    boss_music.set_volume(0.5)
    boss_attack_snd = pygame.mixer.Sound('Sounds/bossAttack.wav')
    boss_attack_snd.set_volume(0.7)
    wave_attack_snd = pygame.mixer.Sound('Sounds/waveAttack.wav')
    wave_attack_snd.set_volume(0.6)
    boss_death_snd = pygame.mixer.Sound('Sounds/bossDeath.wav')
    boss_death_snd.set_volume(0.8)
except Exception:
    boss_spawn_snd = boss_phase_snd = spawn_enemies_snd = boss_music = boss_attack_snd = wave_attack_snd = boss_death_snd = None

try:
    player_death_snd = pygame.mixer.Sound('Sounds/playerDeath.wav')
    player_death_snd.set_volume(0.8)
except Exception:
    player_death_snd = None

try:
    select_sound = pygame.mixer.Sound('Sounds/select.wav')
    select_sound.set_volume(0.5)
    shoot_sound = pygame.mixer.Sound('Sounds/shoot.wav')
    shoot_sound.set_volume(0.5)
except Exception:
    select_sound = None
    shoot_sound = None

boss_attack_frames = []
try:
    b_atk_sheet = pygame.image.load('tileset/bossAttack_sheet.png').convert_alpha()
    fw = b_atk_sheet.get_height()
    for i in range(b_atk_sheet.get_width() // fw):
        boss_attack_frames.append(pygame.transform.scale(b_atk_sheet.subsurface((i * fw, 0, fw, fw)), (120, 120)))
except Exception: pass

wave_frames = []
try:
    w_sheet = pygame.image.load('tileset/waveAttack_sheet.png').convert_alpha()
    fw = w_sheet.get_height()
    for i in range(w_sheet.get_width() // fw):
        # Увеличиваем волну до 140x140
        wave_frames.append(pygame.transform.scale(w_sheet.subsurface((i * fw, 0, fw, fw)), (140, 140)))
except Exception: pass

try:
    shopper_img = pygame.image.load('tileset/shopper.png').convert_alpha()
    shopper_img = pygame.transform.scale(shopper_img, (40, 40))
except Exception:
    shopper_img = pygame.Surface((40, 40))

try:
    chest_img = pygame.image.load('tileset/gold_chest.png').convert_alpha()
    chest_img = pygame.transform.scale(chest_img, (40, 40))
    chest_opened_img = pygame.image.load('tileset/opened_gold_chest.png').convert_alpha()
    chest_opened_img = pygame.transform.scale(chest_opened_img, (40, 40))
    chest_open_sound = pygame.mixer.Sound('Sounds/open.wav')
    chest_open_sound.set_volume(0.5)

    chest_sheet = pygame.image.load('tileset/gold_chest_sheet.png').convert_alpha()
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
    exp_sheet = pygame.image.load('tileset/explosion_sheet.png').convert_alpha()

    frame_size = exp_sheet.get_height()
    frames_count = exp_sheet.get_width() // frame_size

    for i in range(frames_count):
        rect = pygame.Rect(i * frame_size, 0, frame_size, frame_size)
        frame = exp_sheet.subsurface(rect)
        explosion_frames.append(pygame.transform.scale(frame, (120, 120)))
except Exception as e:
    print(f"Ошибка загрузки explosion_sheet.png: {e}")

logo_gif = pygame.image.load('mathcrawl.png')
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
cursor = pygame.image.load('tileset/cursor.png').convert_alpha()
cursor = pygame.transform.scale(cursor, (32, 32))
cursor_hand = pygame.image.load('tileset/cursorhand.png').convert_alpha()
cursor_hand = pygame.transform.scale(cursor_hand, (32, 32))
current_cursor = cursor

coin_img = pygame.image.load('tileset/gold_coin.png').convert_alpha()
coin_img = pygame.transform.scale(coin_img, (20, 20))

coin_frames = []
try:
    coin_sheet = pygame.image.load('tileset/gold_coin_sheet.png').convert_alpha()
    frame_w = coin_sheet.get_height()
    for i in range(coin_sheet.get_width() // frame_w):
        frame = coin_sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_w))
        coin_frames.append(pygame.transform.scale(frame, (20, 20)))
except Exception as e:
    print("Ошибка загрузки gold_coin_sheet.png:", e)
    coin_frames = [coin_img]

enemy_frames = {'down': [], 'left': [], 'right': [], 'up': []}
try:
    sheet = pygame.image.load('tileset/enemy_sheet.png').convert_alpha()
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
    b_sheet = pygame.image.load('tileset/boss_sheet.png').convert_alpha()
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
    temp_heart = pygame.image.load('tileset/heart1.png').convert_alpha()
    temp_halfheart = pygame.image.load('tileset/halfheart1.png').convert_alpha()

    heart_size = (58, 58)

    heart_img = pygame.transform.smoothscale(temp_heart, heart_size)
    halfheart_img = pygame.transform.smoothscale(temp_halfheart, heart_size)
except Exception:
    heart_img = None
    halfheart_img = None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 195, 215)
GRAY = (120, 120, 120)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)


class RoomType(Enum):
    NORMAL = 1
    TREASURE = 2
    SHOP = 3
    BOSS = 4
    NEXT_FLOOR = 5

portal_frames = {RoomType.NORMAL: [], RoomType.TREASURE: [], RoomType.SHOP: [], RoomType.BOSS: [], RoomType.NEXT_FLOOR: []}
try:
    portal_sheet = pygame.image.load('tileset/blue_portal_sheet.png').convert_alpha()
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

class PlayerStats:
    def __init__(self):
        self.problems_attempted = 0
        self.problems_correct = 0
        self.incorrect_problems = []
        self.problem_types_stats = {
            'equation': {'attempted': 0, 'correct': 0},
            'sequence': {'attempted': 0, 'correct': 0},
            'logic': {'attempted': 0, 'correct': 0},
            'percentage': {'attempted': 0, 'correct': 0}
        }

    def add_problem_result(self, problem, is_correct):
        self.problems_attempted += 1
        if is_correct:
            self.problems_correct += 1
        else:
            self.incorrect_problems.append(problem)

        self.problem_types_stats[problem.problem_type]['attempted'] += 1
        if is_correct:
            self.problem_types_stats[problem.problem_type]['correct'] += 1

    def get_success_rate(self):
        if self.problems_attempted == 0:
            return 0
        return (self.problems_correct / self.problems_attempted) * 100

    def get_grade(self):
        success_rate = self.get_success_rate()
        if success_rate >= 90:
            return "Отлично (5)"
        elif success_rate >= 75:
            return "Хорошо (4)"
        elif success_rate >= 60:
            return "Удовлетворительно (3)"
        else:
            return "Неудовлетворительно (2)"

    def get_type_success_rate(self, problem_type):
        stats = self.problem_types_stats[problem_type]
        if stats['attempted'] == 0:
            return 0
        return (stats['correct'] / stats['attempted']) * 100


class MathProblem:
    def __init__(self, problem_type, condition, solution, difficulty, explanation=""):
        self.problem_type = problem_type
        self.condition = condition
        self.solution = solution
        self.difficulty = difficulty
        self.explanation = explanation

    def get_solution_text(self):
        return f"Правильный ответ: {self.solution}"

    def get_explanation(self):
        if self.explanation:
            return self.explanation
        if self.problem_type == 'equation':
            return f"Решение: {self.condition.replace('?', str(self.solution))}"
        elif self.problem_type == 'sequence':
            nums = self.condition.replace("Продолжи: ", "").split(", ")
            for i, num in enumerate(nums):
                if num == "?":
                    return f"Пропущенное число: {self.solution}. Это арифметическая/геометрическая прогрессия."
        elif self.problem_type == 'percentage':
             return f"Это задача на проценты. Ответ: {self.solution}"
        return "Правильный ответ указан выше"


try:
    medkit_img = pygame.image.load('tileset/medkit.png').convert_alpha()
    medkit_img = pygame.transform.scale(medkit_img, (30, 30))
except Exception:
    medkit_img = pygame.Surface((30, 30))
    medkit_img.fill((255, 100, 100))
    pygame.draw.rect(medkit_img, WHITE, (12, 5, 6, 20))
    pygame.draw.rect(medkit_img, WHITE, (5, 12, 20, 6))


class Medkit:
    def __init__(self, x, y, heal_amount=2):
        self.x = x
        self.y = y
        self.heal_amount = heal_amount
        self.image = medkit_img
        self.rect = self.image.get_rect(center=(x + 15, y + 15))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class MathProblemGenerator:
    def __init__(self):
        self.used_problems = set()

    @staticmethod
    def generate_problem(difficulty):
        types_available = ['addition', 'subtraction']
        if difficulty >= 2:
            types_available.extend(['multiplication', 'sequence'])
        if difficulty >= 3:
            types_available.extend(['division', 'percentage'])
        if difficulty >= 4:
            types_available.extend(['equation'])

        ptype = random.choice(types_available)

        if ptype == 'addition':
            a = random.randint(10 * difficulty, 30 * difficulty)
            b = random.randint(10 * difficulty, 30 * difficulty)
            return MathProblem('equation', f"Реши: {a} + {b} = ?", a + b, difficulty, f"Складываем {a} и {b}, получаем {a + b}.")
        elif ptype == 'subtraction':
            a = random.randint(20 * difficulty, 40 * difficulty)
            b = random.randint(5 * difficulty, a)
            return MathProblem('equation', f"Реши: {a} - {b} = ?", a - b, difficulty, f"Вычитаем {b} из {a}, получаем {a - b}.")
        elif ptype == 'multiplication':
            a = random.randint(2 + difficulty, 8 + difficulty * 2)
            b = random.randint(2 + difficulty, 8 + difficulty * 2)
            return MathProblem('equation', f"Реши: {a} * {b} = ?", a * b, difficulty, f"Умножаем {a} на {b}, получаем {a * b}.")
        elif ptype == 'division':
            b = random.randint(2 + difficulty, 8 + difficulty)
            res = random.randint(2 + difficulty, 10 + difficulty * 2)
            a = b * res
            return MathProblem('equation', f"Реши: {a} / {b} = ?", res, difficulty, f"Делим {a} на {b}, получаем {res}.")
        elif ptype == 'sequence':
            start = random.randint(1, 10 * difficulty)
            step = random.randint(2, 4 + difficulty)
            missing = start + 3 * step
            seq = f"{start}, {start + step}, {start + 2 * step}, ?, {start + 4 * step}"
            return MathProblem('sequence', f"Продолжи: {seq}", missing, difficulty, f"Шаг прогрессии равен {step}. Значит {start + 2*step} + {step} = {missing}.")
        elif ptype == 'percentage':
            total = random.choice([50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000])
            percent = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
            res = int(total * percent / 100)
            return MathProblem('percentage', f"Найди {percent}% от {total}", res, difficulty, f"Чтобы найти {percent}%, нужно {total} умножить на {percent} и разделить на 100. ({total} * {percent} / 100 = {res}).")
        elif ptype == 'equation':
            x = random.randint(2, 10 + difficulty * 2)
            mult = random.randint(2, 5 + difficulty)
            return MathProblem('equation', f"Найди X: {mult} * X = {mult * x}", x, difficulty, f"Чтобы найти X, делим {mult*x} на {mult}, получаем {x}.")


class SaveManager:
    def __init__(self):
        self.saves_dir = "saves"
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)

    def get_save_files(self):
        saves = []
        for file in os.listdir(self.saves_dir):
            if file.endswith('.json'):
                save_path = os.path.join(self.saves_dir, file)
                try:
                    with open(save_path, 'r') as f:
                        data = json.load(f)
                    saves.append({
                        'name': file[:-5],
                        'path': save_path,
                        'timestamp': data.get('timestamp', ''),
                        'rooms_cleared': data.get('rooms_cleared', 0)
                    })
                except Exception:
                    continue
        return sorted(saves, key=lambda x: x['timestamp'], reverse=True)

    def save_game(self, game, save_name):
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'rooms_cleared': game.rooms_cleared,
            'last_merchant_room': game.last_merchant_room,
            'last_treasury_room': game.last_treasury_room,
            'current_room_pos': game.current_room_pos,
            'music_volume': game.music_volume,
            'sound_volume': game.sound_volume,
            'merchant_power_levels': Merchant.global_power_levels,
            'player': self._get_player_data(game.player),
            'rooms': self._get_rooms_data(game.rooms),
            'current_room': self._get_current_room_data(game.current_room)
        }

        save_path = os.path.join(self.saves_dir, f"{save_name}.json")
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)

        return True

    def load_game(self, game, save_name):
        save_path = os.path.join(self.saves_dir, f"{save_name}.json")
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
        except Exception:
            return False

        game.rooms_cleared = save_data['rooms_cleared']
        game.last_merchant_room = save_data['last_merchant_room']
        game.last_treasury_room = save_data['last_treasury_room']
        game.current_room_pos = tuple(save_data['current_room_pos'])
        game.music_volume = save_data['music_volume']
        game.sound_volume = save_data['sound_volume']

        Merchant.global_power_levels = save_data['merchant_power_levels']

        game.rooms = self._restore_rooms(save_data['rooms'], game)
        game.current_room = game.rooms[game.current_room_pos]

        self._restore_current_room(game.current_room, save_data['current_room'])

        self._restore_player(game.player, save_data['player'])

        return True

    def _get_player_data(self, player):
        return {
            'x': player.x,
            'y': player.y,
            'health': player.health,
            'max_health': player.max_health,
            'money': player.money,
            'damage': player.damage,
            'speed': player.speed,
            'time_bonus': player.time_bonus,
            'enemy_reduction': player.enemy_reduction,
            'enemy_health_reduction': player.enemy_health_reduction,
            'inventory': self._get_inventory_data(player.inventory)
        }

    def _get_inventory_data(self, inventory):
        items_data = []
        for item in inventory.items:
            if isinstance(item, Weapon):
                items_data.append({
                    'type': 'weapon',
                    'name': item.name,
                    'damage': item.damage,
                    'is_automatic': item.is_automatic,
                    'fire_rate': item.fire_rate,
                    'current_ammo': item.current_ammo
                })
            elif isinstance(item, Artifact):
                items_data.append({
                    'type': 'artifact',
                    'name': item.name,
                    'description': item.description
                })

        equipped_data = {}
        if inventory.equipped['weapon']:
            weapon = inventory.equipped['weapon']
            equipped_data['weapon'] = {
                'name': weapon.name,
                'damage': weapon.damage,
                'is_automatic': weapon.is_automatic,
                'fire_rate': weapon.fire_rate,
                'current_ammo': weapon.current_ammo
            }

        if inventory.equipped['artifact']:
            artifact = inventory.equipped['artifact']
            equipped_data['artifact'] = {
                'name': artifact.name,
                'description': artifact.description
            }

        return {
            'items': items_data,
            'equipped': equipped_data
        }

    def _get_rooms_data(self, rooms):
        rooms_data = {}
        for pos, room in rooms.items():
            if isinstance(pos, tuple):
                rooms_data[f"{pos[0]},{pos[1]}"] = {
                    'type': room.type.name,
                    'pos': room.pos,
                    'cleared': room.cleared,
                    'discovered': room.discovered,
                    'difficulty': room.difficulty
                }
        return rooms_data

    def _get_current_room_data(self, current_room):
        portals_data = []
        for portal in current_room.portals:
            portal_data = portal.copy()
            portal_data['type'] = portal_data['type'].name
            portals_data.append(portal_data)

        room_data = {
            'enemies': [],
            'coins': [],
            'walls': [],
            'portals': portals_data,
            'timer_active': current_room.timer_active,
            'time_remaining': current_room.time_remaining,
            'time_limit': current_room.time_limit,
            'timer_start': current_room.timer_start,
            'solution_shown': current_room.solution_shown
        }

        for wall in current_room.walls:
            wall_data = {
                'x': wall.x,
                'y': wall.y,
                'is_obstacle': wall.is_obstacle,
                'movable': wall.movable
            }
            room_data['walls'].append(wall_data)

        if current_room.math_problem:
            room_data['math_problem'] = {
                'problem_type': current_room.math_problem.problem_type,
                'condition': current_room.math_problem.condition,
                'solution': current_room.math_problem.solution,
                'difficulty': current_room.math_problem.difficulty
            }

        for enemy in current_room.enemies:
            enemy_data = {
                'x': enemy.x,
                'y': enemy.y,
                'enemy_type': enemy.enemy_type,
                'health': enemy.health,
                'max_health': enemy.max_health,
                'math_value': enemy.math_value,
                'is_correct': enemy.is_correct
            }
            room_data['enemies'].append(enemy_data)

        for coin in current_room.coins:
            coin_data = {
                'x': coin.x,
                'y': coin.y,
                'amount': coin.amount
            }
            room_data['coins'].append(coin_data)

        return room_data

    def _restore_rooms(self, rooms_data, game):
        rooms = {'game': game}
        for pos_str, room_data in rooms_data.items():
            x, y = map(int, pos_str.split(','))
            pos = (x, y)
            room_type = RoomType[room_data['type']]
            room = Room(room_type, pos, rooms, room_data['difficulty'])
            room.cleared = room_data['cleared']
            room.discovered = room_data['discovered']
            rooms[pos] = room
        return rooms

    def _restore_current_room(self, current_room, room_data):
        current_room.portals = []
        for portal_data in room_data['portals']:
            portal = portal_data.copy()
            portal['type'] = RoomType[portal_data['type']]
            current_room.portals.append(portal)

        current_room.timer_active = room_data['timer_active']
        current_room.time_remaining = room_data['time_remaining']
        current_room.time_limit = room_data['time_limit']
        current_room.timer_start = room_data['timer_start']
        current_room.solution_shown = room_data['solution_shown']

        if current_room.timer_active:
            current_room.timer_start = pygame.time.get_ticks() - (
                    current_room.time_limit - current_room.time_remaining) * 1000

        current_room.walls = []
        for wall_data in room_data['walls']:
            wall = Wall(wall_data['x'], wall_data['y'], wall_data['is_obstacle'])
            wall.movable = wall_data['movable']
            current_room.walls.append(wall)

        if 'math_problem' in room_data and room_data['math_problem']:
            math_data = room_data['math_problem']
            current_room.math_problem = MathProblem(
                math_data['problem_type'],
                math_data['condition'],
                math_data['solution'],
                math_data['difficulty']
            )

        current_room.enemies = []
        for enemy_data in room_data['enemies']:
            if enemy_data['enemy_type'] == "math":
                enemy = Enemy(
                    enemy_data['x'],
                    enemy_data['y'],
                    enemy_data['enemy_type'],
                    enemy_data['math_value'],
                    enemy_data['is_correct']
                )
            elif enemy_data['enemy_type'] == "boss":
                enemy = Boss(enemy_data['x'], enemy_data['y'], 50)
                if enemy_data['health'] <= enemy_data['max_health'] * 0.33:
                    enemy.phase = 3
                elif enemy_data['health'] <= enemy_data['max_health'] * 0.66:
                    enemy.phase = 2
                else:
                    enemy.phase = 1
                enemy.state = 'active'
                enemy.invulnerable = False
                enemy.shield_active = False
            else:
                enemy = Enemy(enemy_data['x'], enemy_data['y'], enemy_data['enemy_type'])

            enemy.health = enemy_data['health']
            enemy.max_health = enemy_data['max_health']
            current_room.enemies.append(enemy)

        current_room.coins = []
        for coin_data in room_data['coins']:
            coin = Coin(coin_data['x'], coin_data['y'], coin_data['amount'])
            current_room.coins.append(coin)

    def _restore_player(self, player, player_data):
        player.x = player_data['x']
        player.y = player_data['y']
        player.health = player_data['health']
        player.max_health = player_data['max_health']
        player.money = player_data['money']
        player.damage = player_data['damage']
        player.speed = player_data['speed']
        player.time_bonus = player_data['time_bonus']
        player.enemy_reduction = player_data['enemy_reduction']
        player.enemy_health_reduction = player_data['enemy_health_reduction']

        player.inventory.items = []
        for item_data in player_data['inventory']['items']:
            if item_data['type'] == 'weapon':
                weapon = Weapon(
                    item_data['name'],
                    item_data['damage'],
                    item_data['is_automatic'],
                    item_data['fire_rate']
                )
                weapon.current_ammo = item_data['current_ammo']
                player.inventory.items.append(weapon)
            elif item_data['type'] == 'artifact':
                for artifact in player.game.artifacts_pool:
                    if artifact.name == item_data['name']:
                        player.inventory.items.append(artifact)
                        break

        if 'weapon' in player_data['inventory']['equipped']:
            weapon_data = player_data['inventory']['equipped']['weapon']
            weapon = Weapon(
                weapon_data['name'],
                weapon_data['damage'],
                weapon_data['is_automatic'],
                weapon_data['fire_rate']
            )
            weapon.current_ammo = weapon_data['current_ammo']
            player.inventory.equipped['weapon'] = weapon

        if 'artifact' in player_data['inventory']['equipped']:
            artifact_data = player_data['inventory']['equipped']['artifact']
            for artifact in player.game.artifacts_pool:
                if artifact.name == artifact_data['name']:
                    player.inventory.equipped['artifact'] = artifact
                    break


class Merchant:
    global_power_levels = {
        "Health Up": {
            "level": 0,
            "max_level": 5
        },
        "Damage Up": {
            "level": 0,
            "max_level": 3
        },
        "Speed Up": {
            "level": 0,
            "max_level": 2
        },
        "Time Up": {
            "level": 0,
            "max_level": 3
        },
        "Enemy Reduction": {
            "level": 0,
            "max_level": 2
        },
        "Enemy Health Down": {
            "level": 0,
            "max_level": 2
        },
        "Dash Faster": {
            "level": 0,
            "max_level": 3
        }
    }

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.image = shopper_img
        self.phrases = ["Эй, путник, есть монеты?", "Только лучший товар!", "Защита не бывает лишней.", "Время - деньги!", "Не стой, покупай!"]
        self.current_phrase = random.choice(self.phrases)
        self.phrase_timer = pygame.time.get_ticks()
        self.last_purchase_time = 0
        self.purchase_cooldown = 500
        self.power_ups = [{
            "name": "Health Up",
            "cost": 50,
            "effect": lambda p: (setattr(p, 'max_health', p.max_health + 2), setattr(p, 'health', p.health + 2))
        }, {
            "name": "Damage Up",
            "cost": 75,
            "effect": lambda p: setattr(p, 'damage', p.damage + 5)
        }, {
            "name": "Speed Up",
            "cost": 60,
            "effect": lambda p: setattr(p, 'speed', p.speed + 1)
        }, {
            "name": "Time Up",
            "cost": 80,
            "effect": lambda p: setattr(p, 'time_bonus', p.time_bonus + 5)
        }, {
            "name": "Enemy Reduction",
            "cost": 100,
            "effect": lambda p: setattr(p, 'enemy_reduction', p.enemy_reduction + 1)
        }, {
            "name": "Enemy Health Down",
            "cost": 90,
            "effect": lambda p: setattr(p, 'enemy_health_reduction', p.enemy_health_reduction + 0.15)
        }, {
            "name": "Dash Faster",
            "cost": 80,
            "effect": lambda p: setattr(p, 'dash_cooldown', max(200, p.dash_cooldown - 250))
        }]
        self.current_offerings = random.sample(self.power_ups, 3)
        self.selected_item = None
        self.interaction_range = 60

    def draw(self, screen, player=None):
        current_time = pygame.time.get_ticks()
        if current_time - self.phrase_timer > 5000:
            self.current_phrase = random.choice(self.phrases)
            self.phrase_timer = current_time

        angle = 0
        if player:
            dx = player.x - self.x
            dy = player.y - self.y
            angle = math.degrees(-math.atan2(dy, dx)) - 90

        rotated_img = pygame.transform.rotate(self.image, angle)
        rect = rotated_img.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))

        # Тень
        shadow_rect = pygame.Rect(0, 0, self.size * 0.7, self.size * 0.3)
        shadow_rect.center = (self.x + self.size // 2, self.y + self.size - 5)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 120), shadow_surface.get_rect())
        screen.blit(shadow_surface, shadow_rect.topleft)

        screen.blit(rotated_img, rect.topleft)

        if player and self.check_collision(player) and self.selected_item is None:
            font = pygame.font.Font('PixelizerBold.ttf', 24)
            prompt_text = font.render("Нажмите E, чтобы закупиться", True, WHITE)
            bg_rect = pygame.Rect(self.x - 110, self.y - 65, prompt_text.get_width() + 20, prompt_text.get_height() + 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            screen.blit(prompt_text, (self.x - 100, self.y - 60))
        elif self.selected_item is None:
            # Фразы торговца
            font = pygame.font.Font('PixelizerBold.ttf', 20)
            phrase_text = font.render(self.current_phrase, True, GOLD)
            bg_rect = pygame.Rect(self.x + self.size // 2 - phrase_text.get_width() // 2 - 10, self.y - 35,
                                  phrase_text.get_width() + 20, phrase_text.get_height() + 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            pygame.draw.rect(screen, GOLD, bg_rect, 1, border_radius=5)
            screen.blit(phrase_text, (self.x + self.size // 2 - phrase_text.get_width() // 2, self.y - 30))

        if self.selected_item is not None:
            # Полупрозрачный фон для всего экрана, чтобы выделить магазин
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
            screen.blit(overlay, (0, 0))

            menu_width = 460
            menu_height = 340
            menu_x = (WINDOW_SIZE[0] - menu_width) // 2
            menu_y = (WINDOW_SIZE[1] - menu_height) // 2

            pygame.draw.rect(screen, (20, 20, 25), (menu_x, menu_y, menu_width, menu_height))
            pygame.draw.rect(screen, CYAN, (menu_x, menu_y, menu_width, menu_height), 3)
            pygame.draw.rect(screen, (40, 40, 50), (menu_x, menu_y, menu_width, 40))
            pygame.draw.rect(screen, CYAN, (menu_x, menu_y, menu_width, 40), 2)

            title_font = pygame.font.Font('PixelizerBold.ttf', 32)
            title_text = title_font.render("ТЕРМИНАЛ УЛУЧШЕНИЙ", True, GOLD)
            screen.blit(title_text, (menu_x + menu_width // 2 - title_text.get_width() // 2, menu_y + 5))

            close_btn_rect = pygame.Rect(menu_x + menu_width - 35, menu_y + 5, 30, 30)
            mouse_pos = pygame.mouse.get_pos()
            close_btn_color = RED if close_btn_rect.collidepoint(mouse_pos) else (150, 50, 50)
            pygame.draw.rect(screen, close_btn_color, close_btn_rect, border_radius=5)
            font = pygame.font.Font('PixelizerBold.ttf', 30)
            x_text = font.render("X", True, WHITE)
            screen.blit(x_text, (close_btn_rect.centerx - x_text.get_width() // 2,
                                 close_btn_rect.centery - x_text.get_height() // 2 + 2))

            font = pygame.font.Font('PixelizerBold.ttf', 24)
            for i, item in enumerate(self.current_offerings):
                y_pos = menu_y + 60 + i * 90

                item_bg_rect = pygame.Rect(menu_x + 10, y_pos, menu_width - 20, 80)
                if item_bg_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (40, 40, 50), item_bg_rect, border_radius=8)
                else:
                    pygame.draw.rect(screen, (30, 30, 35), item_bg_rect, border_radius=8)
                pygame.draw.rect(screen, (60, 60, 70), item_bg_rect, 1, border_radius=8)

                name_text = font.render(item["name"], True, CYAN)
                screen.blit(name_text, (menu_x + 20, y_pos + 10))

                if "Health" in item["name"]:
                    desc = "Увеличивает макс. здоровье"
                elif "Speed" in item["name"]:
                    desc = "Увеличивает скорость движения"
                elif "Time" in item["name"]:
                    desc = "Добавляет время на решение"
                elif "Enemy Reduction" in item["name"]:
                    desc = "Уменьшает количество врагов"
                elif "Enemy Health" in item["name"]:
                    desc = "Уменьшает здоровье врагов"
                elif "Dash Faster" in item["name"]:
                    desc = "Ускоряет откат рывка"
                else:
                    desc = "Увеличивает базовый урон"

                desc_text = font.render(desc, True, (180, 180, 180))
                screen.blit(desc_text, (menu_x + 20, y_pos + 40))

                current_level = self.global_power_levels[item['name']]['level']
                max_level = self.global_power_levels[item['name']]['max_level']

                # Отрисовка прогресса уровня
                level_text = font.render(f"Lv.{current_level}/{max_level}", True, GOLD)
                screen.blit(level_text, (menu_x + 20, y_pos + 60))

                if current_level < max_level:
                    cost_text = font.render(str(item['cost']), True, WHITE)
                    screen.blit(cost_text, (menu_x + menu_width - 160, y_pos + 25))
                    screen.blit(coin_img, (menu_x + menu_width - 160 + cost_text.get_width() + 5, y_pos + 25))

                    button_rect = pygame.Rect(menu_x + menu_width - 110, y_pos + 20, 90, 40)
                    button_color = GOLD if button_rect.collidepoint(mouse_pos) else (100, 100, 100)
                    pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
                    buy_text = font.render("КУПИТЬ", True, BLACK)
                    screen.blit(buy_text, (
                        button_rect.centerx - buy_text.get_width() // 2,
                        button_rect.centery - buy_text.get_height() // 2 + 2))

                    if button_rect.collidepoint(mouse_pos) or close_btn_rect.collidepoint(mouse_pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                else:
                    max_text = font.render("МАКСИМУМ", True, (100, 100, 100))
                    screen.blit(max_text, (menu_x + menu_width - 130, y_pos + 25))

    def check_collision(self, player):
        if abs(player.x + player.size // 2 - self.x - self.size // 2) < self.interaction_range and \
                abs(player.y + player.size // 2 - self.y - self.size // 2) < self.interaction_range:
            return True
        else:
            return False

    def get_clicked_item(self, mouse_pos):
        menu_width = 460
        menu_height = 340
        menu_x = (WINDOW_SIZE[0] - menu_width) // 2
        menu_y = (WINDOW_SIZE[1] - menu_height) // 2

        for i, item in enumerate(self.current_offerings):
            y_pos = menu_y + 60 + i * 90
            button_rect = pygame.Rect(menu_x + menu_width - 110, y_pos + 20, 90, 40)
            if button_rect.collidepoint(mouse_pos):
                return i
        return None

    def try_purchase(self, player, item_index):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_purchase_time < self.purchase_cooldown):
            return False

        if item_index is not None and item_index < len(self.current_offerings):
            item = self.current_offerings[item_index]
            current_level = self.global_power_levels[item['name']]['level']
            max_level = self.global_power_levels[item['name']]['max_level']

            if player.money >= item['cost'] and current_level < max_level:
                self.last_purchase_time = current_time
                player.money -= item['cost']
                item['effect'](player)
                self.global_power_levels[item['name']]['level'] += 1
                return True
            return False


class Coin:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.frames = coin_frames if 'coin_frames' in globals() and coin_frames else [coin_img]
        self.current_frame = 0
        self.last_anim_update = pygame.time.get_ticks()
        self.rect = self.frames[0].get_rect(center=(x + 15, y + 15))

    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_anim_update > 100:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_anim_update = current_time

        image = self.frames[self.current_frame]
        new_rect = image.get_rect(center=self.rect.center)
        screen.blit(image, new_rect.topleft)


floor_texture = pygame.image.load('tileset/stonefloorai1.png')
wall_texture = pygame.image.load('tileset/brickwall1.png')
obstacle_texture = pygame.image.load('tileset/woodbox.png')

TILE_SIZE = 40
floor_texture = pygame.transform.scale(floor_texture, (TILE_SIZE, TILE_SIZE))
wall_texture = pygame.transform.scale(wall_texture, (TILE_SIZE, TILE_SIZE))
obstacle_texture = pygame.transform.scale(obstacle_texture, (TILE_SIZE, TILE_SIZE))


class Room:
    def __init__(self, room_type=RoomType.NORMAL, pos=(0, 0), rooms=None, difficulty=1):
        self.type = room_type
        self.walls = []
        self.enemies = []
        self.chests = []
        self.portals = []
        self.coins = []
        self.pos = pos
        self.rooms = rooms if rooms is not None else {}
        self.discovered = False
        self.cleared = False
        self.math_problem = None
        self.solution_shown = False
        self.generator = MathProblemGenerator()
        self.difficulty = difficulty
        self.time_limit = 25
        self.time_remaining = self.time_limit
        self.timer_active = False
        self.timer_start = 0
        self.damage_texts = []
        self.enemy_bullets = []
        self.particles = []
        self.shells = []
        self.explosions = []
        self.merchant = None
        self.floor_positions = []
        self.medkits = []

        if self.type in [RoomType.SHOP, RoomType.TREASURE]:
            self.add_portal(RoomType.NORMAL)
        self.generate_room()

    def generate_room(self):
        self.floor_positions = []
        for x in range(0, WINDOW_SIZE[0], TILE_SIZE):
            for y in range(0, WINDOW_SIZE[1], TILE_SIZE):
                self.floor_positions.append((x, y))

        for x in range(0, WINDOW_SIZE[0], TILE_SIZE):
            wall = Wall(x, 0, False)
            self.walls.append(wall)

        for x in range(0, WINDOW_SIZE[0], TILE_SIZE):
            wall = Wall(x, WINDOW_SIZE[1] - TILE_SIZE, False)
            self.walls.append(wall)

        for y in range(0, WINDOW_SIZE[1], TILE_SIZE):
            wall = Wall(0, y, False)
            self.walls.append(wall)

        for y in range(0, WINDOW_SIZE[1], TILE_SIZE):
            wall = Wall(WINDOW_SIZE[0] - TILE_SIZE, y, False)
            self.walls.append(wall)

        if self.type != RoomType.BOSS and self.type != RoomType.SHOP:
            spawn_zone_radius = 80
            center_x = WINDOW_SIZE[0] // 2
            center_y = WINDOW_SIZE[1] // 2

            for _ in range(10):
                while True:
                    x = random.randrange(80, WINDOW_SIZE[0] - 120, 40)
                    y = random.randrange(80, WINDOW_SIZE[1] - 120, 40)
                    distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    if distance > spawn_zone_radius:
                        self.walls.append(Wall(x, y, True))
                        break

        if self.type == RoomType.BOSS:
            cw, ch = WINDOW_SIZE
            self.walls.append(Wall(120, 120, True))
            self.walls.append(Wall(cw - 160, 120, True))
            self.walls.append(Wall(120, ch - 160, True))
            self.walls.append(Wall(cw - 160, ch - 160, True))

        if self.type == RoomType.SHOP:
            self.merchant = Merchant(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)

        if self.type == RoomType.NORMAL:
            self.math_problem = self.generator.generate_problem(self.difficulty)

            # Рандомное количество и типы врагов (от 3 до 6 в зависимости от сложности)
            num_enemies = random.randint(3, 4 + min(self.difficulty // 2, 2))

            player = None
            if 'game' in self.rooms and hasattr(self.rooms['game'], 'player'):
                player = self.rooms['game'].player
                num_enemies = max(2, num_enemies - player.enemy_reduction)

            possible_behaviors = ["basic", "basic", "sniper"]
            if self.difficulty >= 2:
                possible_behaviors.extend(["ghost", "scout"])
            if self.difficulty >= 3:
                possible_behaviors.append("tank")

            behaviors = [random.choice(possible_behaviors) for _ in range(num_enemies)]
            roles = ["wrong"] * num_enemies
            roles[random.randint(0, num_enemies - 1)] = "correct"

            for i in range(num_enemies):
                self.add_enemy(behaviors[i], roles[i])
        elif self.type == RoomType.BOSS:
            self.add_enemy("boss")

        if self.type == RoomType.TREASURE:
            self.chests.append(Chest(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2, self.rooms['game']))

    def add_portal(self, room_type):
        player = None
        if 'game' in self.rooms and hasattr(self.rooms['game'], 'player'):
            player = self.rooms['game'].player

        attempts = 0
        while attempts < 100:
            x = random.randint(80, WINDOW_SIZE[0] - 120)
            y = random.randint(80, WINDOW_SIZE[1] - 120)
            portal_valid = True

            for wall in self.walls:
                if (x + 40 > wall.x and x < wall.x + wall.size and y + 40 > wall.y and y < wall.y + wall.size):
                    portal_valid = False
                    break

                # Защита от спавна на сундуках
            if portal_valid:
                for chest in self.chests:
                    if (
                            x + 40 > chest.x and x < chest.x + chest.size and y + 40 > chest.y and y < chest.y + chest.size):
                        portal_valid = False
                        break

            # Защита от спавна на монетках
            if portal_valid:
                for coin in self.coins:
                    if (x + 40 > coin.x and x < coin.x + 20 and y + 40 > coin.y and y < coin.y + 20):
                        portal_valid = False
                        break

            # Защита от спавна в центре (чтобы игрок не телепортировался сразу при входе)
            if portal_valid:
                center_dist = math.sqrt(
                    (x + 20 - WINDOW_SIZE[0] // 2) ** 2 + (y + 20 - WINDOW_SIZE[1] // 2) ** 2)
                if center_dist < 100:
                    portal_valid = False

            # Проверка, чтобы портал не заспавнился прямо под игроком
            if portal_valid and player:
                dist = math.sqrt(
                    (x + 20 - (player.x + player.size // 2)) ** 2 + (y + 20 - (player.y + player.size // 2)) ** 2)
                if dist < 120:
                    portal_valid = False

            if portal_valid:
                self.portals.append({'type': room_type, 'x': x, 'y': y, 'size': 40})
                break
            attempts += 1

    def add_enemy(self, behavior="basic", role="wrong"):
        enemy_spawn_attempts = 0
        max_attempts = 50
        center_x = WINDOW_SIZE[0] // 2
        center_y = WINDOW_SIZE[1] // 2
        min_distance_from_center = 150

        while enemy_spawn_attempts < max_attempts:
            x = random.randrange(80, WINDOW_SIZE[0] - 120, 40)
            y = random.randrange(80, WINDOW_SIZE[1] - 120, 40)

            distance_to_center = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance_to_center < min_distance_from_center:
                enemy_spawn_attempts += 1
                continue

            valid_position = True

            # Безопасная зона вокруг игрока (чтобы враги не спавнились на голове)
            if 'game' in self.rooms and hasattr(self.rooms['game'], 'player'):
                player = self.rooms['game'].player
                dist_to_player = math.sqrt((x - player.x) ** 2 + (y - player.y) ** 2)
                if dist_to_player < 200:
                    enemy_spawn_attempts += 1
                    continue

            spawn_size = 100 if behavior == "boss" else 70
            for wall in self.walls:
                if (
                        x + spawn_size > wall.x and x < wall.x + wall.size and y + spawn_size > wall.y and y < wall.y + wall.size):
                    valid_position = False
                    break

            if valid_position:
                for enemy in self.enemies:
                    # Учитываем размер уже стоящих врагов
                    e_size = 100 if getattr(enemy, 'enemy_type', '') == 'boss' else 70
                    if (
                            x + spawn_size > enemy.x and x < enemy.x + e_size and y + spawn_size > enemy.y and y < enemy.y + e_size):
                        valid_position = False
                        break

            if valid_position:
                success_rate = 50
                player = None
                if 'game' in self.rooms and hasattr(self.rooms['game'], 'player'):
                    player = self.rooms['game'].player
                    if player.stats.problems_attempted > 0:
                        success_rate = player.stats.get_success_rate()

                if self.type == RoomType.BOSS and behavior == "boss":
                    boss = Boss(x, y, success_rate)
                    if player:
                        boss.max_health = int(boss.max_health * (1 - player.enemy_health_reduction))
                        boss.health = boss.max_health
                    self.enemies.append(boss)
                else:
                    if role == "correct":
                        value = self.math_problem.solution
                        is_correct = True
                    else:
                        wrong_answer = self.math_problem.solution + random.randint(-10, 10)
                        while wrong_answer == self.math_problem.solution or wrong_answer <= 0:
                            wrong_answer = self.math_problem.solution + random.randint(-10, 10)
                        value = wrong_answer
                        is_correct = False

                    enemy = Enemy(x, y, behavior, value, is_correct, success_rate)
                    if player:
                        enemy.max_health = int(enemy.max_health * (1 - player.enemy_health_reduction))
                        enemy.health = enemy.max_health
                    self.enemies.append(enemy)
                break

            enemy_spawn_attempts += 1

    def start_timer(self):
        self.timer_active = True
        self.time_remaining = self.time_limit
        self.timer_start = pygame.time.get_ticks()

    def update_timer(self):
        if self.timer_active:
            elapsed = (pygame.time.get_ticks() - self.timer_start) / 1000
            self.time_remaining = max(0, self.time_limit - elapsed)
            if self.time_remaining <= 0:
                self.timer_active = False
                return True
        return False


class Wall:
    def __init__(self, x, y, is_obstacle=False):
        self.x = x
        self.y = y
        self.size = TILE_SIZE
        self.is_obstacle = is_obstacle
        self.texture = obstacle_texture if is_obstacle else wall_texture
        self.movable = False

    def draw(self, screen):
        screen.blit(self.texture, (self.x, self.y))

    def try_move(self, dx, dy, walls):
        if dx != 0 and dy != 0:
            return False

        new_x = self.x + dx * 5
        new_y = self.y + dy * 5

        for wall in walls:
            if wall != self and (
                    new_x + self.size > wall.x and new_x < wall.x + wall.size and new_y + self.size > wall.y and new_y < wall.y + wall.size):
                return False

        if new_x < TILE_SIZE or new_x > WINDOW_SIZE[0] - TILE_SIZE * 2 or new_y < TILE_SIZE or new_y > WINDOW_SIZE[
            1] - TILE_SIZE * 2:
            return False

        self.x = new_x
        self.y = new_y
        return True


class Inventory:
    def __init__(self):
        self.items = []
        self.equipped = {'weapon': None, 'artifact': None}
        self.visible = False
        self.cell_size = 60
        self.padding = 10
        self.rows = 4
        self.cols = 5
        self.scroll_offset = 0
        self.font = pygame.font.Font('PixelizerBold.ttf', 24)
        self.selected_item = None

    def add_item(self, item):
        self.items.append(item)
        return True

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def equip_item(self, item):
        equipped = False
        if isinstance(item, Weapon):
            if self.equipped['weapon']:
                self.items.append(self.equipped['weapon'])
            self.equipped['weapon'] = item
            self.remove_item(item)
            equipped = True
        elif isinstance(item, Artifact):
            if self.equipped['artifact']:
                self.items.append(self.equipped['artifact'])
            self.equipped['artifact'] = item
            self.remove_item(item)
            equipped = True

        if equipped and 'equip_sound' in globals() and equip_sound:
            equip_sound.play()

    def unequip_item(self, slot):
        if self.equipped[slot]:
            item = self.equipped[slot]
            if self.add_item(item):
                self.equipped[slot] = None
                if 'equip_sound' in globals() and equip_sound:
                    equip_sound.play()
                return True
        return False

    def draw(self, screen, player):
        if not self.visible:
            return

        # Полупрозрачный фон
        surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
        screen.blit(surface, (0, 0))

        # Размеры панелей
        panel_width = 700
        panel_height = 480
        panel_x = (WINDOW_SIZE[0] - panel_width) // 2
        panel_y = (WINDOW_SIZE[1] - panel_height) // 2

        # Главная панель инвентаря
        pygame.draw.rect(screen, (30, 30, 35), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(screen, CYAN, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)

        # Заголовок
        title_font = pygame.font.Font('PixelizerBold.ttf', 40)
        title = title_font.render("ИНВЕНТАРЬ И СТАТИСТИКА", True, GOLD)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, panel_y + 15))

        # левая панель статистики
        stats_x = panel_x + 30
        stats_y = panel_y + 80
        pygame.draw.rect(screen, (20, 20, 25), (stats_x - 10, stats_y - 10, 250, panel_height - 90), border_radius=10)
        pygame.draw.rect(screen, (60, 60, 70), (stats_x - 10, stats_y - 10, 250, panel_height - 90), 2,
                         border_radius=10)

        stat_font = pygame.font.Font('PixelizerBold.ttf', 24)
        stats = [
            ("Здоровье", f"{player.health}/{player.total_max_health}", RED),
            ("Урон (баз.)", f"{player.total_damage}", ORANGE),
            ("Скорость", f"{player.total_speed}", CYAN),
            ("Доп. Время", f"+{player.time_bonus} сек", GOLD),
            ("Врагов меньше", f"-{player.enemy_reduction}", GREEN),
            ("Слабость врагов", f"-{int(player.enemy_health_reduction * 100)}%", PURPLE)
        ]

        for i, (name, val, color) in enumerate(stats):
            s_name = stat_font.render(name + ":", True, (200, 200, 200))
            s_val = stat_font.render(val, True, color)
            screen.blit(s_name, (stats_x, stats_y + i * 40))
            screen.blit(s_val, (stats_x + 230 - s_val.get_width(), stats_y + i * 40))

        # правая панель предметов
        inv_x = stats_x + 280
        inv_y = stats_y

        # Экипировано
        equip_title = self.font.render("ЭКИПИРОВАНО", True, WHITE)
        screen.blit(equip_title, (inv_x, inv_y))

        pygame.draw.rect(screen, (40, 40, 50), (inv_x, inv_y + 30, self.cell_size * 2 + self.padding, self.cell_size),
                         border_radius=8)
        pygame.draw.rect(screen, GOLD, (inv_x, inv_y + 30, self.cell_size * 2 + self.padding, self.cell_size), 2,
                         border_radius=8)

        if self.equipped['weapon']:
            if hasattr(self.equipped['weapon'], 'icon'):
                icon_rect = self.equipped['weapon'].icon.get_rect(
                    center=(inv_x + self.cell_size // 2, inv_y + 30 + self.cell_size // 2))
                screen.blit(self.equipped['weapon'].icon, icon_rect.topleft)
            else:
                text = self.font.render(self.equipped['weapon'].name[:10], True, CYAN)
                screen.blit(text, (inv_x + 5, inv_y + 30 + self.cell_size // 2 - text.get_height() // 2))

        if self.equipped['artifact']:
            if hasattr(self.equipped['artifact'], 'icon'):
                icon_rect = self.equipped['artifact'].icon.get_rect(
                    center=(inv_x + self.cell_size + self.padding + self.cell_size // 2,
                            inv_y + 30 + self.cell_size // 2))
                screen.blit(self.equipped['artifact'].icon, icon_rect.topleft)
            else:
                text = self.font.render(self.equipped['artifact'].name[:10], True, PURPLE)
                screen.blit(text, (inv_x + self.cell_size + self.padding + 5,
                                   inv_y + 30 + self.cell_size // 2 - text.get_height() // 2))

            # Сетка предметов
        grid_start_y = inv_y + 110

        mouse_pos = pygame.mouse.get_pos()
        tooltip_item = None

        for row in range(self.rows):
            for col in range(self.cols):
                x = inv_x + col * (self.cell_size + self.padding)
                y = grid_start_y + row * (self.cell_size + self.padding)

                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                is_hovered = cell_rect.collidepoint(mouse_pos)

                pygame.draw.rect(screen, (60, 60, 70) if is_hovered else (40, 40, 45), cell_rect, border_radius=5)
                pygame.draw.rect(screen, WHITE if is_hovered else (100, 100, 110), cell_rect, 2, border_radius=5)

                idx = (self.scroll_offset + row) * self.cols + col
                if idx < len(self.items):
                    item = self.items[idx]

                    if hasattr(item, 'icon'):
                        # Масштабирование иконки под ячейку
                        icon_rect = item.icon.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                        screen.blit(item.icon, icon_rect.topleft)
                    else:
                        text = self.font.render(item.name[:6], True, WHITE)
                        screen.blit(text, (x + 5, y + self.cell_size // 2 - text.get_height() // 2))

                    if is_hovered:
                        tooltip_item = item

        if tooltip_item:
            font_title = pygame.font.Font('PixelizerBold.ttf', 24)
            font_desc = pygame.font.Font('PixelizerBold.ttf', 18)

            title_text = font_title.render(tooltip_item.name, True, GOLD)

            if hasattr(tooltip_item, 'description'):
                desc_text = tooltip_item.description
            else:
                auto_str = "Автомат." if getattr(tooltip_item, 'is_automatic', False) else "Одиночн."
                desc_text = f"Урон: {getattr(tooltip_item, 'damage', 0)} | {auto_str}"

            wrapped_desc = player.game.wrap_text(desc_text, font_desc, 220)

            # Расчет размеров тултипа
            tooltip_w = max(250, title_text.get_width() + 75)
            tooltip_h = max(80, 20 + 48 + 10 + len(wrapped_desc) * 20)

            t_x = mouse_pos[0] + 15
            t_y = mouse_pos[1] + 15

            # Ограничение по экрану (чтобы не уходил за рамки)
            if t_x + tooltip_w > WINDOW_SIZE[0]:
                t_x = WINDOW_SIZE[0] - tooltip_w - 5
            if t_y + tooltip_h > WINDOW_SIZE[1]:
                t_y = WINDOW_SIZE[1] - tooltip_h - 5

            bg_rect = pygame.Rect(t_x, t_y, tooltip_w, tooltip_h)
            pygame.draw.rect(screen, (20, 20, 25, 235), bg_rect, border_radius=8)
            pygame.draw.rect(screen, CYAN, bg_rect, 2, border_radius=8)

            # Отрисовка иконки
            if hasattr(tooltip_item, 'icon'):
                screen.blit(tooltip_item.icon, (t_x + 10, t_y + 10))
                pygame.draw.rect(screen, WHITE, (t_x + 10, t_y + 10, 48, 48), 1, border_radius=4)

            # Заголовок
            screen.blit(title_text, (t_x + 65, t_y + 15))

            # Описание
            for i, line in enumerate(wrapped_desc):
                line_surf = font_desc.render(line, True, (200, 200, 200))
                screen.blit(line_surf, (t_x + 10, t_y + 65 + i * 20))

    def handle_click(self, pos):
        if not self.visible:
            return

        panel_width = 700
        panel_height = 480
        panel_x = (WINDOW_SIZE[0] - panel_width) // 2
        panel_y = (WINDOW_SIZE[1] - panel_height) // 2
        stats_x = panel_x + 30
        stats_y = panel_y + 80
        inv_x = stats_x + 280
        inv_y = stats_y

        equipped_y = inv_y + 30
        grid_start_y = inv_y + 110

        # Клик по экипированным
        if pos[1] >= equipped_y and pos[1] <= equipped_y + self.cell_size:
            if pos[0] >= inv_x and pos[0] <= inv_x + self.cell_size:
                self.unequip_item('weapon')
            elif pos[0] >= inv_x + self.cell_size + self.padding and pos[0] <= inv_x + (
                    self.cell_size + self.padding) * 2:
                self.unequip_item('artifact')

        # Клик по инвентарю
        for row in range(self.rows):
            for col in range(self.cols):
                x = inv_x + col * (self.cell_size + self.padding)
                y = grid_start_y + row * (self.cell_size + self.padding)
                if pos[0] >= x and pos[0] <= x + self.cell_size and pos[1] >= y and pos[
                    1] <= y + self.cell_size:
                    idx = (self.scroll_offset + row) * self.cols + col
                    if idx < len(self.items):
                        self.equip_item(self.items[idx])


class Player:
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.game = game
        self.size = 50

        # мета прокачка
        meta_speed_bonus = game.meta_upgrades['speed'] * 0.25
        self.speed = 5 + meta_speed_bonus

        meta_hp_bonus = game.meta_upgrades['hp']  # +1 HP (0.5 heart) per level
        self.health = 6 + meta_hp_bonus
        self.max_health = 6 + meta_hp_bonus

        meta_dmg_bonus = game.meta_upgrades['damage']  # +1 damage per level
        self.damage = 10 + meta_dmg_bonus

        self.last_damage_time = 0
        self.money = 0
        self.bullets = []
        self.angle = 0
        self.target_angle = 0
        self.rotation_speed = 0.1
        self.gun_offset = 50
        self.inventory = Inventory()
        starting_weapon = Weapon("Pistol", 10, False, 200)
        self.inventory.equipped['weapon'] = starting_weapon
        self.last_melee_attack = 0
        self.melee_cooldown = 500
        self.melee_damage = 15
        self.melee_range = 60
        self.image = pygame.image.load('tileset/player.png')
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.time_bonus = 0
        self.enemy_reduction = 0
        self.enemy_health_reduction = 0
        self.stats = PlayerStats()

        # Настройки рывка
        self.is_dashing = False
        self.dash_speed_multiplier = 3.5
        self.dash_duration = 200
        self.dash_cooldown = 1000
        self.last_dash_time = 0
        self.dash_dx = 0
        self.dash_dy = 0
        self.trail_positions = []
        self.is_dying = False
        self.death_anim_timer = 0
        self.dash_ready_flash_time = 0
        self.dash_was_ready = True
        self.last_shoot_sound_time = 0
        self.infinite_ammo = False

    @property
    def total_speed(self):
        s = self.speed
        if self.inventory.equipped['artifact'] and self.inventory.equipped['artifact'].name == "Speed Boots":
            s *= 1.5
        return s

    @property
    def total_max_health(self):
        m = self.max_health
        if self.inventory.equipped['artifact'] and self.inventory.equipped['artifact'].name == "Heart Crystal":
            m += 2
        return m

    @property
    def total_damage(self):
        d = self.damage
        if self.inventory.equipped['artifact'] and self.inventory.equipped['artifact'].name == "Power Ring":
            d += 10
        return d

    @property
    def reload_multiplier(self):
        if self.inventory.equipped['artifact'] and self.inventory.equipped['artifact'].name == "Quick Reload":
            return 0.5
        return 1.0

    @property
    def is_cloaked(self):
        if getattr(self, 'godmode', False):
            return True
        if self.inventory.equipped['artifact'] and self.inventory.equipped['artifact'].name == "Invisibility Cloak":
            return pygame.time.get_ticks() % 4000 < 1000
        return False

    def start_dash(self, dx, dy, mouse_pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time >= self.dash_cooldown:
            self.is_dashing = True
            self.last_dash_time = current_time
            if dx == 0 and dy == 0:
                # Если стоит на месте, рывок в сторону курсора
                mx, my = mouse_pos
                angle = math.atan2(my - (self.y + self.size // 2), mx - (self.x + self.size // 2))
                self.dash_dx = math.cos(angle)
                self.dash_dy = math.sin(angle)
            else:
                # Рывок в сторону движения (с нормализацией диагонали)
                length = math.sqrt(dx * dx + dy * dy)
                self.dash_dx = dx / length
                self.dash_dy = dy / length
            return True
        return False

    def draw(self, screen):
        if getattr(self, 'is_dying', False):
            return

        current_time = pygame.time.get_ticks()

        # Отрисовка следа от рывка (Dash Trail)
        if self.is_dashing:
            self.trail_positions.append((self.x, self.y, self.angle, current_time))

        self.trail_positions = [t for t in self.trail_positions if current_time - t[3] < 150]

        for tx, ty, tangle, ttime in self.trail_positions:
            alpha = max(0, 100 - int((current_time - ttime) / 150 * 100))
            t_img = pygame.transform.rotate(self.image, math.degrees(-tangle))
            t_img.set_alpha(alpha)
            t_rect = t_img.get_rect(center=(tx + self.size // 2, ty + self.size // 2))
            screen.blit(t_img, t_rect.topleft)

        # Отрисовка тени под игроком
        shadow_rect = pygame.Rect(0, 0, self.size * 0.7, self.size * 0.3)
        shadow_rect.center = (self.x + self.size // 2, self.y + self.size - 5)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 120), shadow_surface.get_rect())
        screen.blit(shadow_surface, shadow_rect.topleft)

        angle_diff = (self.target_angle - self.angle) % (2 * math.pi)
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        self.angle += angle_diff * self.rotation_speed

        rotated_image = pygame.transform.rotate(self.image, math.degrees(-self.angle) + 0)
        new_rect = rotated_image.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))

        # Анимация рывка и мерцания при получении урона
        if getattr(self, 'dash_ready_flash_time', 0) > 0 and current_time - self.dash_ready_flash_time < 150:
            # Вспышка циановым цветом когда рывок восстановился
            rotated_image.fill((0, 200, 200), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(rotated_image, new_rect.topleft)
        elif self.is_dashing or self.is_cloaked:
            # Полупрозрачность для рывка ИЛИ активного плаща-невидимки
            rotated_image.set_alpha(128)
            screen.blit(rotated_image, new_rect.topleft)
        elif current_time - self.last_damage_time < 1000:
            if (current_time // 100) % 2 == 0:
                screen.blit(rotated_image, new_rect.topleft)
        else:
            rotated_image.set_alpha(255)
            screen.blit(rotated_image, new_rect.topleft)

        weapon = self.inventory.equipped['weapon']
        if weapon and weapon.is_reloading:
            weapon.update_reload(current_time)
            if weapon.current_frame < len(weapon.reload_frames):
                reload_frame = weapon.reload_frames[weapon.current_frame]
                screen.blit(reload_frame, (self.x + self.size // 2 - 25, self.y - 60))

    def update(self, mouse_pos):
        current_time = pygame.time.get_ticks()

        if getattr(self, 'is_dying', False):
            if current_time - self.death_anim_timer < 2500:
                if current_time % 2 == 0:
                    px = self.x + self.size // 2 + random.randint(-15, 15)
                    py = self.y + self.size // 2 + random.randint(-15, 15)
                    for _ in range(4):
                        self.game.current_room.particles.append(Particle(px, py, (50, 150, 255)))
            else:
                self.game.game_over = True
                self.game.show_menu = True
            return

        if self.is_dashing and current_time - self.last_dash_time > self.dash_duration:
            self.is_dashing = False

        # Отслеживание восстановления рывка
        dash_is_ready_now = (current_time - self.last_dash_time >= self.dash_cooldown)
        if dash_is_ready_now and not getattr(self, 'dash_was_ready', True):
            self.dash_ready_flash_time = current_time
        self.dash_was_ready = dash_is_ready_now

        dx = mouse_pos[0] - (self.x + self.size // 2)
        dy = mouse_pos[1] - (self.y + self.size // 2)
        self.target_angle = math.atan2(dy, dx)


    def melee_attack(self, current_room):
        if getattr(self, 'is_dying', False): return
        for enemy in current_room.enemies[:]:
            dist = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
            if dist <= self.melee_range:
                artifact_bonus = self.total_damage - self.damage
                final_melee = self.melee_damage + artifact_bonus
                enemy.health -= final_melee

                # Защита от убийства босса одной атакой
                if getattr(enemy, 'enemy_type', '') == 'boss':
                    if enemy.phase == 1 and enemy.health < enemy.max_health * 0.66:
                        enemy.health = enemy.max_health * 0.66
                    elif enemy.phase == 2 and enemy.health < enemy.max_health * 0.33:
                        enemy.health = enemy.max_health * 0.33
                    elif enemy.phase == 3 and enemy.health <= 0 and getattr(enemy, 'state', '') != 'dying':
                        enemy.health = 1
                        enemy.state = 'dying'
                        enemy.invulnerable = True
                        enemy.death_timer = pygame.time.get_ticks()
                        if 'boss_death_snd' in globals() and boss_death_snd: boss_death_snd.play()

                # Спавн всплывающего урона
                color = WHITE
                if enemy.enemy_type == "math":
                    color = RED
                elif enemy.enemy_type == "boss":
                    color = PURPLE
                current_room.damage_texts.append(
                    DamageText(enemy.x + enemy.size // 2, enemy.y, final_melee, color))

                if enemy.health <= 0:
                    current_room.enemies.remove(enemy)
                    if current_room.type != RoomType.BOSS:
                        current_room.coins.append(Coin(enemy.x, enemy.y, enemy.money))
                    if random.random() < 0.10:  # 10% шанс на аптечку
                        if not hasattr(current_room, 'medkits'): current_room.medkits = []
                        current_room.medkits.append(Medkit(enemy.x, enemy.y, random.choice([1, 2])))

    def shoot(self, target_x, target_y, current_room=None):
        if getattr(self, 'is_dying', False): return
        current_time = pygame.time.get_ticks()

        if not self.inventory.equipped['weapon']:
            if current_time - self.last_melee_attack >= self.melee_cooldown:
                self.melee_attack(current_room)
                self.last_melee_attack = current_time
            return

        weapon = self.inventory.equipped['weapon']
        if not weapon.can_shoot(current_time):
            return

        # Правильный подсчет урона: базовый урон игрока = 10, все что выше - это бонусы.
        bonus_damage = self.total_damage - 10
        weapon_base = weapon.damage if weapon else 10
        damage = weapon_base + bonus_damage

        if not getattr(self, 'infinite_ammo', False):
            weapon.current_ammo -= 1
        weapon.last_shot = current_time

        # Исправление зацикленного/наложенного звука для скорострельного оружия
        if current_time - getattr(self, 'last_shoot_sound_time', 0) > 100 or weapon.fire_rate >= 150:
            if 'shoot_sound' in globals() and shoot_sound:
                base_vol = 0.5 * self.game.sound_volume
                if weapon.fire_rate < 150:
                    base_vol *= 0.25  # автоматы и огнемет намного тише
                shoot_sound.set_volume(base_vol)
                shoot_sound.play()
            self.last_shoot_sound_time = current_time

        # Легкая тряска экрана при выстреле
        self.game.screen_shake = max(getattr(self.game, 'screen_shake', 0), 3)

        # Вылет гильзы
        if current_room and weapon.name not in ["Rocket Launcher", "Grenade Launcher", "Flamethrower", "Railgun",
                                                "Crossbow"]:
            shell_angle = math.atan2(target_y - (self.y + self.size // 2),
                                     target_x - (self.x + self.size // 2)) + math.pi / 2
            current_room.shells.append(Shell(self.x + self.size // 2, self.y + self.size // 2, shell_angle))

        # Проверка на стихийные и взрывные снаряды
        is_explosive = weapon.name in ["Rocket Launcher", "Grenade Launcher"]
        bullet_effect = None
        if weapon.name == "Flamethrower":
            bullet_effect = "burn"

        if self.inventory.equipped['artifact']:
            if self.inventory.equipped['artifact'].name == "Explosive Rounds":
                is_explosive = True
            elif self.inventory.equipped['artifact'].name == "Fire Stone":
                bullet_effect = "burn"
            elif self.inventory.equipped['artifact'].name == "Frost Amulet":
                bullet_effect = "freeze"

        # Умный генератор пуль с учетом особенностей оружия
        def create_bullet(angle, speed_mult=1.0):
            b = Bullet(self.x + self.size // 2, self.y + self.size // 2, angle, damage, is_explosive, bullet_effect)
            if weapon.name == "Flamethrower":
                b.color = ORANGE
                b.size = random.randint(8, 14)
                b.speed = 8 * speed_mult
            elif weapon.name == "Railgun":
                b.color = CYAN
                b.size = 6
                b.speed = 18 * speed_mult
            elif weapon.name == "Crossbow":
                b.color = BROWN
                b.size = 4
                b.speed = 12 * speed_mult
            elif weapon.name == "Sniper Rifle":
                b.size = 6
                b.speed = 20 * speed_mult
            elif weapon.name in ["Rocket Launcher", "Grenade Launcher"]:
                b.speed = 7 * speed_mult
            return b

        if weapon.name == "Shotgun":
            for _ in range(5):
                spread = random.uniform(-0.3, 0.3)
                dx = target_x - (self.x + self.size // 2)
                dy = target_y - (self.y + self.size // 2)
                angle = math.atan2(dy, dx) + spread
                self.bullets.append(create_bullet(angle, random.uniform(0.8, 1.2)))
        elif weapon.name == "Railgun":
            spread = random.uniform(-0.1, 0.1)
            dx = target_x - (self.x + self.size // 2)
            dy = target_y - (self.y + self.size // 2)
            angle = math.atan2(dy, dx) + spread
            self.bullets.append(create_bullet(angle))
        else:
            dx = target_x - (self.x + self.size // 2)
            dy = target_y - (self.y + self.size // 2)
            angle = math.atan2(dy, dx)
            spread = random.uniform(-0.1, 0.1) if weapon.name == "Flamethrower" else 0
            self.bullets.append(create_bullet(angle + spread))

    def move(self, dx, dy, walls):
        if getattr(self, 'is_dying', False): return
        if self.is_dashing:
            dx = self.dash_dx
            dy = self.dash_dy
            current_speed = self.total_speed * self.dash_speed_multiplier
        else:
            if dx != 0 and dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length
            current_speed = self.total_speed

        new_x = self.x + dx * current_speed
        new_y = self.y + dy * current_speed

        can_move = True
        wall_to_push = None

        for wall in walls:
            if (
                    new_x + self.size > wall.x and new_x < wall.x + wall.size and new_y + self.size > wall.y and new_y < wall.y + wall.size):
                if wall.is_obstacle and wall.movable:
                    wall_to_push = wall
                else:
                    can_move = False
                break

        if wall_to_push:
            if wall_to_push.try_move(dx * self.speed, dy * self.speed, walls):
                self.x = new_x
                self.y = new_y
        elif can_move:
            self.x = new_x
            self.y = new_y

    def record_math_result(self, problem, is_correct):
        self.stats.add_problem_result(problem, is_correct)


class Bullet:
    def __init__(self, x, y, angle, damage, is_explosive=False, effect=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.size = 8 if is_explosive else 5
        self.damage = damage
        self.color = ORANGE if is_explosive else WHITE
        self.is_explosive = is_explosive
        self.effect = effect
        self.is_wave = False
        self.wave_frames = wave_frames if 'wave_frames' in globals() else []
        self.current_frame = 0
        self.last_anim = pygame.time.get_ticks()

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, screen):
        if self.is_wave and self.wave_frames:
            t = pygame.time.get_ticks()
            if t - self.last_anim > 50:
                self.current_frame = (self.current_frame + 1) % len(self.wave_frames)
                self.last_anim = t
            img = self.wave_frames[self.current_frame]
            img = pygame.transform.rotate(img, math.degrees(-self.angle))
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class DamageText:
    def __init__(self, x, y, damage, color=WHITE):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.font = pygame.font.Font('PixelizerBold.ttf', 20)
        self.alpha = 255
        self.speed_y = 1.5
        self.lifetime = 60

    def update(self):
        self.y -= self.speed_y
        self.lifetime -= 1
        if self.lifetime < 20:
            self.alpha = max(0, int((self.lifetime / 20) * 255))

    def draw(self, screen):
        if self.alpha > 0:
            text_surface = self.font.render(f"-{self.damage}", True, self.color)
            text_surface.set_alpha(self.alpha)
            screen.blit(text_surface, (self.x - text_surface.get_width() // 2, self.y))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.size = random.uniform(4, 10)
        self.lifetime = random.randint(20, 40)
        self.max_lifetime = self.lifetime

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.85 
        self.dy *= 0.85
        self.size *= 0.92
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            s = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            s.fill((self.color[0], self.color[1], self.color[2], alpha))
            screen.blit(s, (int(self.x), int(self.y)))

class Shell:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        spread = random.uniform(-0.5, 0.5)
        speed = random.uniform(3, 6)
        self.dx = math.cos(angle + spread) * speed
        self.dy = math.sin(angle + spread) * speed
        self.lifetime = 120
        self.color = (255, 215, 0)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-20, 20)

    def update(self):
        if self.lifetime > 60:
            self.x += self.dx
            self.y += self.dy
            self.dx *= 0.85
            self.dy *= 0.85
            self.rotation += self.rot_speed
            self.rot_speed *= 0.85
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            s = pygame.Surface((6, 3), pygame.SRCALPHA)
            alpha = 255 if self.lifetime > 30 else int((self.lifetime / 30) * 255)
            s.fill((self.color[0], self.color[1], self.color[2], alpha))
            s = pygame.transform.rotate(s, self.rotation)
            screen.blit(s, (int(self.x), int(self.y)))

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frames = explosion_frames
        self.current_frame = 0
        self.anim_speed = 30
        self.last_update = pygame.time.get_ticks()
        self.is_finished = False

    def update(self, current_time):
        if self.frames and current_time - self.last_update > self.anim_speed:
            self.current_frame += 1
            self.last_update = current_time
            if self.current_frame >= len(self.frames):
                self.is_finished = True

    def draw(self, screen):
        if not self.is_finished and self.frames:
            frame = self.frames[self.current_frame]
            rect = frame.get_rect(center=(self.x, self.y))
            screen.blit(frame, rect)


class Enemy:
    def __init__(self, x, y, enemy_type="normal", math_value=None, is_correct=False, success_rate=50):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.math_value = math_value
        self.is_correct = is_correct

        if enemy_type == "tank":
            self.size = 60
            self.speed = 0.5
            self.health = 50
            self.color = (139, 0, 0)
        elif enemy_type == "scout":
            self.size = 40
            self.speed = 2
            self.health = 20
            self.color = (255, 165, 0)
        elif enemy_type == "basic" or enemy_type == "math":
            self.size = 70
            self.speed = 1
            self.health = 100
            self.color = RED
        elif enemy_type == "sniper":
            self.size = 60
            self.speed = 1.5
            self.health = 50
            self.color = ORANGE
        elif enemy_type == "ghost":
            self.size = 65
            self.speed = 0.8
            self.health = 70
            self.color = PURPLE
        else:
            self.size = 20
            self.speed = 1
            self.health = 30
            self.color = RED

        self.max_health = self.health
        self.bullets = []

        # переменные для новых врагов
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_cooldown = 2000 
        self.ghost_timer = pygame.time.get_ticks()
        self.is_ghost = False
        self.hit_timer = 0

        # Эффекты статуса
        self.base_speed = self.speed
        self.burn_time = 0
        self.last_burn_damage = 0
        self.freeze_time = 0

        # Хитбокс для столкновений
        self.hitbox_size = int(self.size * 0.45)

        # Параметры анимации
        self.direction = 'down'
        self.anim_frame = 0
        self.last_anim_update = pygame.time.get_ticks()
        self.anim_speed = 150

        # Динамический размер награды с врагов
        base_money = random.randint(5, 15)
        if success_rate >= 80:
            self.money = int(base_money * 1.5)  # На 50% больше монет
        elif success_rate <= 40:
            self.money = int(base_money * 0.7)  # На 30% меньше монет
        else:
            self.money = base_money

    def draw(self, screen, hint_mode=False):
        current_time = pygame.time.get_ticks()

        # Логика мерцания для призрака
        if self.enemy_type == "ghost":
            if current_time - self.ghost_timer > 3000:
                self.is_ghost = not self.is_ghost
                self.ghost_timer = current_time

        # Отрисовка тени под врагом (если он не в невидимости)
        if not (self.enemy_type == "ghost" and self.is_ghost):
            shadow_rect = pygame.Rect(0, 0, self.size * 0.7, self.size * 0.3)
            shadow_rect.center = (self.x + self.size // 2, self.y + self.size - 5)
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, 120), shadow_surface.get_rect())
            screen.blit(shadow_surface, shadow_rect.topleft)

        # Отрисовка анимированного спрайта врага
        if 'enemy_frames' in globals() and enemy_frames:
            if current_time - self.last_anim_update > self.anim_speed:
                self.anim_frame = (self.anim_frame + 1) % 4
                self.last_anim_update = current_time

            frame_to_draw = enemy_frames[self.direction][self.anim_frame].copy()
            frame_to_draw = pygame.transform.scale(frame_to_draw, (self.size, self.size))

            if self.enemy_type == "ghost" and self.is_ghost:
                frame_to_draw.set_alpha(80)

            # Окрашивание от эффектов
            if self.freeze_time > 0:
                frame_to_draw.fill((0, 100, 200), special_flags=pygame.BLEND_RGB_ADD)
            if self.burn_time > 0:
                frame_to_draw.fill((150, 50, 0), special_flags=pygame.BLEND_RGB_ADD)

            # Вспышка при попадании (Hit Flash)
            if current_time - getattr(self, 'hit_timer', 0) < 100:
                frame_to_draw.fill((200, 200, 200), special_flags=pygame.BLEND_RGB_ADD)

            screen.blit(frame_to_draw, (self.x, self.y))
        else:
            if self.enemy_type == "ghost" and self.is_ghost:
                s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                s.fill((self.color[0], self.color[1], self.color[2], 80))
                screen.blit(s, (self.x, self.y))
            else:
                draw_color = self.color
                if self.freeze_time > 0:
                    draw_color = (0, 150, 255)
                elif self.burn_time > 0:
                    draw_color = ORANGE

                if current_time - getattr(self, 'hit_timer', 0) < 100:
                    pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))
                else:
                    pygame.draw.rect(screen, draw_color, (self.x, self.y, self.size, self.size))

        # Полоска здоровья
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y + self.size + 5, self.size, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y + self.size + 5, self.size * health_ratio, 5))

        # Отрисовка парящего экрана над врагом
        if self.math_value is not None:
            monitor_width = int(self.size * 0.6)
            monitor_height = int(self.size * 0.35)
            monitor_x = self.x + (self.size - monitor_width) // 2
            monitor_y = self.y - monitor_height - 5  # Позиция над спрайтом

            # Полупрозрачная подложка для экрана
            s = pygame.Surface((monitor_width, monitor_height), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, 200), (0, 0, monitor_width, monitor_height), border_radius=5)
            screen.blit(s, (monitor_x, monitor_y))

            # рамка
            frame_color = GREEN if (hint_mode and getattr(self, 'is_correct', False)) else CYAN
            pygame.draw.rect(screen, frame_color, (monitor_x, monitor_y, monitor_width, monitor_height), 2,
                             border_radius=5)

            # Крупное число
            font_size = int(monitor_height * 0.9)
            font = pygame.font.Font('PixelizerBold.ttf', font_size)
            text_color = GREEN if (hint_mode and getattr(self, 'is_correct', False)) else WHITE
            value_text = font.render(str(self.math_value), True, text_color)
            text_rect = value_text.get_rect(center=(monitor_x + monitor_width // 2, monitor_y + monitor_height // 2))
            screen.blit(value_text, text_rect)

    def move_towards(self, target, walls, enemies):
        current_time = pygame.time.get_ticks()

        # Обновление эффектов статуса
        if self.freeze_time > 0:
            self.speed = self.base_speed * 0.4  # Замедление на 60%
            self.freeze_time -= 16
        else:
            self.speed = self.base_speed

        if self.burn_time > 0:
            self.burn_time -= 16
            if current_time - self.last_burn_damage > 500:  # Урон раз в 0.5 сек
                self.health -= 2
                self.last_burn_damage = current_time
                if hasattr(target, 'game'):
                    target.game.current_room.damage_texts.append(DamageText(self.x + self.size // 2, self.y, 2, ORANGE))
                    target.game.current_room.particles.append(
                        Particle(self.x + self.size // 2, self.y + self.size // 2, ORANGE))

        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist != 0:
            # Логика поведения для разных врагов
            is_moving = True

            if self.enemy_type == "sniper":
                if dist < 200:
                    dx = -dx 
                    dy = -dy
                elif dist > 350:
                    pass
                else:
                    is_moving = False  # Останавливается, чтобы стрелять

            if is_moving:
                def check_move(test_dx, test_dy):
                    offset = (self.size - getattr(self, 'hitbox_size', self.size)) / 2
                    hit_x = self.x + test_dx + offset
                    hit_y = self.y + test_dy + offset
                    hit_s = getattr(self, 'hitbox_size', self.size)

                    for wall in walls:
                        if hit_x + hit_s > wall.x and hit_x < wall.x + wall.size and hit_y + hit_s > wall.y and hit_y < wall.y + wall.size:
                            return False
                    for enemy in enemies:
                        if enemy != self:
                            e_offset = (enemy.size - getattr(enemy, 'hitbox_size', enemy.size)) / 2
                            e_hit_x = enemy.x + e_offset
                            e_hit_y = enemy.y + e_offset
                            e_hit_s = getattr(enemy, 'hitbox_size', enemy.size)
                            if hit_x + hit_s > e_hit_x and hit_x < e_hit_x + e_hit_s and hit_y + hit_s > e_hit_y and hit_y < e_hit_y + e_hit_s:
                                return False
                    return True

                dx_step = dx / dist * self.speed
                dy_step = dy / dist * self.speed

                # Улучшенное скольжение с обходом (AABB sliding)
                moved = False
                if check_move(dx_step, dy_step):
                    self.x += dx_step
                    self.y += dy_step
                    moved = True
                else:
                    moved_x = False
                    moved_y = False
                    if abs(dx_step) > 0.1 and check_move(dx_step, 0):
                        self.x += dx_step
                        moved_x = True
                    if abs(dy_step) > 0.1 and check_move(0, dy_step):
                        self.y += dy_step
                        moved_y = True

                    if moved_x or moved_y:
                        moved = True

               
                if not moved:
                    if abs(dx) > abs(dy):
                        slide_dir = self.speed if dy > 0 else -self.speed
                        if check_move(0, slide_dir):
                            self.y += slide_dir
                        elif check_move(0, -slide_dir):
                            self.y -= slide_dir
                    else:
                        slide_dir = self.speed if dx > 0 else -self.speed
                        if check_move(slide_dir, 0):
                            self.x += slide_dir
                        elif check_move(-slide_dir, 0):
                            self.x -= slide_dir

                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'

    def apply_knockback(self, angle, force, walls, enemies):
        if getattr(self, 'enemy_type', '') == "boss":
            force *= 0.15  # Босс отбрасывается гораздо слабее

        test_dx = math.cos(angle) * force
        test_dy = math.sin(angle) * force

        offset = (self.size - getattr(self, 'hitbox_size', self.size)) / 2
        hit_x = self.x + test_dx + offset
        hit_y = self.y + test_dy + offset
        hit_s = getattr(self, 'hitbox_size', self.size)

        can_move = True

        for wall in walls:
            if hit_x + hit_s > wall.x and hit_x < wall.x + wall.size and hit_y + hit_s > wall.y and hit_y < wall.y + wall.size:
                can_move = False
                break

        if can_move:
            for other_enemy in enemies:
                if other_enemy != self:
                    e_offset = (other_enemy.size - getattr(other_enemy, 'hitbox_size', other_enemy.size)) / 2
                    e_hit_x = other_enemy.x + e_offset
                    e_hit_y = other_enemy.y + e_offset
                    e_hit_s = getattr(other_enemy, 'hitbox_size', other_enemy.size)
                    if hit_x + hit_s > e_hit_x and hit_x < e_hit_x + e_hit_s and hit_y + hit_s > e_hit_y and hit_y < e_hit_y + e_hit_s:
                        can_move = False
                        break

        if can_move:
            self.x += test_dx
            self.y += test_dy


class Boss(Enemy):
    def __init__(self, x, y, success_rate=50):
        super().__init__(x, y, "boss", None, False, success_rate)
        self.size = 120
        self.health = 2000
        self.max_health = 2000
        self.speed = 1.0
        self.phase = 1
        self.state = 'spawning'
        self.spawn_y = self.y + 150
        self.invulnerable = True
        self.shield_active = False
        self.shield_timer = 0
        self.shield_charging = False
        self.shield_charge_timer = 0

        self.is_shooting_barrage = False
        self.barrage_timer = 0
        self.last_barrage_shot = 0

        self.boss_anim_state = "idle"
        self.attack_anim_timer = 0

        self.attack_timer = pygame.time.get_ticks()
        self.cones = []
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_dx = 0
        self.dash_dy = 0
        self.dash_warning = False
        self.dash_warning_timer = 0
        self.dash_target_angle = 0
        self.death_timer = 0
        self.attack_anim_angle = 0

        if 'boss_spawn_snd' in globals() and boss_spawn_snd:
            boss_spawn_snd.play()
        if 'boss_music' in globals() and boss_music:
            level_music.stop()
            boss_music.play(-1)

        self.money = 500

    def draw(self, screen, hint_mode=False):
        current_time = pygame.time.get_ticks()
        draw_x, draw_y = self.x, self.y

        if self.state == 'spawning':
            draw_x += random.randint(-4, 4)
            draw_y = self.spawn_y
            self.spawn_y -= 1.5
            if self.spawn_y <= self.y:
                self.state = 'active'
                self.invulnerable = False
                self.y = self.spawn_y

        # Телеграф для волн
        for cone in self.cones:
            if current_time - cone['time'] < 1500:
                points = [
                    (self.x + self.size // 2, self.y + self.size // 2),
                    (self.x + self.size // 2 + math.cos(cone['angle'] - 0.25) * 800,
                     self.y + self.size // 2 + math.sin(cone['angle'] - 0.25) * 800),
                    (self.x + self.size // 2 + math.cos(cone['angle'] + 0.25) * 800,
                     self.y + self.size // 2 + math.sin(cone['angle'] + 0.25) * 800)
                ]
                s = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                pygame.draw.polygon(s, (255, 0, 0, 100), points)
                screen.blit(s, (0, 0))

        # Анимация и отрисовка босса
        if 'boss_frames' in globals() and boss_frames:
            if current_time - self.last_anim_update > self.anim_speed:
                self.anim_frame = (self.anim_frame + 1) % 4
                self.last_anim_update = current_time
            img = boss_frames[self.direction][self.anim_frame].copy()
            img = pygame.transform.scale(img, (self.size, self.size))
        else:
            img = pygame.Surface((self.size, self.size))
            img.fill((100, 0, 0))

        # Оттенки и мелкая тряска
        if getattr(self, 'is_dashing', False):
            img.fill((255, 50, 50), special_flags=pygame.BLEND_RGB_MULT)
        elif getattr(self, 'dash_warning', False):
            img.fill((255, 180, 180), special_flags=pygame.BLEND_RGB_ADD)
        elif self.phase == 2:
            img.fill((200, 150, 100), special_flags=pygame.BLEND_RGB_MULT)
        elif self.phase == 3:
            img.fill((150, 50, 50), special_flags=pygame.BLEND_RGB_MULT)
            draw_x += random.randint(-2, 2)
            draw_y += random.randint(-2, 2)

        if self.boss_anim_state == "attack":
            draw_x += random.randint(-5, 5)
            draw_y += random.randint(-5, 5)
            if current_time - self.attack_anim_timer > 500:
                self.boss_anim_state = "idle"

        if self.state == 'dying':
            draw_x += random.randint(-10, 10)
            draw_y += random.randint(-10, 10)
            img.fill((current_time % 255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)

        if getattr(self, 'dash_warning', False):
            # Линия прицеливания
            end_x = self.x + self.size // 2 + math.cos(self.dash_target_angle) * 1000
            end_y = self.y + self.size // 2 + math.sin(self.dash_target_angle) * 1000
            pygame.draw.line(screen, (255, 50, 50), (self.x + self.size // 2, self.y + self.size // 2),
                                 (end_x, end_y), 4)

        screen.blit(img, (draw_x, draw_y))

        # Отрисовка взмаха (атаки) поверх и рядом с боссом
        if self.boss_anim_state == "attack" and 'boss_attack_frames' in globals() and boss_attack_frames:
            frame_idx = ((current_time - self.attack_anim_timer) // max(1,
                                                                                500 // len(boss_attack_frames))) % len(
                boss_attack_frames)
            slash_img = boss_attack_frames[frame_idx]
            angle = getattr(self, 'attack_anim_angle', 0)

            slash_img_rot = pygame.transform.rotate(slash_img, math.degrees(-angle))

            offset_x = math.cos(angle) * (self.size * 0.6)
            offset_y = math.sin(angle) * (self.size * 0.6)
            slash_rect = slash_img_rot.get_rect(
                center=(draw_x + self.size // 2 + offset_x, draw_y + self.size // 2 + offset_y))
            screen.blit(slash_img_rot, slash_rect.topleft)

        # Предупреждение о щите и сам щит
        if self.shield_charging:
            pygame.draw.circle(screen, GOLD, (int(draw_x + self.size // 2), int(draw_y + self.size // 2)),
                               self.size // 2 + 15, 2)
            if (current_time // 100) % 2 == 0:
                pygame.draw.circle(screen, WHITE, (int(draw_x + self.size // 2), int(draw_y + self.size // 2)),
                                   self.size // 2 + 18, 2)
        elif self.shield_active:
            pygame.draw.circle(screen, CYAN, (int(draw_x + self.size // 2), int(draw_y + self.size // 2)),
                               self.size // 2 + 15, 4)

        if self.state != 'spawning':
            health_ratio = max(0, self.health / self.max_health)
            pygame.draw.rect(screen, RED, (self.x, self.y - 15, self.size, 8))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 15, self.size * health_ratio, 8))

    def move_towards(self, target, walls, enemies):
        current_time = pygame.time.get_ticks()
        if self.state == 'spawning':
            if hasattr(target, 'game'): target.game.screen_shake = 2
            return

        if self.state == 'dying':
            if hasattr(target, 'game'):
                target.game.screen_shake = 12
                # Серия хаотичных взрывов по всему боссу
                if current_time % 10 == 0:
                    target.game.current_room.explosions.append(
                        Explosion(self.x + random.randint(0, self.size), self.y + random.randint(0, self.size)))

            if current_time - self.death_timer > 3000:
                self.health = 0
            return

        if self.state == 'waiting_math':
            return

        if self.phase == 1 and self.health <= self.max_health * 0.66:
            self.start_phase(2, target.game)
            return
        elif self.phase == 2 and self.health <= self.max_health * 0.33:
            self.start_phase(3, target.game)
            return

        if getattr(self, 'dash_warning', False):
            if current_time - self.dash_warning_timer > 300:
                self.dash_warning = False
                self.is_dashing = True
                self.dash_timer = current_time
                self.dash_dx = math.cos(self.dash_target_angle) * 22
                self.dash_dy = math.sin(self.dash_target_angle) * 22
                if hasattr(target, 'game'): target.game.screen_shake = 8
            return 

        if self.shield_charging and current_time - self.shield_charge_timer > 500:
            self.shield_charging = False
            self.shield_active = True
            self.shield_timer = current_time

        if self.is_shooting_barrage:
            if current_time - self.barrage_timer > 1500:
                self.is_shooting_barrage = False
            elif current_time - self.last_barrage_shot > 150:
                self.last_barrage_shot = current_time
                dirs = 3 if self.phase == 1 else 5
                base = random.uniform(0, math.pi)
                for i in range(dirs):
                    angle = base + i * (2 * math.pi / dirs)
                    b = Bullet(self.x + self.size // 2, self.y + self.size // 2, angle, 2)
                    b.color = PURPLE
                    b.speed = 5
                    b.size = 8
                    target.game.current_room.enemy_bullets.append(b)

        # Уменьшенный хитбокс для стен, чтобы босс мог проходить между ящиками
        hitbox_s = 70
        offset = (self.size - hitbox_s) / 2

        # Обработка Яростного Рывка (Dash) для 3 фазы
        if getattr(self, 'is_dashing', False):
            if current_time - self.dash_timer < 400:
                new_x = self.x + self.dash_dx
                new_y = self.y + self.dash_dy

                can_dash = True
                hit_x = new_x + offset
                hit_y = new_y + offset
                for wall in walls:
                    if hit_x + hitbox_s > wall.x and hit_x < wall.x + wall.size and hit_y + hitbox_s > wall.y and hit_y < wall.y + wall.size:
                        can_dash = False
                        break
                if can_dash:
                    self.x = new_x
                    self.y = new_y

                self.x = max(40 - offset, min(self.x, WINDOW_SIZE[0] - 40 - self.size + offset))
                self.y = max(40 - offset, min(self.y, WINDOW_SIZE[1] - 40 - self.size + offset))

                dist_to_player = math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
                if dist_to_player < self.size // 2 + target.size // 2 and not getattr(target, 'is_cloaked', False) and not getattr(target, 'godmode', False) and not getattr(target, 'is_dying', False):
                    if current_time - getattr(target, 'last_damage_time', 0) > 1000:
                        target.health -= 2
                        target.last_damage_time = current_time
                        if hasattr(target, 'game'): target.game.screen_shake = 10
                        if 'hurt_sound' in globals() and hurt_sound: hurt_sound.play()

                if current_time % 2 == 0 and hasattr(target, 'game'):
                    target.game.current_room.particles.append(
                        Particle(self.x + self.size // 2, self.y + self.size // 2, RED))
                return
            else:
                self.is_dashing = False

        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        target_dx, target_dy = 0, 0
        if self.phase == 1:
            self.speed = 1.0
            if dist > 0:
                target_dx = (dx / dist) * self.speed
                target_dy = (dy / dist) * self.speed
        elif self.phase >= 2:
            self.speed = 1.8 if self.phase == 2 else 2.5
            if dist > 0:
                target_dx = (dx / dist) * self.speed
                target_dy = (dy / dist) * self.speed

        def check_boss_move(test_dx, test_dy):
            hit_x = self.x + test_dx + offset
            hit_y = self.y + test_dy + offset
            for wall in walls:
                if hit_x + hitbox_s > wall.x and hit_x < wall.x + wall.size and hit_y + hitbox_s > wall.y and hit_y < wall.y + wall.size:
                    return False
            return True

        if target_dx != 0 or target_dy != 0:
            if check_boss_move(target_dx, target_dy):
                self.x += target_dx
                self.y += target_dy
            else:
                if abs(target_dx) > 0.1 and check_boss_move(target_dx, 0):
                    self.x += target_dx
                if abs(target_dy) > 0.1 and check_boss_move(0, target_dy):
                    self.y += target_dy

        self.x = max(40 - offset, min(self.x, WINDOW_SIZE[0] - 40 - self.size + offset))
        self.y = max(40 - offset, min(self.y, WINDOW_SIZE[1] - 40 - self.size + offset))

        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'

        if current_time - self.attack_timer > 2500:
            self.attack_timer = current_time
            self.attack(target)

        # Выпуск волн с задержкой 0.5с друг от друга
        for cone in self.cones[:]:
            if current_time - cone['time'] > 1500:
                if 'waves_spawned' not in cone:
                    cone['waves_spawned'] = 0
                    cone['last_wave_time'] = 0

                if current_time - cone['last_wave_time'] >= 500:
                    self.boss_anim_state = "attack"
                    self.attack_anim_timer = current_time
                    self.attack_anim_angle = cone['angle'] 
                    if 'boss_attack_snd' in globals() and boss_attack_snd: boss_attack_snd.play()

                    w = Bullet(self.x + self.size // 2, self.y + self.size // 2, cone['angle'], 2)
                    w.is_wave = True
                    w.speed = 15
                    w.size = 20
                    target.game.current_room.enemy_bullets.append(w)
                    if 'wave_attack_snd' in globals() and wave_attack_snd: wave_attack_snd.play()

                    cone['waves_spawned'] += 1
                    cone['last_wave_time'] = current_time

                    if cone['waves_spawned'] >= 3:
                        self.cones.remove(cone)

        # Щит длится 1 секунду
        if self.shield_active and not self.state == 'waiting_math' and current_time - self.shield_timer > 1000:
            self.shield_active = False

    def attack(self, target):
        room = target.game.current_room
        if self.phase == 3:
            atk = random.choice(['shield', 'spiral', 'telegraph', 'dash'])
        elif self.phase == 2:
            atk = random.choice(['shield', 'shoot', 'telegraph'])
        else:
            atk = random.choice(['shield', 'shoot'])

        if atk == 'shield':
            self.shield_charging = True
            self.shield_charge_timer = pygame.time.get_ticks()
        elif atk == 'shoot':
            self.is_shooting_barrage = True
            self.barrage_timer = pygame.time.get_ticks()
            self.last_barrage_shot = 0
        elif atk == 'spiral':
            for i in range(16):
                angle = i * (2 * math.pi / 16)
                b = Bullet(self.x + self.size // 2, self.y + self.size // 2, angle, 2)
                b.color = RED
                b.speed = 6
                b.size = 10
                room.enemy_bullets.append(b)
        elif atk == 'telegraph':
            angle = math.atan2(target.y - self.y, target.x - self.x)
            self.cones.append({'angle': angle, 'time': pygame.time.get_ticks()})
            if self.phase == 3:
                self.cones.append({'angle': angle + 0.8, 'time': pygame.time.get_ticks()})
                self.cones.append({'angle': angle - 0.8, 'time': pygame.time.get_ticks()})
        elif atk == 'dash':
            self.dash_warning = True
            self.dash_warning_timer = pygame.time.get_ticks()
            self.dash_target_angle = math.atan2(target.y - self.y, target.x - self.x)

    def start_phase(self, phase, game):
        self.phase = phase
        self.state = 'waiting_math'
        self.invulnerable = True
        self.shield_active = True
        if 'boss_phase_snd' in globals() and boss_phase_snd:
            boss_phase_snd.play()

        room = game.current_room
        floor_bonus = getattr(game, 'floor', 1) - 1
        room.math_problem = room.generator.generate_problem(room.difficulty + phase + floor_bonus)

        if 'spawn_enemies_snd' in globals() and spawn_enemies_snd:
            spawn_enemies_snd.play()

        num = 3 + phase
        for i in range(num):
            role = "correct" if i == 0 else "wrong"
            room.add_enemy("math", role)


class Chest:
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.size = 40
        self.state = "closed"
        self.anim_frame = 0
        self.last_anim_time = 0

        available_artifacts = []
        for a in game.artifacts_pool:
            has_artifact = False
            if game.player.inventory.equipped.get('artifact') and game.player.inventory.equipped[
                'artifact'].name == a.name:
                has_artifact = True
            for item in game.player.inventory.items:
                if hasattr(item, 'name') and item.name == a.name:
                    has_artifact = True
            if not has_artifact:
                available_artifacts.append(a)

        pool = available_artifacts + game.weapons_pool
        self.item = random.choice(pool) if pool else None
        self.in_range = False
    def draw(self, screen):
        current_time = pygame.time.get_ticks()

        if self.state == "closed":
            if 'chest_img' in globals() and chest_img:
                screen.blit(chest_img, (self.x, self.y))
            else:
                pygame.draw.rect(screen, GOLD, (self.x, self.y, self.size, self.size))

            if self.in_range:
                font = pygame.font.Font('PixelizerBold.ttf', 24)
                text = font.render("Press E to open", True, WHITE)
                bg_rect = pygame.Rect(self.x - 30, self.y - 25, text.get_width() + 10, text.get_height() + 5)
                pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect, border_radius=5)
                screen.blit(text, (self.x - 25, self.y - 22))

        elif self.state == "opening":
            if 'chest_frames' in globals() and chest_frames:
                if current_time - self.last_anim_time > 100:  # 100ms per frame
                    self.anim_frame += 1
                    self.last_anim_time = current_time
                    if self.anim_frame >= len(chest_frames):
                        self.state = "opened"
                        self.anim_frame = len(chest_frames) - 1

                if self.anim_frame < len(chest_frames):
                    screen.blit(chest_frames[self.anim_frame], (self.x, self.y))
            else:
                self.state = "opened"

        elif self.state == "opened":
            if 'chest_opened_img' in globals() and chest_opened_img:
                screen.blit(chest_opened_img, (self.x, self.y))
            else:
                pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.size, self.size))

    def check_interaction(self, player):
        self.in_range = (abs(player.x + player.size / 2 - (self.x + self.size / 2)) < 60 and abs(
            player.y + player.size / 2 - (self.y + self.size / 2)) < 60)
        return self.in_range

    def open(self):
        if self.state == "closed":
            self.state = "opening"
            self.last_anim_time = pygame.time.get_ticks()
            if 'chest_open_sound' in globals() and chest_open_sound:
                chest_open_sound.play()


class Artifact:
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect
        filename = name.lower().replace(' ', '_') + '.png'
        try:
            self.icon = pygame.image.load(f'tileset/{filename}').convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (48, 48))
        except Exception:
            self.icon = pygame.Surface((48, 48))
            self.icon.fill((100, 100, 100))
            pygame.draw.rect(self.icon, WHITE, (0, 0, 48, 48), 1)


class Weapon:
    def __init__(self, name, damage, is_automatic, fire_rate):
        self.name = name
        self.damage = damage
        self.is_automatic = is_automatic
        self.fire_rate = fire_rate
        self.last_shot = 0

        filename = name.lower().replace(' ', '_') + '.png'
        try:
            self.icon = pygame.image.load(f'tileset/{filename}').convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (48, 48))
        except Exception:
            self.icon = pygame.Surface((48, 48))
            self.icon.fill((100, 100, 100))
            pygame.draw.rect(self.icon, WHITE, (0, 0, 48, 48), 1)

        self.ammo_capacity = {
            "Pistol": 10,
            "Shotgun": 2,
            "Sniper Rifle": 5,
            "Rocket Launcher": 1,
            "Automatic Rifle": 30,
            "Machine Gun": 50,
            "Railgun": 75,
            "Flamethrower": 125
        }.get(name, 30)

        self.current_ammo = self.ammo_capacity
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_duration = 1000
        self.current_reload_duration = 1000

        self.reload_frames = []
        try:
            sheet = pygame.image.load('tileset/reload_sheet.png').convert_alpha()
            frame_size = sheet.get_height()
            frames_count = sheet.get_width() // frame_size

            for i in range(frames_count):
                rect = pygame.Rect(i * frame_size, 0, frame_size, frame_size)
                frame = sheet.subsurface(rect)
                self.reload_frames.append(pygame.transform.scale(frame, (50, 50)))
        except Exception as e:
            print(f"Ошибка загрузки reload_sheet.png: {e}")
            dummy = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.reload_frames = [dummy]
        self.current_frame = 0

    def can_shoot(self, current_time):
        return (current_time - self.last_shot >= self.fire_rate and not self.is_reloading and self.current_ammo > 0)

    def start_reload(self, current_time, reload_multiplier=1.0):
        global reload_sound
        if not self.is_reloading and self.current_ammo < self.ammo_capacity:
            self.is_reloading = True
            self.reload_start_time = current_time
            self.current_reload_duration = self.reload_duration * reload_multiplier
            self.current_frame = 0
            if 'reload_sound' in globals() and reload_sound:
                reload_sound.play()

    def update_reload(self, current_time):
        if self.is_reloading:
            time_elapsed = current_time - self.reload_start_time
            if time_elapsed >= self.current_reload_duration:
                self.is_reloading = False
                self.current_ammo = self.ammo_capacity
            else:
                frame_time = self.current_reload_duration / len(self.reload_frames)
                self.current_frame = int(time_elapsed / frame_time) % len(self.reload_frames)


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font('PixelizerBold.ttf', 36)
        self.active = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        r = min(255, self.color[0] + (30 if is_hovered else 0))
        g = min(255, self.color[1] + (30 if is_hovered else 0))
        b = min(255, self.color[2] + (30 if is_hovered else 0))
        current_color = (r, g, b)

        pygame.draw.rect(screen, (20, 20, 20), (self.rect.x + 4, self.rect.y + 6, self.rect.width, self.rect.height),
                         border_radius=8)
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE if is_hovered else (200, 200, 200), self.rect, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, WHITE)
        # Эффект нажатия/наведения на текст
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - (2 if is_hovered else 0)))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            if 'select_sound' in globals() and select_sound:
                select_sound.play()
            return True
        return False


class Game:
    def __init__(self):
        self.show_menu = True
        self.show_settings = False
        self.notifications = []
        self.rooms_cleared = 0
        self.last_merchant_room = -3
        self.last_treasury_room = -2
        self.active_menu = None
        self.console_active = False
        self.analysis_scroll_offset = 0
        self.analysis_content_height = 0
        self.console_text = ""
        self.console_font = pygame.font.Font('PixelizerBold.ttf', 24)
        self.main_menu_button_positions = {
            'play': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 50),
            'settings': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 20),
            'save': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 90),
            'load': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 160),
            'exit': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 230)
        }
        self.sound_volume = 1.0
        self.music_volume = 0.5
        pygame.mixer.music.set_volume(self.music_volume)

        self.play_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 140, 200, 50, "Играть",
                                  (50, 100, 200))
        self.meta_shop_button = Button(WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 - 80, 260, 50, "Мета-Магазин",
                                       (200, 150, 50))
        self.settings_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 20, 200, 50, "Настройки",
                                      (210, 30, 150))
        self.info_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 40, 200, 50, "Управление",
                                  (50, 150, 200))
        self.save_button = Button(WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 100, 260, 50, "Сохранить игру",
                                  (210, 30, 150))
        self.load_button = Button(WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 160, 260, 50, "Загрузить игру",
                                  (210, 30, 150))
        self.exit_button = Button(WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 220, 260, 50, "Выход из игры",
                                  (50, 50, 150))

        self.restart_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 50, 200, 50, "Restart",
                                     (210, 30, 150))
        self.to_menu_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 50, 200, 50, "В меню",
                                     (110, 30, 150))
        self.analysis_button = Button(WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 10, 260, 50, "Анализ знаний",
                                      (50, 50, 150))
        self.fullscreen_button = Button(WINDOW_SIZE[0] // 2 - 125, WINDOW_SIZE[1] // 2 + 200, 250, 50, "Полный экран",
                                        (50, 150, 200))
        self.meta_back_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] - 80, 200, 50, "Назад", (150, 50, 50))
        self.info_back_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] - 80, 200, 50, "Назад", (150, 50, 50))

        self.hard_reset_button = Button(WINDOW_SIZE[0] // 2 - 150, WINDOW_SIZE[1] // 2 + 260, 300, 40,
                                        "СБРОС ПРОГРЕССА", (200, 50, 50))
        self.confirming_reset = False
        self.confirm_reset_timer = 0

        self.main_menu_button_positions = {
            'play': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 140),
            'meta': (WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 - 80),
            'settings': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 - 20),
            'info': (WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 40),
            'save': (WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 100),
            'load': (WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 160),
            'exit': (WINDOW_SIZE[0] // 2 - 130, WINDOW_SIZE[1] // 2 + 220)
        }

        loaded_settings = load_settings()
        self.sound_volume = loaded_settings.get('sound_volume', 1.0)
        self.music_volume = loaded_settings.get('music_volume', 0.5)
        self.shake_intensity = loaded_settings.get('shake_intensity', 1.0)
        self.show_damage_numbers = loaded_settings.get('show_damage_numbers', True)
        self.knowledge_points = loaded_settings.get('knowledge_points', 0)
        self.meta_upgrades = loaded_settings.get('meta_upgrades', {'hp': 0, 'speed': 0, 'damage': 0})
        self.unlocked_items = loaded_settings.get('unlocked_items',
                                                  ['Pistol', 'Automatic Rifle', 'Speed Boots', 'Power Ring',
                                                   'Heart Crystal'])

        self.apply_sound_volumes()

        self.save_manager = SaveManager()
        self.save_name_input = ""
        self.show_save_menu = False
        self.show_load_menu = False
        self.show_meta_shop = False
        self.show_info = False
        self.saves_list = []
        self.show_analysis = False

        self.all_artifacts = [
            Artifact("Speed Boots", "Увеличивает скорость бега на 50%", None),
            Artifact("Power Ring", "Увеличивает базовый урон на 10", None),
            Artifact("Heart Crystal", "Увеличивает макс. здоровье (+1 сердце)", None),
            Artifact("Explosive Rounds", "Снаряды взрываются по области", None),
            Artifact("Fire Stone", "Ваше оружие поджигает врагов", None),
            Artifact("Frost Amulet", "Снаряды замораживают и замедляют", None),
            Artifact("Quick Reload", "Ускоряет перезарядку в 2 раза", None),
            Artifact("Invisibility Cloak", "Неуязвимость на 1 сек каждые 4 сек", None)
        ]
        self.artifacts_pool = [a for a in self.all_artifacts if a.name in self.unlocked_items]

        self.all_weapons = [
            Weapon("Pistol", 10, False, 200),
            Weapon("Automatic Rifle", 5, True, 100),
            Weapon("Shotgun", 25, False, 500),
            Weapon("Sniper Rifle", 50, False, 1000),
            Weapon("Rocket Launcher", 100, False, 2000),
            Weapon("Machine Gun", 2, True, 50),
            Weapon("Grenade Launcher", 30, False, 750),
            Weapon("Flamethrower", 1, True, 10),
            Weapon("Railgun", 3, True, 50),
            Weapon("Crossbow", 15, False, 300)
        ]
        self.weapons_pool = [w for w in self.all_weapons if w.name in self.unlocked_items]

        self.meta_unlockables = [
            {"name": "Shotgun", "cost": 100, "type": "weapon"},
            {"name": "Machine Gun", "cost": 150, "type": "weapon"},
            {"name": "Sniper Rifle", "cost": 200, "type": "weapon"},
            {"name": "Crossbow", "cost": 250, "type": "weapon"},
            {"name": "Grenade Launcher", "cost": 300, "type": "weapon"},
            {"name": "Flamethrower", "cost": 350, "type": "weapon"},
            {"name": "Rocket Launcher", "cost": 450, "type": "weapon"},
            {"name": "Railgun", "cost": 600, "type": "weapon"},
            {"name": "Explosive Rounds", "cost": 200, "type": "artifact"},
            {"name": "Fire Stone", "cost": 250, "type": "artifact"},
            {"name": "Frost Amulet", "cost": 250, "type": "artifact"},
            {"name": "Quick Reload", "cost": 300, "type": "artifact"},
            {"name": "Invisibility Cloak", "cost": 400, "type": "artifact"},
        ]

        self.console_history = []
        self.console_history_idx = 0
        self.console_suggestions = []
        self.console_suggestion_idx = 0
        self.console_commands = {
            'help': {'aliases': ['h', '?'], 'args': [], 'desc': 'Показать список команд'},
            'give': {'aliases': ['g', 'i'], 'args': ['item'], 'desc': 'Выдать предмет (оружие/артефакт)'},
            'spawn': {'aliases': ['s', 'sp'], 'args': ['enemy'], 'desc': 'Призвать врага (basic, sniper, boss...)'},
            'money': {'aliases': ['m', 'eco'], 'args': ['amount'], 'desc': 'Добавить монеты'},
            'health': {'aliases': ['hp', 'heal'], 'args': ['amount'], 'desc': 'Добавить/отнять здоровье'},
            'stat': {'aliases': ['st'], 'args': ['stat_name', 'value'], 'desc': 'Изменить статы (speed, damage...)'},
            'killall': {'aliases': ['win', 'nuke'], 'args': [], 'desc': 'Убить всех врагов (верный ответ)'},
            'hint': {'aliases': ['show'], 'args': [], 'desc': 'Вкл/выкл подсветку правильного ответа'},
            'godmode': {'aliases': ['god', 'iddqd'], 'args': [], 'desc': 'Вкл/выкл бессмертие'},
            'infammo': {'aliases': ['inf', 'ammo'], 'args': [], 'desc': 'Вкл/выкл бесконечные патроны'},
            'giveall': {'aliases': ['all'], 'args': [], 'desc': 'Выдать все предметы'},
            'knowledge': {'aliases': ['kp', 'oz'], 'args': ['amount'], 'desc': 'Добавить Очки Знаний'}
        }
        self.hint_mode = False
        self.console_vocab = {
            'item': [w.name for w in self.weapons_pool] + [a.name for a in self.artifacts_pool],
            'enemy': ['basic', 'math', 'sniper', 'ghost', 'scout', 'tank', 'boss'],
            'stat_name': ['speed', 'damage', 'max_health', 'time_bonus', 'enemy_reduction', 'enemy_health_reduction']
        }
        self.console_log = []
        self.floor = 1
        self.floor_surface = pygame.Surface(WINDOW_SIZE)
        self.screen_shake = 0
        self.game_over = False

        self.light_mask = pygame.Surface((300, 300), pygame.SRCALPHA)
        for i in range(150, 0, -3):
            alpha = int(255 * (i / 150))
            pygame.draw.circle(self.light_mask, (255, 255, 255, alpha), (150, 150), i)
        self.small_light_mask = pygame.transform.scale(self.light_mask, (100, 100))

        self.reset_game()

    def apply_sound_volumes(self):
        sound_mappings = [
            ('reload_sound', 0.5), ('hurt_sound', 0.5), ('dash_sound', 0.5),
            ('powerup_sound', 0.5), ('pickup_coin_sound', 0.3), ('equip_sound', 0.5),
            ('explosion_sound', 0.5), ('portal_sound', 0.5), ('boss_spawn_snd', 0.6),
            ('boss_phase_snd', 0.6), ('spawn_enemies_snd', 1.0), ('boss_attack_snd', 0.7),
            ('wave_attack_snd', 0.6), ('boss_death_snd', 0.8), ('player_death_snd', 0.8),
            ('chest_open_sound', 0.5), ('logo_snd', 1.0), ('select_sound', 0.5),
            ('shoot_sound', 0.5)
        ]
        for name, vol in sound_mappings:
            if name in globals() and globals()[name]:
                globals()[name].set_volume(vol * self.sound_volume)

    def update_console_suggestions(self):
        text = self.console_text
        self.console_suggestions = []
        if not text.startswith('/'): return

        parts = text[1:].split(' ')
        cmd_part = parts[0].lower()

        if len(parts) == 1:
            for cmd, info in self.console_commands.items():
                if cmd.startswith(cmd_part) or any(a.startswith(cmd_part) for a in info['aliases']):
                    self.console_suggestions.append(cmd)
        else:
            cmd_name = None
            for name, info in self.console_commands.items():
                if cmd_part == name or cmd_part in info['aliases']:
                    cmd_name = name
                    break

            if cmd_name:
                arg_idx = len(parts) - 2
                if arg_idx < len(self.console_commands[cmd_name]['args']):
                    arg_type = self.console_commands[cmd_name]['args'][arg_idx]
                    if arg_type in self.console_vocab:
                        arg_val = " ".join(parts[1:]).lower() if arg_type == 'item' else parts[-1].lower()
                        for v in self.console_vocab[arg_type]:
                            if v.lower().startswith(arg_val):
                                self.console_suggestions.append(v)
                    elif arg_type in ['amount', 'value']:
                        self.console_suggestions.append("<введите число>")

        self.console_suggestion_idx = 0

    def execute_console_command(self):
        def log_msg(msg):
            self.console_log.append(msg)
            if len(self.console_log) > 15:
                self.console_log.pop(0)

        cmd_line = self.console_text.strip()
        if not cmd_line.startswith('/'): return

        log_msg(f"> {cmd_line}")

        if not self.console_history or self.console_history[-1] != cmd_line:
            self.console_history.append(cmd_line)
        self.console_history_idx = len(self.console_history)

        parts = cmd_line[1:].split(' ')
        cmd_part = parts[0].lower()
        args = parts[1:]

        cmd_name = None
        for name, info in self.console_commands.items():
            if cmd_part == name or cmd_part in info['aliases']:
                cmd_name = name
                break

        if not cmd_name:
            log_msg(f'Ошибка: Неизвестная команда {cmd_part}')
            return

        try:
            if cmd_name == 'help':
                log_msg('--- СПИСОК КОМАНД ---')
                for name, info in self.console_commands.items():
                    al = ", ".join(info['aliases'])
                    log_msg(f'/{name} [{al}] - {info["desc"]}')
            elif cmd_name == 'give':
                item_name = " ".join(args).lower()
                found = False
                for w in self.weapons_pool:
                    if w.name.lower() == item_name:
                        self.player.inventory.add_item(Weapon(w.name, w.damage, w.is_automatic, w.fire_rate))
                        log_msg(f'Выдано оружие: {w.name}')
                        found = True; break
                if not found:
                    for a in self.artifacts_pool:
                        if a.name.lower() == item_name:
                            self.player.inventory.add_item(Artifact(a.name, a.description, a.effect))
                            log_msg(f'Выдан артефакт: {a.name}')
                            found = True; break
                if not found:
                    log_msg(f'Ошибка: Предмет не найден ({item_name})')
            elif cmd_name == 'spawn':
                enemy_type = args[0].lower()
                self.current_room.add_enemy(enemy_type, "wrong")
                log_msg(f'Призван враг: {enemy_type}')
            elif cmd_name == 'money':
                amount = int(args[0])
                self.player.money += amount
                log_msg(f'Баланс изменен. Текущий: {self.player.money}')
            elif cmd_name == 'health':
                amount = int(args[0])
                self.player.health = min(self.player.total_max_health, max(0, self.player.health + amount))
                log_msg(f'Здоровье изменено. Текущее: {self.player.health}')
            elif cmd_name == 'stat':
                stat_name = args[0].lower()
                value = float(args[1])
                setattr(self.player, stat_name, value)
                log_msg(f'Характеристика {stat_name} установлена на {value}')
            elif cmd_name == 'killall':
                if self.current_room.type in [RoomType.NORMAL, RoomType.BOSS] and not self.current_room.cleared:
                    correct_enemy = next((e for e in self.current_room.enemies if getattr(e, 'is_correct', False)),
                                         None)
                    if correct_enemy:
                        correct_enemy.health = 0
                        log_msg("Все враги уничтожены (Ответ верен)")
                    else:
                        log_msg("Ошибка: В комнате нет правильного ответа")
                else:
                    log_msg("Команда работает только в активных комнатах с задачами")
            elif cmd_name == 'hint':
                self.hint_mode = not getattr(self, 'hint_mode', False)
                log_msg(f"Режим подсказок {'ВКЛЮЧЕН' if self.hint_mode else 'ВЫКЛЮЧЕН'}")
            elif cmd_name == 'godmode':
                self.player.godmode = not getattr(self.player, 'godmode', False)
                log_msg(f"Режим Бога {'ВКЛЮЧЕН' if self.player.godmode else 'ВЫКЛЮЧЕН'}")
            elif cmd_name == 'infammo':
                self.player.infinite_ammo = not getattr(self.player, 'infinite_ammo', False)
                log_msg(f"Бесконечные патроны {'ВКЛЮЧЕНЫ' if self.player.infinite_ammo else 'ВЫКЛЮЧЕНЫ'}")
            elif cmd_name == 'giveall':
                for w in getattr(self, 'all_weapons', self.weapons_pool):
                    self.player.inventory.add_item(Weapon(w.name, w.damage, w.is_automatic, w.fire_rate))
                for a in getattr(self, 'all_artifacts', self.artifacts_pool):
                    self.player.inventory.add_item(Artifact(a.name, a.description, a.effect))
                log_msg("Выданы абсолютно все предметы! (Используйте колесико мыши)")
            elif cmd_name == 'knowledge':
                self.knowledge_points += int(args[0])
                log_msg(f'Очки знаний добавлены. Текущие: {self.knowledge_points}')
        except Exception:
            log_msg('Ошибка: Неверные аргументы команды')

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def reset_game(self):
        self.floor = 1
        self.rooms_cleared = 0
        self.last_merchant_room = -3
        self.last_treasury_room = -2
        self.player = Player(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2, self)
        self.rooms = self.generate_floor()
        self.current_room_pos = (0, 0)
        self.current_room = self.rooms[self.current_room_pos]
        self.current_room.discovered = True
        self.game_over = False
        self.show_analysis = False
        Merchant.global_power_levels = {
            "Health Up": {"level": 0, "max_level": 5},
            "Damage Up": {"level": 0, "max_level": 3},
            "Speed Up": {"level": 0, "max_level": 2},
            "Time Up": {"level": 0, "max_level": 3},
            "Enemy Reduction": {"level": 0, "max_level": 2},
            "Enemy Health Down": {"level": 0, "max_level": 2},
            "Dash Faster": {"level": 0, "max_level": 3}
        }

        self.floor_surface = pygame.Surface(WINDOW_SIZE)
        for x, y in self.current_room.floor_positions:
            self.floor_surface.blit(floor_texture, (x, y))

    def add_portal(self, room_type):
        self.current_room.add_portal(room_type)

    def check_room_transition(self):
        for portal in self.current_room.portals:
            if (abs(self.player.x - portal['x']) < 40 and abs(self.player.y - portal['y']) < 40):
                for wall in self.current_room.walls:
                    wall.movable = False

                adjacent_positions = [
                    (self.current_room_pos[0], self.current_room_pos[1] - 1),
                    (self.current_room_pos[0], self.current_room_pos[1] + 1),
                    (self.current_room_pos[0] - 1, self.current_room_pos[1]),
                    (self.current_room_pos[0] + 1, self.current_room_pos[1])
                ]
                random.shuffle(adjacent_positions)

                new_pos = None
                for pos in adjacent_positions:
                    if pos not in self.rooms:
                        new_pos = pos
                        break

                if new_pos is None:
                    radius = 1
                    found = False
                    while not found:
                        for dx in range(-radius, radius + 1):
                            for dy in range(-radius, radius + 1):
                                check_pos = (self.current_room_pos[0] + dx, self.current_room_pos[1] + dy)
                                if check_pos not in self.rooms:
                                    new_pos = check_pos
                                    found = True
                                    break
                            if found:
                                break
                        radius += 1

                # Ускоренная и расширенная адаптивная система сложности
                base_diff = min(8, max(1, self.rooms_cleared // 2 + 1))
                if self.player.stats.problems_attempted > 0:
                    success = self.player.stats.get_success_rate()
                    if success >= 85:
                        difficulty = min(8, base_diff + 2)  # Прыгаем на 2 уровня за отличную игру
                    elif success >= 65:
                        difficulty = min(8, base_diff + 1)
                    elif success <= 40:
                        difficulty = max(1, base_diff - 1)
                    else:
                        difficulty = base_diff
                else:
                    difficulty = base_diff

                room_type = portal['type']
                if isinstance(room_type, str):
                    room_type = RoomType[room_type]

                self.rooms[new_pos] = Room(room_type, new_pos, self.rooms, difficulty)
                self.current_room_pos = new_pos
                self.current_room = self.rooms[new_pos]
                self.current_room.discovered = True
                self.player.x = (WINDOW_SIZE[0] - self.player.size) // 2
                self.player.y = (WINDOW_SIZE[1] - self.player.size) // 2

                self.floor_surface.fill((0, 0, 0)) 
                for x, y in self.current_room.floor_positions:
                    self.floor_surface.blit(floor_texture, (x, y))

                # Звук портала
                if 'portal_sound' in globals() and portal_sound:
                    portal_sound.play()

                if portal['type'] == RoomType.NEXT_FLOOR:
                    self.floor += 1
                    self.rooms_cleared = 0
                    self.rooms = self.generate_floor()
                    self.current_room_pos = (0, 0)
                    self.current_room = self.rooms[self.current_room_pos]
                    self.current_room.discovered = True
                    self.player.x = (WINDOW_SIZE[0] - self.player.size) // 2
                    self.player.y = (WINDOW_SIZE[1] - self.player.size) // 2
                    self.floor_surface.fill((0, 0, 0))
                    for x, y in self.current_room.floor_positions:
                        self.floor_surface.blit(floor_texture, (x, y))

                    if 'boss_music' in globals() and boss_music: boss_music.stop()
                    level_music.stop()
                    if 'level2_music' in globals() and level2_music: level2_music.stop()

                    if self.floor >= 2 and 'level2_music' in globals() and level2_music:
                        level2_music.play(-1)
                    else:
                        level_music.play(-1)
                    return

                if portal['type'] != RoomType.SHOP and portal['type'] != RoomType.TREASURE:
                    self.rooms_cleared += 1
                    if portal['type'] == RoomType.BOSS:
                        level_music.stop()
                        if 'level2_music' in globals() and level2_music: level2_music.stop()
                    elif not pygame.mixer.get_busy() and not (hasattr(self.current_room, 'enemies') and any(
                            e.enemy_type == 'boss' for e in self.current_room.enemies)):
                        level_music.stop()
                        if 'level2_music' in globals() and level2_music: level2_music.stop()
                        if getattr(self, 'floor', 1) >= 2 and 'level2_music' in globals() and level2_music:
                            level2_music.play(-1)
                        else:
                            level_music.play(-1)

    def check_room_completion(self):
        if not self.current_room.cleared and len(self.current_room.enemies) == 0:
            self.current_room.cleared = True
            if self.current_room.type != RoomType.BOSS:
                for wall in self.current_room.walls:
                    if wall.is_obstacle:
                        wall.movable = True

            if self.current_room.type == RoomType.NORMAL:
                normal_rooms_cleared = sum(1 for room in self.rooms.values()
                                           if isinstance(room, Room) and
                                           room.type == RoomType.NORMAL and
                                           room.cleared)

                possible_types = [RoomType.NORMAL]

                if self.rooms_cleared >= 5 and not any(
                        t in possible_types for t in [RoomType.TREASURE, RoomType.SHOP, RoomType.BOSS]):
                    possible_types.append(RoomType.TREASURE)

                if self.rooms_cleared - self.last_treasury_room >= random.randint(1, 2):
                    possible_types.append(RoomType.TREASURE)

                if self.rooms_cleared - self.last_merchant_room >= random.randint(2, 3):
                    possible_types.append(RoomType.SHOP)

                if normal_rooms_cleared >= 5:
                    possible_types.append(RoomType.BOSS)

                num_portals = random.randint(1, 2)
                portals_added = []

                for _ in range(num_portals):
                    if not possible_types:
                        break

                    portal_type = random.choice(possible_types)

                    possible_types.remove(portal_type)

                    self.current_room.add_portal(portal_type)
                    portals_added.append(portal_type)

                if RoomType.SHOP in portals_added:
                    self.last_merchant_room = self.rooms_cleared
                if RoomType.TREASURE in portals_added:
                    self.last_treasury_room = self.rooms_cleared

    def generate_floor(self):
        rooms = {}
        current_pos = (0, 0)
        rooms['game'] = self
        # Генерация стартовой комнаты, остальные будут создаваться динамически
        rooms[current_pos] = Room(pos=current_pos, rooms=rooms, difficulty=1)
        rooms[current_pos].discovered = True
        return rooms

    def draw_knowledge_analysis(self, screen):
        surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 220), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
        screen.blit(surface, (0, 0))

        stats = self.player.stats
        font_large = pygame.font.Font('PixelizerBold.ttf', 48)
        font_medium = pygame.font.Font('PixelizerBold.ttf', 32)
        font_small = pygame.font.Font('PixelizerBold.ttf', 24)

        title = font_large.render('АНАЛИЗ ЗНАНИЙ', True, WHITE)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, 50 - self.analysis_scroll_offset))

        y_pos = 120 - self.analysis_scroll_offset
        success_rate = stats.get_success_rate()
        grade = stats.get_grade()

        texts = [
            f"Всего решено задач: {stats.problems_attempted}",
            f"Правильно решено: {stats.problems_correct}",
            f"Успешность: {success_rate:.1f}%",
            f"ОЦЕНКА: {grade}"
        ]

        for text in texts:
            if y_pos > -50 and y_pos < WINDOW_SIZE[1]:
                text_surface = font_medium.render(text, True, WHITE)
                screen.blit(text_surface, (WINDOW_SIZE[0] // 2 - text_surface.get_width() // 2, y_pos))
            y_pos += 40

        y_pos += 30

        if y_pos > -50 and y_pos < WINDOW_SIZE[1]:
            type_title = font_medium.render("Статистика по типам задач:", True, CYAN)
            screen.blit(type_title, (WINDOW_SIZE[0] // 2 - type_title.get_width() // 2, y_pos))
        y_pos += 40

        type_names = {
            'equation': 'Уравнения',
            'sequence': 'Последовательности',
            'percentage': 'Задачи на проценты'
        }

        for problem_type in ['equation', 'sequence', 'percentage']:
            if y_pos > -50 and y_pos < WINDOW_SIZE[1]:
                rate = stats.get_type_success_rate(problem_type)
                type_stats = stats.problem_types_stats[problem_type]
                text = f"{type_names[problem_type]}: {type_stats['correct']}/{type_stats['attempted']} ({rate:.1f}%)"
                text_surface = font_small.render(text, True, WHITE)
                screen.blit(text_surface, (WINDOW_SIZE[0] // 2 - text_surface.get_width() // 2, y_pos))
            y_pos += 30

        if stats.incorrect_problems:
            y_pos += 30
            if y_pos > -50 and y_pos < WINDOW_SIZE[1]:
                incorrect_title = font_medium.render("Неправильно решенные задачи:", True, RED)
                screen.blit(incorrect_title, (WINDOW_SIZE[0] // 2 - incorrect_title.get_width() // 2, y_pos))
            y_pos += 40

            for i, problem in enumerate(stats.incorrect_problems[:5]):
                if y_pos > -100 and y_pos < WINDOW_SIZE[1]:
                    condition_text = font_small.render(f"Задача: {problem.condition}", True, WHITE)
                    solution_text = font_small.render(f"Правильный ответ: {problem.solution}", True, GREEN)

                    screen.blit(condition_text, (50, y_pos))
                    screen.blit(solution_text, (50, y_pos + 25))

                    explanation = f"Объяснение: {problem.get_explanation()}"
                    explanation_lines = self.wrap_text(explanation, font_small, WINDOW_SIZE[0] - 100)

                    for j, line in enumerate(explanation_lines):
                        if y_pos + 50 + j * 25 < WINDOW_SIZE[1]:
                            explanation_text = font_small.render(line, True, (200, 200, 200))
                            screen.blit(explanation_text, (50, y_pos + 50 + j * 25))

                    y_pos += 50 + len(explanation_lines) * 25
                else:
                    y_pos += 85

                y_pos += 85

                if i == 4 and len(stats.incorrect_problems) > 5:
                    if y_pos > -50 and y_pos < WINDOW_SIZE[1]:
                        more_text = font_small.render(f"... и еще {len(stats.incorrect_problems) - 5} задач", True,
                                                      WHITE)
                        screen.blit(more_text, (50, y_pos))
                    y_pos += 30
                    break

        continue_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] - 100, 200, 50, "Продолжить", (50, 170, 50))
        continue_btn.draw(screen)

        self.analysis_content_height = y_pos + 150

        return continue_btn.rect if 'continue_btn' in locals() else pygame.Rect(0, 0, 0, 0)

    def draw_save_menu(self, screen, mouse_pos):
        surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 200), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
        screen.blit(surface, (0, 0))

        font = pygame.font.Font('PixelizerBold.ttf', 48)
        text = font.render('Сохранение игры', True, WHITE)
        screen.blit(text, (WINDOW_SIZE[0] // 2 - text.get_width() // 2, WINDOW_SIZE[1] // 3 - 50))

        pygame.draw.rect(screen, (100, 100, 100), (WINDOW_SIZE[0] // 2 - 150, WINDOW_SIZE[1] // 2 - 50, 300, 40))
        font = pygame.font.Font('PixelizerBold.ttf', 24)
        name_text = font.render(self.save_name_input, True, WHITE)
        screen.blit(name_text, (WINDOW_SIZE[0] // 2 - 140, WINDOW_SIZE[1] // 2 - 40))

        save_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 20, 200, 50, "Сохранить", (50, 50, 50))
        save_btn.draw(screen)

        cancel_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 90, 200, 50, "Отмена", (50, 50, 50))
        cancel_btn.draw(screen)

        if save_btn.rect.collidepoint(mouse_pos) or cancel_btn.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw_load_menu(self, screen, mouse_pos):
        surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 200), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
        screen.blit(surface, (0, 0))

        font = pygame.font.Font('PixelizerBold.ttf', 48)
        text = font.render('Загрузка игры', True, WHITE)
        screen.blit(text, (WINDOW_SIZE[0] // 2 - text.get_width() // 2, WINDOW_SIZE[1] // 4 - 50))

        self.saves_list = self.save_manager.get_save_files()
        font = pygame.font.Font('PixelizerBold.ttf', 24)

        for i, save in enumerate(self.saves_list):
            y_pos = WINDOW_SIZE[1] // 3 + i * 60
            save_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, y_pos, 400, 50)

            if save_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (100, 100, 100), save_rect)
            else:
                pygame.draw.rect(screen, (70, 70, 70), save_rect)

            name_text = font.render(save['name'], True, WHITE)
            screen.blit(name_text, (save_rect.x + 10, save_rect.y + 10))

            info_font = pygame.font.Font('PixelizerBold.ttf', 16)
            timestamp = datetime.fromisoformat(save['timestamp']).strftime("%d.%m.%Y %H:%M")
            info_text = info_font.render(f"Комнат: {save['rooms_cleared']} | {timestamp}", True, (200, 200, 200))
            screen.blit(info_text, (save_rect.x + 10, save_rect.y + 35))

        cancel_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] - 100, 200, 50, "Отмена", (50, 50, 50))
        cancel_btn.draw(screen)

        if cancel_btn.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw_info_menu(self, screen, mouse_pos):
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 220), overlay.get_rect())
        screen.blit(overlay, (0, 0))

        menu_width = 540
        menu_height = 460
        menu_x = (WINDOW_SIZE[0] - menu_width) // 2
        menu_y = (WINDOW_SIZE[1] - menu_height) // 2

        pygame.draw.rect(screen, (20, 20, 25), (menu_x, menu_y, menu_width, menu_height), border_radius=10)
        pygame.draw.rect(screen, CYAN, (menu_x, menu_y, menu_width, menu_height), 3, border_radius=10)

        font_title = pygame.font.Font('PixelizerBold.ttf', 48)
        title = font_title.render("УПРАВЛЕНИЕ", True, GOLD)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, menu_y + 20))

        font_normal = pygame.font.Font('PixelizerBold.ttf', 28)
        controls = [
            ("WASD / Стрелки", "Перемещение"),
            ("ЛКМ", "Стрельба / Удар"),
            ("Пробел / Shift", "Рывок (Dash)"),
            ("E (англ.)", "Взаимодействие"),
            ("R", "Перезарядка"),
            ("Tab", "Инвентарь и Статы"),
            ("~ (Тильда)", "Консоль команд"),
            ("Esc", "Пауза / Назад")
        ]

        y_offset = menu_y + 90
        for key, desc in controls:
            key_text = font_normal.render(key, True, CYAN)
            desc_text = font_normal.render(f"- {desc}", True, WHITE)
            screen.blit(key_text, (menu_x + 30, y_offset))
            screen.blit(desc_text, (menu_x + 230, y_offset))
            y_offset += 35

        self.info_back_button.draw(screen)

    def draw_meta_shop(self, screen, mouse_pos):
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 230), overlay.get_rect())
        screen.blit(overlay, (0, 0))

        menu_width = 740
        menu_height = 560
        menu_x = (WINDOW_SIZE[0] - menu_width) // 2
        menu_y = (WINDOW_SIZE[1] - menu_height) // 2

        pygame.draw.rect(screen, (20, 20, 25), (menu_x, menu_y, menu_width, menu_height), border_radius=10)
        pygame.draw.rect(screen, GOLD, (menu_x, menu_y, menu_width, menu_height), 3, border_radius=10)

        font_title = pygame.font.Font('PixelizerBold.ttf', 48)
        title = font_title.render("МЕТА-ПРОКАЧКА", True, GOLD)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, menu_y + 15))

        font_normal = pygame.font.Font('PixelizerBold.ttf', 24)
        kp_text = font_normal.render(f"Очки Знаний: {int(self.knowledge_points)}", True, CYAN)
        screen.blit(kp_text, (WINDOW_SIZE[0] // 2 - kp_text.get_width() // 2, menu_y + 60))

        # Upgrades (Левая колонка)
        upgrades = [
            ("hp", "Макс. Здоровье (+0.5 сер.)", 50, 10),
            ("speed", "Скорость бега (+5%)", 40, 10),
            ("damage", "Базовый урон (+1)", 60, 10)
        ]

        y_offset = menu_y + 110
        for key, name, base_cost, max_lvl in upgrades:
            lvl = self.meta_upgrades[key]
            cost = base_cost * (lvl + 1)

            text = font_normal.render(f"{name} [Lv {lvl}/{max_lvl}]", True, WHITE)
            screen.blit(text, (menu_x + 20, y_offset))

            if lvl < max_lvl:
                btn_rect = pygame.Rect(menu_x + 360, y_offset - 5, 100, 35)
                color = GOLD if btn_rect.collidepoint(mouse_pos) else (100, 100, 100)
                if self.knowledge_points < cost: color = (100, 50, 50)
                pygame.draw.rect(screen, color, btn_rect, border_radius=5)
                cost_text = font_normal.render(f"{cost} ОЗ", True, BLACK if color == GOLD else WHITE)
                screen.blit(cost_text, (btn_rect.centerx - cost_text.get_width() // 2,
                                        btn_rect.centery - cost_text.get_height() // 2))
            else:
                max_text = font_normal.render("МАКСИМУМ", True, GREEN)
                screen.blit(max_text, (menu_x + 360, y_offset))

            y_offset += 45

        # Unlocks (Нижняя секция)
        unl_title = font_normal.render("РАЗБЛОКИРОВКА ПРЕДМЕТОВ", True, GOLD)
        screen.blit(unl_title, (WINDOW_SIZE[0] // 2 - unl_title.get_width() // 2, y_offset + 10))
        y_offset += 50

        locked_items = [item for item in self.meta_unlockables if item['name'] not in self.unlocked_items]

        for i, item in enumerate(locked_items[:5]):  # Покажем топ 5
            text = font_normal.render(f"{item['name']} ({'Оружие' if item['type'] == 'weapon' else 'Артефакт'})", True,
                                      (200, 200, 200))
            screen.blit(text, (menu_x + 20, y_offset))

            btn_rect = pygame.Rect(menu_x + 360, y_offset - 5, 100, 35)
            color = CYAN if btn_rect.collidepoint(mouse_pos) else (50, 100, 150)
            if self.knowledge_points < item['cost']: color = (100, 50, 50)
            pygame.draw.rect(screen, color, btn_rect, border_radius=5)
            cost_text = font_normal.render(f"{item['cost']} ОЗ", True, BLACK if color == CYAN else WHITE)
            screen.blit(cost_text,
                        (btn_rect.centerx - cost_text.get_width() // 2, btn_rect.centery - cost_text.get_height() // 2))

            try:
                filename = item['name'].lower().replace(' ', '_') + '.png'
                icon = pygame.image.load(f'tileset/{filename}').convert_alpha()
                icon = pygame.transform.scale(icon, (32, 32))
                screen.blit(icon, (menu_x + 480, y_offset - 5))
            except Exception:
                pass

            y_offset += 45

        if len(locked_items) > 5:
            more_text = font_normal.render(f"...и еще {len(locked_items) - 5} скрытых предметов", True, GRAY)
            screen.blit(more_text, (menu_x + 20, y_offset))

        self.meta_back_button.draw(screen)

    def draw_menu(self, screen, mouse_pos):
        screen.fill(CYAN)
        if self.game_over and self.show_analysis:
            continue_rect = self.draw_knowledge_analysis(screen)

            if continue_rect.collidepoint(mouse_pos):
                screen.blit(cursor_hand, (mouse_pos[0] - 16, mouse_pos[1] - 16))
                if pygame.mouse.get_pressed()[0]:
                    self.show_analysis = False
            else:
                screen.blit(cursor, (mouse_pos[0] - 16, mouse_pos[1] - 16))

        elif self.game_over:
            font = pygame.font.Font('PixelizerBold.ttf', 74)
            text = font.render('Game Over', True, RED)
            screen.blit(text, (WINDOW_SIZE[0] // 2 - text.get_width() // 2, WINDOW_SIZE[1] // 2 - 100))

            self.analysis_button.rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 10)
            self.restart_button.rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 80)
            self.to_menu_button.rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 150)

            self.analysis_button.draw(screen)
            self.restart_button.draw(screen)
            self.to_menu_button.draw(screen)

            if (self.analysis_button.rect.collidepoint(mouse_pos) or
                    self.restart_button.rect.collidepoint(mouse_pos) or
                    self.to_menu_button.rect.collidepoint(mouse_pos)):
                screen.blit(cursor_hand, (mouse_pos[0] - 16, mouse_pos[1] - 16))
            else:
                screen.blit(cursor, (mouse_pos[0] - 16, mouse_pos[1] - 16))

        elif self.show_save_menu:
            self.draw_save_menu(screen, mouse_pos)
        elif getattr(self, 'show_meta_shop', False):
            self.draw_meta_shop(screen, mouse_pos)
        elif getattr(self, 'show_info', False):
            self.draw_info_menu(screen, mouse_pos)
        elif self.show_load_menu:
            self.draw_load_menu(screen, mouse_pos)
        elif self.show_settings:
            # Полупрозрачный фон для всего экрана
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
            screen.blit(overlay, (0, 0))

            menu_width = 460
            menu_height = 550
            menu_x = (WINDOW_SIZE[0] - menu_width) // 2
            menu_y = (WINDOW_SIZE[1] - menu_height) // 2

            # Основной фон меню
            pygame.draw.rect(screen, (20, 20, 25), (menu_x, menu_y, menu_width, menu_height), border_radius=10)
            pygame.draw.rect(screen, CYAN, (menu_x, menu_y, menu_width, menu_height), 3, border_radius=10)

            title_font = pygame.font.Font('PixelizerBold.ttf', 48)
            title_text = title_font.render("НАСТРОЙКИ", True, GOLD)
            screen.blit(title_text, (menu_x + menu_width // 2 - title_text.get_width() // 2, menu_y + 15))

            font = pygame.font.Font('PixelizerBold.ttf', 32)

            # Музыка
            text = font.render(f'Музыка: {int(self.music_volume * 100)}%', True, WHITE)
            screen.blit(text, (menu_x + 80, menu_y + 70))
            pygame.draw.rect(screen, (50, 50, 60), (menu_x + 80, menu_y + 105, 300, 20), border_radius=5)
            pygame.draw.rect(screen, CYAN, (menu_x + 80, menu_y + 105, 300 * self.music_volume, 20), border_radius=5)

            # Звуки
            text = font.render(f'Звуки: {int(self.sound_volume * 100)}%', True, WHITE)
            screen.blit(text, (menu_x + 80, menu_y + 145))
            pygame.draw.rect(screen, (50, 50, 60), (menu_x + 80, menu_y + 180, 300, 20), border_radius=5)
            pygame.draw.rect(screen, CYAN, (menu_x + 80, menu_y + 180, 300 * self.sound_volume, 20), border_radius=5)

            # Тряска
            text = font.render(f'Тряска экрана: {int(self.shake_intensity * 100)}%', True, WHITE)
            screen.blit(text, (menu_x + 80, menu_y + 220))
            pygame.draw.rect(screen, (50, 50, 60), (menu_x + 80, menu_y + 255, 300, 20), border_radius=5)
            pygame.draw.rect(screen, CYAN, (menu_x + 80, menu_y + 255, 300 * self.shake_intensity, 20), border_radius=5)

            # Урон
            dmg_status = "ВКЛ" if self.show_damage_numbers else "ВЫКЛ"
            text = font.render(f'Числа урона: {dmg_status}', True, WHITE)
            screen.blit(text, (menu_x + 80, menu_y + 295))

            toggle_rect = pygame.Rect(menu_x + 80, menu_y + 325, 300, 40)
            pygame.draw.rect(screen, (40, 40, 50), toggle_rect, border_radius=5)
            pygame.draw.rect(screen, CYAN, toggle_rect, 2, border_radius=5)
            btn_text = font.render("ПЕРЕКЛЮЧИТЬ", True, GOLD)
            screen.blit(btn_text, (toggle_rect.centerx - btn_text.get_width() // 2,
                                   toggle_rect.centery - btn_text.get_height() // 2 + 2))

            # Кнопка полного экрана
            self.fullscreen_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.fullscreen_button.rect.y = menu_y + 380
            self.fullscreen_button.draw(screen)

            # Логика возврата текста кнопки подтверждения сброса прогресса (через 3 секунды)
            if getattr(self, 'confirming_reset', False):
                if pygame.time.get_ticks() - self.confirm_reset_timer > 3000:
                    self.confirming_reset = False
                    self.hard_reset_button.text = "СБРОС ПРОГРЕССА"
                    self.hard_reset_button.color = (200, 50, 50)

            self.hard_reset_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.hard_reset_button.rect.y = menu_y + 440
            self.hard_reset_button.draw(screen)

        elif self.active_menu == "escape":
            surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            pygame.draw.rect(surface, (0, 0, 0, 200), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
            screen.blit(surface, (0, 0))

            font = pygame.font.Font('PixelizerBold.ttf', 48)
            text = font.render('Пауза', True, WHITE)
            screen.blit(text, (WINDOW_SIZE[0] // 2 - text.get_width() // 2, WINDOW_SIZE[1] // 4 - 30))

            self.restart_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.restart_button.rect.centery = WINDOW_SIZE[1] // 2 - 40
            self.settings_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.settings_button.rect.centery = WINDOW_SIZE[1] // 2 + 30
            self.to_menu_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.to_menu_button.rect.centery = WINDOW_SIZE[1] // 2 + 100
            self.save_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.save_button.rect.centery = WINDOW_SIZE[1] // 2 + 170
            self.load_button.rect.centerx = WINDOW_SIZE[0] // 2
            self.load_button.rect.centery = WINDOW_SIZE[1] // 2 + 240

            self.restart_button.draw(screen)
            self.settings_button.draw(screen)
            self.to_menu_button.draw(screen)
            self.save_button.draw(screen)
            self.load_button.draw(screen)

            back_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 310, 200, 50, "Назад", (50, 50, 50))
            back_button.draw(screen)

            if (self.restart_button.rect.collidepoint(mouse_pos) or
                    self.settings_button.rect.collidepoint(mouse_pos) or
                    back_button.rect.collidepoint(mouse_pos)):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            self.play_button.rect.x, self.play_button.rect.y = self.main_menu_button_positions['play']
            self.meta_shop_button.rect.x, self.meta_shop_button.rect.y = self.main_menu_button_positions['meta']
            self.settings_button.rect.x, self.settings_button.rect.y = self.main_menu_button_positions['settings']
            self.info_button.rect.x, self.info_button.rect.y = self.main_menu_button_positions['info']
            self.save_button.rect.x, self.save_button.rect.y = self.main_menu_button_positions['save']
            self.load_button.rect.x, self.load_button.rect.y = self.main_menu_button_positions['load']
            self.exit_button.rect.x, self.exit_button.rect.y = self.main_menu_button_positions['exit']

            current_frame = logo_frames[int(time.time() * 10) % len(logo_frames)]
            logo_rect = current_frame.get_rect()
            logo_rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 3 - 80)
            screen.blit(current_frame, logo_rect)

            if not getattr(self, 'show_settings', False) and not getattr(self, 'show_meta_shop',
                                                                             False) and not getattr(self, 'show_info',
                                                                                                    False):
                self.play_button.draw(screen)
                self.meta_shop_button.draw(screen)
                self.settings_button.draw(screen)
                self.info_button.draw(screen)
                self.save_button.draw(screen)
                self.load_button.draw(screen)
                self.exit_button.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        use_hand_cursor = False

        if getattr(self, 'show_info', False):
            if getattr(self, 'info_back_button', None) and self.info_back_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True
        elif getattr(self, 'show_meta_shop', False):
            if getattr(self, 'meta_back_button', None) and self.meta_back_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True
            else:
                menu_width = 740
                menu_height = 560
                menu_x = (WINDOW_SIZE[0] - menu_width) // 2
                menu_y = (WINDOW_SIZE[1] - menu_height) // 2
                if menu_x + 360 <= mouse_pos[0] <= menu_x + 460 and menu_y + 100 <= mouse_pos[1] <= menu_y + 500:
                    use_hand_cursor = True
        elif getattr(self, 'show_settings', False):
            if self.fullscreen_button.rect.collidepoint(mouse_pos) or self.hard_reset_button.rect.collidepoint(
                    mouse_pos):
                use_hand_cursor = True
            back_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 100, (WINDOW_SIZE[1] - 550) // 2 + 490, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                use_hand_cursor = True
        elif not getattr(self, 'show_settings', False) and not getattr(self, 'show_meta_shop',
                                                                           False) and not getattr(self, 'show_info',
                                                                                                  False):
            if self.play_button.rect.collidepoint(mouse_pos) or self.meta_shop_button.rect.collidepoint(
                    mouse_pos) or getattr(self, 'info_button', None) and self.info_button.rect.collidepoint(
                    mouse_pos) or self.settings_button.rect.collidepoint(
                    mouse_pos) or self.save_button.rect.collidepoint(
                    mouse_pos) or self.load_button.rect.collidepoint(
                    mouse_pos) or self.exit_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True

        if getattr(self, 'show_meta_shop', False):
            if getattr(self, 'meta_back_button', None) and self.meta_back_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True
            else:
                menu_width = 740
                menu_height = 560
                menu_x = (WINDOW_SIZE[0] - menu_width) // 2
                menu_y = (WINDOW_SIZE[1] - menu_height) // 2
                if menu_x + 360 <= mouse_pos[0] <= menu_x + 460 and menu_y + 100 <= mouse_pos[1] <= menu_y + 500:
                    use_hand_cursor = True
        elif getattr(self, 'show_settings', False):
            if self.fullscreen_button.rect.collidepoint(mouse_pos) or self.hard_reset_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True
            back_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 100, (WINDOW_SIZE[1] - 620) // 2 + 550, 200, 50)
            if back_rect.collidepoint(mouse_pos):
                use_hand_cursor = True
        elif not getattr(self, 'show_settings', False) and not getattr(self, 'show_meta_shop', False):
            if self.play_button.rect.collidepoint(mouse_pos) or self.meta_shop_button.rect.collidepoint(
                    mouse_pos) or self.settings_button.rect.collidepoint(
                    mouse_pos) or self.save_button.rect.collidepoint(
                    mouse_pos) or self.load_button.rect.collidepoint(
                    mouse_pos) or self.exit_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True

        if (self.game_over or self.active_menu == "escape") and self.restart_button.rect.collidepoint(mouse_pos):
            use_hand_cursor = True
        elif self.active_menu == "escape":
            back_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 310, 200, 50, "Назад", (50, 50, 50))
            if back_button.rect.collidepoint(mouse_pos):
                use_hand_cursor = True

        if use_hand_cursor:
            screen.blit(cursor_hand, (mouse_pos[0] - 16, mouse_pos[1] - 16))
        else:
            screen.blit(cursor, (mouse_pos[0] - 16, mouse_pos[1] - 16))

    def draw_minimap(self, screen):
        map_rect = pygame.Rect(WINDOW_SIZE[0] - 160, 20, 140, 140)

        # Полупрозрачный фон миникарты
        surface = pygame.Surface((map_rect.width, map_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (30, 30, 30, 180), surface.get_rect())
        screen.blit(surface, (map_rect.x, map_rect.y))
        pygame.draw.rect(screen, WHITE, map_rect, 2)

        cell_size = 15
        center_x = map_rect.x + map_rect.width // 2
        center_y = map_rect.y + map_rect.height // 2

        for pos_key, room in self.rooms.items():
            if isinstance(pos_key, tuple) and room.discovered:
                # Относительная позиция от текущей комнаты
                dx = pos_key[0] - self.current_room_pos[0]
                dy = pos_key[1] - self.current_room_pos[1]

                draw_x = center_x + dx * (cell_size + 2) - cell_size // 2
                draw_y = center_y + dy * (cell_size + 2) - cell_size // 2

                if map_rect.collidepoint(draw_x, draw_y) and map_rect.collidepoint(draw_x + cell_size,
                                                                                   draw_y + cell_size):
                    color = (100, 100, 100) 

                    if pos_key == self.current_room_pos:
                        color = WHITE
                    elif room.type == RoomType.BOSS:
                        color = RED
                    elif room.type == RoomType.SHOP:
                        color = GREEN
                    elif room.type == RoomType.TREASURE:
                        color = GOLD

                    pygame.draw.rect(screen, color, (draw_x, draw_y, cell_size, cell_size))
                    pygame.draw.rect(screen, (50, 50, 50), (draw_x, draw_y, cell_size, cell_size), 1)

                    if not room.cleared and pos_key != self.current_room_pos:
                        pygame.draw.rect(screen, RED, (draw_x + cell_size // 2 - 2, draw_y + cell_size // 2 - 2, 4, 4))


def main():
    global screen, is_fullscreen

    loaded_settings = load_settings()
    is_fullscreen = loaded_settings.get('is_fullscreen', False)
    if is_fullscreen:
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED | pygame.FULLSCREEN)

    game = Game()

    try:
        icon_img = pygame.image.load('tileset/cyanBorderIcon.png').convert_alpha()
        pygame.display.set_icon(icon_img)
    except Exception as e:
        icon_img = None
        print("Ошибка загрузки иконки:", e)

    # Заставка
    splash_duration = 3500
    start_time = pygame.time.get_ticks()

    try:
        logo_snd = pygame.mixer.Sound('Sounds/logo.wav')
        logo_snd.set_volume(game.sound_volume)
        logo_snd.play()
    except Exception:
        pass

    splash_font = pygame.font.Font('PixelizerBold.ttf', 64)
    splash_text = splash_font.render('MathCrawl', True, CYAN)

    while pygame.time.get_ticks() - start_time < splash_duration:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                splash_duration = 0
                if 'logo_snd' in locals():
                    logo_snd.stop()
                break

        if splash_duration == 0:
            break

        progress = (pygame.time.get_ticks() - start_time) / splash_duration
        screen.fill(BLACK)

        # Плавное появление и исчезновение
        alpha = min(255, int(progress * 2 * 255))
        if progress > 0.8:
            alpha = max(0, int((1.0 - progress) * 5 * 255))

        # Плавное увеличение
        scale = 1.0 + progress * 0.4
        if icon_img:
            try:
                scaled_logo = pygame.transform.smoothscale(icon_img, (int(96 * scale), int(96 * scale)))
                scaled_logo.set_alpha(alpha)
                logo_rect = scaled_logo.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 40))
                screen.blit(scaled_logo, logo_rect)
            except Exception:
                pass

        splash_text.set_alpha(alpha)
        text_rect = splash_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 60))
        screen.blit(splash_text, text_rect)

        pygame.display.flip()
        clock.tick(60)
    # конец застаыки

    if 'menu_music' in globals() and menu_music:
        menu_music.set_volume(game.music_volume)
        menu_music.play(-1)

    running = True
    level_music.set_volume(game.music_volume)
    if 'level2_music' in globals() and level2_music:
        level2_music.set_volume(game.music_volume)
    if 'boss_music' in globals() and boss_music:
        boss_music.set_volume(game.music_volume)

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEWHEEL:
                if game.show_analysis:
                    game.analysis_scroll_offset -= event.y * 30
                    max_scroll = max(0, game.analysis_content_height - WINDOW_SIZE[1] + 100)
                    game.analysis_scroll_offset = max(0, min(game.analysis_scroll_offset, max_scroll))
                elif game.player.inventory.visible:
                    game.player.inventory.scroll_offset = max(0, game.player.inventory.scroll_offset - event.y)
                    max_inv_scroll = max(0, (
                                len(game.player.inventory.items) - 1) // game.player.inventory.cols - game.player.inventory.rows + 1)
                    game.player.inventory.scroll_offset = min(game.player.inventory.scroll_offset, max_inv_scroll)
            elif event.type == KEYDOWN:
                if event.key == K_TAB and not game.console_active:
                    game.player.inventory.visible = not game.player.inventory.visible
                elif event.key == K_r and not game.console_active:
                    if game.player.inventory.equipped['weapon']:
                        game.player.inventory.equipped['weapon'].start_reload(pygame.time.get_ticks(),
                                                                              game.player.reload_multiplier)
                elif event.key == K_ESCAPE and not game.console_active:
                    if getattr(game, 'show_info', False):
                        game.show_info = False
                    elif game.show_settings:
                        game.show_settings = False
                    elif getattr(game, 'show_meta_shop', False):
                        game.show_meta_shop = False
                        game.reset_game()
                    elif game.player.inventory.visible:
                        game.player.inventory.visible = False
                    elif not game.show_menu:
                        game.active_menu = "escape"
                        game.show_menu = True
                    elif game.active_menu == "escape":
                        game.show_menu = False
                        game.active_menu = None
                elif event.key == K_l and not game.console_active:
                    for enemy in game.current_room.enemies[:]:
                        game.current_room.coins.append(Coin(enemy.x, enemy.y, enemy.money))
                        game.current_room.enemies.remove(enemy)
                elif event.key == K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED | pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED)
                    save_settings(game.music_volume, game.sound_volume, is_fullscreen, game.shake_intensity, game.show_damage_numbers)
                elif event.key == K_BACKQUOTE:
                    game.console_active = not game.console_active
                    if not game.console_active:
                        game.console_text = ""
                    else:
                        game.update_console_suggestions()
                elif game.console_active:
                    if event.key == K_RETURN:
                        game.execute_console_command()
                        game.console_text = ""
                        game.update_console_suggestions()
                    elif event.key == K_BACKSPACE:
                        game.console_text = game.console_text[:-1]
                        game.update_console_suggestions()
                    elif event.key == K_TAB:
                        if game.console_suggestions:
                            sugg = game.console_suggestions[game.console_suggestion_idx]
                            if sugg != "<введите число>":
                                parts = game.console_text.split(' ')
                                if len(parts) == 1:
                                    game.console_text = '/' + sugg + ' '
                                else:
                                    cmd_part = parts[0][1:].lower()
                                    cmd_name = None
                                    for name, info in game.console_commands.items():
                                        if cmd_part == name or cmd_part in info['aliases']:
                                            cmd_name = name
                                            break
                                    if cmd_name and game.console_commands[cmd_name]['args'] and \
                                            game.console_commands[cmd_name]['args'][0] == 'item':
                                        game.console_text = parts[0] + ' ' + sugg + ' '
                                    else:
                                        parts[-1] = sugg
                                        game.console_text = ' '.join(parts) + ' '
                            game.update_console_suggestions()
                    elif event.key == K_UP:
                        if game.console_suggestions:
                            game.console_suggestion_idx = (game.console_suggestion_idx - 1) % len(
                                game.console_suggestions)
                        elif game.console_history:
                            game.console_history_idx = max(0, game.console_history_idx - 1)
                            game.console_text = game.console_history[game.console_history_idx]
                            game.update_console_suggestions()
                    elif event.key == K_DOWN:
                        if game.console_suggestions:
                            game.console_suggestion_idx = (game.console_suggestion_idx + 1) % len(
                                game.console_suggestions)
                        elif game.console_history:
                            game.console_history_idx = min(len(game.console_history), game.console_history_idx + 1)
                            if game.console_history_idx == len(game.console_history):
                                game.console_text = ""
                            else:
                                game.console_text = game.console_history[game.console_history_idx]
                            game.update_console_suggestions()
                    else:
                        if event.unicode.isprintable():
                            game.console_text += event.unicode
                            game.update_console_suggestions()
                elif game.show_save_menu:
                    if event.key == K_RETURN and game.save_name_input:
                        if game.save_manager.save_game(game, game.save_name_input):
                            game.notifications.append({'text': f'Игра сохранена как: {game.save_name_input}',
                                                       'start_time': pygame.time.get_ticks()})
                            game.show_save_menu = False
                            game.save_name_input = ""
                    elif event.key == K_BACKSPACE:
                        game.save_name_input = game.save_name_input[:-1]
                    elif event.unicode.isprintable():
                        if len(game.save_name_input) < 20:
                            game.save_name_input += event.unicode

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if game.show_menu:
                        if game.game_over:
                            if game.show_analysis:
                                continue_rect = game.draw_knowledge_analysis(screen)
                                if continue_rect.collidepoint(mouse_pos):
                                    game.show_analysis = False
                            elif game.analysis_button.is_clicked(mouse_pos):
                                game.show_analysis = True
                                game.analysis_scroll_offset = 0
                            elif game.restart_button.is_clicked(mouse_pos):
                                level_music.stop()
                                if 'level2_music' in globals() and level2_music: level2_music.stop()
                                defeat_music.stop()
                                if 'boss_music' in globals() and boss_music: boss_music.stop()
                                game.reset_game()
                                game.show_menu = False
                                game.active_menu = None
                                level_music.play(-1)
                            elif game.to_menu_button.is_clicked(mouse_pos):
                                defeat_music.stop()
                                menu_music.stop()
                                level_music.stop()
                                if 'level2_music' in globals() and level2_music: level2_music.stop()
                                if 'boss_music' in globals() and boss_music: boss_music.stop()
                                menu_music.play(-1)
                                game.show_menu = True
                                game.game_over = False
                        elif game.show_save_menu:
                            save_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 20, 200, 50, "Сохранить",
                                              (50, 50, 50))
                            cancel_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 90, 200, 50, "Отмена",
                                                (50, 50, 50))

                            if save_btn.is_clicked(mouse_pos) and game.save_name_input:
                                if game.save_manager.save_game(game, game.save_name_input):
                                    game.notifications.append({'text': f'Игра сохранена как: {game.save_name_input}',
                                                               'start_time': pygame.time.get_ticks()})
                                    game.show_save_menu = False
                                    game.save_name_input = ""
                            elif cancel_btn.is_clicked(mouse_pos):
                                game.show_save_menu = False
                                game.save_name_input = ""
                        elif game.show_load_menu:
                            cancel_btn = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] - 100, 200, 50, "Отмена",
                                                (50, 50, 50))

                            for i, save in enumerate(game.saves_list):
                                y_pos = WINDOW_SIZE[1] // 3 + i * 60
                                save_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, y_pos, 400, 50)
                                if save_rect.collidepoint(mouse_pos):
                                    if game.save_manager.load_game(game, save['name']):
                                        menu_music.stop()
                                        level_music.stop()
                                        defeat_music.stop()
                                        if 'boss_music' in globals() and boss_music: boss_music.stop()
                                        if 'level2_music' in globals() and level2_music: level2_music.stop()

                                        game.notifications.append({'text': f'Загружено: {save["name"]}',
                                                                   'start_time': pygame.time.get_ticks()})
                                        game.show_load_menu = False
                                        game.show_menu = False
                                        if game.current_room.type != RoomType.BOSS:
                                            if getattr(game, 'floor',
                                                       1) >= 2 and 'level2_music' in globals() and level2_music:
                                                level2_music.play(-1)
                                            else:
                                                level_music.play(-1)
                                        else:
                                            if 'boss_music' in globals() and boss_music: boss_music.play(-1)
                                    break

                            if cancel_btn.is_clicked(mouse_pos):
                                game.show_load_menu = False
                        elif game.show_settings:
                            menu_width = 460
                            menu_height = 550
                            menu_x = (WINDOW_SIZE[0] - menu_width) // 2
                            menu_y = (WINDOW_SIZE[1] - menu_height) // 2

                            def handle_settings_click():
                                # Музыка
                                if menu_y + 95 <= mouse_pos[1] <= menu_y + 135 and menu_x + 80 <= mouse_pos[0] <= menu_x + 380:
                                    game.music_volume = max(0.0, min(1.0, (mouse_pos[0] - (menu_x + 80)) / 300))
                                    menu_music.set_volume(game.music_volume)
                                    level_music.set_volume(game.music_volume)
                                    if 'level2_music' in globals() and level2_music: level2_music.set_volume(game.music_volume)
                                    if 'boss_music' in globals() and boss_music: boss_music.set_volume(game.music_volume)
                                    defeat_music.set_volume(game.music_volume)
                                    save_settings(game.music_volume, game.sound_volume, is_fullscreen, game.shake_intensity, game.show_damage_numbers, game.knowledge_points, game.meta_upgrades, game.unlocked_items)
                                    return True
                                # Звуки
                                elif menu_y + 170 <= mouse_pos[1] <= menu_y + 210 and menu_x + 80 <= mouse_pos[0] <= menu_x + 380:
                                    game.sound_volume = max(0.0, min(1.0, (mouse_pos[0] - (menu_x + 80)) / 300))
                                    game.apply_sound_volumes()
                                    save_settings(game.music_volume, game.sound_volume, is_fullscreen,
                                                  game.shake_intensity, game.show_damage_numbers, game.knowledge_points,
                                                  game.meta_upgrades, game.unlocked_items)
                                    return True
                                # Тряска
                                elif menu_y + 245 <= mouse_pos[1] <= menu_y + 285 and menu_x + 80 <= mouse_pos[0] <= menu_x + 380:
                                    game.shake_intensity = max(0.0, min(1.0, (mouse_pos[0] - (menu_x + 80)) / 300))
                                    save_settings(game.music_volume, game.sound_volume, is_fullscreen,game.shake_intensity, game.show_damage_numbers,game.knowledge_points, game.meta_upgrades, game.unlocked_items)
                                    return True
                                # Тумблер урона
                                elif menu_y + 320 <= mouse_pos[1] <= menu_y + 370 and menu_x + 80 <= mouse_pos[0] <= menu_x + 380:
                                    game.show_damage_numbers = not game.show_damage_numbers
                                    save_settings(game.music_volume, game.sound_volume, is_fullscreen,game.shake_intensity, game.show_damage_numbers,game.knowledge_points, game.meta_upgrades, game.unlocked_items)
                                    return True
                                return False

                            handle_settings_click()

                            # Кнопка Полный экран
                            game.fullscreen_button.rect.y = menu_y + 380
                            if game.fullscreen_button.is_clicked(mouse_pos):
                                is_fullscreen = not is_fullscreen
                                if is_fullscreen:
                                    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED | pygame.FULLSCREEN)
                                else:
                                    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED)
                                save_settings(game.music_volume, game.sound_volume, is_fullscreen,game.shake_intensity, game.show_damage_numbers, game.knowledge_points,game.meta_upgrades, game.unlocked_items)

                            # Кнопка Сброса прогресса с подтверждением
                            game.hard_reset_button.rect.y = menu_y + 440
                            if game.hard_reset_button.is_clicked(mouse_pos):
                                if getattr(game, 'confirming_reset', False):
                                    game.knowledge_points = 0
                                    game.meta_upgrades = {'hp': 0, 'speed': 0, 'damage': 0}
                                    game.unlocked_items = ['Pistol', 'Automatic Rifle', 'Speed Boots', 'Power Ring','Heart Crystal']
                                    save_settings(game.music_volume, game.sound_volume, is_fullscreen, game.shake_intensity, game.show_damage_numbers,game.knowledge_points, game.meta_upgrades, game.unlocked_items)
                                    game.notifications.append({'text': 'Прогресс сброшен!', 'start_time': pygame.time.get_ticks()})
                                    game.reset_game()
                                    game.confirming_reset = False
                                    game.hard_reset_button.text = "СБРОС ПРОГРЕССА"
                                    game.hard_reset_button.color = (200, 50, 50)
                                else:
                                    game.confirming_reset = True
                                    game.confirm_reset_timer = pygame.time.get_ticks()
                                    game.hard_reset_button.text = "ТОЧНО? (КЛИК)"
                                    game.hard_reset_button.color = (255, 0, 0)

                            # Кнопка Назад
                            back_button = Button(WINDOW_SIZE[0] // 2 - 100, menu_y + 490, 200, 50, "Назад",(150, 50, 50))
                            if back_button.is_clicked(mouse_pos):
                                game.show_settings = False
                                game.confirming_reset = False
                                game.hard_reset_button.text = "СБРОС ПРОГРЕССА"
                                game.hard_reset_button.color = (200, 50, 50)

                        elif getattr(game, 'show_meta_shop', False):
                            if getattr(game, 'meta_back_button', None) and game.meta_back_button.is_clicked(mouse_pos):
                                game.show_meta_shop = False
                                game.reset_game()  
                            else:
                                menu_width = 740
                                menu_height = 560
                                menu_x = (WINDOW_SIZE[0] - menu_width) // 2
                                menu_y = (WINDOW_SIZE[1] - menu_height) // 2

                                # Клики по покупке характеристик
                                upgrades = [("hp", 50, 10), ("speed", 40, 10), ("damage", 60, 10)]
                                y_offset = menu_y + 110
                                for key, base_cost, max_lvl in upgrades:
                                    lvl = game.meta_upgrades[key]
                                    cost = base_cost * (lvl + 1)
                                    if lvl < max_lvl:
                                        btn_rect = pygame.Rect(menu_x + 360, y_offset - 5, 100, 35)
                                        if btn_rect.collidepoint(mouse_pos) and game.knowledge_points >= cost:
                                            if 'powerup_sound' in globals() and powerup_sound: powerup_sound.play()
                                            game.knowledge_points -= cost
                                            game.meta_upgrades[key] += 1
                                            save_settings(game.music_volume, game.sound_volume, is_fullscreen, game.shake_intensity, game.show_damage_numbers, game.knowledge_points, game.meta_upgrades, game.unlocked_items)
                                    y_offset += 45

                                # Клики по покупке предметов
                                y_offset += 60
                                locked_items = [item for item in game.meta_unlockables if item['name'] not in game.unlocked_items]
                                for i, item in enumerate(locked_items[:5]):
                                    btn_rect = pygame.Rect(menu_x + 360, y_offset - 5, 100, 35)
                                    if btn_rect.collidepoint(mouse_pos) and game.knowledge_points >= item['cost']:
                                        if 'equip_sound' in globals() and equip_sound: equip_sound.play()
                                        game.knowledge_points -= item['cost']
                                        game.unlocked_items.append(item['name'])
                                        game.artifacts_pool = [a for a in game.all_artifacts if a.name in game.unlocked_items]
                                        game.weapons_pool = [w for w in game.all_weapons if w.name in game.unlocked_items]
                                        save_settings(game.music_volume, game.sound_volume, is_fullscreen,game.shake_intensity, game.show_damage_numbers,game.knowledge_points, game.meta_upgrades, game.unlocked_items)
                                    y_offset += 45

                        elif game.active_menu == "escape":
                            back_button = Button(WINDOW_SIZE[0] // 2 - 100, WINDOW_SIZE[1] // 2 + 310, 200, 50,
                                                    "Назад", (50, 50, 50))
                            if game.restart_button.is_clicked(mouse_pos):
                                level_music.stop()
                                if 'level2_music' in globals() and level2_music: level2_music.stop()
                                defeat_music.stop()
                                if 'boss_music' in globals() and boss_music: boss_music.stop()
                                game.reset_game()
                                game.show_menu = False
                                game.active_menu = None
                                level_music.play(-1)
                            elif game.settings_button.is_clicked(mouse_pos):
                                game.show_settings = True
                            elif game.to_menu_button.is_clicked(mouse_pos):
                                level_music.stop()
                                if 'level2_music' in globals() and level2_music: level2_music.stop()
                                defeat_music.stop()
                                if 'boss_music' in globals() and boss_music: boss_music.stop()
                                game.show_menu = True
                                game.active_menu = None
                                menu_music.stop()
                                menu_music.play(-1)
                            elif game.save_button.is_clicked(mouse_pos):
                                game.show_save_menu = True
                                game.save_name_input = ""
                            elif game.load_button.is_clicked(mouse_pos):
                                game.show_load_menu = True
                                game.saves_list = game.save_manager.get_save_files()
                            elif back_button.is_clicked(mouse_pos):
                                game.show_menu = False
                                game.active_menu = None
                        elif getattr(game, 'show_info', False):
                            if getattr(game, 'info_back_button', None) and game.info_back_button.is_clicked(
                                        mouse_pos):
                                game.show_info = False
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and game.play_button.is_clicked(
                                    mouse_pos):
                            menu_music.stop()
                            level_music.stop()
                            if 'level2_music' in globals() and level2_music: level2_music.stop()
                            defeat_music.stop()
                            if 'boss_music' in globals() and boss_music: boss_music.stop()
                            game.show_menu = False
                            if game.current_room.type == RoomType.BOSS:
                                if 'boss_music' in globals() and boss_music: boss_music.play(-1)
                            else:
                                if getattr(game, 'floor', 1) >= 2 and 'level2_music' in globals() and level2_music:
                                    level2_music.play(-1)
                                else:
                                    level_music.play(-1)
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and getattr(
                            game, 'meta_shop_button', None) and game.meta_shop_button.is_clicked(mouse_pos):
                            game.show_meta_shop = True
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and getattr(
                            game, 'info_button', None) and game.info_button.is_clicked(mouse_pos):
                            game.show_info = True
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and game.settings_button.is_clicked(
                                    mouse_pos):
                            game.show_settings = not game.show_settings
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and game.save_button.is_clicked(
                                    mouse_pos):
                            game.show_save_menu = True
                            game.save_name_input = ""
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and game.load_button.is_clicked(
                                    mouse_pos):
                            game.show_load_menu = True
                            game.saves_list = game.save_manager.get_save_files()
                        elif not getattr(game, 'show_settings', False) and not getattr(game, 'show_meta_shop',
                                                                                           False) and not getattr(game,
                                                                                                                  'show_info',
                                                                                                                  False) and not game.show_load_menu and game.exit_button.is_clicked(
                                    mouse_pos):
                            running = False
                    else:
                        if game.player.inventory.visible:
                            game.player.inventory.handle_click(mouse_pos)
                        elif not game.show_menu:
                            shop_open = (game.current_room.type == RoomType.SHOP and hasattr(game.current_room,
                                                                                             'merchant') and game.current_room.merchant.selected_item is not None)
                            if not shop_open:
                                if game.player.inventory.equipped['weapon']:
                                    weapon = game.player.inventory.equipped['weapon']
                                    if weapon.can_shoot(pygame.time.get_ticks()):
                                        game.player.shoot(mouse_pos[0], mouse_pos[1], game.current_room)
                                        weapon.last_shot = pygame.time.get_ticks()

       
        if pygame.mouse.get_pressed()[0] and not game.show_menu and not game.game_over and not game.console_active:
            if not game.player.inventory.visible:
                shop_open = (game.current_room.type == RoomType.SHOP and hasattr(game.current_room,'merchant') and game.current_room.merchant.selected_item is not None)
                if not shop_open:
                    if game.player.inventory.equipped['weapon']:
                        weapon = game.player.inventory.equipped['weapon']
                        if weapon.is_automatic and weapon.can_shoot(pygame.time.get_ticks()):
                            game.player.shoot(mouse_pos[0], mouse_pos[1], game.current_room)
                            weapon.last_shot = pygame.time.get_ticks()

        # Пауза логики, если открыт инвентарь или активно меню
        if not game.show_menu and not game.game_over and not game.console_active and not game.player.inventory.visible:
            keys = pygame.key.get_pressed()
            dx = keys[K_d] - keys[K_a]
            dy = keys[K_s] - keys[K_w]

            # Обработка рывка
            if (keys[K_SPACE] or keys[K_LSHIFT]) and not game.player.is_dashing:
                if game.player.start_dash(dx, dy, mouse_pos):
                    if 'dash_sound' in globals() and dash_sound:
                        dash_sound.play()

            game.player.move(dx, dy, game.current_room.walls)
            game.player.update(mouse_pos)
            game.check_room_transition()

            if game.current_room.type == RoomType.NORMAL and not game.current_room.cleared:
                if not game.current_room.timer_active:
                    game.current_room.time_limit = 25 + game.player.time_bonus
                    game.current_room.start_timer()
                if game.current_room.update_timer():
                    # При истечении таймера игрок получает урон, но комната НЕ зачищается
                    game.player.health -= 1
                    game.player.last_damage_time = pygame.time.get_ticks()
                    game.notifications.append(
                        {'text': 'Время вышло! -0.5 сердца', 'start_time': pygame.time.get_ticks()})
                    if hurt_sound:
                        hurt_sound.play()
                    game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)

            for bullet in game.player.bullets[:]:
                bullet.move()
                if (bullet.x < 0 or bullet.x > WINDOW_SIZE[0] or bullet.y < 0 or bullet.y > WINDOW_SIZE[1]):
                    game.player.bullets.remove(bullet)
                    continue

                wall_hit = False
                for wall in game.current_room.walls:
                    if (
                            bullet.x > wall.x and bullet.x < wall.x + wall.size and bullet.y > wall.y and bullet.y < wall.y + wall.size):
                        wall_hit = True
                        break

                if wall_hit:
                    if bullet.is_explosive:
                        if 'explosion_sound' in globals() and explosion_sound:
                            explosion_sound.play()
                        game.current_room.explosions.append(Explosion(bullet.x, bullet.y))
                        game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)

                        # Черный след от взрыва на полу
                        scorch = pygame.Surface((100, 100), pygame.SRCALPHA)
                        pygame.draw.circle(scorch, (20, 20, 20, 180), (50, 50), random.randint(35, 45))
                        game.floor_surface.blit(scorch, (bullet.x - 50, bullet.y - 50))

                        # Частицы от разрушения препятствия/взрыва
                        for _ in range(15):
                            game.current_room.particles.append(Particle(bullet.x, bullet.y, ORANGE))
                            game.current_room.particles.append(
                                Particle(bullet.x, bullet.y, (100, 100, 100)))

                        blast_radius = 250
                        for aoe_enemy in game.current_room.enemies:
                            dist = math.sqrt((aoe_enemy.x - bullet.x) ** 2 + (aoe_enemy.y - bullet.y) ** 2)
                            if dist < blast_radius:
                                blast_angle = math.atan2(aoe_enemy.y + aoe_enemy.size // 2 - bullet.y,
                                                         aoe_enemy.x + aoe_enemy.size // 2 - bullet.x)
                                knockback_force = 60 * (1 - dist / blast_radius)
                                aoe_enemy.apply_knockback(blast_angle, knockback_force, game.current_room.walls,
                                                          game.current_room.enemies)

                    if bullet in game.player.bullets:
                        game.player.bullets.remove(bullet)
                    continue

                for enemy in game.current_room.enemies[:]:
                    # Призрак неуязвим в состоянии невидимости
                    if enemy.enemy_type == "ghost" and enemy.is_ghost:
                        continue

                    if (
                            bullet.x > enemy.x and bullet.x < enemy.x + enemy.size and bullet.y > enemy.y and bullet.y < enemy.y + enemy.size):

                        if getattr(enemy, 'shield_active', False):
                            bullet.angle += math.pi + random.uniform(-0.2, 0.2)
                            bullet.color = RED
                            game.current_room.enemy_bullets.append(bullet)
                            if bullet in game.player.bullets:
                                game.player.bullets.remove(bullet)
                            continue

                        if getattr(enemy, 'invulnerable', False):
                            if bullet in game.player.bullets:
                                game.player.bullets.remove(bullet)
                            continue

                        if bullet.is_explosive:
                            if 'explosion_sound' in globals() and explosion_sound:
                                explosion_sound.set_volume(game.sound_volume)
                                explosion_sound.play()
                            game.current_room.explosions.append(Explosion(bullet.x, bullet.y))
                            game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)

                            # Черный след от взрыва на полу
                            scorch = pygame.Surface((100, 100), pygame.SRCALPHA)
                            pygame.draw.circle(scorch, (20, 20, 20, 180), (50, 50), random.randint(35, 45))
                            game.floor_surface.blit(scorch, (bullet.x - 50, bullet.y - 50))

                            # Огненные частицы от взрыва
                            for _ in range(15):
                                game.current_room.particles.append(Particle(bullet.x, bullet.y, ORANGE))

                            blast_radius = 250
                            for aoe_enemy in game.current_room.enemies:
                                dist = math.sqrt((aoe_enemy.x - bullet.x) ** 2 + (aoe_enemy.y - bullet.y) ** 2)
                                if dist < blast_radius:
                                    blast_angle = math.atan2(aoe_enemy.y + aoe_enemy.size // 2 - bullet.y,
                                                             aoe_enemy.x + aoe_enemy.size // 2 - bullet.x)
                                    knockback_force = 60 * (1 - dist / blast_radius)  # Усилили отбрасывание
                                    aoe_enemy.apply_knockback(blast_angle, knockback_force, game.current_room.walls,
                                                              game.current_room.enemies)

                        enemy.health -= bullet.damage
                        if getattr(enemy, 'enemy_type', '') == 'boss':
                            if enemy.phase == 1 and enemy.health < enemy.max_health * 0.66:
                                enemy.health = enemy.max_health * 0.66
                            elif enemy.phase == 2 and enemy.health < enemy.max_health * 0.33:
                                enemy.health = enemy.max_health * 0.33
                            elif enemy.phase == 3 and enemy.health <= 0 and getattr(enemy, 'state', '') != 'dying':
                                enemy.health = 1
                                enemy.state = 'dying'
                                enemy.invulnerable = True
                                enemy.death_timer = pygame.time.get_ticks()
                                if 'boss_death_snd' in globals() and boss_death_snd: boss_death_snd.play()
                        enemy.hit_timer = pygame.time.get_ticks()

                        # Наложение стихий
                        if bullet.effect == 'burn':
                            enemy.burn_time = 3000
                        elif bullet.effect == 'freeze':
                            enemy.freeze_time = 3000

                        if not bullet.is_explosive:
                            enemy.apply_knockback(bullet.angle, 10, game.current_room.walls, game.current_room.enemies)

                        # Спавн всплывающего урона
                        color = WHITE
                        if enemy.enemy_type == "math":
                            color = RED
                        elif enemy.enemy_type == "boss":
                            color = PURPLE
                        game.current_room.damage_texts.append(
                            DamageText(enemy.x + enemy.size // 2, enemy.y, bullet.damage, color))

                        if enemy.health <= 0:
                            if enemy.math_value is not None:
                                game.player.record_math_result(game.current_room.math_problem, enemy.is_correct)

                                for _ in range(25):
                                    game.current_room.particles.append(
                                        Particle(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2,
                                                 GREEN if enemy.is_correct else RED))

                                if enemy.is_correct:
                                    for e in game.current_room.enemies[:]:
                                        if e != enemy and getattr(e, 'math_value', None) is not None:
                                            # В комнате босса монеты за врагов НЕ выпадают
                                            if game.current_room.type != RoomType.BOSS:
                                                game.current_room.coins.append(Coin(e.x, e.y, e.money))
                                            if random.random() < 0.10:
                                                if not hasattr(game.current_room,
                                                               'medkits'): game.current_room.medkits = []
                                                game.current_room.medkits.append(
                                                    Medkit(e.x, e.y, random.choice([1, 2])))
                                            for _ in range(5):
                                                game.current_room.particles.append(
                                                    Particle(e.x + e.size // 2, e.y + e.size // 2, e.color))

                                    game.current_room.enemies = [e for e in game.current_room.enemies if
                                                                 getattr(e, 'math_value', None) is None]

                                    for e in game.current_room.enemies:
                                        if e.enemy_type == 'boss':
                                            e.state = 'active'
                                            e.invulnerable = False
                                            e.shield_active = False

                                    game.screen_shake = max(getattr(game, 'screen_shake', 0), 8)
                                    success = game.player.stats.get_success_rate()
                                    reward = 35 if success >= 80 else (25 if success >= 50 else 15)
                                    game.player.money += reward

                                    # мета-валюта
                                    kp_reward = game.current_room.difficulty * 3
                                    game.knowledge_points += kp_reward
                                    save_settings(game.music_volume, game.sound_volume, is_fullscreen,
                                                  game.shake_intensity, game.show_damage_numbers, game.knowledge_points,
                                                  game.meta_upgrades, game.unlocked_items)

                                    game.notifications.append(
                                        {'text': f'Правильно! +{reward} монет, +{kp_reward} ОЗ',
                                         'start_time': pygame.time.get_ticks()})

                                    if game.current_room.type != RoomType.BOSS:
                                        for wall in game.current_room.walls:
                                            if wall.is_obstacle:
                                                wall.movable = True
                                else:
                                    game.player.health -= 1
                                    game.player.last_damage_time = pygame.time.get_ticks()
                                    game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)
                                    if hurt_sound:
                                        hurt_sound.set_volume(game.sound_volume)
                                        hurt_sound.play()
                                    game.notifications.append(
                                        {'text': 'Неверно! -0.5 сердца', 'start_time': pygame.time.get_ticks()})
                                    game.current_room.enemies.remove(enemy)
                            else:
                                for _ in range(10):
                                    game.current_room.particles.append(
                                        Particle(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2, enemy.color))
                                game.screen_shake = max(getattr(game, 'screen_shake', 0), 5)
                                game.current_room.enemies.remove(enemy)
                                if game.current_room.type != RoomType.BOSS:
                                    game.current_room.coins.append(Coin(enemy.x, enemy.y, enemy.money))
                                if random.random() < 0.10:
                                    if not hasattr(game.current_room, 'medkits'): game.current_room.medkits = []
                                    game.current_room.medkits.append(Medkit(enemy.x, enemy.y, random.choice([1, 2])))

                                if enemy.enemy_type == 'boss':
                                    game.current_room.add_portal(RoomType.NEXT_FLOOR)
                                    if 'boss_music' in globals() and boss_music:
                                        boss_music.stop()

                        if bullet in game.player.bullets:
                            game.player.bullets.remove(bullet)
                        break

            # Логика вражеских пуль
            for bullet in game.current_room.enemy_bullets[:]:
                bullet.move()
                if (bullet.x < 0 or bullet.x > WINDOW_SIZE[0] or bullet.y < 0 or bullet.y > WINDOW_SIZE[1]):
                    game.current_room.enemy_bullets.remove(bullet)
                    continue

                wall_hit = False
                for wall in game.current_room.walls:
                    if (bullet.x > wall.x and bullet.x < wall.x + wall.size and bullet.y > wall.y and bullet.y < wall.y + wall.size):
                        game.current_room.enemy_bullets.remove(bullet)
                        wall_hit = True
                        break

                if wall_hit:
                    continue

                # Попадание в игрока
                if (bullet.x > game.player.x and bullet.x < game.player.x + game.player.size and
                        bullet.y > game.player.y and bullet.y < game.player.y + game.player.size):
                    if not getattr(game.player, 'is_dying', False) and not game.player.is_dashing and not game.player.is_cloaked and pygame.time.get_ticks() - game.player.last_damage_time > 1000:
                        game.player.health -= 1
                        game.player.last_damage_time = pygame.time.get_ticks()
                        game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)
                        if hurt_sound:
                            hurt_sound.set_volume(game.sound_volume)
                            hurt_sound.play()
                    if bullet in game.current_room.enemy_bullets:
                        game.current_room.enemy_bullets.remove(bullet)

            for enemy in game.current_room.enemies[:]:
                enemy.move_towards(game.player, game.current_room.walls, game.current_room.enemies)

                if getattr(enemy, 'enemy_type', '') == 'boss' and enemy.phase == 3 and enemy.health <= 0 and getattr(
                        enemy, 'state', '') != 'dying':
                    enemy.health = 1
                    enemy.state = 'dying'
                    enemy.invulnerable = True
                    enemy.death_timer = pygame.time.get_ticks()
                    if 'boss_death_snd' in globals() and boss_death_snd: boss_death_snd.play()

                # Проверка смерти от горения или других эффектов вне пуль
                if enemy.health <= 0:
                    if enemy.math_value is not None:
                        game.player.record_math_result(game.current_room.math_problem, enemy.is_correct)

                        for _ in range(25):
                            game.current_room.particles.append(
                                Particle(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2,
                                         GREEN if enemy.is_correct else RED))

                        if enemy.is_correct:
                            for e in game.current_room.enemies[:]:
                                if e != enemy and getattr(e, 'math_value', None) is not None:
                                    if game.current_room.type != RoomType.BOSS:
                                        game.current_room.coins.append(Coin(e.x, e.y, e.money))
                                    if random.random() < 0.10:
                                        if not hasattr(game.current_room, 'medkits'): game.current_room.medkits = []
                                        game.current_room.medkits.append(Medkit(e.x, e.y, random.choice([1, 2])))
                                    for _ in range(5):
                                        game.current_room.particles.append(
                                            Particle(e.x + e.size // 2, e.y + e.size // 2, e.color))

                            game.current_room.enemies = [e for e in game.current_room.enemies if
                                                         getattr(e, 'math_value', None) is None]

                            for e in game.current_room.enemies:
                                if e.enemy_type == 'boss':
                                    e.state = 'active'
                                    e.invulnerable = False
                                    e.shield_active = False

                            game.screen_shake = max(getattr(game, 'screen_shake', 0), 8)
                            success = game.player.stats.get_success_rate()
                            reward = 35 if success >= 80 else (25 if success >= 50 else 15)
                            game.player.money += reward
                            game.notifications.append(
                                {'text': f'Правильно! +{reward} монет', 'start_time': pygame.time.get_ticks()})

                            if game.current_room.type != RoomType.BOSS:
                                for wall in game.current_room.walls:
                                    if wall.is_obstacle:
                                        wall.movable = True
                        else:
                            game.player.health -= 1
                            game.player.last_damage_time = pygame.time.get_ticks()
                            game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)
                            if hurt_sound:
                                hurt_sound.set_volume(game.sound_volume)
                                hurt_sound.play()
                            game.notifications.append(
                                {'text': 'Неверно! -0.5 сердца', 'start_time': pygame.time.get_ticks()})
                            game.current_room.enemies.remove(enemy)
                    else:
                        for _ in range(10):
                            game.current_room.particles.append(
                                Particle(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2, enemy.color))
                        game.screen_shake = max(getattr(game, 'screen_shake', 0), 5)
                        game.current_room.enemies.remove(enemy)
                        if game.current_room.type != RoomType.BOSS:
                            game.current_room.coins.append(Coin(enemy.x, enemy.y, enemy.money))
                        if random.random() < 0.10:
                            if not hasattr(game.current_room, 'medkits'): game.current_room.medkits = []
                            game.current_room.medkits.append(Medkit(enemy.x, enemy.y, random.choice([1, 2])))

                        if enemy.enemy_type == 'boss':
                            game.current_room.add_portal(RoomType.NEXT_FLOOR)
                            if 'boss_music' in globals() and boss_music:
                                boss_music.stop()
                    continue

                # Логика стрельбы снайпера
                if enemy.enemy_type == "sniper":
                    if pygame.time.get_ticks() - enemy.last_shot_time > enemy.shoot_cooldown:
                        enemy.last_shot_time = pygame.time.get_ticks()
                        if 'shoot_sound' in globals() and shoot_sound:
                            shoot_sound.set_volume(0.15 * game.sound_volume)  # Снайпер стреляет тише игрока
                            shoot_sound.play()
                        dx = (game.player.x + game.player.size // 2) - (enemy.x + enemy.size // 2)
                        dy = (game.player.y + game.player.size // 2) - (enemy.y + enemy.size // 2)
                        angle = math.atan2(dy, dx)
                        b = Bullet(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2, angle, 1)
                        b.color = ORANGE
                        b.speed = 6
                        game.current_room.enemy_bullets.append(b)

                p_center = (game.player.x + game.player.size // 2, game.player.y + game.player.size // 2)
                e_center = (enemy.x + enemy.size // 2, enemy.y + enemy.size // 2)

                if (abs(p_center[0] - e_center[0]) < enemy.hitbox_size // 2 + game.player.size // 2 and
                        abs(p_center[1] - e_center[1]) < enemy.hitbox_size // 2 + game.player.size // 2 and
                        game.current_room.type != RoomType.SHOP):
                    if not getattr(game.player, 'is_dying', False) and not game.player.is_dashing and not game.player.is_cloaked and pygame.time.get_ticks() - game.player.last_damage_time > 1000:
                        game.player.health -= 1
                        game.player.last_damage_time = pygame.time.get_ticks()
                        game.screen_shake = max(getattr(game, 'screen_shake', 0), 15)
                        if hurt_sound:
                            hurt_sound.set_volume(game.sound_volume)
                            hurt_sound.play()

            player_rect = pygame.Rect(game.player.x, game.player.y, game.player.size, game.player.size)
            for coin in game.current_room.coins[:]:
                if player_rect.colliderect(coin.rect):
                    if 'pickup_coin_sound' in globals() and pickup_coin_sound:
                        pickup_coin_sound.set_volume(game.sound_volume)
                        pickup_coin_sound.play()
                    game.player.money += coin.amount
                    game.current_room.coins.remove(coin)

            if hasattr(game.current_room, 'medkits'):
                for medkit in game.current_room.medkits[:]:
                    if player_rect.colliderect(medkit.rect):
                        if game.player.health < game.player.total_max_health:
                            if 'powerup_sound' in globals() and powerup_sound:
                                powerup_sound.set_volume(game.sound_volume)
                                powerup_sound.play()
                            game.player.health = min(game.player.total_max_health,
                                                     game.player.health + medkit.heal_amount)
                            game.current_room.medkits.remove(medkit)
                            game.notifications.append({'text': f'+ Здоровье!', 'start_time': pygame.time.get_ticks()})

            if game.player.health <= 0 and not getattr(game.player, 'is_dying', False):
                game.player.is_dying = True
                game.player.health = 0
                game.player.death_anim_timer = pygame.time.get_ticks()
                if 'player_death_snd' in globals() and player_death_snd:
                    player_death_snd.play()
                level_music.stop()
                if 'level2_music' in globals() and level2_music: level2_music.stop()
                if 'boss_music' in globals() and boss_music: boss_music.stop()
                menu_music.stop()
                defeat_music.play(-1)
                defeat_music.set_volume(game.music_volume)

            game.check_room_completion()

            if game.current_room.type == RoomType.TREASURE:
                for chest in game.current_room.chests:
                    chest.check_interaction(game.player)
                    if chest.state == "closed" and chest.in_range and keys[K_e]:
                        chest.open()
                        game.player.money += 50
                        if chest.item:
                            if isinstance(chest.item, Weapon) or isinstance(chest.item, Artifact):
                                game.player.inventory.add_item(chest.item)
                                game.notifications.append(
                                    {'text': f'Получено: {chest.item.name}', 'start_time': pygame.time.get_ticks()})

        elif (game.player.inventory.visible or game.active_menu == "escape") and game.current_room.timer_active:
         
            game.current_room.timer_start += clock.get_time()

        screen.fill(CYAN)

        if game.show_menu:
            game.draw_menu(screen, mouse_pos)
            if game.show_settings:
                menu_height = 620
                menu_y = (WINDOW_SIZE[1] - menu_height) // 2
                back_button = Button(WINDOW_SIZE[0] // 2 - 100, menu_y + 550, 200, 50, "Назад", (150, 50, 50))
                back_button.draw(screen)
                if back_button.rect.collidepoint(mouse_pos) or game.fullscreen_button.rect.collidepoint(mouse_pos):
                    screen.blit(cursor_hand, (mouse_pos[0] - 16, mouse_pos[1] - 16))
                else:
                    screen.blit(cursor, (mouse_pos[0] - 16, mouse_pos[1] - 16))
        else:
            display_surface = pygame.Surface(WINDOW_SIZE)

            temp_floor = floor_texture.copy()
            temp_wall = wall_texture.copy()
            temp_obs = obstacle_texture.copy()
            if getattr(game, 'floor', 1) > 1:
                tint = (180, 100, 220)
                temp_floor.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
                temp_wall.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
                temp_obs.fill(tint, special_flags=pygame.BLEND_RGB_MULT)

            temp_floor_surface = pygame.Surface(WINDOW_SIZE)
            for x, y in game.current_room.floor_positions:
                temp_floor_surface.blit(temp_floor, (x, y))
            display_surface.blit(temp_floor_surface, (0, 0))

            for wall in game.current_room.walls:
                if wall.is_obstacle:
                    display_surface.blit(temp_obs, (wall.x, wall.y))
                else:
                    display_surface.blit(temp_wall, (wall.x, wall.y))

            current_ticks = pygame.time.get_ticks()
            for portal in game.current_room.portals:
                p_type = portal['type']
                if 'portal_frames' in globals() and portal_frames[p_type]:
                    frame_idx = (current_ticks // 100) % len(portal_frames[p_type])
                    display_surface.blit(portal_frames[p_type][frame_idx], (portal['x'], portal['y']))
                else:
                    color = {RoomType.NORMAL: BLUE, RoomType.TREASURE: GOLD, RoomType.SHOP: GREEN, RoomType.BOSS: RED}[
                        p_type]
                    pygame.draw.circle(display_surface, color,
                                       (portal['x'] + portal['size'] // 2, portal['y'] + portal['size'] // 2),
                                       portal['size'] // 2)
                    pygame.draw.circle(display_surface, WHITE,
                                       (portal['x'] + portal['size'] // 2, portal['y'] + portal['size'] // 2),
                                       portal['size'] // 2, 2)
            for chest in game.current_room.chests:
                chest.draw(display_surface)

            if hasattr(game.current_room, 'medkits'):
                for medkit in game.current_room.medkits:
                    medkit.draw(display_surface)

            # Обновление и отрисовка гильз и частиц на полу
            if hasattr(game.current_room, 'shells'):
                for shell in game.current_room.shells[:]:
                    shell.update()
                    shell.draw(display_surface)
                    if shell.lifetime <= 0:
                        game.current_room.shells.remove(shell)
            if hasattr(game.current_room, 'particles'):
                for particle in game.current_room.particles[:]:
                    particle.update()
                    particle.draw(display_surface)
                    if particle.lifetime <= 0:
                        game.current_room.particles.remove(particle)

            if hasattr(game.current_room, 'explosions'):
                current_ticks = pygame.time.get_ticks()
                for exp in game.current_room.explosions[:]:
                    exp.update(current_ticks)
                    exp.draw(display_surface)
                    if exp.is_finished:
                        game.current_room.explosions.remove(exp)

            for enemy in game.current_room.enemies:
                hint_active = getattr(game, 'hint_mode', False)
                enemy.draw(display_surface, hint_active)
            for bullet in game.player.bullets:
                bullet.draw(display_surface)
            for bullet in game.current_room.enemy_bullets:
                bullet.draw(display_surface)
            for coin in game.current_room.coins:
                coin.draw(display_surface)

                # Обновление и отрисовка всплывающего урона
            for dmg_text in game.current_room.damage_texts[:]:
                dmg_text.update()
                if getattr(game, 'show_damage_numbers', True):
                    dmg_text.draw(display_surface)
                if dmg_text.lifetime <= 0:
                    game.current_room.damage_texts.remove(dmg_text)

            game.player.draw(display_surface)

            # Применение тряски экрана (Screen Shake с учетом интенсивности)
            shake_x, shake_y = 0, 0
            if hasattr(game, 'screen_shake') and game.screen_shake > 0:
                actual_shake = game.screen_shake * getattr(game, 'shake_intensity', 1.0)
                if actual_shake > 0:
                    shake_x = random.randint(-int(actual_shake), int(actual_shake))
                    shake_y = random.randint(-int(actual_shake), int(actual_shake))
                game.screen_shake = max(0, game.screen_shake - 0.5)  # Затухание тряски

            screen.blit(display_surface, (shake_x, shake_y))

            if game.current_room.type in [RoomType.NORMAL, RoomType.BOSS] and game.current_room.math_problem:
                font = pygame.font.Font('PixelizerBold.ttf', 28)
                problem_text = font.render(game.current_room.math_problem.condition, True, WHITE)

                # Темная полупрозрачная подложка для читаемости
                text_bg = pygame.Surface((problem_text.get_width() + 40, problem_text.get_height() + 10),
                                         pygame.SRCALPHA)
                pygame.draw.rect(text_bg, (0, 0, 0, 180), text_bg.get_rect(), border_radius=8)

                text_x = WINDOW_SIZE[0] // 2 - problem_text.get_width() // 2
                text_y = 85

                screen.blit(text_bg, (text_x - 20, text_y - 5))
                screen.blit(problem_text, (text_x, text_y))

            if game.current_room.type == RoomType.NORMAL and game.current_room.timer_active:
                font = pygame.font.Font('PixelizerBold.ttf', 36)
                time_text = font.render(f'Time: {int(game.current_room.time_remaining)}', True, WHITE)
                screen.blit(time_text, (WINDOW_SIZE[0] - 150, 175))

            font = pygame.font.Font('PixelizerBold.ttf', 36)

            # Отрисовка сердечек с переносом строк
            start_x = 40
            start_y = 120
            drawn_health = 0
            current_x = start_x
            heart_spacing = 55

            while drawn_health + 2 <= game.player.health:
                if heart_img:
                    screen.blit(heart_img, (current_x, start_y))
                current_x += heart_spacing
                drawn_health += 2

                # Перенос на новую строку после 4 сердец, чтобы не закрывать задачу по центру
                if current_x >= start_x + heart_spacing * 4:
                    current_x = start_x
                    start_y += 45

            if game.player.health > drawn_health:
                if halfheart_img:
                    screen.blit(halfheart_img, (current_x, start_y))

            money_y = max(160, start_y + 70)
            money_val_text = font.render(str(game.player.money), True, WHITE)
            bg_width = money_val_text.get_width() + 50
            pygame.draw.rect(screen, (0, 0, 0, 180), (35, money_y - 5, bg_width, 40), border_radius=8)
            pygame.draw.rect(screen, GOLD, (35, money_y - 5, bg_width, 40), 2, border_radius=8)
            if 'coin_frames' in globals() and coin_frames:
                screen.blit(pygame.transform.scale(coin_frames[0], (24, 24)), (45, money_y + 3))
            screen.blit(money_val_text, (75, money_y))

            rooms_text = font.render(f'Rooms: {game.rooms_cleared}', True, WHITE)
            rooms_text_rect = rooms_text.get_rect(center=(WINDOW_SIZE[0] // 2, 30))
            screen.blit(rooms_text, rooms_text_rect)

            # Отрисовка миникарты
            game.draw_minimap(screen)

            if game.player.inventory.equipped['weapon']:
                weapon = game.player.inventory.equipped['weapon']
                ammo_text = font.render(f'Ammo: {weapon.current_ammo}/{weapon.ammo_capacity}', True, WHITE)
                ammo_rect = ammo_text.get_rect()
                screen.blit(ammo_text, (WINDOW_SIZE[0] - ammo_rect.width - 70, WINDOW_SIZE[1] - 70))

                # Отрисовка магазина
            if game.current_room.type == RoomType.SHOP and hasattr(game.current_room, 'merchant'):
                merchant = game.current_room.merchant
                merchant.draw(screen, game.player)

                keys = pygame.key.get_pressed()
                if merchant.check_collision(game.player):
                    if keys[K_e]:
                        merchant.selected_item = 0
                    elif merchant.selected_item is not None:
                        mouse_pos = pygame.mouse.get_pos()
                        clicked_item = merchant.get_clicked_item(mouse_pos)
                        if clicked_item is not None and pygame.mouse.get_pressed()[0]:
                            if merchant.try_purchase(game.player, clicked_item):
                                if 'powerup_sound' in globals() and powerup_sound:
                                    powerup_sound.play()
                                game.notifications.append(
                                    {'text': 'Улучшение куплено!', 'start_time': pygame.time.get_ticks()})
                        if merchant.selected_item is not None:
                            menu_width = 460
                            menu_height = 340
                            menu_x = (WINDOW_SIZE[0] - menu_width) // 2
                            menu_y = (WINDOW_SIZE[1] - menu_height) // 2
                            close_btn_rect = pygame.Rect(menu_x + menu_width - 35, menu_y + 5, 30, 30)
                            if close_btn_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                                merchant.selected_item = None
                else:
                    merchant.selected_item = None

                # Отрисовка инвентаря поверх всего интерфейса
            game.player.inventory.draw(screen, game.player)

            if game.console_active:
                surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                pygame.draw.rect(surface, (0, 0, 0, 204), (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
                screen.blit(surface, (0, 0))

                # Отрисовка лога консоли (истории)
                if hasattr(game, 'console_log') and game.console_log:
                    log_h = len(game.console_log) * 25
                    log_y = WINDOW_SIZE[1] - 45 - log_h
                    if game.console_suggestions:
                        log_y -= min(7, len(game.console_suggestions)) * 25 + 10

                    pygame.draw.rect(screen, (20, 20, 20, 180), (10, log_y, WINDOW_SIZE[0] - 20, log_h),
                                     border_radius=5)
                    for i, msg in enumerate(game.console_log):
                        msg_text = game.console_font.render(msg, True, (200, 200, 200))
                        screen.blit(msg_text, (15, log_y + i * 25 + 2))

                # Отрисовка подсказок со скроллом
                if game.console_suggestions:
                    start_idx = max(0, min(game.console_suggestion_idx - 3, len(game.console_suggestions) - 7))
                    visible_suggs = game.console_suggestions[start_idx: start_idx + 7]

                    sugg_h = len(visible_suggs) * 25
                    sugg_y = WINDOW_SIZE[1] - 45 - sugg_h
                    pygame.draw.rect(screen, (30, 30, 35), (10, sugg_y, 300, sugg_h), border_radius=5)
                    pygame.draw.rect(screen, CYAN, (10, sugg_y, 300, sugg_h), 1, border_radius=5)

                    for i, sugg in enumerate(visible_suggs):
                        actual_idx = start_idx + i
                        color = GOLD if actual_idx == game.console_suggestion_idx else WHITE
                        prefix = "> " if actual_idx == game.console_suggestion_idx else "  "
                        s_text = game.console_font.render(prefix + sugg, True, color)
                        screen.blit(s_text, (15, sugg_y + i * 25 + 2))

                pygame.draw.rect(screen, (50, 50, 50), (10, WINDOW_SIZE[1] - 40, WINDOW_SIZE[0] - 20, 30))
                text = game.console_font.render(game.console_text, True, WHITE)
                screen.blit(text, (15, WINDOW_SIZE[1] - 35))

            current_time = pygame.time.get_ticks()
            game.notifications = [n for n in game.notifications if current_time - n['start_time'] < 2000]
            font = pygame.font.Font('PixelizerBold.ttf', 24)
            for i, notification in enumerate(game.notifications):
                text = font.render(notification['text'], True, WHITE)
                screen.blit(text, (10, 250 + i * 30))

            menu_width = 400
            menu_height = 300
            menu_x = (WINDOW_SIZE[0] - menu_width) // 2
            menu_y = (WINDOW_SIZE[1] - menu_height) // 2

            use_hand_cursor = False

            if game.player.inventory.visible:
                panel_width = 700
                panel_height = 480
                panel_x = (WINDOW_SIZE[0] - panel_width) // 2
                panel_y = (WINDOW_SIZE[1] - panel_height) // 2
                stats_x = panel_x + 30
                stats_y = panel_y + 80
                inv_x = stats_x + 280
                inv_y = stats_y
                equipped_y = inv_y + 30
                grid_start_y = inv_y + 110

                if mouse_pos[1] >= equipped_y and mouse_pos[1] <= equipped_y + game.player.inventory.cell_size:
                    if mouse_pos[0] >= inv_x and mouse_pos[0] <= inv_x + game.player.inventory.cell_size:
                        use_hand_cursor = True
                    elif mouse_pos[0] >= inv_x + game.player.inventory.cell_size + game.player.inventory.padding and \
                            mouse_pos[0] <= inv_x + (
                            game.player.inventory.cell_size + game.player.inventory.padding) * 2:
                        use_hand_cursor = True

                for row in range(game.player.inventory.rows):
                    for col in range(game.player.inventory.cols):
                        x = inv_x + col * (game.player.inventory.cell_size + game.player.inventory.padding)
                        y = grid_start_y + row * (game.player.inventory.cell_size + game.player.inventory.padding)
                        if (mouse_pos[0] >= x and mouse_pos[0] <= x + game.player.inventory.cell_size and mouse_pos[
                            1] >= y and mouse_pos[1] <= y + game.player.inventory.cell_size):
                            idx = (game.player.inventory.scroll_offset + row) * game.player.inventory.cols + col
                            if idx < len(game.player.inventory.items):
                                use_hand_cursor = True

            if (game.current_room.type == RoomType.SHOP and hasattr(game.current_room,
                                                                    'merchant') and game.current_room.merchant.selected_item is not None):
                menu_width = 460
                menu_height = 340
                menu_x = (WINDOW_SIZE[0] - menu_width) // 2
                menu_y = (WINDOW_SIZE[1] - menu_height) // 2

                for i in range(len(game.current_room.merchant.current_offerings)):
                    button_rect = pygame.Rect(menu_x + menu_width - 110, menu_y + 60 + i * 90 + 20, 90, 40)
                    if button_rect.collidepoint(mouse_pos):
                        use_hand_cursor = True

                close_btn_rect = pygame.Rect(menu_x + menu_width - 35, menu_y + 5, 30, 30)
                if close_btn_rect.collidepoint(mouse_pos):
                    use_hand_cursor = True

            if use_hand_cursor:
                screen.blit(cursor_hand, (mouse_pos[0] - 16, mouse_pos[1] - 16))
            else:
                screen.blit(cursor, (mouse_pos[0] - 16, mouse_pos[1] - 16))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()