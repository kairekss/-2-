"""
ОКФРС. ПЗ №2. Бонус 2.
Анимированный переключатель с неоновой подсветкой.
"""
import tkinter as tk


BG_TOP     = "#0a0e1c"
BG_BOTTOM  = "#141a30"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
NEON       = "#22d3ee"
GREEN      = "#22c55e"
GREEN_GLOW = "#0a4a26"
RED        = "#ff3860"
RED_GLOW   = "#5a0a1e"
TEXT_MAIN  = "#eef2ff"
TEXT_DIM   = "#5c6a90"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class Tumbler:
    def __init__(self, canvas, cx, cy, on_change=None):
        self.canvas = canvas
        self.cx, self.cy = cx, cy
        self.on_change = on_change

        self.W, self.H = 280, 120
        self.LEVER_W, self.LEVER_H = 110, 90
        self.state = False
        self.animating = False

        self._build()
        for item in self.clickable:
            canvas.tag_bind(item, "<Button-1>", self.toggle)

    def _build(self):
        c = self.canvas
        x = self.cx - self.W//2
        y = self.cy - self.H//2
        W, H = self.W, self.H

        # внешний ореол
        self.outer_glow = []
        for i in range(8, 0, -1):
            item = c.create_oval(
                x - i*2, y - i*2, x+W + i*2, y+H + i*2,
                outline=lerp(RED_GLOW, BG_TOP, i*0.1), width=1)
            self.outer_glow.append(item)

        # тень корпуса
        c.create_rectangle(x+6, y+8, x+W+6, y+H+8,
                           fill="#02040a", outline="")

        # корпус (металлический оттенок)
        self.body = c.create_rectangle(x, y, x+W, y+H,
                                       fill="#1a2035",
                                       outline=PANEL_BRD, width=2)
        # внутренняя рамка
        c.create_rectangle(x+4, y+4, x+W-4, y+H-4,
                           outline=lerp(NEON, PANEL_BG, 0.85), width=1)

        # внутренняя дорожка
        c.create_rectangle(x+20, y+H//2-12, x+W-20, y+H//2+12,
                           fill="#05070f", outline="#1a2340")

        # подписи ON / OFF
        self.lbl_off = c.create_text(
            x + 50, y + H + 32, text="OFF",
            fill=RED, font=("Consolas", 13, "bold"))
        self.lbl_on = c.create_text(
            x + W - 50, y + H + 32, text="ON",
            fill=TEXT_DIM, font=("Consolas", 13, "bold"))

        # сам рычажок
        self.x_off = x + 18
        self.x_on  = x + W - self.LEVER_W - 18
        self.y_lever = y + (H - self.LEVER_H) // 2

        self._draw_lever()

    def _draw_lever(self):
        c = self.canvas
        x = self.x_off if not self.state else self.x_on
        y = self.y_lever
        LW, LH = self.LEVER_W, self.LEVER_H
        color = RED if not self.state else GREEN

        # тень
        self.lever_shadow = c.create_rectangle(
            x+3, y+3, x+LW+3, y+LH+3,
            fill="#02040a", outline="")

        # тело
        self.lever = c.create_rectangle(
            x, y, x+LW, y+LH,
            fill=color,
            outline=lerp(color, "#ffffff", 0.55),
            width=2)

        # верхний блик
        self.lever_gloss = c.create_rectangle(
            x+5, y+5, x+LW-5, y+LH//2,
            fill=lerp(color, "#ffffff", 0.4), outline="")

        # иконка внутри
        cx = x + LW//2
        cy = y + LH//2
        symbol = "✕" if not self.state else "⚡"
        self.lever_icon = c.create_text(
            cx, cy, text=symbol, fill="#ffffff",
            font=("Segoe UI", 24, "bold"))

        self.clickable = [self.body, self.lever,
                          self.lever_shadow, self.lever_gloss,
                          self.lever_icon]

    def toggle(self, e=None):
        if self.animating:
            return
        self.state = not self.state
        self.animating = True

        # подписи
        self.canvas.itemconfig(self.lbl_on,
                               fill=GREEN if self.state else TEXT_DIM)
        self.canvas.itemconfig(self.lbl_off,
                               fill=RED if not self.state else TEXT_DIM)

        # цвет
        color = GREEN if self.state else RED
        self.canvas.itemconfig(self.lever, fill=color,
                               outline=lerp(color, "#ffffff", 0.55))
        self.canvas.itemconfig(self.lever_gloss,
                               fill=lerp(color, "#ffffff", 0.4))
        self.canvas.itemconfig(self.lever_icon,
                               text="⚡" if self.state else "✕")

        # свечение снаружи
        glow_color = GREEN if self.state else RED
        for i, gid in enumerate(self.outer_glow):
            spread = (8 - i) * 2
            col = lerp(glow_color, BG_TOP, i*0.12) if self.state else \
                  lerp(glow_color, BG_TOP, 0.85)
            self.canvas.itemconfig(gid, outline=col)

        target = self.x_on if self.state else self.x_off
        self._animate(target)

        if self.on_change:
            self.on_change(self.state)

    def _animate(self, target):
        cur = self.canvas.coords(self.lever)[0]
        if abs(cur - target) < 3:
            self.animating = False
            return
        step = 6 if target > cur else -6
        for tag_item in (self.lever, self.lever_shadow,
                         self.lever_gloss, self.lever_icon):
            self.canvas.move(tag_item, step, 0)
        self.canvas.after(12, lambda: self._animate(target))


class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Бонус 2 · Анимированный тумблер")
        root.geometry("900x560")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=900, height=560,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        for i in range(560):
            self.canvas.create_line(0, i, 900, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/560))

        # заголовок
        self.canvas.create_text(450, 50,
                                text="АНИМИРОВАННЫЙ ТУМБЛЕР",
                                fill=TEXT_MAIN,
                                font=("Segoe UI", 24, "bold"))
        self.canvas.create_text(450, 84,
                                text="ОКФРС · ПЗ №2 · Бонус 2 · неон ON/OFF",
                                fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(250, 108, 650, 108, fill=NEON, width=2)
        self.canvas.create_line(250, 110, 650, 110,
                                fill=lerp(NEON, BG_TOP, 0.7))

        # тумблер
        Tumbler(self.canvas, 450, 280, on_change=self.on_change)

        # статус
        self.status = self.canvas.create_text(
            450, 480,
            text="○ Отключено",
            fill=RED, font=("Consolas", 15, "bold"))

        self.canvas.create_text(450, 530,
                                text="© ОКФРС · ПЗ №2 · Бонус 2",
                                fill="#2a3350", font=("Segoe UI", 9))

    def on_change(self, state):
        self.canvas.itemconfig(
            self.status,
            text="⚡ Включено" if state else "○ Отключено",
            fill=GREEN if state else RED)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()