import pygame
import json
import os
from datetime import datetime
from pygame.locals import *
from config import *
from assets import *
from entities import *

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
        # Очистка имени файла от запрещенных символов
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            save_name = save_name.replace(char, '')
        
        # Если после очистки имя пустое или состоит из пробелов, дефолт
        save_name = save_name.strip()
        if not save_name:
            save_name = "save_game"

        save_data = {
            'timestamp': datetime.now().isoformat(),
            'rooms_cleared': game.rooms_cleared,
            'last_merchant_room': game.last_merchant_room,
            'last_treasury_room': game.last_treasury_room,
            'current_room_pos': game.current_room_pos,
            'floor': game.floor,
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
        game.floor = save_data.get('floor', 1)
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