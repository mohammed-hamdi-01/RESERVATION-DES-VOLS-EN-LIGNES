# Les importations necessaires

from fileinput import close
from platform import release
import socket, threading


# Mutex pour assurer l'exlusion mutuelle
bank_mutex=threading.Lock()

#Liste des actions autorisée par le serveur pour le client
actions_autorisees=[]
actions_autorisees.append("ConsulterVols")
actions_autorisees.append("ConsulterHistoriqueTransaction")
actions_autorisees.append("ConsulterFacture")
actions_autorisees.append("demande")
actions_autorisees.append("Annulation")
current_threads=[]
msgsize=1024
facture="factures.txt"
vol="vols.txt" #vols.txt
hist="histo.txt"


# Gestion des clients a travers les threads
class threadClients(threading.Thread):

    # Recuperer l'adresse et la socket du client connecté
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("nouvelle connexion est ajoutée: ", clientAddress)

    # Recuperer l'action autorisé pour le client connecté afin de l'excéuter
    def run(self):
        print ("connexion d'aprés : ", clientAddress)
        self.csocket.send(bytes("hello",'utf-8'))
        rsp = ''
        while True:
            try:
                data = self.csocket.recv(3072)          
            except socket.error as e:
                print("socket disconnectee !")
                break
            rsp = data.decode()
            if rsp!="Salut":
                print("communication d'aprés client necéssite une action:",rsp.split(",")[0])
                keyword=rsp.split(",")[0]
                if keyword in actions_autorisees:
                    NotificationServeur(clientAddress,rsp,self.csocket)
                elif rsp=='exit':
                    break
                else:
                    msg=" n'est pas reconnu comme une action !"
                    self.csocket.send(bytes(msg,'UTF-8'))

        print("client dont l'adresse est : ", clientAddress , " est deconnete ..")   
# fin de la classe



# Notifier a chaque fois le serveur de l'action effectuer par le(s) client(s) afin
# de poursuivre le process fait par chaque client

def NotificationServeur(ip,message,csock):
    elements=message.split(",")
    if elements[0] == "ConsulterVols":
        msg=Consulter_vols()

        csock.send(bytes(msg,'UTF-8'))
    if elements[0] == "ConsulterHistoriqueTransaction":
        msg=Consulter_Transaction_Vols()

        csock.send(bytes(msg,'UTF-8'))
    if elements[0] =="ConsulterFacture":
        msg=Consulter_Facture_agence(elements[1])
        csock.send(bytes(msg,'UTF-8'))  
    if elements[0] == "demande":
        bank_mutex.acquire()
        if(demande(int(elements[1]),int(elements[2]),int(elements[3]))):
            
            msg="demande avec succes !"
            csock.send(bytes(msg,'UTF-8'))
        else:
            msg="reference invalide , verifiez !"
            csock.send(bytes(msg,'UTF-8'))
        bank_mutex.release()
    if elements[0] == "Annulation":
        bank_mutex.acquire()
        if(annulation(int(elements[1]),int(elements[2]),int(elements[3]))):
            msg=" Annulation avec succes !"
            csock.send(bytes(msg,'UTF-8'))
        else:
            msg="Annulation echoue !!"
            csock.send(bytes(msg,'UTF-8'))          
        bank_mutex.release()


# Consulter les Details concernant tous les vols  

def Consulter_vols():
    msg=""
    vols =open("vols.txt",'r') 
    ligne_vol = vols.readlines()
    for i in ligne_vol:
        columns=i.split(',')
        vols.close()
        msg+="Ref : {},   Destination : {},   Nombre Places : {},   Prix Place : {}.".format(columns[0],columns[1],columns[2],columns[3])
    if msg == "" :
        return "n'y a pas!"

    return  msg
    


# Consulter les Details concernant un vol spécifique 

def Consulter_vol(ref):
    vols =open("vols.txt",'r') 
    ligne_vol = vols.readlines()
    for i in ligne_vol:
        columns=i.split(',')
        if int(columns[0])==int(ref):
            vols.close()
            msg="les informations de cet vol est : Destination : {}, Nombre Places : {}, Prix Place : {}.".format(columns[1],columns[2],columns[3])
            return  msg
    return "Vol n'existe pas!"

# Suivre tous les transactions

def Consulter_Transaction_Vols():
    response=""
    histo =open("histo.txt",'r') 
    hs_list_of_lines = histo.readlines()
    for i in hs_list_of_lines:
        columns=i.split(',')
        response+="Ref : {},     Agence : {},   Transaction : {},   Valeur : {},   Résultat: {}\n".format(columns[0],columns[1],columns[2],columns[3],columns[4])
    histo.close()
    if response=="":
        response="Pas de transactions"
    return response

# Suivre les transactions d'une reference bien précise 

def Consulter_Transaction_Vol(ref):
    response=""
    histo =open("histo.txt",'r') 
    hs_list_of_lines = histo.readlines()
    for i in hs_list_of_lines:
        columns=i.split(',')
        if int(columns[0])==int(ref):
            response+="Transaction:\nAgence:{}   Transaction:{}   Valeur:{}   Résultat:{}\n".format(columns[1],columns[2],columns[3],columns[4])
    histo.close()
    if response=="":
        response="Pas de transactions faite avec cette reference"
    return response


# Parcourir le fichier Factures pour extraire le montant a payer pour une agence spécifique

def Consulter_Facture_agence(refag):
    facture =open("factures.txt",'r') 
    fs_list_of_lines = facture.readlines()
    for i in fs_list_of_lines:
        columns=i.split(',')
        if int(columns[0])==int(refag):
            return "la facture a payer est :"+columns[1]
    return "agence n'existe pas !"


# Verification de l'existance du Vol au niveau du fichier Vols

def Verification_Vol_Existence(refvol):
    vols=open("vols.txt","r")
    ligne_vols = vols.readlines()
    
    for i in ligne_vols:
        columns=i.split(',')
        if int(columns[0])==refvol:
            return True
    return False

#nombre de places d'une vol spécifique

def Consulter_Nbr_Plc_vol(ref):
    vols =open("vols.txt",'r') 
    ligne_vol = vols.readlines()
    for i in ligne_vol:
        columns=i.split(',')
        if int(columns[0])==int(ref):
            vols.close()
            return  columns[2]
    return "Vol n'existe pas!"

#Prix d'une vol spécifique
 
def Consulter_Prix_vol(ref):
    vols =open("vols.txt",'r') 
    ligne_vol = vols.readlines()
    for i in ligne_vol:
        columns=i.split(',')
        if int(columns[0])==int(ref):
            vols.close()
            return  int(columns[3])
    return "Vol n'existe pas!"

# Mise à jours du factures aprés demande ou annulation d'argent

def Maj_Factures():
    histo=open(hist,"r")
    factures = open(facture,"w")
    montantFacturee1=0
    montantFacturee2=0
    ligne_histo = histo.readlines()
    for i in range(len(ligne_histo)):
        columns=ligne_histo[i].split(',')
        p=Consulter_Prix_vol(columns[0])
        if int(columns[1])==1:
            if(columns[2]=="Annulation"):
                montantFacturee1-=p*columns[3]
                montantFacturee1+=p*columns[3]*0.1
            else :
                montantFacturee1+=p*columns[3]
        if int(columns[1])==2:
            if(columns[2]=="Annulation"):
                montantFacturee2-=p*columns[3]
                montantFacturee2+=p*columns[3]*0.1
            else :
                montantFacturee2+=p*columns[3]
    histo.close()
    factures.write("\n1,{}".format(montantFacturee1))
    factures.write("\n2,{}".format(montantFacturee2))
    factures.close()
    return True
    


            
# annulation de vol dans l'histo 

def annulation(ref,agence,nbplace):
    if Verification_Vol_Existence(ref)==False:
        print("vol n'existe pas !")
    histos = open(hist,"r")
    ligne_histo = histos.readlines()
    nb_demandé=0
    for i in ligne_histo:
        columns=i.split(',')
        if int(columns[0])==int(ref) and int(agence)==int(columns[1]) and (columns[2]=="Demande") and columns[4]=="succès" :
            nb_demandé+=columns[3]
        elif int(columns[0])==int(ref) and int(agence)==int(columns[1]) and (columns[2]=="Annulation") and columns[4]=="succès" :
            nb_demandé-=columns[3]
    histos.close()
    histo=open(hist,"a")
    if nbplace>nb_demandé :
        histo.write("\n{},{},annulaton,{},impossible".format(ref,agence,nbplace))
        histo.close()
        Maj_Factures()
        return False
    else:
        histo.write("\n{},{},annulation,{},succes".format(ref,agence,nbplace))
        histo.close()
        Maj_Factures()
        return True

# demande de vol dans l'histo 
def demande(ref,Agence,nbPlace):
    if Verification_Vol_Existence(ref)==False:
        return "vol n'existe pas !"
    success=False
    vols = open(vol,"r")
    ligne_vol = vols.readlines()
    for i in ligne_vol:
        columns=i.split(',')
        if int(columns[0])==int(ref):
            if columns[2]>=nbPlace :
                success=True
                vols.close()
                break
    histo=open(hist,"a")
    if success:
        histo.write("\n{},{},demande,{},succès".format(ref,Agence,nbPlace))
        histo.close()
        Maj_Factures()
        return success
    else:
        histo.write("\n{},{},demande,{},impossible".format(ref,Agence,nbPlace))
        histo.close()
        Maj_Factures()
        return success



        


             
LOCALHOST = "127.0.0.1"
PORT = 8084
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))

print("Serveur disponible")
print("En attente pour les requtes des clients..")
while True:
    # Boucle principale
    server.listen(1)
    clientsock, clientAddress = server.accept()
    # retourner le couple (socket,addresse)
    newthread = threadClients(clientAddress, clientsock)
    newthread.start()
    current_threads.append(newthread)

