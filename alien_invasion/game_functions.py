import sys
import pygame

from bullet import Bullet
from alien import Alien
from time import sleep


def check_events(ai):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ai.ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai, mouse_x, mouse_y)


def check_keydown_events(event, ai):
    if event.key == pygame.K_RIGHT:
        ai.ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ai.ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai.settings, ai.screen, ai.ship, ai.bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_play_button(ai, mouse_x, mouse_y):
    button_clicked = ai.play_button.rect.collidepoint(mouse_x, mouse_y)

    if button_clicked and not ai.stats.game_active:
        ai.settings.initialise_dynamic_settings()

        pygame.mouse.set_visible(False)

        ai.stats.reset_stats()
        ai.stats.game_active = True

        ai.sb.prep_score()
        ai.sb.prep_high_score()
        ai.sb.prep_level()
        ai.sb.prep_ships()

        ai.aliens.empty()
        ai.bullets.empty()

        create_fleet(ai.settings, ai.screen, ai.ship, ai.aliens)

        ai.ship.center_ship()


def check_high_score(stats, sb):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def check_bullet_alien_collisions(ai):
    collisions = pygame.sprite.groupcollide(ai.bullets, ai.aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            ai.stats.score += ai.settings.alien_points * len(ai.aliens)
            ai.sb.prep_score()

        check_high_score(ai.stats, ai.sb)

    if len(ai.aliens) == 0:
        ai.bullets.empty()
        ai.settings.increase_speed()

        ai.stats.level += 1
        ai.sb.prep_level()

        create_fleet(ai.settings, ai.screen, ai.ship, ai.aliens)


def check_aliens_bottom(ai):
    screen_rect = ai.screen.get_rect()
    for alien in ai.aliens.sprites():
        if alien.rect.top >= screen_rect.bottom:
            ship_hit(ai)
            break


def check_fleet_edges(ai_settings, aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def get_number_aliens_x(ai_settings, alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width

    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number

    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):

            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def change_fleet_direction(ai_settings, aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed

    ai_settings.fleet_direction *= -1


def ship_hit(ai):
    if ai.stats.ship_left > 0:
        ai.stats.ship_left -= 1

        ai.sb.prep_ships()

        ai.aliens.empty()
        ai.bullets.empty()

        create_fleet(ai.settings, ai.screen, ai.ship, ai.aliens)

        ai.ship.center_ship()

        sleep(0.5)
    else:
        ai.stats.game_active = False
        pygame.mouse.set_visible(True)


def update_aliens(ai):
    check_fleet_edges(ai.settings, ai.aliens)
    ai.aliens.update()

    if pygame.sprite.spritecollideany(ai.ship, ai.aliens):
        ship_hit(ai)

    check_aliens_bottom(ai)


def update_bullets(ai):
    ai.bullets.update()

    for bullet in ai.bullets.copy():
        if bullet.rect.bottom <= 0:
            ai.bullets.remove(bullet)

    check_bullet_alien_collisions(ai)


def update_screen(ai):
    ai.screen.fill(ai.settings.bg_colour)

    for bullet in ai.bullets.sprites():
        bullet.draw_bullet()

    ai.ship.blitme()
    ai.aliens.draw(ai.screen)

    ai.sb.show_score()

    if not ai.stats.game_active:
        ai.play_button.draw_button()

    pygame.display.flip()