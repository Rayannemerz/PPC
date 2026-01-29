import time, os, socket, random
from multiprocessing.managers import SyncManager, ValueProxy

def prey_process(nb_herbe, nb_prey, secheresse_status, grid_status, prey_pos):
    pid = os.getpid()
    energie = random.randint(80, 120)
    nb_prey.value += 1
    
    # Position initiale aléatoire
    position = random.randint(0, 399)
    prey_pos[pid] = position #enregistre la position dans le dict partagé
    
    last_repro = time.time() - 10 # pour permettre une reproduction tout les 10sec
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

                # Manger et jaunir uniquement si la proie a faim
                if energie < 80 and grid_status[position] == 0:
                    if energie < 50 and nb_herbe.value > 2:
                        nb_herbe.value -= 2  # consommation réelle
                        energie += 40
                        print(f"[PROIE {pid}] Mange la case {position}")
                    else:
                        if nb_herbe.value > 0:
                            nb_herbe.value -= 1
                    # La case perd l'herbe seulement si la proie a mangé
                    grid_status[position] = 1
            
            #reproduction si assez d'énergie et de temps écoulé
            if energie > 90 and (time.time() - last_repro) > 10 and nb_herbe.value > 10:
                energie -= 40
                last_repro = time.time()
                try:
                    # Si l'espèce est éteinte (sécurité), ne pas reproduire
                    if nb_prey.value == 0:
                        raise RuntimeError("espèce PREY éteinte")
                    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # crée une socket TCP et ipv4
                    soc.settimeout(1.0)  # fixe un délai max pour la connexion
                    soc.connect(('localhost', 8080))  # se connecte au serveur local (port 8080)
                    soc.sendall(b"PREY")  # envoie le message de reproduction binaire
                    soc.close()  # ferme la connexion
                    print(f"[PROIE {pid}] Un petit est né !")
                except Exception as e: #affichage erreur reproduction
                    print(f"[PROIE {pid}] Échec reproduction : {e}")
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
    SyncManager.register("get_grid") #enregistre coté client pour pouvoir appeler m.get...
    SyncManager.register("get_prey_pos")
    #lire et partager depuis un autre process (valueProxy)
    
    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc') 
    m.connect()
    prey_process(m.get_herbe(), m.get_prey(), m.get_secheresse(), m.get_grid(), m.get_prey_pos())
