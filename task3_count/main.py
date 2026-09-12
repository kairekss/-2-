"""
ОКФРС. ПЗ №2. Программа 3.
Количество случайных чисел задаётся TrackBar.
"""
import tkinter as tk
import random


BG_TOP     = "#0d1020"
BG_BOTTOM  = "#1a1f35"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
ACCENT     = "#ff3860"
GREEN      = "#22c55e"
NEON       = "#00d4ff"
TEXT_MAIN  = "#e8ecf8"
TEXT_DIM   = "#6b7a9c"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 width=280, height=52, color=ACCENT):
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

    def set_text(self, t):
        self.text = t
        self._draw()

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
        root.title("ОКФРС · Программа 3 · Количество через TrackBar")
        root.geometry("1000x720")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1000, height=720,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        self._draw_bg()
        self._draw_header()
        self._draw_controls()
        self._draw_memo()
        self._draw_button()
        self._draw_footer()

    def _draw_bg(self):
        for i in range(720):
            self.canvas.create_line(0, i, 1000, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/720))

    def _draw_header(self):
        self.canvas.create_text(
            500, 42, text="КОЛИЧЕСТВО ЧЕРЕЗ TRACKBAR",
            fill=TEXT_MAIN, font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(
            500, 74,
            text="ОКФРС · ПЗ №2 · Программа 3 · диапазон 0..100",
            fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(180, 100, 820, 100, fill=NEON, width=2)
        self.canvas.create_line(180, 102, 820, 102,
                                fill=lerp(NEON, BG_TOP, 0.7), width=1)

    def _draw_controls(self):
        self.canvas.create_rectangle(78, 120, 922, 250,
                                     fill=PANEL_BG, outline=PANEL_BRD)

        self.canvas.create_text(
            100, 140, text="▸ КОЛИЧЕСТВО ЧИСЕЛ (1..1000)",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")

        self.scale = tk.Scale(
            self.root, from_=1, to=1000, orient="horizontal",
            bg=PANEL_BG, fg=TEXT_MAIN, troughcolor="#060a16",
            highlightthickness=0, bd=0, length=620,
            activebackground=NEON, font=("Segoe UI", 10),
            command=self.on_change)
        self.scale.set(50)
        self.canvas.create_window(100, 162, window=self.scale, anchor="nw")

        # индикатор
        self.value_lbl = self.canvas.create_text(
            780, 178, text="50",
            fill=GREEN, font=("Consolas", 22, "bold"), anchor="w")

        self.canvas.create_text(
            100, 228, text="→ сколько чисел сгенерировать в диапазоне 0..100",
            fill=TEXT_DIM, font=("Segoe UI", 9), anchor="w")

    def _draw_memo(self):
        self.canvas.create_text(
            80, 275, text="▸ MEMO · РЕЗУЛЬТАТ",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")
        self.canvas.create_rectangle(
            78, 297, 922, 610,
            fill=PANEL_BG, outline=PANEL_BRD)

        self.memo = tk.Text(
            self.root, bg=PANEL_BG, fg=NEON,
            insertbackground=TEXT_MAIN,
            font=("Consolas", 10), bd=0,
            highlightthickness=0, wrap="word",
            selectbackground="#1e3a5f")
        self.canvas.create_window(92, 308, window=self.memo,
                                  anchor="nw", width=816, height=292)

    def _draw_button(self):
        btn = NeonButton(self.root, "СГЕНЕРИРОВАТЬ",
                         command=self.generate,
                         width=320, height=54)
        self.canvas.create_window(500, 645, window=btn)

    def _draw_footer(self):
        self.canvas.create_text(
            500, 710,
            text="© ОКФРС · Практическое занятие 2 · Программа 3",
            fill="#2f3a5a", font=("Segoe UI", 9))

    def on_change(self, val):
        self.canvas.itemconfig(self.value_lbl, text=val)

    def generate(self):
        n = self.scale.get()
        nums = [random.randint(0, 100) for _ in range(n)]
        self.memo.delete(1.0, tk.END)
        self.memo.insert(tk.END, "   ".join(f"{x:3d}" for x in nums))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()