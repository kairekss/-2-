"""
ОКФРС. ПЗ №2. Программа 2.
Диапазон задаётся TrackBar. Значение меняется вручную или по таймеру.
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
GRAY       = "#7a8098"
NEON       = "#00d4ff"
TEXT_MAIN  = "#e8ecf8"
TEXT_DIM   = "#6b7a9c"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


# ---------------- КНОПКА ----------------
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 width=240, height=48, color=ACCENT):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0)
        self.command = command
        self.text = text
        self.color = color
        self.w, self.h = width, height
        self.hovered = False
        self.pressed = False
        self.enabled = True          # <-- добавили флаг активности
        self._draw()
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress>", self._press)
        self.bind("<ButtonRelease>", self._release)

    def _draw(self):
        self.delete("all")
        c = self.color
        if not self.enabled:
            c = "#3a4058"
        elif self.pressed:
            c = lerp(self.color, "#000000", 0.25)
        elif self.hovered:
            c = lerp(self.color, "#ffffff", 0.15)

        if self.hovered and self.enabled:
            for i in range(4, 0, -1):
                self.create_rectangle(-i, -i, self.w+i, self.h+i,
                                      outline=lerp(self.color, PANEL_BG, i*0.2))

        self.create_rectangle(4, 5, self.w+4, self.h+5,
                              fill="#050810", outline="")
        self.create_rectangle(0, 0, self.w, self.h, fill=c,
                              outline=lerp(c, "#ffffff", 0.4) if self.enabled else "#4a5070")
        if self.enabled:
            self.create_rectangle(2, 2, self.w-2, self.h//2,
                                  fill=lerp(c, "#ffffff", 0.25), outline="")
        self.create_text(self.w/2, self.h/2, text=self.text,
                         fill="#ffffff" if self.enabled else "#8a90a8",
                         font=("Segoe UI", 11, "bold"))

    # ----- методы, которые могли падать -----
    def set_text(self, text):
        self.text = text
        self._draw()

    def set_color(self, color):
        self.color = color
        self._draw()

    # ----- события -----
    def _enter(self, e):
        if not self.enabled: return
        self.hovered = True
        self.configure(cursor="hand2")
        self._draw()

    def _leave(self, e):
        self.hovered = False
        self.pressed = False
        self.configure(cursor="")
        self._draw()

    def _press(self, e):
        if not self.enabled: return
        self.pressed = True
        self._draw()

    def _release(self, e):
        if not self.enabled: return
        self.pressed = False
        self._draw()
        # ВАЖНО: защита от None
        if callable(self.command):
            self.command()


# ---------------- ПРИЛОЖЕНИЕ ----------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Программа 2 · Диапазон через TrackBar")
        root.geometry("1000x720")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1000, height=720,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        # сначала объявляем атрибуты (иначе None)
        self.auto_running = False
        self.auto_btn = None
        self.gen_btn = None
        self.clear_btn = None

        self._draw_bg()
        self._draw_header()
        self._draw_controls()
        self._draw_memo()
        self._draw_footer()

    def _draw_bg(self):
        for i in range(720):
            self.canvas.create_line(0, i, 1000, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/720))

    def _draw_header(self):
        self.canvas.create_text(
            500, 42, text="ДИАПАЗОН ЧЕРЕЗ TRACKBAR",
            fill=TEXT_MAIN, font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(
            500, 74,
            text="ОКФРС · ПЗ №2 · Программа 2 · вручную или по таймеру",
            fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(180, 100, 820, 100, fill=NEON, width=2)
        self.canvas.create_line(180, 102, 820, 102,
                                fill=lerp(NEON, BG_TOP, 0.7), width=1)

    def _draw_controls(self):
        self.canvas.create_rectangle(
            78, 120, 922, 260,
            fill=PANEL_BG, outline=PANEL_BRD)

        self.canvas.create_text(
            100, 140, text="▸ МАКСИМАЛЬНОЕ ЗНАЧЕНИЕ (0..100)",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")

        self.scale = tk.Scale(
            self.root, from_=1, to=100, orient="horizontal",
            bg=PANEL_BG, fg=TEXT_MAIN, troughcolor="#060a16",
            highlightthickness=0, bd=0, length=500,
            activebackground=NEON,
            font=("Segoe UI", 10),
            command=self.on_change)
        self.scale.set(100)
        self.canvas.create_window(100, 160, window=self.scale, anchor="nw")

        self.value_lbl = self.canvas.create_text(
            700, 178, text="MAX = 100",
            fill=GREEN, font=("Consolas", 14, "bold"), anchor="w")

        # --- кнопки ---
        self.auto_btn = NeonButton(
            self.root, "▶  АВТО",
            command=self.toggle_auto,
            width=200, height=44, color=GREEN)
        self.canvas.create_window(100, 215, window=self.auto_btn, anchor="nw")

        self.gen_btn = NeonButton(
            self.root, "＋  ОДНО ЧИСЛО",
            command=self.gen_one,
            width=200, height=44, color=ACCENT)
        self.canvas.create_window(320, 215, window=self.gen_btn, anchor="nw")

        self.clear_btn = NeonButton(
            self.root, "✕  ОЧИСТИТЬ",
            command=self.clear,
            width=200, height=44, color=GRAY)
        self.canvas.create_window(540, 215, window=self.clear_btn, anchor="nw")

    def _draw_memo(self):
        self.canvas.create_text(
            80, 285, text="▸ MEMO · РЕЗУЛЬТАТ",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")
        self.canvas.create_rectangle(
            78, 307, 922, 640,
            fill=PANEL_BG, outline=PANEL_BRD)

        self.memo = tk.Text(
            self.root, bg=PANEL_BG, fg=NEON,
            insertbackground=TEXT_MAIN,
            font=("Consolas", 11), bd=0,
            highlightthickness=0, wrap="word",
            selectbackground="#1e3a5f")
        self.canvas.create_window(92, 318, window=self.memo,
                                  anchor="nw", width=816, height=312)

    def _draw_footer(self):
        self.canvas.create_text(
            500, 700,
            text="© ОКФРС · Практическое занятие 2 · Программа 2",
            fill="#2f3a5a", font=("Segoe UI", 9))

    # --------- логика ---------
    def on_change(self, val):
        self.canvas.itemconfig(self.value_lbl, text=f"MAX = {val}")

    def gen_one(self):
        hi = int(self.scale.get())
        n = random.randint(0, hi)
        self.memo.insert(tk.END, f"  {n}")
        self.memo.see(tk.END)

    def clear(self):
        self.memo.delete(1.0, tk.END)

    def toggle_auto(self):
        # если кнопки по какой-то причине нет — выходим
        if self.auto_btn is None:
            return

        self.auto_running = not self.auto_running

        if self.auto_running:
            self.auto_btn.set_text("■  СТОП")
            self.auto_btn.set_color(RED)
            self._auto_tick()
        else:
            self.auto_btn.set_text("▶  АВТО")
            self.auto_btn.set_color(GREEN)

    def _auto_tick(self):
        if not self.auto_running:
            return
        new_val = random.randint(1, 100)
        self.scale.set(new_val)
        self.gen_one()
        self.root.after(300, self._auto_tick)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()