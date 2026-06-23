import tkinter as tk
import math
import time
import ctypes


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
        self._aiin = False
        self._aiin_job = None
        self._click_job = None
        self._skip_release = False
        self._dclick_ms = ctypes.windll.user32.GetDoubleClickTime()
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
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
        if self._skip_release:
            self._skip_release = False
            return
        if not self._moved:
            if self._click_job:
                self.root.after_cancel(self._click_job)
            self._click_job = self.root.after(self._dclick_ms, self._on_single_click)

    def _on_single_click(self):
        self._click_job = None
        if self._aiin_job:
            self.root.after_cancel(self._aiin_job)
        self._aiin = True
        self._aiin_job = self.root.after(2000, self._hide_aiin)

    def _hide_aiin(self):
        self._aiin = False
        self._aiin_job = None

    def _on_double_click(self, event):
        if self._click_job:
            self.root.after_cancel(self._click_job)
            self._click_job = None
        self._skip_release = True
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
            fill="#000000", outline="#333333", width=1,
        )

        # 時間マーカー（12時位置のみドット、他は小ドット）
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            r = self.radius - 6
            x = self.cx + r * math.cos(angle)
            y = self.cy + r * math.sin(angle)
            size = 3 if i % 3 == 0 else 1.5
            c.create_oval(x - size, y - size, x + size, y + size, fill="#555555", outline="")

        now = time.localtime()
        h = now.tm_hour % 12
        m = now.tm_min
        s = now.tm_sec

        # 時針
        hour_angle = (h + m / 60) * 30
        self._hand(hour_angle, self.radius * 0.5, 4, "#ffffff")

        # 分針
        min_angle = (m + s / 60) * 6
        self._hand(min_angle, self.radius * 0.72, 2, "#ffffff")

        # 秒針
        sec_angle = s * 6
        self._hand(sec_angle, self.radius * 0.82, 1, "#ff4444")

        # 中心ドット
        r = 3
        c.create_oval(self.cx - r, self.cy - r, self.cx + r, self.cy + r, fill="#ffffff", outline="")

        # アイーン表示
        if self._aiin:
            c.create_text(self.cx, self.cy - self.radius * 0.6, text="アイーン♡",
                          fill="#ff69b4", font=("Helvetica", 9, "bold"))

        # 日付表示（文字盤の下）
        date_str = time.strftime("%Y-%m-%d")
        c.create_text(self.cx, self.size + self.date_area // 2, text=date_str, fill="#444444", font=("Helvetica", 10))

    def tick(self):
        self.draw()
        self.root.after(1000, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("+100+100")
    AnalogClock(root)
    root.mainloop()
