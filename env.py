from multiprocessing.managers import SyncManager
import signal
import socket
import os
import time
import threading
from multiprocessing import Process, Value, Manager
from prey import prey_process
from predator import predator_process
import tkinter as tk
from display import start_screen

nb_herbe=Value('i', 100)
nb_prey = Value('i', 0)
nb_predator = Value('i', 0)
# 'b' veut dire boolean (True/False)
# 0 = False (pas de sécheresse), 1 = True (sécheresse)
secheresse_status = Value('b', 0) 

def secheresse(signum,frame):
    if secheresse_status.value == 0:
        secheresse_status.value = 1
        print("Début de la sécheresse !")
    else:
        secheresse_status.value = 0
        print("L'eau est revenue !")

def grow_grass(nb_herbe, secheresse_status):
    if secheresse_status.value == 0: 
        nb_herbe.value += 5
        print(f"L'herbe pousse : {nb_herbe.value}")
    time.sleep(8) 
  

def run_env(nb_herbe, nb_prey, nb_predator, secheresse_status):
    signal.signal(signal.SIGUSR1, secheresse)
    print("ouverture du serveur")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#port ipv4 et TCP
    server_socket.bind(('localhost', 8080)) # reserve le port 8080
    server_socket.listen(5)# max 5 clients en attente max le reste sont refusés
    server_socket.settimeout(2.0)#attente de 2 secondes pour une connexion

    # Lancer l'écran dans un thread séparé
    display_thread = threading.Thread(target=start_screen, args=(nb_prey, nb_predator, nb_herbe))
    display_thread.daemon = True
    display_thread.start()

    thread_affichage = threading.Thread(
        target=start_screen, 
        args=(nb_prey, nb_predator, nb_herbe)
    )
    thread_affichage.daemon = True # Il s'arrête si env.py s'arrête
    thread_affichage.start()

    while True:
        grow_grass(nb_herbe, secheresse_status)
        
        try:
            client_conn, addr = server_socket.accept()# attend une connexion et crée un socket pour communiquer
            data = client_conn.recv(1024).decode() #reçoit des données du client
            print(f"Un nouvel animal arrive de {addr}")
            if data == "PREY":
                print(f"Création d'une proie via {addr}")
                p = Process(target=prey_process, args=(nb_herbe, nb_prey,secheresse_status))
                p.daemon = True # Pour que le processus s'arrête si le serveur s'arrête
                p.start() # Lancement du processus

            elif data == "PREDATOR":
                print(f"Création d'un prédateur via {addr}")
                p = Process(target=predator_process, args=(nb_prey, nb_predator,secheresse_status))
                p.daemon = True # Pour que le processus s'arrête si le serveur s'arrête
                p.start() # Lancement du processus

            client_conn.close() # On ferme la connexion une fois l'animal enregistré

        except socket.timeout:
            # Si personne ne vient après 2 sec, on recommence la boucle
            # (ce qui fait repousser l'herbe)
            continue

if __name__ == '__main__':
    with SyncManager(address=('127.0.0.1', 50000), authkey=b'abc') as manager:
        nb_herbe=manager.Value('i', 100)
        nb_prey = manager.Value('i', 0)
        nb_predator = manager.Value('i', 0)
        secheresse_status = manager.Value('b', 0)
        manager.register("NB_HERBE", nb_herbe)
        manager.register("NB_PREY", nb_prey)
        manager.register("NB_PREDATOR", nb_predator)    
        manager.register("SECHERESSE_STATUS", secheresse_status)
        p = Process(target=run_env, args=(nb_herbe, nb_prey, nb_predator, secheresse_status))
        p.start()
        p.join()
