import tkinter as tk
from tkinter import ttk
import re
import threading
import pyperclip
import pystray
from PIL import Image, ImageDraw, ImageFont
import keyboard

# --- BẢNG MÀU CÁ NHÂN HÓA (DARK GOLD THEME CHO NULY) ---
BG_COLOR = "#121417"          # Nền chính xám đen
CONTAINER_COLOR = "#1B1E23"   # Nền khối nhập liệu
ACCENT_GOLD = "#F59E0B"       # Vàng Amber gold
ACCENT_HOVER = "#D97706"      # Vàng đậm khi hover
TEXT_COLOR = "#F3F4F6"        # Trắng sáng
TEXT_MUTED = "#9CA3AF"        # Xám ghi
BORDER_COLOR = "#2D3748"      # Viền

class NulyMDOptimizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nuly • Markdown Token Optimizer")
        self.root.geometry("480x560")
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-topmost", True)
        
        # Đặt góc dưới bên phải màn hình
        self.position_bottom_right()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.setup_ui()
        self.setup_system_tray()
        self.setup_global_hotkey()

    def position_bottom_right(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        w, h = 480, 560
        x = screen_w - w - 24
        y = screen_h - h - 64  # Tránh che thanh Taskbar
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def setup_ui(self):
        container = tk.Frame(self.root, bg=BG_COLOR, padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        # Header mang thương hiệu cá nhân
        header_frame = tk.Frame(container, bg=BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        lbl_badge = tk.Label(
            header_frame, text="NULY WORKSPACE", font=("Segoe UI", 8, "bold"),
            bg="#2A2415", fg=ACCENT_GOLD, padx=8, pady=2
        )
        lbl_badge.pack(side=tk.LEFT)

        lbl_shortcut = tk.Label(
            header_frame, text="Phím tắt: Ctrl + Alt + M", font=("Segoe UI", 8),
            bg=BG_COLOR, fg=TEXT_MUTED
        )
        lbl_shortcut.pack(side=tk.RIGHT)

        # Khung Text Input
        self.txt_input = tk.Text(
            container, wrap=tk.WORD, height=12,
            font=("Consolas", 10), bg=CONTAINER_COLOR, fg=TEXT_COLOR,
            insertbackground=ACCENT_GOLD, bd=0, highlightthickness=1,
            highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_GOLD,
            padx=10, pady=10
        )
        self.txt_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tùy chọn nén
        opts_frame = tk.Frame(container, bg=BG_COLOR)
        opts_frame.pack(fill=tk.X, pady=(0, 10))

        self.opt_condense_spaces = tk.BooleanVar(value=True)
        self.opt_normalize_lists = tk.BooleanVar(value=True)

        chk_space = tk.Checkbutton(
            opts_frame, text="Cắt khoảng trắng & dòng trống kép",
            variable=self.opt_condense_spaces, bg=BG_COLOR, fg=TEXT_COLOR,
            selectcolor=CONTAINER_COLOR, activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
            font=("Segoe UI", 9)
        )
        chk_space.pack(side=tk.LEFT)

        chk_list = tk.Checkbutton(
            opts_frame, text="Tối ưu Markdown Bullets",
            variable=self.opt_normalize_lists, bg=BG_COLOR, fg=TEXT_COLOR,
            selectcolor=CONTAINER_COLOR, activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
            font=("Segoe UI", 9)
        )
        chk_list.pack(side=tk.LEFT, padx=(12, 0))

        # Các nút bấm hành động
        btn_frame = tk.Frame(container, bg=BG_COLOR)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        btn_paste = tk.Button(
            btn_frame, text="⚡ Dán & Nén Ngay", command=self.paste_and_convert,
            bg=ACCENT_GOLD, fg="#000000", activebackground=ACCENT_HOVER, activeforeground="#000000",
            font=("Segoe UI", 9, "bold"), bd=0, pady=8, cursor="hand2"
        )
        btn_paste.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_copy = tk.Button(
            btn_frame, text="Copy Kết Quả", command=self.convert_and_copy,
            bg=CONTAINER_COLOR, fg=TEXT_COLOR, activebackground="#2A303C", activeforeground=TEXT_COLOR,
            font=("Segoe UI", 9, "bold"), bd=0, pady=8, cursor="hand2"
        )
        btn_copy.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        # Thanh trạng thái / Bộ đếm token tiết kiệm
        self.status_bar = tk.Label(
            container, text="Sẵn sàng nén văn bản gửi AI...", font=("Segoe UI", 8),
            bg=BG_COLOR, fg=TEXT_MUTED, anchor="w"
        )
        self.status_bar.pack(fill=tk.X)

    def clean_markdown(self, text: str) -> str:
        """Thu gọn dữ liệu triệt để nhằm tiết kiệm token tối đa."""
        if not text:
            return ""

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in text.split("\n")]

        if self.opt_normalize_lists.get():
            normalized = []
            for line in lines:
                # Gộp các ký tự list dài dòng về dấu gạch ngang '-' chuẩn token Markdown
                line = re.sub(r"^[\*•\+]\s+", "- ", line)
                line = re.sub(r"^\d+[\.\)]\s+", "- ", line)
                normalized.append(line)
            lines = normalized

        if self.opt_condense_spaces.get():
            condensed = []
            prev_blank = False
            for line in lines:
                if not line:
                    if not prev_blank:
                        condensed.append("")
                        prev_blank = True
                else:
                    condensed.append(line)
                    prev_blank = False
            lines = condensed

        return "\n".join(lines).strip()

    def convert_and_copy(self):
        raw = self.txt_input.get("1.0", tk.END).strip()
        if not raw:
            return
        
        compressed = self.clean_markdown(raw)
        pyperclip.copy(compressed)

        raw_chars = len(raw)
        comp_chars = len(compressed)
        saved = max(0, raw_chars - comp_chars)
        est_tokens = saved // 4

        self.status_bar.config(
            text=f"✓ Đã copy! Tiết kiệm: {saved} ký tự (~{est_tokens} tokens cho AI)",
            fg=ACCENT_GOLD
        )

    def paste_and_convert(self):
        content = pyperclip.paste()
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert(tk.END, content)
        self.convert_and_copy()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def setup_global_hotkey(self):
        def on_hotkey():
            if self.root.state() == "withdrawn":
                self.root.after(0, self.show_window)
            else:
                self.root.after(0, self.hide_window)

        threading.Thread(target=lambda: keyboard.add_hotkey("ctrl+alt+m", on_hotkey), daemon=True).start()

    def create_nuly_icon(self):
        """Vẽ Icon cá nhân hóa chữ N màu Gold nền tròn đen."""
        img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # Nền tròn đen tuyền viền vàng
        d.ellipse([2, 2, 62, 62], fill="#121417", outline=ACCENT_GOLD, width=3)
        # Vẽ biểu tượng chữ N sắc nét
        d.polygon([(20, 46), (20, 18), (27, 18), (38, 36), (38, 18), (44, 18), (44, 46), (37, 46), (26, 28), (26, 46)], fill=ACCENT_GOLD)
        return img

    def setup_system_tray(self):
        icon_img = self.create_nuly_icon()
        menu = pystray.Menu(
            pystray.MenuItem("Mở Nuly MD Optimizer", lambda: self.root.after(0, self.show_window), default=True),
            pystray.MenuItem("Thoát", self.quit_app)
        )
        self.tray_icon = pystray.Icon("Nuly_MD_Optimizer", icon_img, "Nuly • MD Token Saver", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def quit_app(self):
        self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NulyMDOptimizer()
    app.run()