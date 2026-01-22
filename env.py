import signal
import socket
import os
import time
from multiprocessing import Process, Value
from prey import prey_process
from predator import predator_process

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
    if secheresse_status.value == 0: # pas de sécheresse
        with nb_herbe.get_lock(): #pour pas que les prey mangent en même temps
            nb_herbe.value += 5
            print(f"L'herbe pousse : {nb_herbe.value}")
    else:
        print("Sécheresse en cours... l'herbe ne pousse plus.")

def run_env(nb_herbe, nb_prey, nb_predator, secheresse_status):
    signal.signal(signal.SIGUSR1, secheresse)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#port ipv4 et TCP
    server_socket.bind(('localhost', 8080)) # reserve le port 8080
    server_socket.listen(5)# max 5 clients en attente max le reste sont refusés
    server_socket.settimeout(2.0)#attente de 2 secondes pour une connexion
    while True:
        grow_grass(nb_herbe, secheresse_status)
        time.sleep(5)
        
        try:
            client_conn, addr = server_socket.accept()# attend une connexion et crée un socket pour communiquer
            data = client_conn.recv(1024).decode() #reçoit des données du client
            print(f"Un nouvel animal arrive de {addr}")
            if data == "PREY":
                print(f"Création d'une proie via {addr}")
                p = Process(target=prey_process, args=(nb_herbe, nb_prey))
                p.daemon = True # Pour que le processus s'arrête si le serveur s'arrête
                p.start() # Lancement du processus

            elif data == "PREDATOR":
                print(f"Création d'un prédateur via {addr}")
                p = Process(target=predator_process, args=(nb_prey, nb_predator))
                p.daemon = True # Pour que le processus s'arrête si le serveur s'arrête
                p.start() # Lancement du processus

            client_conn.close() # On ferme la connexion une fois l'animal enregistré

        except socket.timeout:
            # Si personne ne vient après 2 sec, on recommence la boucle
            # (ce qui fait repousser l'herbe)
            continue

