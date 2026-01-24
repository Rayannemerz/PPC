from multiprocessing.managers import SyncManager, ValueProxy
import signal, socket, os, time, threading, random
from multiprocessing import Process, Value, Manager
from prey import prey_process
from display import start_screen

# Variables pour le signal
nb_herbe = None
secheresse_status = None
grid_status = None

def secheresse_handler(signum, frame):
    if secheresse_status is None: return
    if secheresse_status.value == 0:
        secheresse_status.value = 1
        for i in range(len(grid_status)):
            if random.random() > 0.8: grid_status[i] = 1
        print("Sécheresse : La grille jaunit !")
    else:
        secheresse_status.value = 0
        for i in range(len(grid_status)): grid_status[i] = 0
        print("Pluie : La grille redevient verte !")

def grow_grass(nb_herbe, secheresse_status, grid_status):
    if secheresse_status.value == 0:
        # On verdit au plus une case jaune et on incrémente l'herbe seulement si la case redevient verte
        indices_jaunes = [i for i, val in enumerate(grid_status) if val == 1]
        if indices_jaunes:
            idx = random.choice(indices_jaunes)
            grid_status[idx] = 0  # Jaune -> Vert
            nb_herbe.value += 1

def run_env(nb_herbe_p, nb_prey_p, nb_predator_p, secheresse_status_p, grid_status_p, prey_pos_p, pred_pos_p):
    global nb_herbe, secheresse_status, grid_status
    nb_herbe, secheresse_status, grid_status = nb_herbe_p, secheresse_status_p, grid_status_p
    
    signal.signal(signal.SIGUSR1, secheresse_handler)
    print(f"Serveur actif. PID: {os.getpid()}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)
    server_socket.settimeout(1.0)

    # Lancer l'affichage
    threading.Thread(target=start_screen, args=(nb_prey_p, nb_predator_p, nb_herbe_p, grid_status_p, prey_pos_p, pred_pos_p), daemon=True).start()

    # Spawner 3 prédateurs initiaux
    from predator import predator_process
    for _ in range(3):
        p = Process(target=predator_process, args=(nb_prey_p, nb_predator_p, grid_status_p, pred_pos_p, prey_pos_p))
        p.daemon = True
        p.start()

    while True:
        # Resynchroniser les compteurs avec l'état réel
        try:
            nb_prey_p.value = len(prey_pos_p)
            nb_predator_p.value = len(pred_pos_p)
            nb_herbe_p.value = sum(1 for v in grid_status_p if v == 0)
        except Exception:
            pass

        grow_grass(nb_herbe, secheresse_status, grid_status)
        time.sleep(1) # Fréquence de repousse
        try:
            client_conn, addr = server_socket.accept()
            data = client_conn.recv(1024).decode()
            if data == "PREY":
                # Interdire la réapparition si l'espèce est éteinte
                if nb_prey_p.value == 0:
                    print("[ENV] Repro PREY ignorée: espèce éteinte.")
                else:
                    p = Process(target=prey_process, args=(nb_herbe_p, nb_prey_p, secheresse_status_p, grid_status_p, prey_pos_p))
                    p.daemon = True
                    p.start()
            elif data == "PREDATOR":
                from predator import predator_process
                # Interdire la réapparition si l'espèce est éteinte
                if nb_predator_p.value == 0:
                    print("[ENV] Repro PREDATOR ignorée: espèce éteinte.")
                else:
                    p = Process(target=predator_process, args=(nb_prey_p, nb_predator_p, grid_status_p, pred_pos_p, prey_pos_p))
                    p.daemon = True
                    p.start()
            client_conn.close()
        except socket.timeout:
            continue

if __name__ == '__main__':
    # Utilisation d'un Manager parent pour stabiliser les objets
    m_init = Manager()
    shared_herbe = m_init.Value('i', 100)
    shared_prey = m_init.Value('i', 0)
    shared_pred = m_init.Value('i', 0)
    shared_sech = m_init.Value('b', 0)
    shared_grid = m_init.list([0]*400)
    shared_prey_pos = m_init.dict()  # {PID: position_index}
    shared_pred_pos = m_init.dict()  # {PID: position_index}
    
    # Initialiser des cases jaunes aléatoires au démarrage
    for _ in range(30):  # 30 cases jaunes aléatoires
        idx = random.randint(0, 399)
        shared_grid[idx] = 1

    # Enregistrement des noms attendus par les clients
    SyncManager.register("get_herbe", callable=lambda: shared_herbe, proxytype=ValueProxy)
    SyncManager.register("get_prey", callable=lambda: shared_prey, proxytype=ValueProxy)
    SyncManager.register("get_predator", callable=lambda: shared_pred, proxytype=ValueProxy)
    SyncManager.register("get_secheresse", callable=lambda: shared_sech, proxytype=ValueProxy)
    SyncManager.register("get_grid", callable=lambda: shared_grid, exposed=['__getitem__', '__setitem__', '__len__', '__iter__', 'append', 'extend', 'pop', 'remove', 'count', 'index'])
    SyncManager.register("get_prey_pos", callable=lambda: shared_prey_pos, exposed=['__getitem__', '__setitem__', '__delitem__', 'items', 'keys', 'values', '__len__', '__contains__'])
    SyncManager.register("get_pred_pos", callable=lambda: shared_pred_pos, exposed=['__getitem__', '__setitem__', '__delitem__', 'items', 'keys', 'values', '__len__', '__contains__'])

    # Attendre que le port se libère et lancer le manager
    import socket as sock
    for attempt in range(10):
        try:
            manager = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
            manager.start()
            break
        except (OSError, EOFError) as e:
            if attempt < 9:
                print(f"Tentative {attempt+1}: Port occupé, attente...")
                time.sleep(2)
            else:
                raise
    
    try:
        p_env = Process(target=run_env, args=(shared_herbe, shared_prey, shared_pred, shared_sech, shared_grid, shared_prey_pos, shared_pred_pos))
        p_env.daemon = False
        p_env.start()
        p_env.join()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    finally:
        manager.shutdown()
