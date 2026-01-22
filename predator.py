import time
import os
import socket
from multiprocessing import Process

def predator_process(nb_prey, nb_predator):
    energie = 200 # Plus résistant qu'une proie
    pid = os.getpid()# Récupère l'ID du processus module os
    
    with nb_predator.get_lock(): # Incrémente le nombre de prédateurs
        nb_predator.value += 1
    print(f"[PREDATEUR {pid}] Chasseur en ligne !")

    while energie > 0:
        time.sleep(3) # Chasse toutes les 3 secondes
        energie -= 10 # Se dépense beaucoup
        if energie > 180:
                energie -= 100 #reproduction coûte cher
                print(f"[PREDATEUR {pid}] Se reproduit !")
                try:
                    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    soc.connect(('localhost', 8080))
                    soc.send("PREDATOR".encode())
                    soc.close()
                except:
                    pass
        
        if energie < 40:
            with nb_prey.get_lock():
                if nb_prey.value > 0:
                    nb_prey.value -= 1 # Il mange une proie
                    energie += 50
                    print(f"[PREDATEUR {pid}] J'ai mangé une proie ! Energie: {energie}")
                else:
                    print(f"[PREDATEUR {pid}] Pas de proie en vue... je m'affame.")
    
    with nb_predator.get_lock():
        nb_predator.value -= 1
        print(f"[PREDATEUR {pid}] Mort d'épuisement.")
  
