"""
ОКФРС. ПЗ №2. Бонус 3.
Шкала радиосвязи 88..108 MHz с анимированной стрелкой.
"""
import tkinter as tk
import random


BG_TOP     = "#0a0e1c"
BG_BOTTOM  = "#141a30"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
NEON       = "#22d3ee"
GREEN      = "#22c55e"
AMBER      = "#f4b942"
RED        = "#ff3860"
TEXT_MAIN  = "#eef2ff"
TEXT_DIM   = "#5c6a90"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class RadioScale:
    def __init__(self, canvas, on_change=None):
        self.canvas = canvas
        self.on_change = on_change
        self.x_min, self.x_max = 130, 970
        self.y_top, self.y_mid, self.y_bot = 280, 360, 430
        self.pos = self.x_min
        self.direction = 1
        self.running = False

        self._draw_body()
        self._draw_scale()
        self._draw_arrow()

    def _draw_body(self):
        c = self.canvas
        # корпус прибора
        c.create_rectangle(80, 190, 1020, 490,
                           fill="#1a2035", outline=PANEL_BRD, width=2)
        c.create_rectangle(92, 202, 1008, 478,
                           outline=lerp(NEON, PANEL_BG, 0.85), width=1)

        # фон шкалы — тёплый «винтаж»
        c.create_rectangle(self.x_min-25, self.y_top-35,
                           self.x_max+25, self.y_bot+25,
                           fill="#1a0f08", outline="#4a3b2a", width=2)
        c.create_rectangle(self.x_min-20, self.y_top-30,
                           self.x_max+20, self.y_bot+20,
                           fill="#2a1a0a", outline="")

        # надписи MHz / SELECTIVITY
        c.create_text((self.x_min+self.x_max)/2, 235,
                      text="MHz",
                      fill=AMBER, font=("Consolas", 16, "bold"))
        c.create_text((self.x_min+self.x_max)/2, 258,
                      text="HIGH   SELECTIVITY",
                      fill=AMBER, font=("Consolas", 10, "italic"))

        # подпись «ЧАСТОТА»
        c.create_text(550, 130, text="ЧАСТОТА",
                      fill=TEXT_DIM, font=("Segoe UI", 10, "bold"))
        # большая цифра
        self.freq_lbl = c.create_text(
            550, 165, text="88.0 MHz",
            fill=GREEN, font=("Consolas", 34, "bold"))

    def _draw_scale(self):
        c = self.canvas
        # крупные деления + цифры
        for i in range(11):
            x = self.x_min + i * (self.x_max - self.x_min) / 10
            h = 32 if i % 2 == 0 else 16
            c.create_line(x, self.y_mid-24, x, self.y_mid-24+h,
                          fill=AMBER, width=2 if i % 2 == 0 else 1)
            if i % 2 == 0:
                freq = 88 + i*2
                c.create_text(x, self.y_mid+40, text=str(freq),
                              fill=AMBER,
                              font=("Consolas", 15, "bold"))
        # мелкие деления
        for i in range(51):
            x = self.x_min + i * (self.x_max - self.x_min) / 50
            c.create_line(x, self.y_mid-24, x, self.y_mid-16,
                          fill="#a08050", width=1)

        # «станции» — точки на шкале
        for freq in (92, 99, 105):
            t = (freq - 88) / 20
            x = self.x_min + t * (self.x_max - self.x_min)
            c.create_line(x, self.y_mid-4, x, self.y_mid+4,
                          fill=GREEN, width=2)
            c.create_text(x, self.y_mid-42, text="▮",
                          fill=GREEN, font=("Segoe UI", 10))

        # нижняя полоса
        c.create_rectangle(self.x_min-25, self.y_mid+55,
                           self.x_max+25, self.y_bot+10,
                           fill="#1a0f05", outline="#4a3b2a")
        c.create_text((self.x_min+self.x_max)/2, self.y_mid+80,
                      text="FM   STEREO   SCAN",
                      fill=AMBER, font=("Consolas", 9, "italic"))

    def _draw_arrow(self):
        c = self.canvas
        # тень
        self.shadow = c.create_line(
            self.pos+3, self.y_bot+30,
            self.pos+3, self.y_mid-24,
            fill="#2a0510", width=4)
        # тело
        self.line = c.create_line(
            self.pos, self.y_bot+30,
            self.pos, self.y_mid-24,
            fill=RED, width=3)
        # треугольник
        self.head = c.create_polygon(
            self.pos-11, self.y_mid-24,
            self.pos+11, self.y_mid-24,
            self.pos,    self.y_mid-50,
            fill=RED, outline=lerp(RED, "#ffffff", 0.5))

    def _freq(self):
        t = (self.pos - self.x_min) / (self.x_max - self.x_min)
        return 88 + t*20

    def _move(self):
        c = self.canvas
        c.coords(self.line, self.pos, self.y_bot+30,
                 self.pos, self.y_mid-24)
        c.coords(self.shadow, self.pos+3, self.y_bot+30,
                 self.pos+3, self.y_mid-24)
        c.coords(self.head,
                 self.pos-11, self.y_mid-24,
                 self.pos+11, self.y_mid-24,
                 self.pos,    self.y_mid-50)

        freq = self._freq()
        c.itemconfig(self.freq_lbl, text=f"{freq:5.1f} MHz")

        # «станции» — 92, 99, 105
        near = min(abs(freq - s) for s in (92, 99, 105))
        if near < 0.3:
            c.itemconfig(self.freq_lbl, fill=GREEN)
        elif near < 0.8:
            c.itemconfig(self.freq_lbl, fill=AMBER)
        else:
            c.itemconfig(self.freq_lbl, fill=RED)

        if self.on_change:
            self.on_change(freq)

    def start(self):
        if not self.running:
            self.running = True
            self._tick()

    def stop(self):
        self.running = False

    def set_random(self):
        self.pos = random.randint(self.x_min, self.x_max)
        self._move()

    def _tick(self):
        if not self.running:
            return
        if self.pos >= self.x_max:
            self.direction = -1
        elif self.pos <= self.x_min:
            self.direction = 1
        self.pos += 5 * self.direction
        self._move()
        self.canvas.after(18, self._tick)


class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 width=200, height=48, color=NEON):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0)
        self.command = command
        self.text = text
        self.color = color
        self.w, self.h = width, height
        self.hovered = False
        self.pressed = False
        self._draw()
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress>", self._press)
        self.bind("<ButtonRelease>", self._release)

    def _draw(self):
        self.delete("all")
        c = self.color
        if self.pressed:
            c = lerp(self.color, "#000000", 0.3)
        elif self.hovered:
            c = lerp(self.color, "#ffffff", 0.2)
        if self.hovered:
            for i in range(4, 0, -1):
                self.create_rectangle(-i, -i, self.w+i, self.h+i,
                                      outline=lerp(self.color, PANEL_BG, i*0.2))
        self.create_rectangle(4, 5, self.w+4, self.h+5,
                              fill="#02040a", outline="")
        self.create_rectangle(0, 0, self.w, self.h, fill=c,
                              outline=lerp(c, "#ffffff", 0.4))
        self.create_rectangle(2, 2, self.w-2, self.h//2,
                              fill=lerp(c, "#ffffff", 0.25), outline="")
        self.create_text(self.w/2, self.h/2, text=self.text,
                         fill="#ffffff", font=("Segoe UI", 11, "bold"))

    def _enter(self, e):
        self.hovered = True; self.configure(cursor="hand2"); self._draw()

    def _leave(self, e):
        self.hovered = False; self.pressed = False
        self.configure(cursor=""); self._draw()

    def _press(self, e):
        self.pressed = True; self._draw()

    def _release(self, e):
        self.pressed = False; self._draw()
        if callable(self.command):
            self.command()


class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Бонус 3 · Шкала радиосвязи")
        root.geometry("1100x600")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1100, height=600,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        for i in range(600):
            self.canvas.create_line(0, i, 1100, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/600))

        self.canvas.create_text(550, 45,
                                text="ШКАЛА РАДИОСВЯЗИ",
                                fill=TEXT_MAIN,
                                font=("Segoe UI", 24, "bold"))
        self.canvas.create_text(550, 78,
                                text="ОКФРС · ПЗ №2 · Бонус 3 · 88..108 MHz",
                                fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(250, 102, 850, 102, fill=NEON, width=2)
        self.canvas.create_line(250, 104, 850, 104,
                                fill=lerp(NEON, BG_TOP, 0.7))

        self.scale = RadioScale(self.canvas)

        # кнопки
        start = NeonButton(self.root, "▶  СТАРТ",
                           command=self.scale.start,
                           width=200, height=48, color=GREEN)
        self.canvas.create_window(360, 520, window=start)

        stop = NeonButton(self.root, "■  СТОП",
                          command=self.scale.stop,
                          width=200, height=48, color=RED)
        self.canvas.create_window(580, 520, window=stop)

        rnd = NeonButton(self.root, "🎲  СЛУЧАЙНО",
                         command=self.scale.set_random,
                         width=200, height=48, color=AMBER)
        self.canvas.create_window(800, 520, window=rnd)

        self.canvas.create_text(550, 575,
                                text="© ОКФРС · ПЗ №2 · Бонус 3",
                                fill="#2a3350", font=("Segoe UI", 9))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()