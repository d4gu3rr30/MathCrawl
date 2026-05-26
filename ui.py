import pygame
from config import *
from assets import *

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font('resources/PixelizerBold.ttf', 36)
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