import tkinter as tk
import time
import threading
from pystray import MenuItem as item, Icon
from PIL import Image, ImageDraw, ImageGrab, ImageTk, ImageFont
import colorsys


class Stopwatch:
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.current_color = "#FFFFFF"
        self.target_color = "#FFFFFF"
        self.is_draggable = False
        self.is_moving = False
        self.last_update_time = 0

        self.create_tray_icon()
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

        self.create_window()

    def create_window(self):
        self.root = tk.Tk()
        self.root.geometry("300x150")
        self.root.overrideredirect(True)

        self.root.attributes("-topmost", True, "-alpha", 0.8)
        self.root.wm_attributes("-transparentcolor", "black")

        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_oval(0, 0, 300, 150, fill='black')

        self.font = ImageFont.truetype("arial.ttf", 48)
        self.time_image = Image.new('RGBA', (300, 150), (0, 0, 0, 0))
        self.time_draw = ImageDraw.Draw(self.time_image)

        self.time_text = self.canvas.create_image(150, 75, image=None)

        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<space>", self.toggle)
        self.root.bind("<Escape>", self.reset)
        self.root.bind("<Button-3>", self.show_context_menu)

        self.update_clock()
        self.delayed_color_update()

        self.root.mainloop()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, 64, 64), fill=(0, 0, 0))
        dc.text((20, 20), '⏱', fill=(255, 255, 255))
        self.menu = (
            item('Возобновить/Пауза', self.toggle_from_tray),
            item('Сброс', self.reset_from_tray),
            item('Разрешить перемещение', self.toggle_draggable),
            item('Выход', self.exit_app),
        )
        self.tray_icon = Icon("Stopwatch", image, "Секундомер", self.menu)

    def toggle_from_tray(self):
        self.toggle()

    def reset_from_tray(self):
        self.reset()

    def toggle_draggable(self):
        self.is_draggable = not self.is_draggable
        if self.is_draggable:
            self.root.config(cursor="fleur")
            new_label = "Запретить перемещение"
        else:
            self.root.config(cursor="")
            new_label = "Разрешить перемещение"

        # Обновляем метку в меню трея
        new_menu = list(self.menu)
        new_menu[2] = item(new_label, self.toggle_draggable)
        self.menu = tuple(new_menu)
        self.tray_icon.update_menu()

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Возобновить/Пауза", command=self.toggle)
        menu.add_command(label="Сброс", command=self.reset)
        menu.add_command(label="Разрешить перемещение" if not self.is_draggable else "Запретить перемещение",
                         command=self.toggle_draggable)
        menu.add_command(label="Выход", command=self.exit_app)
        menu.tk_popup(event.x_root, event.y_root)

    def exit_app(self):
        self.tray_icon.stop()
        self.root.quit()

    def start_move(self, event):
        if self.is_draggable:
            self.x = event.x
            self.y = event.y
            self.is_moving = True

    def do_move(self, event):
        if self.is_draggable and self.is_moving:
            x = self.root.winfo_x() + (event.x - self.x)
            y = self.root.winfo_y() + (event.y - self.y)
            self.root.geometry(f'+{x}+{y}')

    def stop_move(self, event):
        if self.is_draggable and self.is_moving:
            self.is_moving = False
            self.root.after(100, self.delayed_color_update)

    def toggle(self, event=None):
        if self.running:
            self.pause()
        else:
            self.start()

    def start(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True
            self.update_clock()

    def pause(self):
        if self.running:
            self.root.after_cancel(self.timer)
            self.elapsed_time = time.time() - self.start_time
            self.running = False

    def reset(self, event=None):
        self.pause()
        self.elapsed_time = 0
        self.update_time_display("00:00:00")

    def update_clock(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            time_str = time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time))
            self.update_time_display(time_str)
            self.timer = self.root.after(50, self.update_clock)

    def update_time_display(self, time_str):
        self.time_image = Image.new('RGBA', (300, 150), (0, 0, 0, 0))
        self.time_draw = ImageDraw.Draw(self.time_image)
        self.time_draw.text((150, 75), time_str, font=self.font, fill=self.current_color, anchor='mm')
        self.photo = ImageTk.PhotoImage(self.time_image)
        self.canvas.itemconfig(self.time_text, image=self.photo)

    def delayed_color_update(self):
        if not self.is_moving:
            self.update_color()
        self.root.after(500, self.delayed_color_update)

    def update_color(self):
        x = self.root.winfo_rootx() + 150
        y = self.root.winfo_rooty() + 75
        try:
            image = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
            color = image.getpixel((0, 0))

            h, s, v = colorsys.rgb_to_hsv(color[0] / 255, color[1] / 255, color[2] / 255)
            v = 1 - v
            r, g, b = colorsys.hsv_to_rgb(h, s, v)

            self.target_color = '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))
            self.animate_color_change()
        except Exception as e:
            print(f"Error updating color: {e}")

    def animate_color_change(self):
        current_rgb = tuple(int(self.current_color[i:i + 2], 16) for i in (1, 3, 5))
        target_rgb = tuple(int(self.target_color[i:i + 2], 16) for i in (1, 3, 5))

        new_rgb = tuple(int(current + (target - current) * 0.1) for current, target in zip(current_rgb, target_rgb))

        self.current_color = '#{:02x}{:02x}{:02x}'.format(*new_rgb)
        self.update_time_display(time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time)))

        if self.current_color != self.target_color:
            self.root.after(50, self.animate_color_change)


if __name__ == "__main__":
    Stopwatch()