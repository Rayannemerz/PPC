import time
import os
import socket
import threading
from multiprocessing import Process, Value, Manager
from multiprocessing.managers import SyncManager

def prey_process(nb_herbe, nb_prey,secheresse_status): 
    
    energie=100
    if nb_herbe.value > 0:
        nb_herbe.value -= 2
        energie += 20
    print(f"Mange. Herbe restante : {nb_herbe.value}")
    pid = os.getpid() # Récupère l'ID du processus module os
    print(f"[PROIE {pid}] Démarrée avec énergie {energie}.")
    while energie > 0:
        if secheresse_status.value == 1:
            energie -= 2  # La sécheresse fatigue les proies
        else:
            energie-=1 #perd de l'energie moins rapidement 
        time.sleep(2)
        energie -= 5
        if energie >80:
            energie -= 40 # La reproduction coûte cher en énergie
            print(f"[PROIE {os.getpid()}] Se reproduit ! (Energie restante : {energie})")
            reproduction_contact = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#port ipv4 et TCP
            reproduction_contact.connect(('localhost', 8080))# connecte au serveur
            reproduction_contact.send("PREY".encode())# envoie une demande de création de proie
            reproduction_contact.close()

        if energie < 30:
            with nb_herbe.get_lock():
                if nb_herbe.value > 0:
                    nb_herbe.value -= 2
                    energie += 20
                    print(f"[PROIE {pid}] Mange. Herbe restante : {nb_herbe.value}")

    nb_prey.value -= 1
    print(f"[PROIE {pid}] Mort.")

if __name__ == '__main__':

    m = SyncManager(address=('127.0.0.1', 50000), authkey=b'abc')
    m.connect()
    print(m.__dict__)
    nb_herbe = m.NB_HERBE()
    nb_prey = m.NB_PREY()
    secheresse_status = m.SECHERESSE_STATUS()
    prey_process(nb_herbe, nb_prey,secheresse_status)
