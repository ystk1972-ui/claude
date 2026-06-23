import tkinter as tk
import math
import time


class AnalogClock:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.TRANSPARENT_KEY = "#020202"
        self.root.attributes("-transparentcolor", self.TRANSPARENT_KEY)

        self.size = 150
        self.date_area = 24
        self.cx = self.size // 2
        self.cy = self.size // 2
        self.radius = self.size // 2 - 10

        self.canvas = tk.Canvas(
            root,
            width=self.size,
            height=self.size + self.date_area,
            bg=self.TRANSPARENT_KEY,
            highlightthickness=0,
        )
        self.canvas.pack()

        self._make_draggable()
        self.tick()

    def _make_draggable(self):
        self._transparent = False
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<ButtonPress-3>", lambda e: self.root.destroy())

    def _on_press(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()
        self._moved = False

    def _on_drag_motion(self, event):
        self._moved = True
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _on_release(self, event):
        if not self._moved:
            self._transparent = not self._transparent
            alpha = 0.3 if self._transparent else 1.0
            self.root.attributes("-alpha", alpha)

    def _hand(self, angle_deg, length, width, color):
        angle = math.radians(angle_deg - 90)
        x = self.cx + length * math.cos(angle)
        y = self.cy + length * math.sin(angle)
        self.canvas.create_line(
            self.cx, self.cy, x, y,
            width=width, fill=color, capstyle=tk.ROUND,
        )

    def draw(self):
        c = self.canvas
        c.delete("all")

        # 文字盤背景
        c.create_oval(
            self.cx - self.radius, self.cy - self.radius,
            self.cx + self.radius, self.cy + self.radius,
            fill="#000000", outline="#e0e0e0", width=3,
        )

        # 時間マーカー
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                outer = self.radius - 2
                inner = self.radius - 14
                width = 2
                color = "#e0e0e0"
            else:
                outer = self.radius - 5
                inner = self.radius - 10
                width = 1
                color = "#555577"
            x1 = self.cx + inner * math.cos(angle)
            y1 = self.cy + inner * math.sin(angle)
            x2 = self.cx + outer * math.cos(angle)
            y2 = self.cy + outer * math.sin(angle)
            c.create_line(x1, y1, x2, y2, width=width, fill=color)

        # 数字
        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)
            r = self.radius - 28
            x = self.cx + r * math.cos(angle)
            y = self.cy + r * math.sin(angle)
            c.create_text(x, y, text=str(i), fill="#c0c0d0", font=("Helvetica", 8, "bold"))

        now = time.localtime()
        h = now.tm_hour % 12
        m = now.tm_min
        s = now.tm_sec

        # 時針
        hour_angle = (h + m / 60) * 30
        self._hand(hour_angle, self.radius * 0.5, 6, "#e0e0e0")

        # 分針
        min_angle = (m + s / 60) * 6
        self._hand(min_angle, self.radius * 0.72, 4, "#c0c8ff")

        # 秒針
        sec_angle = s * 6
        self._hand(sec_angle, self.radius * 0.82, 2, "#ff6b6b")

        # 中心ドット
        r = 6
        c.create_oval(self.cx - r, self.cy - r, self.cx + r, self.cy + r, fill="#ff6b6b", outline="")

        # 日付表示（文字盤の下）
        date_str = time.strftime("%Y-%m-%d")
        c.create_text(self.cx, self.size + self.date_area // 2, text=date_str, fill="#8888aa", font=("Helvetica", 10))

    def tick(self):
        self.draw()
        self.root.after(1000, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("+100+100")
    AnalogClock(root)
    root.mainloop()
