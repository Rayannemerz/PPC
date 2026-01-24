import time, os, socket, random
from multiprocessing.managers import SyncManager, ValueProxy

def prey_process(nb_herbe, nb_prey, secheresse_status, grid_status, prey_pos):
    pid = os.getpid()
    energie = 100
    nb_prey.value += 1
    
    # Position initiale aléatoire
    position = random.randint(0, 399)
    prey_pos[pid] = position
    
    last_repro = time.time() - 10
    try:
        while energie > 0:
            # Déplacement aléatoire vers une case adjacente
            row = position // 20
            col = position % 20
            moves = []
            if row > 0: moves.append(position - 20)  # haut
            if row < 19: moves.append(position + 20)  # bas
            if col > 0: moves.append(position - 1)  # gauche
            if col < 19: moves.append(position + 1)  # droite
            if moves:
                position = random.choice(moves)
                prey_pos[pid] = position

                # Manger avant de jaunir la case
                if grid_status[position] == 0:
                    if energie < 50 and nb_herbe.value > 2:
                        nb_herbe.value -= 2  # consommation réelle
                        energie += 40
                        print(f"[PROIE {pid}] Mange la case {position}")
                    else:
                        if nb_herbe.value > 0:
                            nb_herbe.value -= 1  # piétine l'herbe même sans faim
                    # La case perd l'herbe dans tous les cas
                    grid_status[position] = 1
            
            # --- REPRODUCTION ---
            if energie > 90 and (time.time() - last_repro) > 10 and nb_herbe.value > 10:
                energie -= 40
                last_repro = time.time()
                try:
                    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    soc.settimeout(1.0)
                    soc.connect(('localhost', 8080))
                    soc.sendall(b"PREY")
                    soc.close()
                    print(f"[PROIE {pid}] Un petit est né !")
                except Exception as e:
                    print(f"[PROIE {pid}] Échec reproduction (Serveur occupé) : {e}")
            time.sleep(2)
            energie -= 10
    finally:
        if pid in prey_pos:
            del prey_pos[pid]
        nb_prey.value -= 1
        print(f"Proie {pid} morte.")

if __name__ == '__main__':
    # Enregistrement identique au serveur
    SyncManager.register("get_herbe", proxytype=ValueProxy)
    SyncManager.register("get_prey", proxytype=ValueProxy)
    SyncManager.register("get_secheresse", proxytype=ValueProxy)
    SyncManager.register("get_grid")
    SyncManager.register("get_prey_pos")
    
    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
    m.connect()
    prey_process(m.get_herbe(), m.get_prey(), m.get_secheresse(), m.get_grid(), m.get_prey_pos())
