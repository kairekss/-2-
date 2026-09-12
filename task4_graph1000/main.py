"""
ОКФРС. ПЗ №2. Программа 4.
Графический вывод 1000 случайных чисел (0..100) в виде точек.
"""
import tkinter as tk
import random


BG_TOP     = "#0d1020"
BG_BOTTOM  = "#1a1f35"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
ACCENT     = "#ff3860"
NEON       = "#00d4ff"
DOT_COLOR  = "#00d4ff"
DOT_HALO   = "#1f4a6e"
GRID       = "#1a2340"
TEXT_MAIN  = "#e8ecf8"
TEXT_DIM   = "#6b7a9c"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 width=320, height=54, color=ACCENT):
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
            c = lerp(self.color, "#000000", 0.25)
        elif self.hovered:
            c = lerp(self.color, "#ffffff", 0.15)

        if self.hovered:
            for i in range(4, 0, -1):
                self.create_rectangle(-i, -i, self.w+i, self.h+i,
                                      outline=lerp(self.color, PANEL_BG, i*0.2))

        self.create_rectangle(4, 5, self.w+4, self.h+5,
                              fill="#050810", outline="")
        self.create_rectangle(0, 0, self.w, self.h, fill=c,
                              outline=lerp(c, "#ffffff", 0.4))
        self.create_rectangle(2, 2, self.w-2, self.h//2,
                              fill=lerp(c, "#ffffff", 0.25), outline="")
        self.create_text(self.w/2, self.h/2, text=self.text,
                         fill="#ffffff", font=("Segoe UI", 12, "bold"))

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
        root.title("ОКФРС · Программа 4 · 1000 точек")
        root.geometry("1100x780")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1100, height=780,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        self._draw_bg()
        self._draw_header()
        self._draw_graph_area()
        self._draw_button()
        self._draw_footer()

    def _draw_bg(self):
        for i in range(780):
            self.canvas.create_line(0, i, 1100, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/780))

    def _draw_header(self):
        self.canvas.create_text(
            550, 42, text="ГРАФИК 1000 ТОЧЕК",
            fill=TEXT_MAIN, font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(
            550, 74,
            text="ОКФРС · ПЗ №2 · Программа 4 · диапазон 0..100",
            fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(230, 100, 870, 100, fill=NEON, width=2)
        self.canvas.create_line(230, 102, 870, 102,
                                fill=lerp(NEON, BG_TOP, 0.7), width=1)

    def _draw_graph_area(self):
        # панель графика
        self.canvas.create_rectangle(80, 130, 1020, 660,
                                     fill="#080b16", outline=PANEL_BRD)

        self.gx0, self.gy0 = 150, 160
        self.gx1, self.gy1 = 990, 620

        # сетка Y + подписи
        for i in range(6):
            gy = self.gy0 + i * (self.gy1 - self.gy0) / 5
            self.canvas.create_line(self.gx0, gy, self.gx1, gy,
                                    fill=GRID, tags="grid")
            val = 100 - i * 20
            self.canvas.create_text(self.gx0 - 15, gy, text=str(val),
                                    fill=TEXT_DIM, font=("Segoe UI", 9),
                                    anchor="e", tags="grid")
        # сетка X
        for i in range(11):
            gx = self.gx0 + i * (self.gx1 - self.gx0) / 10
            self.canvas.create_line(gx, self.gy0, gx, self.gy1,
                                    fill=GRID, tags="grid")

        # оси
        self.canvas.create_line(self.gx0, self.gy1, self.gx1, self.gy1,
                                fill="#4a5578", width=2, tags="grid")
        self.canvas.create_line(self.gx0, self.gy0, self.gx0, self.gy1,
                                fill="#4a5578", width=2, tags="grid")

        # подписи осей
        self.canvas.create_text((self.gx0 + self.gx1) / 2, self.gy1 + 28,
                                text="ПОРЯДКОВЫЙ НОМЕР",
                                fill=TEXT_DIM, font=("Segoe UI", 10),
                                tags="grid")
        self.canvas.create_text(self.gx0 - 55, (self.gy0 + self.gy1) / 2,
                                text="ЗНАЧЕНИЕ", fill=TEXT_DIM,
                                font=("Segoe UI", 10), angle=90,
                                tags="grid")

    def _draw_button(self):
        btn = NeonButton(self.root, "ПОСТРОИТЬ 1000 ТОЧЕК",
                         command=self.build,
                         width=340, height=54)
        self.canvas.create_window(550, 700, window=btn)

    def _draw_footer(self):
        self.canvas.create_text(
            550, 755,
            text="© ОКФРС · Практическое занятие 2 · Программа 4",
            fill="#2f3a5a", font=("Segoe UI", 9))

    def build(self):
        self.canvas.delete("dot")

        nums = [random.randint(0, 100) for _ in range(1000)]
        count = len(nums)
        gw = self.gx1 - self.gx0
        gh = self.gy1 - self.gy0
        step = gw / (count - 1) if count > 1 else gw

        # для 1000 точек — очень маленькие
        r = 1

        for i, n in enumerate(nums):
            x = self.gx0 + i * step
            y = self.gy1 - n / 100 * gh
            # свечение
            self.canvas.create_oval(x - r - 1, y - r - 1,
                                    x + r + 1, y + r + 1,
                                    outline=DOT_HALO, fill="",
                                    tags="dot")
            # сама точка
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=DOT_COLOR, outline="",
                                    tags="dot")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()