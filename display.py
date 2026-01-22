import threading
import time
from multiprocessing import Process, Manager
import arcade
import random

class SimulationView(arcade.Window):
    def __init__(self, nb_prey, nb_predator, nb_herbe):
        super().__init__(800, 800, "Écosystème : Proies vs Prédateurs")
        self.nb_prey = nb_prey
        self.nb_predator = nb_predator
        self.nb_herbe = nb_herbe
        
        # On génère des positions aléatoires pour l'esthétique
        self.positions_prey = []
        self.positions_pred = []

    def on_draw(self):
            arcade.start_render()
            
            # 1. Lire les valeurs partagées (on récupère la valeur actuelle)
            current_prey = self.nb_prey.value
            current_pred = self.nb_predator.value
            
            # 2. Affichage du texte (Tableau de bord)
            arcade.draw_text(f"Proies (Bleu): {current_prey}", 10, 760, arcade.color.BLUE, 18)
            arcade.draw_text(f"Prédateurs (Rouge): {current_pred}", 10, 730, arcade.color.RED, 18)
            arcade.draw_text(f"Herbe (Vert): {self.nb_herbe.value}", 10, 700, arcade.color.GREEN, 18)

            # 3. Dessiner des points pour représenter les populations
            # Note : On simule des positions ici car tes processus n'ont pas de coordonnées X,Y
            for _ in range(current_prey):
                x = random.randint(50, 750)
                y = random.randint(50, 750)
                arcade.draw_circle_filled(x, y, 5, arcade.color.BLUE)

            for _ in range(current_pred):
                x = random.randint(50, 750)
                y = random.randint(50, 750)
                arcade.draw_circle_filled(x, y, 8, arcade.color.RED)

    def start_screen(nb_prey, nb_predator, nb_herbe):
        window = SimulationView(nb_prey, nb_predator, nb_herbe)
        arcade.run()
        

