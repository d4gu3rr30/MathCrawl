import pygame
import random
import math
from config import *
from assets import *
from math_engine import *

class Medkit:
    def __init__(self, x, y, heal_amount=2):
        self.x = x
        self.y = y
        self.heal_amount = heal_amount
        self.image = medkit_img
        self.rect = self.image.get_rect(center=(x + 15, y + 15))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

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
            font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
            prompt_text = font.render("Нажмите E, чтобы закупиться", True, WHITE)
            bg_rect = pygame.Rect(self.x - 110, self.y - 65, prompt_text.get_width() + 20, prompt_text.get_height() + 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            screen.blit(prompt_text, (self.x - 100, self.y - 60))
        elif self.selected_item is None:
            # Фразы торговца
            font = pygame.font.Font('resources/PixelizerBold.ttf', 20)
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

            title_font = pygame.font.Font('resources/PixelizerBold.ttf', 32)
            title_text = title_font.render("ТЕРМИНАЛ УЛУЧШЕНИЙ", True, GOLD)
            screen.blit(title_text, (menu_x + menu_width // 2 - title_text.get_width() // 2, menu_y + 5))

            close_btn_rect = pygame.Rect(menu_x + menu_width - 35, menu_y + 5, 30, 30)
            mouse_pos = pygame.mouse.get_pos()
            close_btn_color = RED if close_btn_rect.collidepoint(mouse_pos) else (150, 50, 50)
            pygame.draw.rect(screen, close_btn_color, close_btn_rect, border_radius=5)
            font = pygame.font.Font('resources/PixelizerBold.ttf', 30)
            x_text = font.render("X", True, WHITE)
            screen.blit(x_text, (close_btn_rect.centerx - x_text.get_width() // 2,
                                 close_btn_rect.centery - x_text.get_height() // 2 + 2))

            font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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


floor_texture = pygame.image.load('resources/tileset/stonefloorai1.png')
wall_texture = pygame.image.load('resources/tileset/brickwall1.png')
obstacle_texture = pygame.image.load('resources/tileset/woodbox.png')

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
        self.font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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
        title_font = pygame.font.Font('resources/PixelizerBold.ttf', 40)
        title = title_font.render("ИНВЕНТАРЬ И СТАТИСТИКА", True, GOLD)
        screen.blit(title, (WINDOW_SIZE[0] // 2 - title.get_width() // 2, panel_y + 15))

        # левая панель статистики
        stats_x = panel_x + 30
        stats_y = panel_y + 80
        pygame.draw.rect(screen, (20, 20, 25), (stats_x - 10, stats_y - 10, 250, panel_height - 90), border_radius=10)
        pygame.draw.rect(screen, (60, 60, 70), (stats_x - 10, stats_y - 10, 250, panel_height - 90), 2,
                         border_radius=10)

        stat_font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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
            font_title = pygame.font.Font('resources/PixelizerBold.ttf', 24)
            font_desc = pygame.font.Font('resources/PixelizerBold.ttf', 18)

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
        self.image = pygame.image.load('resources/tileset/player.png')
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
                    base_vol *= 0.65  # автоматы и огнемет намного тише
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
        self.font = pygame.font.Font('resources/PixelizerBold.ttf', 20)
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
            font = pygame.font.Font('resources/PixelizerBold.ttf', font_size)
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
                font = pygame.font.Font('resources/PixelizerBold.ttf', 24)
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
            self.icon = pygame.image.load(f'resources/tileset/{filename}').convert_alpha()
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
            self.icon = pygame.image.load(f'resources/tileset/{filename}').convert_alpha()
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
            sheet = pygame.image.load('resources/tileset/reload_sheet.png').convert_alpha()
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