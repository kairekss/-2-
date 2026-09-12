"""
ОКФРС. ПЗ №2. Программа 1.
Вывод 1000 случайных чисел (0..100) в Memo по кнопке.
"""
import tkinter as tk
import random


# ----------------------- ПАЛИТРА ПРЕМИУМ -----------------------
BG_TOP     = "#0d1020"
BG_BOTTOM  = "#1a1f35"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
ACCENT     = "#ff3860"
ACCENT_H   = "#ff5c7c"
NEON       = "#00d4ff"
TEXT_MAIN  = "#e8ecf8"
TEXT_DIM   = "#6b7a9c"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


# --------------------- КНОПКА СО СВЕЧЕНИЕМ ---------------------
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 width=280, height=54, color=ACCENT):
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

        # свечение (многослойный контур)
        if self.hovered:
            for i in range(4, 0, -1):
                self.create_rectangle(
                    -i, -i, self.w+i, self.h+i,
                    outline=lerp(self.color, PANEL_BG, i*0.2), width=1)

        # тень
        self.create_rectangle(4, 5, self.w+4, self.h+5,
                              fill="#050810", outline="")
        # тело
        self.create_rectangle(0, 0, self.w, self.h,
                              fill=c, outline=lerp(c, "#ffffff", 0.4),
                              width=1)
        # блик сверху
        self.create_rectangle(2, 2, self.w-2, self.h//2,
                              fill=lerp(c, "#ffffff", 0.25), outline="")
        # текст
        self.create_text(self.w/2, self.h/2, text=self.text,
                         fill="#ffffff", font=("Segoe UI", 12, "bold"))

    def _enter(self, e):
        self.hovered = True
        self.configure(cursor="hand2")
        self._draw()

    def _leave(self, e):
        self.hovered = False
        self.pressed = False
        self.configure(cursor="")
        self._draw()

    def _press(self, e):
        self.pressed = True
        self._draw()

    def _release(self, e):
        self.pressed = False
        self._draw()
        if self.command:
            self.command()


# --------------------------- ПРИЛОЖЕНИЕ ---------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Программа 1 · 1000 чисел в Memo")
        root.geometry("1000x720")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1000, height=720,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        self._draw_bg()
        self._draw_header()
        self._draw_memo()
        self._draw_button()
        self._draw_footer()

    def _draw_bg(self):
        for i in range(720):
            self.canvas.create_line(0, i, 1000, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/720))

    def _draw_header(self):
        self.canvas.create_text(
            500, 42, text="ГЕНЕРАТОР 1000 ЧИСЕЛ",
            fill=TEXT_MAIN, font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(
            500, 74,
            text="ОКФРС · ПЗ №2 · Программа 1 · диапазон 0..100",
            fill=TEXT_DIM, font=("Segoe UI", 10))
        # неоновая линия
        self.canvas.create_line(180, 100, 820, 100,
                                fill=NEON, width=2)
        self.canvas.create_line(180, 102, 820, 102,
                                fill=lerp(NEON, BG_TOP, 0.7), width=1)

    def _draw_memo(self):
        self.canvas.create_text(
            80, 128, text="▸ MEMO · РЕЗУЛЬТАТ",
            fill=NEON, font=("Segoe UI", 10, "bold"), anchor="w")

        # рамка панели
        self.canvas.create_rectangle(78, 150, 922, 610,
                                     fill=PANEL_BG,
                                     outline=PANEL_BRD, width=1)

        self.memo = tk.Text(
            self.root, bg=PANEL_BG, fg=NEON,
            insertbackground=TEXT_MAIN,
            font=("Consolas", 10), bd=0,
            highlightthickness=0, wrap="word",
            selectbackground="#1e3a5f")
        self.canvas.create_window(92, 162, window=self.memo,
                                  anchor="nw", width=816, height=436)

    def _draw_button(self):
        btn = NeonButton(self.root,
                         "СГЕНЕРИРОВАТЬ 1000 ЧИСЕЛ",
                         command=self.generate,
                         width=300, height=54)
        self.canvas.create_window(500, 640, window=btn)

    def _draw_footer(self):
        self.canvas.create_text(
            500, 700,
            text="© ОКФРС · Практическое занятие 2 · Программа 1",
            fill="#2f3a5a", font=("Segoe UI", 9))

    def generate(self):
        nums = [random.randint(0, 100) for _ in range(1000)]
        self.memo.delete(1.0, tk.END)
        self.memo.insert(tk.END, "   ".join(f"{n:3d}" for n in nums))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()