#!/usr/bin/env python3
"""
定时关机程序 - Scheduled Shutdown Timer
支持 Windows / Linux / macOS
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform
import threading
import time
from datetime import datetime, timedelta


class ShutdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("⏰ 定时关机程序")
        self.root.geometry("420x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.remaining = 0
        self.timer_thread = None
        self.running = False
        self.cancelled = False

        self.build_ui()

    def build_ui(self):
        # 标题
        title = tk.Label(
            self.root, text="⏰ 定时关机",
            font=("Microsoft YaHei", 20, "bold"),
            bg="#1a1a2e", fg="#e94560"
        )
        title.pack(pady=15)

        # === 快速设置 ===
        quick_frame = tk.LabelFrame(
            self.root, text="快速设置", bg="#16213e",
            fg="#a0a0a0", font=("Microsoft YaHei", 10),
            padx=10, pady=5
        )
        quick_frame.pack(fill="x", padx=20, pady=5)

        presets = [
            ("30 分钟后", 30),
            ("1 小时后", 60),
            ("2 小时后", 120),
            ("4 小时后", 240),
            ("今晚 23:00", None),
            ("今晚 23:30", None),
        ]
        for i, (text, mins) in enumerate(presets):
            btn = tk.Button(
                quick_frame, text=text,
                font=("Microsoft YaHei", 9),
                bg="#0f3460", fg="white",
                activebackground="#533483", activeforeground="white",
                relief="flat", cursor="hand2",
                command=lambda m=mins, t=text: self.set_preset(m, t)
            )
            btn.grid(row=i // 3, column=i % 3, padx=4, pady=3, sticky="ew")

        for i in range(3):
            quick_frame.columnconfigure(i, weight=1)

        # === 自定义时间 ===
        custom_frame = tk.LabelFrame(
            self.root, text="自定义时间", bg="#16213e",
            fg="#a0a0a0", font=("Microsoft YaHei", 10),
            padx=10, pady=5
        )
        custom_frame.pack(fill="x", padx=20, pady=5)

        # 小时分钟选择
        time_row = tk.Frame(custom_frame, bg="#16213e")
        time_row.pack(pady=5)

        tk.Label(time_row, text="时:", bg="#16213e", fg="white",
                 font=("Microsoft YaHei", 11)).pack(side="left")
        self.hour_var = tk.StringVar(value="23")
        hour_spin = ttk.Spinbox(
            time_row, from_=0, to=23, width=4,
            textvariable=self.hour_var, font=("Microsoft YaHei", 12),
            format="%02.0f"
        )
        hour_spin.pack(side="left", padx=2)

        tk.Label(time_row, text="分:", bg="#16213e", fg="white",
                 font=("Microsoft YaHei", 11)).pack(side="left", padx=(10, 0))
        self.min_var = tk.StringVar(value="00")
        min_spin = ttk.Spinbox(
            time_row, from_=0, to=59, width=4,
            textvariable=self.min_var, font=("Microsoft YaHei", 12),
            format="%02.0f"
        )
        min_spin.pack(side="left", padx=2)

        # 倒计时显示
        self.countdown_label = tk.Label(
            custom_frame, text="等待设置...",
            font=("Microsoft YaHei", 16, "bold"),
            bg="#16213e", fg="#4ecca3"
        )
        self.countdown_label.pack(pady=8)

        # === 操作按钮 ===
        btn_row = tk.Frame(self.root, bg="#1a1a2e")
        btn_row.pack(pady=15)

        self.start_btn = tk.Button(
            btn_row, text="▶ 开始定时",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#4ecca3", fg="#1a1a2e",
            activebackground="#38b08f", activeforeground="white",
            relief="flat", cursor="hand2", width=12,
            command=self.start_timer
        )
        self.start_btn.pack(side="left", padx=10)

        self.cancel_btn = tk.Button(
            btn_row, text="⏹ 取消关机",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#e94560", fg="white",
            activebackground="#c73650", activeforeground="white",
            relief="flat", cursor="hand2", width=12,
            command=self.cancel_timer, state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=10)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪 | 系统: " + platform.system())
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            bg="#0f3460", fg="#a0a0a0",
            font=("Microsoft YaHei", 9), anchor="w"
        )
        status_bar.pack(fill="x", side="bottom")

    def set_preset(self, mins, text):
        if mins is not None:
            self.target_time = datetime.now() + timedelta(minutes=mins)
        else:
            # 处理 "今晚 XX:XX"
            now = datetime.now()
            hour, minute = 23, 0 if "23:00" in text else 30
            self.target_time = now.replace(hour=hour, minute=minute, second=0)
            if self.target_time < now:
                self.target_time += timedelta(days=1)

        self.hour_var.set(f"{self.target_time.hour:02d}")
        self.min_var.set(f"{self.target_time.minute:02d}")
        self.status_var.set(f"已设置: {text} → {self.target_time.strftime('%H:%M')}")

    def start_timer(self):
        if self.running:
            return

        try:
            target_hour = int(self.hour_var.get())
            target_min = int(self.min_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的时间")
            return

        now = datetime.now()
        self.target_time = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)

        if self.target_time <= now:
            self.target_time += timedelta(days=1)

        self.remaining = int((self.target_time - now).total_seconds())

        if self.remaining <= 0:
            messagebox.showerror("错误", "目标时间已过")
            return

        self.running = True
        self.cancelled = False
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.status_var.set(f"已定时: {self.target_time.strftime('%H:%M')} 关机")

        self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
        self.timer_thread.start()

    def countdown(self):
        while self.remaining > 0 and not self.cancelled:
            h, rem = divmod(self.remaining, 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h:02d}:{m:02d}:{s:02d}"

            # 更新 UI
            self.root.after(0, lambda t=time_str: self.countdown_label.config(text=t))

            # 最后 60 秒变红
            if self.remaining <= 60:
                self.root.after(0, lambda: self.countdown_label.config(fg="#e94560"))
            elif self.remaining <= 300:
                self.root.after(0, lambda: self.countdown_label.config(fg="#f0a500"))

            time.sleep(1)
            self.remaining -= 1

        if not self.cancelled and self.remaining <= 0:
            self.root.after(0, self.execute_shutdown)
        elif self.cancelled:
            self.root.after(0, self.reset_ui)

    def execute_shutdown(self):
        self.running = False
        system = platform.system()

        try:
            if system == "Windows":
                subprocess.run(["shutdown", "/s", "/t", "10", "/c", "定时关机程序: 10秒后关机"], check=True)
            elif system == "Linux":
                subprocess.run(["shutdown", "-h", "+0"], check=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            else:
                messagebox.showerror("错误", f"不支持的系统: {system}")
        except Exception as e:
            messagebox.showerror("关机失败", f"执行关机命令失败:\n{e}\n\n请尝试以管理员权限运行")

        self.reset_ui()

    def cancel_timer(self):
        if not self.running:
            return

        self.cancelled = True
        self.running = False

        # 取消系统关机命令
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["shutdown", "/a"], check=False)
            elif system == "Linux":
                subprocess.run(["shutdown", "-c"], check=False)
            elif system == "Darwin":
                subprocess.run(["sudo", "killall", "shutdown"], check=False)
        except Exception:
            pass

        self.status_var.set("已取消关机")
        self.reset_ui()

    def reset_ui(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.countdown_label.config(text="等待设置...", fg="#4ecca3")


def main():
    root = tk.Tk()

    # 设置主题样式
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TSpinbox", fieldbackground="#16213e", foreground="white")

    app = ShutdownTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
