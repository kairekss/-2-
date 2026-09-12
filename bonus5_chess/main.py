"""
ОКФРС. ПЗ №2. Бонус 5.
Играбельная шахматная доска 8x8.

Как играть:
  1. Клик по СВОЕЙ фигуре -> клетка зелёная, возможные ходы голубые/розовые.
  2. Клик по подсвеченной клетке -> фигура идёт туда.
  3. Первыми ходят БЕЛЫЕ (внизу).
"""
import tkinter as tk
from tkinter import messagebox


# ------------------------- ПАЛИТРА -------------------------
BG_TOP     = "#0a0e1c"
BG_BOTTOM  = "#141a30"
PANEL_BG   = "#0f1425"
PANEL_BRD  = "#2a3150"
NEON       = "#22d3ee"
GREEN      = "#22c55e"
ACCENT     = "#ff4d8d"
AMBER      = "#f4b942"
TEXT_MAIN  = "#eef2ff"
TEXT_DIM   = "#5c6a90"

CELL_LIGHT = "#e8d8a8"
CELL_DARK  = "#a07850"
CELL_SEL   = "#22c55e"
CELL_MOVE  = "#22d3ee"
CELL_CAP   = "#ff4d8d"
CELL_CHECK = "#e11d48"

PIECES = {
    "wk": "♔", "wq": "♕", "wr": "♖", "wb": "♗", "wn": "♘", "wp": "♙",
    "bk": "♚", "bq": "♛", "br": "♜", "bb": "♝", "bn": "♞", "bp": "♟",
}


def lerp(c1, c2, t):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))


# ============================================================
#  ЛОГИКА ШАХМАТ
# ============================================================
class ChessGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None]*8 for _ in range(8)]
        self.turn = "w"
        self.history = []
        self.en_passant = None
        self.castling = {"wK": True, "wQ": True, "bK": True, "bQ": True}
        self._setup_start()

    def _setup_start(self):
        order = ["r", "n", "b", "q", "k", "b", "n", "r"]
        for i, p in enumerate(order):
            self.board[0][i] = "b" + p
            self.board[7][i] = "w" + p
        for i in range(8):
            self.board[1][i] = "bp"
            self.board[6][i] = "wp"

    def at(self, r, c):
        if 0 <= r < 8 and 0 <= c < 8:
            return self.board[r][c]
        return None

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == color + "k":
                    return (r, c)
        return None

    def pseudo_moves(self, r, c):
        p = self.at(r, c)
        if not p:
            return []
        color = p[0]
        kind = p[1]
        moves = []

        def add(rr, cc):
            if 0 <= rr < 8 and 0 <= cc < 8:
                tgt = self.board[rr][cc]
                if tgt is None or tgt[0] != color:
                    moves.append((rr, cc))

        def slide(dirs):
            for dr, dc in dirs:
                rr, cc = r + dr, c + dc
                while 0 <= rr < 8 and 0 <= cc < 8:
                    tgt = self.board[rr][cc]
                    if tgt is None:
                        moves.append((rr, cc))
                    else:
                        if tgt[0] != color:
                            moves.append((rr, cc))
                        break
                    rr += dr
                    cc += dc

        if kind == "p":
            dir_ = -1 if color == "w" else 1
            start_row = 6 if color == "w" else 1
            if self.at(r + dir_, c) is None:
                moves.append((r + dir_, c))
                if r == start_row and self.at(r + 2*dir_, c) is None:
                    moves.append((r + 2*dir_, c))
            for dc in (-1, 1):
                rr, cc = r + dir_, c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    tgt = self.board[rr][cc]
                    if tgt and tgt[0] != color:
                        moves.append((rr, cc))
                    elif self.en_passant == (rr, cc):
                        moves.append((rr, cc))
        elif kind == "n":
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),
                           (1,-2),(1,2),(2,-1),(2,1)]:
                add(r + dr, c + dc)
        elif kind == "b":
            slide([(-1,-1),(-1,1),(1,-1),(1,1)])
        elif kind == "r":
            slide([(-1,0),(1,0),(0,-1),(0,1)])
        elif kind == "q":
            slide([(-1,-1),(-1,1),(1,-1),(1,1),
                   (-1,0),(1,0),(0,-1),(0,1)])
        elif kind == "k":
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == 0 and dc == 0:
                        continue
                    add(r + dr, c + dc)
            row = 7 if color == "w" else 0
            if r == row and c == 4:
                if self.castling[color + "K"]:
                    if (self.at(row, 5) is None and
                        self.at(row, 6) is None and
                        self.at(row, 7) == color + "r"):
                        moves.append((row, 6))
                if self.castling[color + "Q"]:
                    if (self.at(row, 3) is None and
                        self.at(row, 2) is None and
                        self.at(row, 1) is None and
                        self.at(row, 0) == color + "r"):
                        moves.append((row, 2))
        return moves

    def is_attacked(self, r, c, by_color):
        for rr in range(8):
            for cc in range(8):
                p = self.board[rr][cc]
                if p and p[0] == by_color:
                    if (r, c) in self.pseudo_moves(rr, cc):
                        return True
        return False

    def in_check(self, color):
        pos = self.find_king(color)
        if not pos:
            return False
        return self.is_attacked(pos[0], pos[1],
                                "b" if color == "w" else "w")

    def legal_moves(self, r, c):
        p = self.at(r, c)
        if not p:
            return []
        color = p[0]
        legal = []
        for (rr, cc) in self.pseudo_moves(r, c):
            snap = self._snapshot()
            self._apply_move((r, c), (rr, cc), commit=False)
            if not self.in_check(color):
                legal.append((rr, cc))
            self._restore(snap)
        return legal

    def _snapshot(self):
        return ([row[:] for row in self.board],
                self.turn, dict(self.castling), self.en_passant)

    def _restore(self, snap):
        board, turn, cast, ep = snap
        self.board = [row[:] for row in board]
        self.turn = turn
        self.castling = dict(cast)
        self.en_passant = ep

    def _apply_move(self, src, dst, commit=True):
        r1, c1 = src
        r2, c2 = dst
        p = self.board[r1][c1]
        color = p[0]
        kind = p[1]

        if kind == "p" and self.en_passant == (r2, c2):
            self.board[r1][c2] = None

        if kind == "k" and abs(c2 - c1) == 2:
            row = r1
            if c2 > c1:
                self.board[row][5] = self.board[row][7]
                self.board[row][7] = None
            else:
                self.board[row][3] = self.board[row][0]
                self.board[row][0] = None

        self.board[r2][c2] = p
        self.board[r1][c1] = None

        if kind == "p" and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = color + "q"

        if kind == "k":
            self.castling[color + "K"] = False
            self.castling[color + "Q"] = False
        if kind == "r":
            row = 7 if color == "w" else 0
            if c1 == 7 and r1 == row:
                self.castling[color + "K"] = False
            if c1 == 0 and r1 == row:
                self.castling[color + "Q"] = False

        self.en_passant = None
        if kind == "p" and abs(r2 - r1) == 2:
            self.en_passant = ((r1 + r2)//2, c1)

        if commit:
            self.turn = "b" if self.turn == "w" else "w"

    def try_move(self, src, dst):
        if dst not in self.legal_moves(*src):
            return False
        piece = self.board[src[0]][src[1]]
        captured = self.board[dst[0]][dst[1]]
        self._apply_move(src, dst, commit=True)
        self.history.append(self._to_san(src, dst, piece, captured))
        return True

    def _to_san(self, src, dst, piece, captured):
        files = "abcdefgh"
        f1, r1 = files[src[1]], 8 - src[0]
        f2, r2 = files[dst[1]], 8 - dst[0]
        sep = "x" if captured else "-"
        pre = piece[1].upper() if piece[1] != "p" else ""
        return f"{pre}{f1}{r1}{sep}{f2}{r2}"

    def has_any_legal(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p[0] == color and self.legal_moves(r, c):
                    return True
        return False

    def status(self):
        color = self.turn
        chk = self.in_check(color)
        has = self.has_any_legal(color)
        if chk and not has:
            return "mat"
        if not chk and not has:
            return "pat"
        if chk:
            return "check"
        return "ok"


# ============================================================
#  ВИЗУАЛЬНАЯ ДОСКА
# ============================================================
class ChessBoardUI:
    def __init__(self, canvas, x0, y0, cell=68, on_change=None):
        self.canvas = canvas
        self.x0, self.y0 = x0, y0
        self.cs = cell
        self.on_change = on_change
        self.game = ChessGame()
        self.selected = None
        self.legal = []
        self.cell_ids = {}
        self.piece_ids = {}
        self.outline_ids = []

        self._draw_frame()
        self._draw_cells()
        self._draw_labels()
        self._render_pieces()

    def _draw_frame(self):
        c = self.canvas
        S = self.cs * 8
        for i in range(5, 0, -1):
            c.create_rectangle(
                self.x0 - i - 14, self.y0 - i - 14,
                self.x0 + S + i + 14, self.y0 + S + i + 14,
                outline=lerp(NEON, BG_TOP, i*0.18), width=1)
        c.create_rectangle(self.x0+10, self.y0+10,
                           self.x0+S+10, self.y0+S+10,
                           fill="#02040a", outline="")
        c.create_rectangle(self.x0 - 8, self.y0 - 8,
                           self.x0 + S + 8, self.y0 + S + 8,
                           fill="#1a2035", outline=PANEL_BRD, width=2)

    def _draw_cells(self):
        c = self.canvas
        for r in range(8):
            for col in range(8):
                x1 = self.x0 + col * self.cs
                y1 = self.y0 + r * self.cs
                x2 = x1 + self.cs
                y2 = y1 + self.cs
                base = CELL_LIGHT if (r + col) % 2 == 0 else CELL_DARK
                item = c.create_rectangle(x1, y1, x2, y2,
                                          fill=base, outline="")
                self.cell_ids[(r, col)] = item

    def _draw_labels(self):
        c = self.canvas
        S = self.cs * 8
        for i, ch in enumerate("abcdefgh"):
            x = self.x0 + i * self.cs + self.cs//2
            c.create_text(x, self.y0 - 22, text=ch.upper(),
                          fill=NEON, font=("Consolas", 12, "bold"))
            c.create_text(x, self.y0 + S + 22, text=ch.upper(),
                          fill=NEON, font=("Consolas", 12, "bold"))
        for i in range(8):
            y = self.y0 + i * self.cs + self.cs//2
            num = 8 - i
            c.create_text(self.x0 - 22, y, text=str(num),
                          fill=NEON, font=("Consolas", 12, "bold"))
            c.create_text(self.x0 + S + 22, y, text=str(num),
                          fill=NEON, font=("Consolas", 12, "bold"))

    def _render_pieces(self):
        for pid in self.piece_ids.values():
            self.canvas.delete(pid)
        for oid in self.outline_ids:
            self.canvas.delete(oid)
        self.piece_ids.clear()
        self.outline_ids.clear()

        for r in range(8):
            for col in range(8):
                p = self.game.board[r][col]
                if not p:
                    continue
                cx = self.x0 + col * self.cs + self.cs//2
                cy = self.y0 + r * self.cs + self.cs//2
                fg = "#ffffff" if p[0] == "w" else "#111111"
                outline = "#000000" if p[0] == "w" else "#ffffff"

                oid = self.canvas.create_oval(
                    cx - self.cs*0.32, cy - self.cs*0.32,
                    cx + self.cs*0.32, cy + self.cs*0.32,
                    outline=outline, width=1, fill="")
                self.outline_ids.append(oid)

                text_id = self.canvas.create_text(
                    cx, cy, text=PIECES[p],
                    fill=fg,
                    font=("Segoe UI Symbol", int(self.cs*0.78), "bold"))
                self.piece_ids[(r, col)] = text_id

    def _refresh_cell_colors(self):
        g = self.game
        check_pos = None
        if g.status() in ("check", "mat"):
            check_pos = g.find_king(g.turn)

        for (r, col), item in self.cell_ids.items():
            base = CELL_LIGHT if (r + col) % 2 == 0 else CELL_DARK
            if self.selected == (r, col):
                color = lerp(base, CELL_SEL, 0.55)
            elif (r, col) in self.legal:
                is_cap = (g.board[r][col] is not None)
                color = lerp(base, CELL_CAP if is_cap else CELL_MOVE, 0.5)
            elif check_pos == (r, col):
                color = lerp(base, CELL_CHECK, 0.6)
            else:
                color = base
            self.canvas.itemconfig(item, fill=color)

    def _notify(self):
        if callable(self.on_change):
            self.on_change(self.game)

    def refresh(self):
        self._notify()

    # ---------- ГЛАВНЫЙ ОБРАБОТЧИК КЛИКА ----------
    def handle_click(self, r, col):
        piece = self.game.board[r][col]

        # 1) если есть выбранная фигура и клик по допустимой клетке — ходим
        if self.selected is not None and (r, col) in self.legal:
            src = self.selected
            ok = self.game.try_move(src, (r, col))
            self.selected = None
            self.legal = []
            if ok:
                self._render_pieces()
                self._refresh_cell_colors()
                self._notify()
            return

        # 2) если клик по своей фигуре — выбираем
        if piece and piece[0] == self.game.turn:
            self.selected = (r, col)
            self.legal = self.game.legal_moves(r, col)
            self._refresh_cell_colors()
            return

        # 3) иначе — снимаем выделение
        self.selected = None
        self.legal = []
        self._refresh_cell_colors()

    def reset(self):
        self.game.reset()
        self.selected = None
        self.legal = []
        self._render_pieces()
        self._refresh_cell_colors()
        self._notify()


# ============================================================
#  КНОПКА
# ============================================================
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


# ============================================================
#  ГЛАВНОЕ ОКНО
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("ОКФРС · Бонус 5 · Шахматная доска")
        root.geometry("1200x900")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=1200, height=900,
                                highlightthickness=0, bg=BG_TOP)
        self.canvas.pack(fill="both", expand=True)

        for i in range(900):
            self.canvas.create_line(0, i, 1200, i,
                                    fill=lerp(BG_TOP, BG_BOTTOM, i/900))

        self.canvas.create_text(600, 45,
                                text="ШАХМАТНАЯ ДОСКА",
                                fill=TEXT_MAIN,
                                font=("Segoe UI", 24, "bold"))
        self.canvas.create_text(600, 78,
                                text="ОКФРС · ПЗ №2 · Бонус 5 · играбельная 8×8",
                                fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_line(300, 102, 900, 102, fill=NEON, width=2)
        self.canvas.create_line(300, 104, 900, 104,
                                fill=lerp(NEON, BG_TOP, 0.7))

        self.canvas.create_rectangle(80, 160, 300, 500,
                                     fill=PANEL_BG, outline=PANEL_BRD)
        self.canvas.create_text(190, 180,
                                text="▸ СТАТУС",
                                fill=ACCENT,
                                font=("Segoe UI", 11, "bold"))
        self.info = tk.Text(self.root,
                            bg=PANEL_BG, fg=NEON,
                            insertbackground=TEXT_MAIN,
                            font=("Consolas", 10), bd=0,
                            highlightthickness=0, wrap="word",
                            state="disabled", cursor="arrow")
        self.info.place(x=92, y=200, width=196, height=290)

        self.board = ChessBoardUI(self.canvas, 340, 160, cell=68,
                                  on_change=self.on_change)
        self.board.refresh()

        # ГЛОБАЛЬНЫЙ обработчик клика по холсту
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        reset_btn = NeonButton(self.root, "↺  СБРОС",
                               command=self.reset,
                               width=200, height=48, color=ACCENT)
        self.canvas.create_window(400, 790, window=reset_btn)

        help_btn = NeonButton(self.root, "?  КАК ИГРАТЬ",
                              command=self.help,
                              width=200, height=48, color=NEON)
        self.canvas.create_window(620, 790, window=help_btn)

        self.canvas.create_text(
            600, 850,
            text="клик по СВОЕЙ фигуре → подсветка ходов → клик по клетке",
            fill=TEXT_DIM, font=("Segoe UI", 10))
        self.canvas.create_text(
            600, 878,
            text="© ОКФРС · ПЗ №2 · Бонус 5",
            fill="#2a3350", font=("Segoe UI", 9))

    def _on_canvas_click(self, event):
        bx = self.board.x0
        by = self.board.y0
        cs = self.board.cs
        col = (event.x - bx) // cs
        row = (event.y - by) // cs
        if 0 <= row < 8 and 0 <= col < 8:
            self.board.handle_click(int(row), int(col))

    def on_change(self, game):
        if self.info is None:
            return
        st = game.status()
        turn = "Белые" if game.turn == "w" else "Чёрные"
        status_map = {
            "ok":    "всё в порядке",
            "check": "⚠ ШАХ!",
            "mat":   "✕ МАТ. Игра окончена",
            "pat":   "◌ ПАТ. Ничья",
        }
        lines = [
            f"Ход:     {turn}",
            f"Статус:  {status_map.get(st, '')}",
            "",
            "▸ ИСТОРИЯ ХОДОВ:",
        ]
        for i, h in enumerate(game.history[-22:], 1):
            lines.append(f"  {i:>3}. {h}")
        self.info.config(state="normal")
        self.info.delete(1.0, tk.END)
        self.info.insert(tk.END, "\n".join(lines))
        self.info.config(state="disabled")

    def reset(self):
        self.board.reset()

    def help(self):
        messagebox.showinfo(
            "Как играть",
            "1. Клик по СВОЕЙ фигуре.\n"
            "   Клетка станет зелёной, возможные ходы —\n"
            "   голубыми (ход) или розовыми (взятие).\n"
            "2. Клик по подсвеченной клетке — фигура идёт.\n"
            "3. Ход переходит другой стороне.\n\n"
            "Первыми ходят БЕЛЫЕ (светлые, снизу).\n\n"
            "Поддерживается:\n"
            "  • все ходы фигур по правилам;\n"
            "  • рокировка;\n"
            "  • взятие на проходе;\n"
            "  • превращение пешки в ферзя;\n"
            "  • определение шаха, мата и пата."
        )


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()