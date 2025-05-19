from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.label import Label
import random
import json
import os
from datetime import datetime

# Tamaño de la ventana (tamaño móvil)
Window.size = (360, 640)
WIDTH, HEIGHT = Window.size

DATA_FILE = "game_data.json"

class Player(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 60)
        self.pos = (WIDTH // 2 - 20, 100)
        with self.canvas:
            Color(0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def move(self, direction):
        x, y = self.pos
        if direction == 'left' and x > 0:
            x -= 10
        elif direction == 'right' and x + self.width < WIDTH:
            x += 10
        self.pos = (x, y)
        self.rect.pos = self.pos

class Obstacle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        width = random.randint(50, 100)
        x = random.randint(0, WIDTH - width)
        self.size = (width, 20)
        self.pos = (x, HEIGHT)
        with self.canvas:
            Color(1, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def move(self, speed):
        x, y = self.pos
        y -= speed
        self.pos = (x, y)
        self.rect.pos = self.pos

class DataItem(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = random.choice(["CSV", "JSON", "SQL"])
        x = random.randint(50, WIDTH - 50)
        self.size = (30, 30)
        self.pos = (x, HEIGHT)
        with self.canvas:
            Color(0, 1, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def move(self, speed):
        x, y = self.pos
        y -= speed
        self.pos = (x, y)
        self.rect.pos = self.pos

class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player()
        self.add_widget(self.player)

        self.obstacles = []
        self.data_items = []
        self.speed = 4
        self.score = 0
        self.data_collected = 0
        self.frame_count = 0

        self.score_label = Label(text="Score: 0", pos=(10, HEIGHT - 30))
        self.high_label = Label(text="High Score: 0", pos=(10, HEIGHT - 60))
        self.data_label = Label(text="Datos: 0", pos=(10, HEIGHT - 90))
        self.add_widget(self.score_label)
        self.add_widget(self.high_label)
        self.add_widget(self.data_label)

        self.game_data = {"scores": [], "dates": []}
        self.high_score = 0
        self.load_data()

        Clock.schedule_interval(self.update, 1/60)
        Window.bind(on_key_down=self.on_key_down)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.game_data = json.load(f)
                if self.game_data["scores"]:
                    self.high_score = max(self.game_data["scores"])
                    self.high_label.text = f"High Score: {self.high_score}"

    def save_data(self):
        self.game_data["scores"].append(self.score)
        self.game_data["dates"].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open(DATA_FILE, "w") as f:
            json.dump(self.game_data, f)

    def on_key_down(self, instance, key, scancode, codepoint, modifiers):
        if key == 276:  # izquierda
            self.player.move("left")
        elif key == 275:  # derecha
            self.player.move("right")

    def update(self, dt):
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            self.spawn_obstacle()
            if random.random() < 0.3:
                self.spawn_data()

        for obs in self.obstacles[:]:
            obs.move(self.speed)
            if obs.y < 0:
                self.remove_widget(obs)
                self.obstacles.remove(obs)
                self.score += 1
            elif obs.collide_widget(self.player):
                self.game_over()

        for item in self.data_items[:]:
            item.move(self.speed)
            if item.y < 0:
                self.remove_widget(item)
                self.data_items.remove(item)
            elif item.collide_widget(self.player):
                self.remove_widget(item)
                self.data_items.remove(item)
                self.data_collected += 1
                self.score += 5

        self.score_label.text = f"Score: {self.score}"
        self.data_label.text = f"Datos: {self.data_collected}"

    def spawn_obstacle(self):
        obs = Obstacle()
        self.obstacles.append(obs)
        self.add_widget(obs)

    def spawn_data(self):
        item = DataItem()
        self.data_items.append(item)
        self.add_widget(item)

    def game_over(self):
        self.save_data()
        self.reset_game()

    def reset_game(self):
        for obs in self.obstacles:
            self.remove_widget(obs)
        for item in self.data_items:
            self.remove_widget(item)
        self.obstacles.clear()
        self.data_items.clear()
        self.score = 0
        self.data_collected = 0
        self.player.pos = (WIDTH // 2 - 20, 100)
        self.player.rect.pos = self.player.pos
        self.high_score = max(self.high_score, self.score)
        self.high_label.text = f"High Score: {self.high_score}"

class DataRunnerApp(App):
    def build(self):
        return Game()

if __name__ == '__main__':
    DataRunnerApp().run()
