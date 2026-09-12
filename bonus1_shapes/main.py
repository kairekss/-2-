"""
ОКФРС. ПЗ №2. Бонус 1.
Кнопки сложной формы — v2 (исправленная).

Исправлено:
  - правильно построены слои: свечение → тень → тело → блик;
  - клик ловится только на верхнем прозрачном слое;
  - hover/press меняют только цвет, не пересоздают объекты;
  - клик можно нажимать много раз, состояние не залипает.
"""
import tkinter as tk
import math
import random


# ------------------------- ПАЛИТРА -------------------------
BG_TOP      = "#0a0e1c"
BG_BOTTOM   = "#141a30"
TEXT_MAIN   = "#eef2ff"
TEXT_DIM    = "#5c6a90"
TEXT_ACCENT = "#7cc4ff"
NEON_CYAN   = "#22d3ee"
NEON_PINK   = "#ff4d8d"
NEON_PURP   = "#a78bfa"
NEON_GOLD   = "#fbbf24"
NEON_ROSE   = "#fb7185"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t))


# ------------------------- ФОН С ЧАСТИЦАМИ -------------------------
class ParticleBackground:
    def __init__(self, canvas, w, h, count=40):
        self.canvas = canvas
        self.w, self.h = w, h
        self.particles = []
        for _ in range(count):
            self.particles.append([
                random.uniform(0, w),
                random.uniform(0, h),
                random.uniform(0.6, 1.7),
                random.uniform(0.15, 0.5),
                random.choice([NEON_CYAN, NEON_PURP, NEON_PINK, "#3b6bff"])
            ])
        self._tick()

    def _tick(self):
        self.canvas.delete("particle")
        for p in self.particles:
            p[1] -= p[3]
            if p[1] < -5:
                p[1] = self.h + 5
                p[0] = random.uniform(0, self.w)
            x, y, r, _, color = p
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=color, outline="",
                                    tags="particle")
        # частицы всегда ниже кнопок
        self.canvas.tag_lower("particle")
        self.canvas.after(35, self._tick)


# ------------------------- КНОПКА-ФИГУРА -------------------------
class FancyShapeButton:
    def __init__(self, canvas, shape, cx, cy, size,
                 base_color, label, command=None):
        self.canvas = canvas
        self.shape = shape
        self.cx, self.cy = cx, cy
        self.size = size
        self.base_color = base_color
        self.label = label
        self.command = command

        self.hovered = False
        self.pressed = False
        self.clicks = 0

        # id слоёв
        self.glow_ids = []
        self.shadow_id = None
        self.body_id = None
        self.ring_id = None       # только для double_oval
        self.gloss_id = None
        self.label_id = None
        self.counter_id = None

        self._build()

    # --------- геометрия ---------
    def _polygon_pts(self, cx, cy, size):
        if self.shape == "triangle":
            return [cx, cy - size/2,
                    cx - size/2, cy + size/2,
                    cx + size/2, cy + size/2]
        if self.shape == "hexagon":
            return self._regular_polygon(cx, cy, size, 6, -30)
        if self.shape == "octagon":
            return self._regular_polygon(cx, cy, size, 8, -22.5)
        if self.shape == "star6":
            pts = []
            for i in range(12):
                a = math.radians(i * 30)
                r = size/2 if i % 2 == 0 else size/4
                pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
            return pts
        return []

    def _regular_polygon(self, cx, cy, size, n, start_deg):
        pts = []
        for i in range(n):
            a = math.radians(i * 360/n + start_deg)
            pts += [cx + size/2 * math.cos(a),
                    cy + size/2 * math.sin(a)]
        return pts

    # --------- сборка ---------
    def _build(self):
        c = self.canvas
        s = self.size

        # ---- 1. СВЕЧЕНИЕ (создаём сразу, слоями, но скрытое цветом фона) ----
        self._create_glow_layers()

        # ---- 2. ТЕНЬ ----
        off = 8
        if self.shape == "double_oval":
            self.shadow_id = c.create_oval(
                self.cx - s/2 + off, self.cy - s/2 + off,
                self.cx + s/2 + off, self.cy + s/2 + off,
                fill="#02040a", outline="")
        else:
            self.shadow_id = c.create_polygon(
                self._polygon_pts(self.cx + off, self.cy + off, s),
                fill="#02040a", outline="")

        # ---- 3. ТЕЛО ----
        if self.shape == "double_oval":
            # внешнее кольцо
            self.ring_id = c.create_oval(
                self.cx - s/2, self.cy - s/2,
                self.cx + s/2, self.cy + s/2,
                outline=self.base_color, width=6, fill="")
            # внутренний круг
            self.body_id = c.create_oval(
                self.cx - s*0.33, self.cy - s*0.33,
                self.cx + s*0.33, self.cy + s*0.33,
                fill=self.base_color, outline="")
        else:
            self.body_id = c.create_polygon(
                self._polygon_pts(self.cx, self.cy, s),
                fill=self.base_color,
                outline=lerp(self.base_color, "#ffffff", 0.45),
                width=2)

        # ---- 4. БЛИК ----
        self._create_gloss()

        # ---- 5. ПРОЗРАЧНАЯ ЗОНА КЛИКА (невидимая, но ловит события) ----
        # Создаём её ПОСЛЕДНЕЙ, чтобы она была сверху и ловила все клики.
        if self.shape == "double_oval":
            self.click_zone = c.create_oval(
                self.cx - s/2 - 5, self.cy - s/2 - 5,
                self.cx + s/2 + 5, self.cy + s/2 + 5,
                fill="", outline="", width=0)
        else:
            self.click_zone = c.create_polygon(
                self._polygon_pts(self.cx, self.cy, s + 10),
                fill="", outline="", width=0)

        # ---- 6. ПОДПИСЬ И СЧЁТЧИК ----
        self.label_id = c.create_text(
            self.cx, self.cy + s/2 + 34,
            text=self.label, fill=TEXT_DIM,
            font=("Segoe UI", 11, "bold"))
        self.counter_id = c.create_text(
            self.cx, self.cy + s/2 + 54,
            text="клик: 0", fill=TEXT_ACCENT,
            font=("Consolas", 9))

        # ---- 7. СОБЫТИЯ — только на click_zone ----
        c.tag_bind(self.click_zone, "<Enter>", self._on_enter)
        c.tag_bind(self.click_zone, "<Leave>", self._on_leave)
        c.tag_bind(self.click_zone, "<ButtonPress>", self._on_press)
        c.tag_bind(self.click_zone, "<ButtonRelease>", self._on_release)
        # чтобы клики работали и на самом теле/блике — тоже подключаем
        for item in (self.body_id, self.ring_id, self.gloss_id):
            if item:
                c.tag_bind(item, "<Enter>", self._on_enter)
                c.tag_bind(item, "<Leave>", self._on_leave)
                c.tag_bind(item, "<ButtonPress>", self._on_press)
                c.tag_bind(item, "<ButtonRelease>", self._on_release)

    # --------- свечение ---------
    def _create_glow_layers(self, visible=False):
        """Создаёт ореол вокруг фигуры. Изначально невидим (цвет фона)."""
        c = self.canvas
        s = self.size
        color_hidden = "#0a0e1c"   # = фон
        self.glow_ids = []

        for i in range(6, 0, -1):
            spread = i * 3
            if self.shape == "double_oval":
                item = c.create_oval(
                    self.cx - s/2 - spread, self.cy - s/2 - spread,
                    self.cx + s/2 + spread, self.cy + s/2 + spread,
                    outline=color_hidden, width=2)
            else:
                pts = self._polygon_pts(self.cx, self.cy, s + spread*2)
                item = c.create_polygon(pts, fill="",
                                        outline=color_hidden, width=2)
            self.glow_ids.append(item)

    def _set_glow(self, level):
        """level 0..1 — уровень свечения."""
        if not self.glow_ids:
            return
        base = self.base_color
        n = len(self.glow_ids)
        for idx, gid in enumerate(self.glow_ids):
            # чем ближе слой, тем ярче
            t = (n - idx) / n
            col = lerp("#0a0e1c", base, level * t)
            self.canvas.itemconfig(gid, outline=col)

    # --------- блик ---------
    def _create_gloss(self):
        c = self.canvas
        s = self.size
        cx, cy = self.cx, self.cy

        if self.shape == "double_oval":
            self.gloss_id = c.create_arc(
                cx - s*0.28, cy - s*0.28,
                cx + s*0.28, cy + s*0.28,
                start=40, extent=100,
                outline=lerp(self.base_color, "#ffffff", 0.75),
                style="arc", width=3)
        elif self.shape == "triangle":
            self.gloss_id = c.create_polygon(
                cx, cy - s/2 + 14,
                cx - s/4, cy - s/10,
                cx + s/4, cy - s/10,
                fill=lerp(self.base_color, "#ffffff", 0.55),
                outline="")
        else:
            self.gloss_id = c.create_polygon(
                cx, cy - s/2 + 10,
                cx - s/3, cy - s/10,
                cx + s/3, cy - s/10,
                fill=lerp(self.base_color, "#ffffff", 0.55),
                outline="")

    # --------- цвет по состоянию ---------
    def _apply_color(self):
        c = self.canvas
        base = self.base_color

        if self.pressed:
            top = lerp(base, "#000000", 0.25)
        elif self.hovered:
            top = lerp(base, "#ffffff", 0.2)
        else:
            top = base

        if self.shape == "double_oval":
            c.itemconfig(self.body_id, fill=top)
            c.itemconfig(self.ring_id, outline=lerp(top, "#ffffff", 0.3))
            if self.gloss_id:
                c.itemconfig(self.gloss_id,
                             outline=lerp(top, "#ffffff", 0.75))
        else:
            c.itemconfig(self.body_id, fill=top,
                         outline=lerp(top, "#ffffff", 0.45))
            if self.gloss_id:
                c.itemconfig(self.gloss_id,
                             fill=lerp(top, "#ffffff", 0.55))

    # --------- сдвиг при нажатии ---------
    def _shift(self, dy):
        c = self.canvas
        items = [self.body_id, self.ring_id, self.gloss_id,
                 self.label_id, self.counter_id]
        for it in items:
            if it:
                c.move(it, 0, dy)

    # --------- события ---------
    def _on_enter(self, e):
        if self.hovered:
            return
        self.hovered = True
        self.canvas.config(cursor="hand2")
        self._apply_color()
        self.canvas.itemconfig(self.label_id, fill=TEXT_MAIN)
        self._fade_glow(0.0, 1.0)

    def _on_leave(self, e):
        self.hovered = False
        self.pressed = False
        self.canvas.config(cursor="")
        self._apply_color()
        self.canvas.itemconfig(self.label_id, fill=TEXT_DIM)
        self._fade_glow(1.0, 0.0)

    def _on_press(self, e):
        if self.pressed:
            return
        self.pressed = True
        self._apply_color()
        self._shift(3)

    def _on_release(self, e):
        if not self.pressed:
            return
        self.pressed = False
        self._apply_color()
        self._shift(-3)
        self.clicks += 1
        self.canvas.itemconfig(
            self.counter_id,
            text=f"клик: {self.clicks}",
            fill=NEON_CYAN)

        # после клика всегда возвращаем «нормальный» hover-цвет
        self._apply_color()

        if callable(self.command):
            self.command()

    # --------- плавное свечение ---------
    def _fade_glow(self, frm, to):
        steps = 6
        if frm == to:
            self._set_glow(to)
            return

        def step(i=0):
            if i > steps:
                self._set_glow(to)
                return
            t = i / steps
            lvl = frm + (to - frm) * t
            self._set_glow(lvl)
            self.canvas.after(20, lambda: step(i + 1))

        step()


# ------------------------- ГЛАВНОЕ ОКНО -------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Бонус 1 · Кнопки сложной формы")
        root.geometry("1200x680")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1200, height=680,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        # 1. градиент (самый нижний слой)
        self._draw_gradient()

        # 2. заголовок
        self._draw_header()

        # 3. частицы
        ParticleBackground(self.canvas, 1200, 680, count=45)

        # 4. кнопки (поверх всего)
        self._spawn_buttons()

        # 5. подпись снизу
        self.canvas.create_text(
            600, 655,
            text="© ОКФРС · ПЗ №2 · Бонус 1 · hover · click · glow",
            fill="#2a3350", font=("Segoe UI", 9))

    def _draw_gradient(self):
        for i in range(680):
            color = lerp(BG_TOP, BG_BOTTOM, i / 680)
            self.canvas.create_line(0, i, 1200, i,
                                    fill=color, tags="bg")

    def _draw_header(self):
        self.canvas.create_text(
            600, 50, text="КНОПКИ СЛОЖНОЙ ФОРМЫ",
            fill=TEXT_MAIN, font=("Segoe UI", 26, "bold"))
        self.canvas.create_text(
            600, 88,
            text="наведи · нажми · почувствуй отклик",
            fill=TEXT_ACCENT, font=("Segoe UI", 11))
        self.canvas.create_line(300, 115, 900, 115,
                                fill=NEON_CYAN, width=2)
        self.canvas.create_line(300, 117, 900, 117,
                                fill=lerp(NEON_CYAN, BG_TOP, 0.7), width=1)

    def _spawn_buttons(self):
        y = 340
        data = [
            ("triangle",    180,  y, 130, NEON_PINK, "ТРЕУГОЛЬНИК"),
            ("hexagon",     400,  y, 140, NEON_GOLD, "ШЕСТИУГОЛЬНИК"),
            ("octagon",     620,  y, 140, NEON_CYAN, "ВОСЬМИУГОЛЬНИК"),
            ("star6",       840,  y, 140, NEON_PURP, "ЗВЕЗДА"),
            ("double_oval", 1030, y, 120, NEON_ROSE, "ДВОЙНОЙ ОВАЛ"),
        ]
        for shape, cx, cy, size, color, label in data:
            FancyShapeButton(self.canvas, shape, cx, cy,
                             size, color, label)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()