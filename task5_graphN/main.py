"""
ОКФРС. ПЗ №2. Программа 5.
Графический вывод N (до 1000) случайных чисел
из диапазона, заданного пользователем.
"""
import tkinter as tk
import random


BG_TOP     = "#0d1020"
BG_BOTTOM  = "#1a1f35"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
ACCENT     = "#ff3860"
GREEN      = "#22c55e"
RED        = "#e74c3c"
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
                 width=320, height=52, color=ACCENT):
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
        root.title("ОКФРС · Программа 5 · N точек из диапазона")
        root.geometry("1150x850")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1150, height=850,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        self._draw_bg()
        self._draw_header()
        self._draw_controls()
        self._draw_graph_area()
        self._draw_button()
        self._draw_footer()

    def _draw_bg(self):
        for i in range(850):
            self.canvas.create_line(0, i, 1150, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/850))

    def _draw_header(self):
        self.canvas.create_text(
            575, 42, text="ГРАФИК N ТОЧЕК",
            fill=TEXT_MAIN, font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(
            575, 74,
            text="ОКФРС · ПЗ №2 · Программа 5 · диапазон и N задаёт пользователь",
            fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(230, 100, 920, 100, fill=NEON, width=2)
        self.canvas.create_line(230, 102, 920, 102,
                                fill=lerp(NEON, BG_TOP, 0.7), width=1)

    def _draw_controls(self):
        # панель управления
        self.canvas.create_rectangle(80, 120, 1070, 280,
                                     fill=PANEL_BG, outline=PANEL_BRD)

        # --- MIN ---
        self.canvas.create_text(
            105, 140, text="▸ MIN (0..99)",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")
        self.s_min = tk.Scale(
            self.root, from_=0, to=99, orient="horizontal",
            bg=PANEL_BG, fg=TEXT_MAIN, troughcolor="#060a16",
            highlightthickness=0, bd=0, length=260,
            activebackground=NEON, font=("Segoe UI", 9))
        self.s_min.set(0)
        self.canvas.create_window(105, 162, window=self.s_min, anchor="nw")

        # --- MAX ---
        self.canvas.create_text(
            390, 140, text="▸ MAX (1..100)",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")
        self.s_max = tk.Scale(
            self.root, from_=1, to=100, orient="horizontal",
            bg=PANEL_BG, fg=TEXT_MAIN, troughcolor="#060a16",
            highlightthickness=0, bd=0, length=260,
            activebackground=NEON, font=("Segoe UI", 9))
        self.s_max.set(100)
        self.canvas.create_window(390, 162, window=self.s_max, anchor="nw")

        # --- КОЛИЧЕСТВО ---
        self.canvas.create_text(
            675, 140, text="▸ N (1..1000)",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")
        self.s_cnt = tk.Scale(
            self.root, from_=1, to=1000, orient="horizontal",
            bg=PANEL_BG, fg=TEXT_MAIN, troughcolor="#060a16",
            highlightthickness=0, bd=0, length=350,
            activebackground=NEON, font=("Segoe UI", 9))
        self.s_cnt.set(300)
        self.canvas.create_window(675, 162, window=self.s_cnt, anchor="nw")

        # статус
        self.status_lbl = self.canvas.create_text(
            575, 255, text="Готово. Настрой параметры и нажми «Построить».",
            fill=TEXT_DIM, font=("Segoe UI", 10))

    def _draw_graph_area(self):
        # панель графика
        self.canvas.create_rectangle(80, 300, 1070, 760,
                                     fill="#080b16", outline=PANEL_BRD)

        self.gx0, self.gy0 = 150, 330
        self.gx1, self.gy1 = 1040, 720

        # оси
        self.canvas.create_line(self.gx0, self.gy1, self.gx1, self.gy1,
                                fill="#4a5578", width=2, tags="axis")
        self.canvas.create_line(self.gx0, self.gy0, self.gx0, self.gy1,
                                fill="#4a5578", width=2, tags="axis")

        # подписи осей
        self.canvas.create_text((self.gx0 + self.gx1) / 2, self.gy1 + 25,
                                text="ПОРЯДКОВЫЙ НОМЕР",
                                fill=TEXT_DIM, font=("Segoe UI", 10),
                                tags="axis")
        self.canvas.create_text(self.gx0 - 55, (self.gy0 + self.gy1) / 2,
                                text="ЗНАЧЕНИЕ", fill=TEXT_DIM,
                                font=("Segoe UI", 10), angle=90,
                                tags="axis")

    def _draw_button(self):
        btn = NeonButton(self.root, "ПОСТРОИТЬ ГРАФИК",
                         command=self.build,
                         width=340, height=54)
        self.canvas.create_window(575, 795, window=btn)

    def _draw_footer(self):
        self.canvas.create_text(
            575, 835,
            text="© ОКФРС · Практическое занятие 2 · Программа 5",
            fill="#2f3a5a", font=("Segoe UI", 9))

    def _clear_dynamic(self):
        self.canvas.delete("grid")
        self.canvas.delete("dot")
        self.canvas.delete("label_axis")

    def build(self):
        low = self.s_min.get()
        high = self.s_max.get()
        count = self.s_cnt.get()

        # валидация
        if low >= high:
            self.canvas.itemconfig(
                self.status_lbl,
                text="✕ Ошибка: MIN должен быть меньше MAX",
                fill=RED)
            return

        self._clear_dynamic()
        self.canvas.itemconfig(
            self.status_lbl,
            text=f"✓ Диапазон: {low}..{high} · Точек: {count}",
            fill=GREEN)

        # сетка Y
        for i in range(6):
            gy = self.gy0 + i * (self.gy1 - self.gy0) / 5
            self.canvas.create_line(self.gx0, gy, self.gx1, gy,
                                    fill=GRID, tags="grid")
            val = high - i * (high - low) / 5
            self.canvas.create_text(self.gx0 - 15, gy, text=f"{int(val)}",
                                    fill=TEXT_DIM, font=("Segoe UI", 9),
                                    anchor="e", tags="grid")

        # сетка X
        for i in range(11):
            gx = self.gx0 + i * (self.gx1 - self.gx0) / 10
            self.canvas.create_line(gx, self.gy0, gx, self.gy1,
                                    fill=GRID, tags="grid")

        # генерация
        nums = [random.randint(low, high) for _ in range(count)]
        gw = self.gx1 - self.gx0
        gh = self.gy1 - self.gy0
        step = gw / (count - 1) if count > 1 else gw
        span = high - low

        # размер точки
        if count <= 100:
            r = 4
        elif count <= 400:
            r = 2
        else:
            r = 1

        for i, n in enumerate(nums):
            x = self.gx0 + i * step
            y = self.gy1 - (n - low) / span * gh

            # свечение (для крупных точек)
            if r >= 2:
                self.canvas.create_oval(x - r - 2, y - r - 2,
                                        x + r + 2, y + r + 2,
                                        outline=DOT_HALO, fill="",
                                        tags="dot")
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=DOT_COLOR, outline="",
                                    tags="dot")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()