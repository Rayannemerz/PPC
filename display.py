import sys
import time
import tkinter as tk
import random
from multiprocessing import Process, Value, Manager
from multiprocessing.managers import SyncManager
#quand le prédateur mange il va dans la mémoire partagée diminuer le nb de proies avec le PID
#un process par prédateur s'enregistre par socket
#stock la position et le PID dans un dict partagé

class SimulationView:
    def __init__(self, nb_prey, nb_predator, nb_herbe):
        # Initialisation de la fenêtre Tkinter
        self.root = tk.Tk()
        self.root.title("Écosystème : Proies vs Prédateurs")
        
        # Tes variables exactes
        self.nb_prey = nb_prey
        self.nb_predator = nb_predator
        self.nb_herbe = nb_herbe
        
        # Création du Canvas pour dessiner (remplace le moteur Arcade)
        self.canvas = tk.Canvas(self.root, width=800, height=800, bg="#FA9C9C")
        self.canvas.pack()

        # Lancer la boucle de dessin
        self.on_draw()
        self.root.mainloop()

    def on_draw(self):
        # Effacer l'écran pour redessiner
        self.canvas.delete("all")
        
        # 1. Lire les valeurs partagées
        current_prey = self.nb_prey.value
        current_pred = self.nb_predator.value
        
        # 2. Affichage du texte (Tableau de bord)
        # On utilise create_text car draw_text est spécifique à Arcade
        self.canvas.create_text(10, 40, anchor="w", text=f"Proies (Bleu): {current_prey}", fill="blue", font=("Arial", 18))
        self.canvas.create_text(10, 70, anchor="w", text=f"Prédateurs (Rouge): {current_pred}", fill="red", font=("Arial", 18))
        self.canvas.create_text(10, 100, anchor="w", text=f"Herbe (Vert): {self.nb_herbe.value}", fill="green", font=("Arial", 18))

        # 3. Dessiner des points pour représenter les populations
        for _ in range(current_prey):
            x = random.randint(50, 750)
            y = random.randint(150, 750)
            # create_oval dessine un cercle (x1, y1, x2, y2)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="blue", outline="white")

        for _ in range(current_pred):
            x = random.randint(50, 750)
            y = random.randint(150, 750)
            self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="red", outline="black")

        # 4. On demande à Tkinter de relancer on_draw dans 500ms (boucle infinie)
        self.root.after(500, self.on_draw)

def start_screen(nb_prey, nb_predator, nb_herbe):
    # Lancement avec tes variables
    window = SimulationView(nb_prey, nb_predator, nb_herbe)

if __name__ == '__main__':
    nb_herbe=Value('i', 100)
    nb_prey = Value('i', 0)
    nb_predator = Value('i', 0)
    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
    m.connect()
    start_screen(nb_prey, nb_predator, nb_herbe)
    
