import time
import os
import socket

def prey_process(nb_herbe, nb_prey): 
    with nb_prey.get_lock():
        nb_prey.value += 1 # Incrémente le nombre de proies
    energie=100
    pid = os.getpid() # Récupère l'ID du processus module os
    print(f"[PROIE {pid}] Démarrée avec énergie {energie}.")
    while energie > 0:
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
                    nb_herbe.value -= 1
                    energie += 20
                    print(f"[PROIE {pid}] Mange. Herbe restante : {nb_herbe.value}")
    with nb_prey.get_lock():
        nb_prey.value -= 1
        print(f"[PROIE {pid}] Mort.")

