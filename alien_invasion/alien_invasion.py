import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship

import game_functions as gf


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        self.play_button = Button(self.settings, self.screen, "Play")

        self.stats = GameStats(self.settings)
        self.sb = Scoreboard(self.settings, self.screen, self.stats)

        self.ship = Ship(self.settings, self.screen)
        self.bullets = Group()
        self.aliens = Group()
        gf.create_fleet(self.settings, self.screen, self.ship, self.aliens)

    def run_game(self):
        while True:
            gf.check_events(self)

            if self.stats.game_active:
                self.ship.update()
                gf.update_bullets(self)
                gf.update_aliens(self)

            gf.update_screen(self)


if __name__ == "__main__":
    alien_invasion = AlienInvasion()
    alien_invasion.run_game()

