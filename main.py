import pygame
import random
import math
import time
import json
from enum import Enum
import os
from datetime import datetime
from pygame.locals import *
from config import *

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

# флаг SCALED для автоматического сохранения пропорций при растягивании
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED)
is_fullscreen = False
pygame.display.set_caption('MATHCRAWL - Образовательный Roguelike')
clock = pygame.time.Clock()

# Загрузка всех картинок и звуков ТОЛЬКО ПОСЛЕ того, как создается окно и включается звук
from assets import *
from math_engine import *
from save_manager import *
from ui import *
from entities import *

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
        self.console_font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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

    def apply_level_settings(self):
        # Остановка всей музыки перед переключением
        pygame.mixer.stop()
        
        # Настройка для 1-го уровня
        if self.floor == 1:
            if level_music: level_music.play(-1)
            self.current_room.color_filter = None
            
        # Настройка для 2-го уровня
        elif self.floor == 2:
            if level2_music: level2_music.play(-1)
            self.current_room.color_filter = PURPLE

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
        font_large = pygame.font.Font('resources/PixelizerBold.ttf', 48)
        font_medium = pygame.font.Font('resources/PixelizerBold.ttf', 32)
        font_small = pygame.font.Font('resources/PixelizerBold.ttf', 24)

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

        font = pygame.font.Font('resources/PixelizerBold.ttf', 48)
        text = font.render('Сохранение игры', True, WHITE)
        screen.blit(text, (WINDOW_SIZE[0] // 2 - text.get_width() // 2, WINDOW_SIZE[1] // 3 - 50))

        pygame.draw.rect(screen, (100, 100, 100), (WINDOW_SIZE[0] // 2 - 150, WINDOW_SIZE[1] // 2 - 50, 300, 40))
        font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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

        font = pygame.font.Font('resources/PixelizerBold.ttf', 48)
        text = font.render('Загрузка игры', True, WHITE)
        screen.blit(text, (WINDOW_SIZE[0] // 2 - text.get_width() // 2, WINDOW_SIZE[1] // 4 - 50))

        self.saves_list = self.save_manager.get_save_files()
        font = pygame.font.Font('resources/PixelizerBold.ttf', 24)

        for i, save in enumerate(self.saves_list):
            y_pos = WINDOW_SIZE[1] // 3 + i * 60
            save_rect = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, y_pos, 400, 50)

            if save_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (100, 100, 100), save_rect)
            else:
                pygame.draw.rect(screen, (70, 70, 70), save_rect)

            name_text = font.render(save['name'], True, WHITE)
            screen.blit(name_text, (save_rect.x + 10, save_rect.y + 10))

            info_font = pygame.font.Font('resources/PixelizerBold.ttf', 16)
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

        font_title = pygame.font.Font('resources/PixelizerBold.ttf', 48)
        title = font_title.render("УПРАВЛЕНИЕ", True, GOLD)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, menu_y + 20))

        font_normal = pygame.font.Font('resources/PixelizerBold.ttf', 28)
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

        font_title = pygame.font.Font('resources/PixelizerBold.ttf', 48)
        title = font_title.render("МЕТА-ПРОКАЧКА", True, GOLD)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, menu_y + 15))

        font_normal = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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
                icon = pygame.image.load(f'resources/tileset/{filename}').convert_alpha()
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
            font = pygame.font.Font('resources/PixelizerBold.ttf', 74)
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

            title_font = pygame.font.Font('resources/PixelizerBold.ttf', 48)
            title_text = title_font.render("НАСТРОЙКИ", True, GOLD)
            screen.blit(title_text, (menu_x + menu_width // 2 - title_text.get_width() // 2, menu_y + 15))

            font = pygame.font.Font('resources/PixelizerBold.ttf', 32)

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

            font = pygame.font.Font('resources/PixelizerBold.ttf', 48)
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
        icon_img = pygame.image.load('resources/tileset/cyanBorderIcon.png').convert_alpha()
        pygame.display.set_icon(icon_img)
    except Exception as e:
        icon_img = None
        print("Ошибка загрузки иконки:", e)

    # Заставка
    splash_duration = 3500
    start_time = pygame.time.get_ticks()

    try:
        logo_snd = pygame.mixer.Sound('resources/Sounds/logo.wav')
        logo_snd.set_volume(game.sound_volume)
        logo_snd.play()
    except Exception:
        pass

    splash_font = pygame.font.Font('resources/PixelizerBold.ttf', 64)
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
                                        game.apply_level_settings()
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
                            explosion_sound.set_volume(0.35 * game.sound_volume)
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
                                explosion_sound.set_volume(0.35 * game.sound_volume)
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
                font = pygame.font.Font('resources/PixelizerBold.ttf', 28)
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
                font = pygame.font.Font('resources/PixelizerBold.ttf', 36)
                time_text = font.render(f'Time: {int(game.current_room.time_remaining)}', True, WHITE)
                screen.blit(time_text, (WINDOW_SIZE[0] - 150, 175))

            font = pygame.font.Font('resources/PixelizerBold.ttf', 36)

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

                # Отрисовка лога консоли
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
            font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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