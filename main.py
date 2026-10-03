from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.utils import platform
import random


def c(r, g, b, a=1.0):
    return (r / 255.0, g / 255.0, b / 255.0, a)


GREEN = c(35, 135, 55)
ROAD = c(48, 48, 55)
WHITE = c(255, 255, 255)
BLACK = c(15, 15, 18)
RED = c(225, 55, 55)
BLUE = c(40, 105, 235)
YELLOW = c(250, 205, 45)
ORANGE = c(245, 125, 35)
PURPLE = c(175, 65, 200)
CYAN = c(50, 210, 220)
GRAY = c(90, 90, 95)
DARK_GRAY = c(35, 35, 40)
WIN_BLUE = c(35, 70, 90)
WIN_DARK = c(30, 55, 70)
ENEMY_COLORS = [RED, BLUE, YELLOW, ORANGE, PURPLE]


class RacingGame(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = 'menu'
        self.score = 0
        self.best_score = 0
        self.game_speed = 7.0
        self.spawn_timer = 0
        self.road_line_offset = 0.0
        self.left_pressed = False
        self.right_pressed = False
        self.enemies = []
        self._textures = {}
        self.player_x = 0
        self.player_y = 0
        self.player_w = 50
        self.player_h = 85
        self.player_speed = 8
        self.road_width = 100
        self.road_left = 0
        self.road_right = 100
        self.lane_width = 25
        self.start_btn = (0, 0, 0, 0)
        self.restart_btn = (0, 0, 0, 0)
        self.left_btn = (0, 0, 0, 0)
        self.right_btn = (0, 0, 0, 0)
        self.pause_btn = (0, 0, 0, 0)

        self.bind(size=self._layout, pos=self._layout)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self._layout()
        Window.bind(on_keyboard=self._on_keyboard)

    def _layout(self, *args):
        w, h = self.width, self.height
        if w < 10 or h < 10:
            return
        self.road_width = w * 0.7
        self.road_left = (w - self.road_width) / 2
        self.road_right = self.road_left + self.road_width
        self.lane_width = self.road_width / 4
        self.player_w = w * 0.09
        self.player_h = w * 0.15
        self.player_speed = w * 0.014

        if self.player_x == 0:
            self.player_x = self.road_left + self.lane_width * 2 + (self.lane_width - self.player_w) / 2
            self.player_y = h * 0.12

        btn_w = (w - w * 0.05 * 3) / 2
        btn_h = h * 0.12
        btn_y = h * 0.02
        self.left_btn = (w * 0.05, btn_y, btn_w, btn_h)
        self.right_btn = (w - w * 0.05 - btn_w, btn_y, btn_w, btn_h)

        sb_w = w * 0.6
        sb_h = h * 0.09
        self.start_btn = ((w - sb_w) / 2, h * 0.32, sb_w, sb_h)
        self.restart_btn = ((w - sb_w) / 2, h * 0.28, sb_w, sb_h)

        pb_w = w * 0.18
        pb_h = h * 0.06
        self.pause_btn = (w - pb_w - w * 0.03, h - pb_h - h * 0.03, pb_w, pb_h)

    def _get_texture(self, key, text, font_size, color):
        cache = self._textures.get(key)
        if cache and cache[0] == text and cache[1] == font_size:
            return cache[2]
        lbl = CoreLabel(text=text, font_size=font_size, color=color)
        lbl.refresh()
        tex = lbl.texture
        self._textures[key] = (text, font_size, tex)
        return tex

    def _draw_text(self, key, text, cx, cy, font_size, color):
        tex = self._get_texture(key, text, font_size, color)
        tw, th = tex.size
        Color(1, 1, 1, 1)
        Rectangle(texture=tex, pos=(cx - tw / 2, cy - th / 2), size=tex.size)

    # ============ GAME LOGIC ============

    def update(self, dt):
        if self.game_state == 'playing':
            self._update_game()
        self.redraw()

    def _update_game(self):
        if self.left_pressed:
            self.player_x -= self.player_speed
        if self.right_pressed:
            self.player_x += self.player_speed

        min_x = self.road_left + self.width * 0.01
        max_x = self.road_right - self.player_w - self.width * 0.01
        self.player_x = max(min_x, min(self.player_x, max_x))

        self.road_line_offset = (self.road_line_offset + self.game_speed) % 75

        self.spawn_timer += 1
        spawn_delay = max(25, int(65 - self.game_speed * 3))
        if self.spawn_timer >= spawn_delay:
            self.spawn_timer = 0
            self._spawn_enemy()

        to_remove = []
        for e in self.enemies:
            e['y'] -= self.game_speed
            if e['y'] + self.player_h < 0:
                to_remove.append(e)
                self.score += 1
                if self.score % 10 == 0:
                    self.game_speed += 0.7
            elif self._collide(e):
                self.game_state = 'gameover'
                if self.score > self.best_score:
                    self.best_score = self.score
        for e in to_remove:
            self.enemies.remove(e)

    def _collide(self, e):
        m = self.player_w * 0.12
        px1, py1 = self.player_x + m, self.player_y + m
        px2, py2 = self.player_x + self.player_w - m, self.player_y + self.player_h - m
        ex1, ey1 = e['x'] + m, e['y'] + m
        ex2, ey2 = e['x'] + self.player_w - m, e['y'] + self.player_h - m
        return px1 < ex2 and px2 > ex1 and py1 < ey2 and py2 > ey1

    def _spawn_enemy(self):
        h = self.height
        available = []
        for lane in range(4):
            x = self.road_left + lane * self.lane_width + (self.lane_width - self.player_w) / 2
            clear = True
            for e in self.enemies:
                if abs(e['x'] - x) < self.player_w * 0.3 and e['y'] > h - self.player_h * 2.5:
                    clear = False
                    break
            if clear:
                available.append(lane)
        if not available:
            return
        lane = random.choice(available)
        x = self.road_left + lane * self.lane_width + (self.lane_width - self.player_w) / 2
        y = h + random.randint(30, 180)
        self.enemies.append({'x': x, 'y': y, 'color': random.choice(ENEMY_COLORS)})

    def reset_game(self):
        self.score = 0
        self.game_speed = 7.0
        self.spawn_timer = 0
        self.road_line_offset = 0
        self.enemies.clear()
        self.left_pressed = False
        self.right_pressed = False
        self.player_x = self.road_left + self.lane_width * 2 + (self.lane_width - self.player_w) / 2
        self.player_y = self.height * 0.22
        self.game_state = 'playing'

    # ============ DRAWING ============

    def redraw(self):
        self.canvas.clear()
        w, h = self.width, self.height
        if w < 10:
            return
        with self.canvas:
            Color(*GREEN)
            Rectangle(pos=(0, 0), size=(w, h))
            if self.game_state == 'menu':
                self._draw_menu()
            else:
                self._draw_game()

    def _draw_road(self):
        w, h = self.width, self.height
        Color(*ROAD)
        Rectangle(pos=(self.road_left, 0), size=(self.road_width, h))
        Color(*WHITE)
        bw = w * 0.012
        Rectangle(pos=(self.road_left, 0), size=(bw, h))
        Rectangle(pos=(self.road_right - bw, 0), size=(bw, h))
        dash_h = 45
        gap = 30
        dist = dash_h + gap
        y_start = -(self.road_line_offset % dist)
        for lane in range(1, 4):
            x = self.road_left + lane * self.lane_width - 3
            y = y_start
            while y < h:
                Color(*WHITE)
                Rectangle(pos=(x, y), size=(6, dash_h))
                y += dist

    def _draw_car(self, x, y, w, h, color):
        r = w * 0.15
        Color(*color)
        RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
        Color(*WIN_BLUE)
        RoundedRectangle(pos=(x + w * 0.12, y + h * 0.58),
                         size=(w * 0.76, h * 0.28), radius=[w * 0.1])
        Color(*WIN_DARK)
        RoundedRectangle(pos=(x + w * 0.12, y + h * 0.18),
                         size=(w * 0.76, h * 0.22), radius=[w * 0.1])
        Color(*WHITE)
        Rectangle(pos=(x + w * 0.08, y + h * 0.93), size=(w * 0.2, h * 0.05))
        Rectangle(pos=(x + w * 0.72, y + h * 0.93), size=(w * 0.2, h * 0.05))

    def _draw_game(self):
        w, h = self.width, self.height
        self._draw_road()
        for e in self.enemies:
            self._draw_car(e['x'], e['y'], self.player_w, self.player_h, e['color'])
        self._draw_car(self.player_x, self.player_y, self.player_w, self.player_h, BLUE)

        self._draw_text('hud_title', 'SHAHADAT RACING', w * 0.25, h * 0.965, w * 0.042, CYAN)
        self._draw_text('hud_score', 'Score: ' + str(self.score), w * 0.13, h * 0.915, w * 0.035, WHITE)
        self._draw_text('hud_speed', 'Speed: ' + str(round(self.game_speed, 1)),
                        w * 0.16, h * 0.875, w * 0.032, WHITE)

        if self.game_state != 'gameover':
            self._draw_pause_button()
        if self.game_state == 'playing':
            self._draw_control_buttons()
        if self.game_state == 'paused':
            self._draw_pause_overlay()
        elif self.game_state == 'gameover':
            self._draw_gameover_overlay()

    def _draw_pause_button(self):
        px, py, pw, ph = self.pause_btn
        Color(*DARK_GRAY)
        RoundedRectangle(pos=(px, py), size=(pw, ph), radius=[12])
        Color(*WHITE)
        Line(rounded_rectangle=(px, py, pw, ph, 12), width=1.5)
        Color(*WHITE)
        bw = pw * 0.08
        bh = ph * 0.5
        Rectangle(pos=(px + pw * 0.36, py + ph * 0.25), size=(bw, bh))
        Rectangle(pos=(px + pw * 0.56, py + ph * 0.25), size=(bw, bh))

    def _draw_control_buttons(self):
        for (bx, by, bw, bh), label, key in [
            (self.left_btn, '◀', 'left'),
            (self.right_btn, '▶', 'right')
        ]:
            Color(*DARK_GRAY)
            RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[20])
            Color(*GRAY)
            Line(rounded_rectangle=(bx, by, bw, bh, 20), width=2)
            self._draw_text('btn_' + key, label, bx + bw / 2, by + bh / 2, bw * 0.32, WHITE)

    def _draw_menu(self):
        w, h = self.width, self.height
        Color(*DARK_GRAY)
        Rectangle(pos=(0, 0), size=(w, h))
        road_w = w * 0.5
        road_x = (w - road_w) / 2
        Color(*ROAD)
        Rectangle(pos=(road_x, 0), size=(road_w, h))
        Color(*WHITE)
        y = 0
        while y < h:
            Rectangle(pos=(w / 2 - 5, y), size=(10, 55))
            y += 100

        self._draw_text('menu_title', 'SHAHADAT RACING', w / 2, h * 0.9, w * 0.09, CYAN)
        self._draw_text('menu_sub', 'MOBILE CAR RACING', w / 2, h * 0.82, w * 0.05, WHITE)

        demo_w = w * 0.09
        demo_h = w * 0.15
        self._draw_car(w / 2 - demo_w / 2, h * 0.6, demo_w, demo_h, BLUE)

        bx, by, bw, bh = self.start_btn
        Color(*BLUE)
        RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[20])
        self._draw_text('menu_start', 'START GAME', bx + bw / 2, by + bh / 2, bw * 0.085, WHITE)

        self._draw_text('menu_best', 'BEST SCORE: ' + str(self.best_score), w / 2, h * 0.2, w * 0.045, YELLOW)
        self._draw_text('menu_info', 'Tap buttons to steer', w / 2, h * 0.14, w * 0.035, WHITE)

    def _draw_pause_overlay(self):
        w, h = self.width, self.height
        Color(0, 0, 0, 0.6)
        Rectangle(pos=(0, 0), size=(w, h))
        self._draw_text('pause_title', 'PAUSED', w / 2, h / 2 + h * 0.03, w * 0.09, YELLOW)
        self._draw_text('pause_info', 'Tap II to continue', w / 2, h / 2 - h * 0.03, w * 0.045, WHITE)

    def _draw_gameover_overlay(self):
        w, h = self.width, self.height
        Color(0, 0, 0, 0.75)
        Rectangle(pos=(0, 0), size=(w, h))
        self._draw_text('go_title', 'GAME OVER', w / 2, h * 0.72, w * 0.11, RED)
        self._draw_text('go_score', 'Score: ' + str(self.score), w / 2, h * 0.64, w * 0.06, WHITE)
        self._draw_text('go_best', 'Best Score: ' + str(self.best_score), w / 2, h * 0.58, w * 0.06, YELLOW)
        bx, by, bw, bh = self.restart_btn
        Color(*BLUE)
        RoundedRectangle(pos=(bx, by), size=(bw, bh), radius=[20])
        self._draw_text('go_restart', 'TAP TO RESTART', bx + bw / 2, by + bh / 2, bw * 0.08, WHITE)

    # ============ TOUCH ============

    def _hit(self, rect, x, y):
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def on_touch_down(self, touch):
        x, y = touch.pos
        if self.game_state == 'menu':
            if self._hit(self.start_btn, x, y):
                self.reset_game()
                return True
        elif self.game_state == 'gameover':
            if self._hit(self.restart_btn, x, y):
                self.reset_game()
                return True
        elif self.game_state == 'playing':
            if self._hit(self.pause_btn, x, y):
                self.game_state = 'paused'
                self.left_pressed = False
                self.right_pressed = False
                return True
            if self._hit(self.left_btn, x, y):
                self.left_pressed = True
                touch.grab(self)
                return True
            if self._hit(self.right_btn, x, y):
                self.right_pressed = True
                touch.grab(self)
                return True
        elif self.game_state == 'paused':
            if self._hit(self.pause_btn, x, y):
                self.game_state = 'playing'
                return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.left_pressed = False
        self.right_pressed = False
        if touch.grab_current is self:
            touch.ungrab(self)
        return super().on_touch_up(touch)

    def _on_keyboard(self, window, key, *args):
        if key == 27:
            if self.game_state == 'playing':
                self.game_state = 'paused'
                return True
            elif self.game_state == 'paused':
                self.game_state = 'playing'
                return True
            elif self.game_state == 'gameover':
                self.game_state = 'menu'
                return True
        return False


class RacingApp(App):
    def build(self):
        self.title = 'SHAHADAT RACING'
        if platform != 'android':
            Window.size = (400, 700)
        return RacingGame()


if __name__ == '__main__':
    RacingApp().run()
