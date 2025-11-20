import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox, font
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

class YouTubeThumbnailCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Thumbnail Creator Pro")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')

        # Canvas setup (YouTube thumbnail size: 1280x720)
        self.canvas_width = 1280
        self.canvas_height = 720
        self.display_scale = 0.5

        # Initialize canvas image
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), '#FFFFFF')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)

        # Layers
        self.layers = []
        self.background_image = None
        self.text_elements = []
        self.shape_elements = []

        # Current settings
        self.current_text = ""
        self.current_font_size = 100
        self.current_font_family = "Arial"
        self.current_text_color = "#FFFFFF"
        self.current_bg_color = "#FF0000"
        self.current_outline_color = "#000000"
        self.current_outline_width = 8
        self.shadow_enabled = True
        self.shadow_offset = 5
        self.text_bold = True
        self.text_italic = False
        self.gradient_enabled = False

        self.setup_ui()
        self.render_canvas()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Canvas
        left_frame = tk.Frame(main_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        canvas_label = tk.Label(left_frame, text="Preview (1280x720)", bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        canvas_label.pack(pady=10)

        self.canvas = tk.Canvas(
            left_frame,
            width=int(self.canvas_width * self.display_scale),
            height=int(self.canvas_height * self.display_scale),
            bg='white',
            highlightthickness=2,
            highlightbackground='#444'
        )
        self.canvas.pack(pady=10, padx=10)

        # Right panel - Controls
        right_frame = tk.Frame(main_frame, bg='#2a2a2a', width=400, relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
        right_frame.pack_propagate(False)

        # Scrollable frame for controls
        canvas_scroll = tk.Canvas(right_frame, bg='#2a2a2a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas_scroll.yview)
        scrollable_frame = tk.Frame(canvas_scroll, bg='#2a2a2a')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )

        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title
        title = tk.Label(scrollable_frame, text="🎨 THUMBNAIL CREATOR", bg='#2a2a2a', fg='#FF0000', font=('Arial', 16, 'bold'))
        title.pack(pady=15)

        # Background Section
        self.create_section(scrollable_frame, "📷 BACKGROUND", [
            ("Load Image", self.load_background_image),
            ("Solid Color", self.set_background_color),
            ("Gradient", self.apply_gradient_background),
            ("Blur Background", self.blur_background),
            ("Brightness", None)
        ])

        self.brightness_scale = tk.Scale(
            scrollable_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
            label="Brightness", bg='#3a3a3a', fg='white', command=self.adjust_brightness
        )
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack(fill=tk.X, padx=20, pady=5)

        # Text Section
        self.create_section(scrollable_frame, "📝 TEXT", [])

        tk.Label(scrollable_frame, text="Text Content:", bg='#2a2a2a', fg='white').pack(pady=5)
        self.text_entry = tk.Entry(scrollable_frame, width=30, font=('Arial', 12))
        self.text_entry.pack(pady=5, padx=20)
        self.text_entry.insert(0, "YOUR TEXT HERE")

        tk.Label(scrollable_frame, text="Font Size:", bg='#2a2a2a', fg='white').pack()
        self.font_size_scale = tk.Scale(
            scrollable_frame, from_=20, to=250, resolution=5, orient=tk.HORIZONTAL,
            bg='#3a3a3a', fg='white', command=self.update_font_size
        )
        self.font_size_scale.set(100)
        self.font_size_scale.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(scrollable_frame, text="Font Family:", bg='#2a2a2a', fg='white').pack()
        self.font_family_var = tk.StringVar(value="Arial")
        font_families = ["Arial", "Impact", "Comic Sans MS", "Times New Roman", "Courier New", "Verdana", "Georgia"]
        font_menu = ttk.Combobox(scrollable_frame, textvariable=self.font_family_var, values=font_families, state='readonly')
        font_menu.pack(pady=5, padx=20)
        font_menu.bind('<<ComboboxSelected>>', self.update_font_family)

        # Font Style
        style_frame = tk.Frame(scrollable_frame, bg='#2a2a2a')
        style_frame.pack(pady=10)

        self.bold_var = tk.BooleanVar(value=True)
        self.italic_var = tk.BooleanVar(value=False)

        tk.Checkbutton(style_frame, text="Bold", variable=self.bold_var, bg='#2a2a2a', fg='white',
                      selectcolor='#1a1a1a', command=self.update_text_style).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(style_frame, text="Italic", variable=self.italic_var, bg='#2a2a2a', fg='white',
                      selectcolor='#1a1a1a', command=self.update_text_style).pack(side=tk.LEFT, padx=5)

        # Text Colors
        color_frame = tk.Frame(scrollable_frame, bg='#2a2a2a')
        color_frame.pack(pady=10)

        tk.Button(color_frame, text="Text Color", command=self.choose_text_color,
                 bg='#4a4a4a', fg='white', width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(color_frame, text="Outline Color", command=self.choose_outline_color,
                 bg='#4a4a4a', fg='white', width=12).pack(side=tk.LEFT, padx=5)

        tk.Label(scrollable_frame, text="Outline Width:", bg='#2a2a2a', fg='white').pack()
        self.outline_scale = tk.Scale(
            scrollable_frame, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL,
            bg='#3a3a3a', fg='white', command=self.update_outline_width
        )
        self.outline_scale.set(8)
        self.outline_scale.pack(fill=tk.X, padx=20, pady=5)

        # Shadow
        self.shadow_var = tk.BooleanVar(value=True)
        tk.Checkbutton(scrollable_frame, text="Enable Shadow", variable=self.shadow_var,
                      bg='#2a2a2a', fg='white', selectcolor='#1a1a1a',
                      command=self.toggle_shadow).pack(pady=5)

        tk.Label(scrollable_frame, text="Shadow Offset:", bg='#2a2a2a', fg='white').pack()
        self.shadow_scale = tk.Scale(
            scrollable_frame, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL,
            bg='#3a3a3a', fg='white', command=self.update_shadow
        )
        self.shadow_scale.set(5)
        self.shadow_scale.pack(fill=tk.X, padx=20, pady=5)

        # Text Position
        tk.Label(scrollable_frame, text="Text Position:", bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)

        position_frame = tk.Frame(scrollable_frame, bg='#2a2a2a')
        position_frame.pack(pady=5)

        positions = [
            ("Top", "top"),
            ("Center", "center"),
            ("Bottom", "bottom")
        ]

        self.text_position_var = tk.StringVar(value="center")
        for text, value in positions:
            tk.Radiobutton(position_frame, text=text, variable=self.text_position_var, value=value,
                          bg='#2a2a2a', fg='white', selectcolor='#1a1a1a',
                          command=self.update_text_position).pack(side=tk.LEFT, padx=10)

        # Add Text Button
        tk.Button(scrollable_frame, text="➕ ADD TEXT", command=self.add_text_to_canvas,
                 bg='#FF0000', fg='white', font=('Arial', 12, 'bold'), pady=10).pack(pady=15, padx=20, fill=tk.X)

        # Shapes Section
        self.create_section(scrollable_frame, "⭐ SHAPES & EFFECTS", [
            ("Add Circle", lambda: self.add_shape("circle")),
            ("Add Rectangle", lambda: self.add_shape("rectangle")),
            ("Add Arrow", lambda: self.add_shape("arrow")),
            ("Add Starburst", self.add_starburst)
        ])

        # Stickers/Emoji Section
        self.create_section(scrollable_frame, "😊 EMOJI & STICKERS", [])

        emoji_frame = tk.Frame(scrollable_frame, bg='#2a2a2a')
        emoji_frame.pack(pady=10)

        emojis = ["🔥", "👍", "😱", "💯", "⚡", "✅", "❌", "⭐", "💪", "🎯", "🚀", "💰", "👉", "🔴", "📈", "⏰"]
        row_frame = None
        for i, emoji in enumerate(emojis):
            if i % 4 == 0:
                row_frame = tk.Frame(emoji_frame, bg='#2a2a2a')
                row_frame.pack()
            tk.Button(row_frame, text=emoji, font=('Arial', 20), command=lambda e=emoji: self.add_emoji(e),
                     bg='#3a3a3a', width=3).pack(side=tk.LEFT, padx=2, pady=2)

        # Export Section
        self.create_section(scrollable_frame, "💾 EXPORT", [
            ("Save Thumbnail", self.save_thumbnail),
            ("Clear Canvas", self.clear_canvas),
            ("Undo Last", self.undo_last)
        ])

        # Templates
        self.create_section(scrollable_frame, "🎨 QUICK TEMPLATES", [
            ("Gaming Style", self.apply_gaming_template),
            ("Tutorial Style", self.apply_tutorial_template),
            ("Vlog Style", self.apply_vlog_template),
            ("Reaction Style", self.apply_reaction_template)
        ])

    def create_section(self, parent, title, buttons):
        section_frame = tk.LabelFrame(parent, text=title, bg='#3a3a3a', fg='#FF0000',
                                     font=('Arial', 11, 'bold'), padx=10, pady=10)
        section_frame.pack(fill=tk.X, padx=15, pady=10)

        for btn_text, btn_command in buttons:
            if btn_command:
                tk.Button(section_frame, text=btn_text, command=btn_command,
                         bg='#4a4a4a', fg='white', width=25, pady=5).pack(pady=3)

    def render_canvas(self):
        # Resize for display
        display_image = self.canvas_image.resize(
            (int(self.canvas_width * self.display_scale),
             int(self.canvas_height * self.display_scale)),
            Image.LANCZOS
        )

        from PIL import ImageTk
        self.photo = ImageTk.PhotoImage(display_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def load_background_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            img = Image.open(file_path)
            img = img.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)
            self.canvas_image = img
            self.canvas_draw = ImageDraw.Draw(self.canvas_image)
            self.render_canvas()

    def set_background_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:
            self.current_bg_color = color[1]
            self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), color[1])
            self.canvas_draw = ImageDraw.Draw(self.canvas_image)
            self.render_canvas()

    def apply_gradient_background(self):
        color1 = colorchooser.askcolor(title="Choose Start Color")
        if not color1[1]:
            return
        color2 = colorchooser.askcolor(title="Choose End Color")
        if not color2[1]:
            return

        from PIL import Image
        img = Image.new('RGB', (self.canvas_width, self.canvas_height))
        draw = ImageDraw.Draw(img)

        r1, g1, b1 = int(color1[1][1:3], 16), int(color1[1][3:5], 16), int(color1[1][5:7], 16)
        r2, g2, b2 = int(color2[1][1:3], 16), int(color2[1][3:5], 16), int(color2[1][5:7], 16)

        for y in range(self.canvas_height):
            ratio = y / self.canvas_height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (self.canvas_width, y)], fill=(r, g, b))

        self.canvas_image = img
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)
        self.render_canvas()

    def blur_background(self):
        self.canvas_image = self.canvas_image.filter(ImageFilter.GaussianBlur(radius=10))
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)
        self.render_canvas()

    def adjust_brightness(self, value):
        if hasattr(self, 'original_image'):
            enhancer = ImageEnhance.Brightness(self.original_image)
            self.canvas_image = enhancer.enhance(float(value))
            self.canvas_draw = ImageDraw.Draw(self.canvas_image)
            self.render_canvas()

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:
            self.current_text_color = color[1]

    def choose_outline_color(self):
        color = colorchooser.askcolor(title="Choose Outline Color")
        if color[1]:
            self.current_outline_color = color[1]

    def update_font_size(self, value):
        self.current_font_size = int(value)

    def update_font_family(self, event):
        self.current_font_family = self.font_family_var.get()

    def update_text_style(self):
        self.text_bold = self.bold_var.get()
        self.text_italic = self.italic_var.get()

    def update_outline_width(self, value):
        self.current_outline_width = int(value)

    def toggle_shadow(self):
        self.shadow_enabled = self.shadow_var.get()

    def update_shadow(self, value):
        self.shadow_offset = int(value)

    def update_text_position(self):
        pass  # Position will be used when adding text

    def add_text_to_canvas(self):
        text = self.text_entry.get()
        if not text:
            messagebox.showwarning("Warning", "Please enter text!")
            return

        try:
            # Try to use system fonts
            font_style = ""
            if self.text_bold and self.text_italic:
                font_style = "bold italic"
            elif self.text_bold:
                font_style = "bold"
            elif self.text_italic:
                font_style = "italic"

            try:
                if font_style:
                    test_font = ImageFont.truetype(f"{self.current_font_family}.ttf", self.current_font_size)
                else:
                    test_font = ImageFont.truetype(f"{self.current_font_family}.ttf", self.current_font_size)
            except:
                # Fallback to default font with size approximation
                test_font = ImageFont.load_default()

            # Calculate text position
            bbox = self.canvas_draw.textbbox((0, 0), text, font=test_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (self.canvas_width - text_width) // 2

            position = self.text_position_var.get()
            if position == "top":
                y = 100
            elif position == "center":
                y = (self.canvas_height - text_height) // 2
            else:  # bottom
                y = self.canvas_height - text_height - 100

            # Draw shadow
            if self.shadow_enabled:
                shadow_x = x + self.shadow_offset
                shadow_y = y + self.shadow_offset

                # Draw outline for shadow
                for adj_x in range(-self.current_outline_width, self.current_outline_width + 1):
                    for adj_y in range(-self.current_outline_width, self.current_outline_width + 1):
                        self.canvas_draw.text((shadow_x + adj_x, shadow_y + adj_y), text,
                                             font=test_font, fill='#00000088')

            # Draw outline
            for adj_x in range(-self.current_outline_width, self.current_outline_width + 1):
                for adj_y in range(-self.current_outline_width, self.current_outline_width + 1):
                    if adj_x * adj_x + adj_y * adj_y <= self.current_outline_width * self.current_outline_width:
                        self.canvas_draw.text((x + adj_x, y + adj_y), text,
                                             font=test_font, fill=self.current_outline_color)

            # Draw main text
            self.canvas_draw.text((x, y), text, font=test_font, fill=self.current_text_color)

            self.render_canvas()

        except Exception as e:
            messagebox.showerror("Error", f"Error adding text: {str(e)}")

    def add_shape(self, shape_type):
        draw = ImageDraw.Draw(self.canvas_image)

        if shape_type == "circle":
            x, y = 100, 100
            radius = 80
            draw.ellipse([x, y, x + radius * 2, y + radius * 2],
                        fill='#FF000080', outline='#FFFFFF', width=5)

        elif shape_type == "rectangle":
            draw.rectangle([50, 50, 300, 150], fill='#0000FF80', outline='#FFFFFF', width=5)

        elif shape_type == "arrow":
            # Simple arrow pointing right
            points = [(100, 300), (200, 250), (200, 280), (350, 280),
                     (350, 320), (200, 320), (200, 350)]
            draw.polygon(points, fill='#FFFF00', outline='#000000', width=3)

        self.render_canvas()

    def add_starburst(self):
        draw = ImageDraw.Draw(self.canvas_image)
        import math

        cx, cy = 200, 200
        outer_radius = 100
        inner_radius = 50
        points = []

        for i in range(16):
            angle = (i * math.pi * 2 / 16) - math.pi / 2
            if i % 2 == 0:
                x = cx + outer_radius * math.cos(angle)
                y = cy + outer_radius * math.sin(angle)
            else:
                x = cx + inner_radius * math.cos(angle)
                y = cy + inner_radius * math.sin(angle)
            points.append((x, y))

        draw.polygon(points, fill='#FFFF00', outline='#FF0000', width=4)
        self.render_canvas()

    def add_emoji(self, emoji):
        try:
            # Create a new layer for emoji
            emoji_img = Image.new('RGBA', (150, 150), (255, 255, 255, 0))
            draw = ImageDraw.Draw(emoji_img)

            try:
                emoji_font = ImageFont.truetype("seguiemj.ttf", 120)
            except:
                try:
                    emoji_font = ImageFont.truetype("Apple Color Emoji.ttc", 120)
                except:
                    emoji_font = ImageFont.load_default()

            draw.text((10, 10), emoji, font=emoji_font, fill='black', embedded_color=True)

            # Paste onto main canvas
            x = (self.canvas_width - 150) // 2
            y = 50

            self.canvas_image.paste(emoji_img, (x, y), emoji_img)
            self.render_canvas()

        except Exception as e:
            messagebox.showwarning("Info", f"Emoji rendering may not be fully supported: {str(e)}")

    def save_thumbnail(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            self.canvas_image.save(file_path, quality=95)
            messagebox.showinfo("Success", f"Thumbnail saved to:\n{file_path}")

    def clear_canvas(self):
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), '#FFFFFF')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)
        self.render_canvas()

    def undo_last(self):
        messagebox.showinfo("Info", "Undo feature - save states before each operation for full undo support")

    def apply_gaming_template(self):
        # Gaming style: Dark background with bright text
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), '#1a0033')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)

        # Add gradient effect
        for y in range(self.canvas_height):
            ratio = y / self.canvas_height
            r = int(26 * (1 - ratio) + 255 * ratio * 0.3)
            g = int(0 * (1 - ratio) + 0 * ratio)
            b = int(51 * (1 - ratio) + 255 * ratio * 0.3)
            self.canvas_draw.line([(0, y), (self.canvas_width, y)], fill=(r, g, b))

        self.render_canvas()
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, "EPIC GAMING MOMENT!")
        self.current_text_color = "#00FF00"
        self.current_outline_color = "#000000"

    def apply_tutorial_template(self):
        # Tutorial style: Clean, professional
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), '#FFFFFF')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)

        # Add blue accent bar
        self.canvas_draw.rectangle([0, 0, self.canvas_width, 150], fill='#0066CC')

        self.render_canvas()
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, "HOW TO: Step by Step")
        self.current_text_color = "#FFFFFF"
        self.current_outline_color = "#003366"

    def apply_vlog_template(self):
        # Vlog style: Bright and colorful
        colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), '#FFE66D')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)

        self.render_canvas()
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, "MY DAY VLOG!")
        self.current_text_color = "#FFFFFF"
        self.current_outline_color = "#FF1744"

    def apply_reaction_template(self):
        # Reaction style: Dramatic
        self.canvas_image = Image.new('RGB', (self.canvas_width, self.canvas_height), '#FF0000')
        self.canvas_draw = ImageDraw.Draw(self.canvas_image)

        self.render_canvas()
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, "YOU WON'T BELIEVE THIS!")
        self.current_text_color = "#FFFF00"
        self.current_outline_color = "#000000"

def main():
    root = tk.Tk()
    app = YouTubeThumbnailCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
