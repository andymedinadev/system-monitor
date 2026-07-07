import customtkinter as ctk
import psutil
import collections

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- Config ---
WINDOW_ALPHA = 0.85
UPDATE_UI_MS = 500          # cada cuánto refresca la UI
SAMPLE_CPU_MS = 100        # cada cuánto muestreamos CPU
SMOOTH_SAMPLES = 5         # tamaño del promedio móvil

cpu_samples = collections.deque(maxlen=SMOOTH_SAMPLES)


def create_overlay():
    root = ctk.CTk()
    root.title("System Monitor")
    root.geometry("100x70+20+20")
    root.attributes("-topmost", True)
    root.attributes("-alpha", WINDOW_ALPHA)
    root.overrideredirect(True)

    frame = ctk.CTkFrame(root, corner_radius=8)
    frame.pack(fill="both", expand=True)

    cpu_label = ctk.CTkLabel(frame, text="CPU: 0%", font=("Segoe UI", 14))
    cpu_label.pack(anchor="w", padx=8, pady=(6, 0))

    ram_label = ctk.CTkLabel(frame, text="RAM: 0%", font=("Segoe UI", 14))
    ram_label.pack(anchor="w", padx=8, pady=(2, 6))

    # --- CLOSE ---
    def close_app(event=None):
    	root.destroy()

    root.bind("<Button-2>", close_app)

    # --- Drag window ---
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def do_move(event):
        x = root.winfo_x() + event.x - root.x
        y = root.winfo_y() + event.y - root.y
        root.geometry(f"+{x}+{y}")

    frame.bind("<Button-1>", start_move)
    frame.bind("<B1-Motion>", do_move)

    # --- CPU smooth sampling ---
    def sample_cpu():
        value = psutil.cpu_percent(interval=None)
        cpu_samples.append(value)
        root.after(SAMPLE_CPU_MS, sample_cpu)

    def get_smooth_cpu():
        if not cpu_samples:
            return 0
        return sum(cpu_samples) / len(cpu_samples)

    # --- UI update ---
    def update_stats():
        cpu = get_smooth_cpu()
        ram = psutil.virtual_memory().percent

        cpu_label.configure(text=f"CPU: {cpu:.1f}%")
        ram_label.configure(text=f"RAM: {ram:.1f}%")

        root.after(UPDATE_UI_MS, update_stats)

    # precalienta psutil para que no devuelva 0 al inicio
    psutil.cpu_percent(interval=None)

    sample_cpu()
    update_stats()

    root.mainloop()
