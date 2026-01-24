import time
import os
import socket
import random
from multiprocessing.managers import SyncManager, ValueProxy

def predator_process(nb_prey, nb_predator, grid_status, pred_pos, prey_pos):
    energie = 200 
    pid = os.getpid()
    last_repro = time.time() - 15
    
    nb_predator.value += 1
    
    # Position initiale aléatoire
    position = random.randint(0, 399)
    pred_pos[pid] = position
    
    print(f"[PREDATEUR {pid}] Chasseur en ligne !")

    try:
        while energie > 0:
            # Trouver la proie la plus proche
            prey_positions = list(prey_pos.values())
            
            if prey_positions:
                # Calculer les distances vers toutes les proies
                min_distance = float('inf')
                target_pos = None
                
                pred_row = position // 20
                pred_col = position % 20
                
                for prey_p in prey_positions:
                    prey_row = prey_p // 20
                    prey_col = prey_p % 20
                    distance = abs(pred_row - prey_row) + abs(pred_col - prey_col)
                    if distance < min_distance:
                        min_distance = distance
                        target_pos = prey_p
                
                # Se déplacer vers la proie la plus proche
                if target_pos is not None:
                    target_row = target_pos // 20
                    target_col = target_pos % 20
                    
                    moves = []
                    row = position // 20
                    col = position % 20
                    
                    # Priorité aux mouvements qui rapprochent de la proie
                    if row > target_row and row > 0:
                        moves.append(position - 20)  # haut
                    if row < target_row and row < 19:
                        moves.append(position + 20)  # bas
                    if col > target_col and col > 0:
                        moves.append(position - 1)  # gauche
                    if col < target_col and col < 19:
                        moves.append(position + 1)  # droite
                    
                    # Si pas de mouvement optimal, bouger vers n'importe quelle direction
                    if not moves:
                        if row > 0: moves.append(position - 20)
                        if row < 19: moves.append(position + 20)
                        if col > 0: moves.append(position - 1)
                        if col < 19: moves.append(position + 1)
                    
                    if moves:
                        position = random.choice(moves)
                        pred_pos[pid] = position
            else:
                # Pas de proie, déplacement aléatoire
                row = position // 20
                col = position % 20
                moves = []
                if row > 0: moves.append(position - 20)
                if row < 19: moves.append(position + 20)
                if col > 0: moves.append(position - 1)
                if col < 19: moves.append(position + 1)
                if moves:
                    position = random.choice(moves)
                    pred_pos[pid] = position
            
            time.sleep(0.66)  # ~3x plus rapide qu'avant
            energie -= 12  # même coût par tick, donc consommation plus rapide dans le temps
            
            # --- CHASSE : Mange si sur la même case qu'une proie ---
            prey_on_case = [p_pid for p_pid, p_pos in list(prey_pos.items()) if p_pos == position]
            if energie < 160 and nb_prey.value > 1 and prey_on_case:
                nb_prey.value -= 1
                energie += 80
                print(f"[PREDATEUR {pid}] Proie dévorée sur case {position}! Energie: {energie}")
            elif nb_prey.value <= 1:
                print(f"[PREDATEUR {pid}] Trop peu de proies, famine...")

            # --- REPRODUCTION ---
            if energie > 200 and nb_prey.value > 5 and (time.time() - last_repro) > 20:
                energie -= 80
                last_repro = time.time()
                try:
                    # Si l'espèce est éteinte (sécurité), ne pas reproduire
                    if nb_predator.value == 0:
                        raise RuntimeError("espèce PREDATOR éteinte")
                    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    soc.settimeout(1.0)
                    soc.connect(('localhost', 8080))
                    soc.sendall(b"PREDATOR")
                    soc.close()
                    print(f"[PREDATEUR {pid}] Un fils est né !")
                except Exception as e:
                    print(f"[PREDATEUR {pid}] Échec reproduction : {e}")
                    
    finally:
        if pid in pred_pos:
            del pred_pos[pid]
        nb_predator.value -= 1
        print(f"[PREDATEUR {pid}] Mort (PID: {pid}).")

if __name__ == '__main__':
    # Enregistrement des noms pour accéder aux objets partagés
    SyncManager.register("get_herbe", proxytype=ValueProxy)
    SyncManager.register("get_prey", proxytype=ValueProxy)
    SyncManager.register("get_predator", proxytype=ValueProxy)
    SyncManager.register("get_secheresse", proxytype=ValueProxy)
    SyncManager.register("get_grid")
    SyncManager.register("get_pred_pos")
    SyncManager.register("get_prey_pos")

    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
    
    try:
        m.connect()
        print("=== Connecté au SyncManager (Predator) ===")
        # On passe les proxies récupérés avec les bons noms
        predator_process(m.get_prey(), m.get_predator(), m.get_grid(), m.get_pred_pos(), m.get_prey_pos())
    except Exception as e:
        print(f"Erreur fatale : {e}")
