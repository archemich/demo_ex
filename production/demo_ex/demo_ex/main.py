import argparse
import math
from pathlib import Path
import tkinter as tk
from typing import Tuple
import random
import sqlite3
import sys

import neat
import pygame as pg
import pandas as pd


global win_res
resource_folder = Path(__file__).parent / 'resources'

def start_win():
    win = tk.Tk()
    win.title("КТбо3-11 Неприн М. А. Вариант 2")
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    button = tk.Button(win, text="Старт", command=(lambda: win.destroy()))
    button.grid(row=1, column=1)
    button.place(relx=0.5, rely=0.5, anchor='center')

    win_width = 200
    win_height = 60
    win_x = int((screen_width / 2))
    win_y = int((screen_height / 2))
    win.geometry("{}x{}+{}+{}".format(win_width, win_height,
                                      win_x - win_width // 2,
                                      win_y - win_height // 2))
    win.bind('<Return>', lambda e: button.invoke())
    win.mainloop()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlite3', type=Path, required=True,
                        help='Path to sqlite3 database.')
    parser.add_argument('--drop', action='store_true', default=False,
                        help='Do drop old records in database?')
    parser.add_argument('--neat-config', type=Path, required=True,
                        help='Path to config for neat.')
    parser.add_argument('--win-resolution', default=(1200, 1080), type=int,
                        nargs=2)

    args = parser.parse_args()
    return args


def init_db(path: Path, drop_old: bool = False) -> sqlite3.Connection:
    """
    Connect to sqlite3 database.

    Arguments
    ---------
    path : pathlib.Path()
        Path to existing or not sqlite3 database file.
    drop_old : bool, optional
    """
    con = sqlite3.connect(path)
    cursor = con.cursor()
    if drop_old:
        cursor.execute("DROP TABLE IF EXISTS Learning_Records")
    cursor.execute("CREATE TABLE IF NOT EXISTS Learning_Records (Iteration_id text,"
                   " Iteration_time text)")
    return con


class Car:
    car_sprites = ("Car1", "Car2", "Car3", "Car4", "Car5")

    def __init__(self):
        self.random_sprite()

        self.angle = 0
        self.speed = 5

        self.radars = []
        self.collision_points = []

        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0

    def random_sprite(self):
        self.car_sprite = pg.image.load(resource_folder / (random.choice(self.car_sprites)
                                        + '.png'))
        self.car_sprite = pg.transform.scale(self.car_sprite,
                                             (math.floor(self.car_sprite.get_size()[0] / 1),
                                              math.floor(self.car_sprite.get_size()[1] / 1)))
        self.car = self.car_sprite

        self.pos = [230, 950]
        self.compute_center()

    def compute_center(self):
        self.center = (self.pos[0] + (self.car.get_size()[0] / 2), self.pos[1] + (self.car.get_size()[1] / 2))

    def draw(self, screen):
        screen.blit(self.car, self.pos)
        self.draw_radars(screen)

    def draw_center(self, screen):
        pg.draw.circle(screen, (0, 72, 186), (math.floor(self.center[0]), math.floor(self.center[1])), 5)

    def draw_radars(self, screen):
        for r in self.radars:
            p, d = r
            pg.draw.line(screen, (183, 235, 70), self.center, p, 1)
            pg.draw.circle(screen, (183, 235, 70), p, 5)

    def compute_radars(self, degree, road):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not road.get_at((x, y)) == App.bg and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def compute_collision_points(self):
        self.compute_center()
        lw = 35
        lh = 35

        lt = [self.center[0] + math.cos(math.radians(360 - (self.angle + 20))) * lw,
              self.center[1] + math.sin(math.radians(360 - (self.angle + 20))) * lh]
        rt = [self.center[0] + math.cos(math.radians(360 - (self.angle + 160))) * lw,
              self.center[1] + math.sin(math.radians(360 - (self.angle + 160))) * lh]
        lb = [self.center[0] + math.cos(math.radians(360 - (self.angle + 200))) * lw,
              self.center[1] + math.sin(math.radians(360 - (self.angle + 200))) * lh]
        rb = [self.center[0] + math.cos(math.radians(360 - (self.angle + 340))) * lw,
              self.center[1] + math.sin(math.radians(360 - (self.angle + 340))) * lh]

        self.collision_points = [lt, rt, lb, rb]

    def draw_collision_points(self, road, screen):
        if not self.collision_points:
            self.compute_collision_points()

        for p in self.collision_points:
            if (road.get_at((int(p[0]), int(p[1]))) == App.bg):
                pg.draw.circle(screen, (255, 0, 0), (int(p[0]), int(p[1])), 5)
            else:
                pg.draw.circle(screen, (15, 192, 252), (int(p[0]), int(p[1])), 5)

    def check_collision(self, road):
        self.is_alive = True

        for p in self.collision_points:
            try:
                if road.get_at((int(p[0]), int(p[1]))) == App.bg:
                    self.is_alive = False
                    break
            except IndexError:
                self.is_alive = False

    def rotate(self, angle):
        orig_rect = self.car_sprite.get_rect()
        rot_image = pg.transform.rotate(self.car_sprite, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()

        self.car = rot_image

    def get_data(self):
        radars = self.radars
        data = [0, 0, 0, 0, 0]

        for i, r in enumerate(radars):
            data[i] = int(r[1] / 30)

        return data

    def get_reward(self):
        return self.distance / 50.0

    def update(self, road):
        self.speed = 2
        (width, height) = win_res
        self.rotate(self.angle)

        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > width - 120:
            self.pos[0] = width - 120

        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > height - 120:
            self.pos[1] = height - 120

        self.distance += self.speed
        self.time_spent += 1

        self.compute_collision_points()
        self.check_collision(road)

        self.radars.clear()
        for d in range(-90, 120, 45):
            self.compute_radars(d, road)


class App:
    bg = (240, 240, 240, 255)

    def __init__(self, connection: sqlite3.Connection,
                   win_resolution: Tuple[int, int]):
        self.con = connection
        self.win_res = win_resolution
        self.generation = 0
        self.start = False

    def run_generation(self, genomes, config):

        nets = []
        cars = []

        for i, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0

            cars.append(Car())

        pg.init()
        screen = pg.display.set_mode(self.win_res)
        clock = pg.time.Clock()
        road = pg.image.load(resource_folder / 'road.png')

        font = pg.font.SysFont("Roboto", 40)
        heading_font = pg.font.SysFont("Roboto", 80)


        self.generation += 1

        import time
        start_time = time.time()
        gen_time = 0

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit(0)
                if event.type == pg.MOUSEMOTION:
                    self.start = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.start = False
                    if event.key == pg.K_f:
                        sys.exit()

            if not self.start:
                continue

            for i, car in enumerate(cars):
                output = nets[i].activate(car.get_data())
                i = output.index(max(output))

                if i == 0:
                    car.angle += 5
                elif i == 1:
                    car.angle = car.angle
                elif i == 2:
                    car.angle -= 5

            cars_left = 0
            for i, car in enumerate(cars):
                if car.is_alive:
                    cars_left += 1
                    car.update(road)
                    genomes[i][1].fitness += car.get_reward()

            if not cars_left:
                break

            screen.blit(road, (0, 0))

            do_stop = False
            for car in cars:
                if car.is_alive:
                    car.draw(screen)
                    time_alive = round(time.time() - start_time, 3)
                    if time_alive == 30:  # seconds
                        do_stop = True
            if do_stop:
                break

            label = heading_font.render("Поколение: " + str(self.generation), True, (40, 40, 40))
            label_rect = label.get_rect()
            label_rect.center = (240, 50)
            screen.blit(label, label_rect)

            label = font.render("Машин осталось: " + str(cars_left), True, (40, 40, 40))
            label_rect = label.get_rect()
            label_rect.center = (240, 100)
            screen.blit(label, label_rect)

            pg.display.flip()
            clock.tick(0)

        gentime = round(time.time() - start_time, 3)
        gen_num = self.generation
        gen_time = gentime
        cursor = self.con.cursor()
        sql = "INSERT INTO Learning_Records VALUES (?, ?)"
        val = (gen_num, gen_time)
        cursor.execute(sql, val)

        sql = "SELECT Iteration_id, Iteration_time FROM Learning_Records " \
              "ORDER BY Iteration_id"
        cursor.execute(sql)
        rows = cursor.fetchall()

        self.con.commit()
        cursor.close()

        res = pd.DataFrame(rows, columns=('Номер итерации', 'Время итерации'))
        print(res)

    def __del__(self):
        self.con.close()


def main():
    args = parse_args()
    global win_res
    win_res = args.win_resolution

    # Thread blocking process
    start_win()
    con = init_db(args.sqlite3, drop_old=args.drop)

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                args.neat_config)

    p = neat.Population(config)
    runner = App(con, args.win_resolution)
    p.run(runner.run_generation, 1000)



if __name__ == '__main__':
    main()