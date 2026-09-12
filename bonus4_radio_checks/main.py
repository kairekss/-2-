"""
ОКФРС. ПЗ №2. Бонус 4.
Кастомные радиокнопки и чекбоксы.
"""
import tkinter as tk


BG_TOP     = "#0a0e1c"
BG_BOTTOM  = "#141a30"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
NEON       = "#22d3ee"
GREEN      = "#22c55e"
ACCENT     = "#ff4d8d"
TEXT_MAIN  = "#eef2ff"
TEXT_DIM   = "#5c6a90"


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


class RadioButton(tk.Canvas):
    def __init__(self, parent, text, value, group_var,
                 width=280, height=46):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0)
        self.text = text
        self.value = value
        self.var = group_var
        self.w, self.h = width, height
        self.hovered = False
        self.var.trace_add("write", lambda *a: self._draw())
        self._draw()
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)

    def _draw(self):
        self.delete("all")
        sel = (self.var.get() == self.value)

        cx, cy, r = 20, self.h//2, 11

        # внешнее кольцо
        ring = NEON if sel else ("#4a5070" if self.hovered else PANEL_BRD)
        self.create_oval(cx-r, cy-r, cx+r, cy+r,
                         outline=ring, width=2, fill="#05070f")

        # точка внутри
        if sel:
            self.create_oval(cx-5, cy-5, cx+5, cy+5,
                             fill=NEON, outline="")

        # текст
        color = TEXT_MAIN if sel else (TEXT_MAIN if self.hovered else TEXT_DIM)
        self.create_text(cx + r + 18, cy, text=self.text,
                         fill=color, anchor="w",
                         font=("Segoe UI", 11, "bold" if sel else "normal"))

        # неоновая линия под выбранным
        if sel:
            self.create_line(cx+r+18, cy+11, self.w-8, cy+11,
                             fill=lerp(NEON, PANEL_BG, 0.5))

    def _enter(self, e):
        self.hovered = True
        self.configure(cursor="hand2")
        self._draw()

    def _leave(self, e):
        self.hovered = False
        self.configure(cursor="")
        self._draw()

    def _click(self, e):
        self.var.set(self.value)


class CheckBox(tk.Canvas):
    def __init__(self, parent, text, var,
                 width=280, height=46, color=GREEN):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0)
        self.text = text
        self.var = var
        self.color = color
        self.w, self.h = width, height
        self.hovered = False
        self.var.trace_add("write", lambda *a: self._draw())
        self._draw()
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)

    def _draw(self):
        self.delete("all")
        chk = self.var.get()

        x0, y0 = 10, self.h//2 - 11
        x1, y1 = x0 + 22, self.h//2 + 11

        border = self.color if chk else ("#4a5070" if self.hovered else PANEL_BRD)
        self.create_rectangle(x0, y0, x1, y1,
                              outline=border, width=2, fill="#05070f")

        # галочка
        if chk:
            self.create_line(x0+5, (y0+y1)//2,
                             x0+9, y1-5,
                             x1-5, y0+5,
                             fill=self.color, width=3,
                             capstyle="round", joinstyle="round")

        # текст
        color = TEXT_MAIN if chk else (TEXT_MAIN if self.hovered else TEXT_DIM)
        self.create_text(x1 + 14, self.h//2, text=self.text,
                         fill=color, anchor="w",
                         font=("Segoe UI", 11, "bold" if chk else "normal"))

    def _enter(self, e):
        self.hovered = True
        self.configure(cursor="hand2")
        self._draw()

    def _leave(self, e):
        self.hovered = False
        self.configure(cursor="")
        self._draw()

    def _click(self, e):
        self.var.set(not self.var.get())


class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Бонус 4 · Радиокнопки и чекбоксы")
        root.geometry("1000x640")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1000, height=640,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        for i in range(640):
            self.canvas.create_line(0, i, 1000, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/640))

        # заголовок
        self.canvas.create_text(500, 45,
                                text="РАДИОКНОПКИ И ЧЕКБОКСЫ",
                                fill=TEXT_MAIN,
                                font=("Segoe UI", 24, "bold"))
        self.canvas.create_text(500, 78,
                                text="ОКФРС · ПЗ №2 · Бонус 4 · элементы выбора",
                                fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(260, 102, 740, 102, fill=NEON, width=2)
        self.canvas.create_line(260, 104, 740, 104,
                                fill=lerp(NEON, BG_TOP, 0.7))

        # ЛЕВАЯ ПАНЕЛЬ — радиокнопки
        self.canvas.create_text(90, 140,
                                text="▸ ВЫБОР ОДНОГО",
                                fill=NEON, font=("Segoe UI", 11, "bold"),
                                anchor="w")
        self.canvas.create_rectangle(80, 165, 470, 420,
                                     fill=PANEL_BG, outline=PANEL_BRD)
        self.canvas.create_text(275, 185,
                                text="Что больше понравилось?",
                                fill=TEXT_DIM, font=("Segoe UI", 10))

        self.radio_var = tk.StringVar(value="opt1")
        opts = [
            ("Кнопки сложной формы",   "opt1", 210),
            ("Анимированный тумблер",  "opt2", 260),
            ("Шкала радиосвязи",       "opt3", 310),
            ("Радиокнопки и чекбоксы", "opt4", 360),
            ("Шахматная доска",        "opt5", 400),
        ]
        for text, val, y in opts:
            RadioButton(self.root, text, val,
                        self.radio_var).place(x=100, y=y)

        # ПРАВАЯ ПАНЕЛЬ — чекбоксы
        self.canvas.create_text(560, 140,
                                text="▸ МНОЖЕСТВЕННЫЙ ВЫБОР",
                                fill=GREEN, font=("Segoe UI", 11, "bold"),
                                anchor="w")
        self.canvas.create_rectangle(550, 165, 920, 420,
                                     fill=PANEL_BG, outline=PANEL_BRD)
        self.canvas.create_text(735, 185,
                                text="Что использовалось в проекте?",
                                fill=TEXT_DIM, font=("Segoe UI", 10))

        self.cb = {
            "Python":       tk.BooleanVar(value=True),
            "Tkinter":      tk.BooleanVar(value=True),
            "PyInstaller":  tk.BooleanVar(value=True),
            "GitHub":       tk.BooleanVar(),
            "Git LFS":      tk.BooleanVar(),
        }
        y = 210
        for name, v in self.cb.items():
            CheckBox(self.root, name, v).place(x=570, y=y)
            y += 42

        # ПАНЕЛЬ СТАТУСА снизу
        self.canvas.create_text(80, 460,
                                text="▸ СТАТУС ВЫБОРА",
                                fill=ACCENT, font=("Segoe UI", 11, "bold"),
                                anchor="w")
        self.canvas.create_rectangle(78, 485, 922, 610,
                                     fill=PANEL_BG, outline=PANEL_BRD)

        self.status = tk.Text(self.root, bg=PANEL_BG, fg=NEON,
                              insertbackground=TEXT_MAIN,
                              font=("Consolas", 11), bd=0,
                              highlightthickness=0, wrap="word")
        self.status.place(x=92, y=498, width=816, height=100)

        # подписка на изменения
        self.radio_var.trace_add("write", lambda *a: self.update_status())
        for v in self.cb.values():
            v.trace_add("write", lambda *a: self.update_status())

        self.update_status()

        self.canvas.create_text(500, 628,
                                text="© ОКФРС · ПЗ №2 · Бонус 4",
                                fill="#2a3350", font=("Segoe UI", 9))

    def update_status(self):
        radio = self.radio_var.get()
        radio_names = {"opt1": "Кнопки сложной формы",
                       "opt2": "Анимированный тумблер",
                       "opt3": "Шкала радиосвязи",
                       "opt4": "Радиокнопки и чекбоксы",
                       "opt5": "Шахматная доска"}
        checked = [k for k, v in self.cb.items() if v.get()]

        text = f"Выбранное:   {radio_names.get(radio, '—')}\n"
        text += f"Отмечено:    {', '.join(checked) if checked else '—'}\n"
        text += f"Итого чекбоксов: {len(checked)} / {len(self.cb)}"

        self.status.delete(1.0, tk.END)
        self.status.insert(tk.END, text)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()