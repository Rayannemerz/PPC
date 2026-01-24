import tkinter as tk
import random
from multiprocessing.managers import SyncManager, ValueProxy

class SimulationView:
    def __init__(self, nb_prey, nb_predator, nb_herbe, grid_status):
        self.root = tk.Tk()
        self.root.title("Écosystème : Proies vs Prédateurs")
        self.grid_size = 40
        self.nb_prey, self.nb_predator, self.nb_herbe, self.grid_status = nb_prey, nb_predator, nb_herbe, grid_status
        self.canvas = tk.Canvas(self.root, width=800, height=800, bg="#073809")
        self.canvas.pack()
        self.on_draw()
        self.root.mainloop()

    def draw_grid(self):
        cols = 20
        for i, status in enumerate(self.grid_status):
            r, c = divmod(i, cols)
            # 0: Herbe, 1: Sec, 2: Proie, 3: Attaque
            color = "#073809"
            if status == 1: color = "#E6D55A"
            elif status == 2: color = "blue"
            elif status == 3: color = "red"
            
            x1, y1 = c * self.grid_size, r * self.grid_size
            self.canvas.create_rectangle(x1, y1, x1+self.grid_size, y1+self.grid_size, fill=color, outline="#0a1a0a")

    def on_draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        try:
            p = self.nb_prey.value; h = self.nb_herbe.value; pr = self.nb_predator.value
        except: return
        self.canvas.create_text(10, 30, anchor="w", text=f"Proies: {p} | Prédateurs: {pr}", fill="cyan", font=("Arial", 14, "bold"))
        self.canvas.create_text(10, 60, anchor="w", text=f"Herbe: {h}", fill="white", font=("Arial", 14))
        self.root.after(400, self.on_draw)

def start_screen(nb_prey, nb_predator, nb_herbe, grid_status):
    SimulationView(nb_prey, nb_predator, nb_herbe, grid_status)

if __name__ == '__main__':
    SyncManager.register("nb_herbe", proxytype=ValueProxy)
    SyncManager.register("nb_prey", proxytype=ValueProxy)
    SyncManager.register("nb_predator", proxytype=ValueProxy)
    SyncManager.register("grid_status")
    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
    m.connect()
    start_screen(m.nb_prey(), m.nb_predator(), m.nb_herbe(), m.grid_status())
