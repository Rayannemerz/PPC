import sys
import time
import tkinter as tk
import random
from multiprocessing import Process, Value, Manager
from multiprocessing.managers import SyncManager, ValueProxy
#quand le prédateur mange il va dans la mémoire partagée diminuer le nb de proies avec le PID
#un process par prédateur s'enregistre par socket
#stock la position et le PID dans un dict partagé

class SimulationView:
    def __init__(self, nb_prey, nb_predator, nb_herbe, grid_status, prey_pos, pred_pos, secheresse_status):
        # Initialisation de la fenêtre Tkinter
        self.root = tk.Tk() #fenetre principale
        self.root.title("Écosystème : Proies vs Prédateurs")
        self.width = 800
        self.height = 800
        self.grid_size = 40 #40 pixels par case
        

        self.nb_prey = nb_prey #compteurs partagés
        self.nb_predator = nb_predator
        self.nb_herbe = nb_herbe
        self.grid_status = grid_status
        self.prey_pos = prey_pos
        self.pred_pos = pred_pos
        self.secheresse_status = secheresse_status  # Pas utilisé dans l'affichage actuel
        # Création du Canvas pour dessiner 
        self.canvas = tk.Canvas(self.root, width=800, height=800, bg="#000000")
        self.canvas.pack() #ajt l'affichage au root

        # Lancer la boucle de dessin
        self.on_draw()#demarre la boucle de dessin
        self.root.mainloop()#demarre la boucle d'evenements tk

    def draw_grid(self):
        rows = 20
        cols = 20
        # On parcourt les 400 cases
        for r in range(rows):
            for c in range(cols):
                index = r * cols + c 
                
                # On vérifie l'état de CHAQUE case dans la liste partagée
                # 0 = Vert (herbe à manger), 1 = Jaune (mangée/sécheresse)
                case_state = self.grid_status[index] 
                
                # Vert ou Jaune
                if case_state == 1:
                    color = "#FFD700"  # Jaune or - cases mangées
                else:
                    color = "#00AA00"  # Vert clair - herbe à manger
                
                # Calcul des coordonnées de la case (carré de 40x40)
                x1 = c * self.grid_size
                y1 = r * self.grid_size
                x2 = x1 + self.grid_size
                y2 = y1 + self.grid_size
                
                # On dessine le petit carré avec bordure fine
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333333", width=1)

    def on_draw(self):
        # Effacer l'écran pour redessiner
        self.canvas.delete("all")
        self.draw_grid() # Dessiner la grille mise à jour
        # 1. Lire la valeur (0 ou 1)
        is_secheresse = self.secheresse_status.value
        status_text = "OUI" if is_secheresse == 1 else "NON"
        status_color = "orange" if is_secheresse == 1 else "lightblue"

        # 2. L'afficher sur le Canvas
        self.canvas.create_text(20, 95, anchor="w", text=f"Sécheresse: {status_text}", fill=status_color, font=("Arial", 14, "bold"))
        # 1. Lire les valeurs partagées
        current_prey = self.nb_prey.value
        current_pred = self.nb_predator.value
        
        # 2. Affichage du texte (Tableau de bord) en haut à gauche
        self.canvas.create_text(20, 20, anchor="w", text=f"Proies: {current_prey}", fill="cyan", font=("Arial", 14, "bold"))
        self.canvas.create_text(20, 45, anchor="w", text=f"Prédateurs: {current_pred}", fill="red", font=("Arial", 14, "bold"))
        self.canvas.create_text(20, 70, anchor="w", text=f"Herbe: {self.nb_herbe.value}", fill="lime", font=("Arial", 14, "bold"))

        # 3. Dessiner des cercles bleus pour les proies (aux vraies positions)
        try:
            prey_dict = dict(self.prey_pos)
            for pid, pos in prey_dict.items():
                row = pos // 20 #calcul ligne division entière
                col = pos % 20 #calcul colonne reste de la division
                x = col * self.grid_size + self.grid_size // 2 #centre du cercle
                y = row * self.grid_size + self.grid_size // 2
                self.canvas.create_oval(x-6, y-6, x+6, y+6, fill="blue", outline="white", width=2)
        except Exception as e:
            pass

        # 4. Dessiner des cercles rouges pour les prédateurs (aux vraies positions)
        try:
            pred_dict = dict(self.pred_pos)
            for pid, pos in pred_dict.items():
                row = pos // 20
                col = pos % 20
                x = col * self.grid_size + self.grid_size // 2
                y = row * self.grid_size + self.grid_size // 2
                self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="red", outline="black", width=2)
        except Exception as e:
            pass

        # 5. On demande à Tkinter de relancer on_draw dans 500ms (boucle infinie)
        self.root.after(500, self.on_draw)

def start_screen(nb_prey, nb_predator, nb_herbe, grid_status, prey_pos, pred_pos, secheresse_status):

    window = SimulationView(nb_prey, nb_predator, nb_herbe, grid_status, prey_pos, pred_pos, secheresse_status)
    
if __name__ == '__main__':
    SyncManager.register("get_herbe", proxytype=ValueProxy)
    SyncManager.register("get_prey", proxytype=ValueProxy)
    SyncManager.register("get_predator", proxytype=ValueProxy)
    SyncManager.register("get_secheresse", proxytype=ValueProxy)
    SyncManager.register("get_grid")
    SyncManager.register("get_prey_pos")
    SyncManager.register("get_pred_pos")
    
    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
    m.connect()
    start_screen(m.get_prey(), m.get_predator(), m.get_herbe(), m.get_grid(), m.get_prey_pos(), m.get_pred_pos())
    
