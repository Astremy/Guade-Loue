from string import printable
from hashlib import sha1

def crypter(fichier, password, maniere):
	if password == "":
		return "Mot de passe inexistant !"
	try:
		load = open(fichier,"r")
		save = load.read()
		load.close()
	except: return "Le fichier n'existe pas !"
	load = open(fichier,"w")
	try:
		sha = sha1(password.encode()).hexdigest()
		if maniere:
			if sha[0].isdigit(): load.write(cryptage(message=save,cle=password,crypt=maniere) + sha)
			else: load.write(sha + cryptage(message=save,cle=password,crypt=maniere))
		else:
			if sha[0].isdigit():
				if save[-40:] == sha: load.write(cryptage(message=save[:-40],cle=password,crypt=maniere))
				else:
					load.write(save)
					return "Mauvais mot de passe !"
			elif save[:40] == sha: load.write(cryptage(message=save[40:],cle=password,crypt=maniere))
			else:
				load.write(save)
				return "Mauvais mot de passe !"
	except:
		load.write(save)
		return "Erreur"
	return "L'opération s'est déroulée avec succès !"

def cryptage(message, cle, crypt):
	dico = {}
	dicofin = {}
	dicocrypt = []
	mess = []
	fin = []
	principal = printable[10:36]+"\n"+printable[:10]+printable[62:-5]+printable[36:62]
	for i,k in enumerate(principal):
		dico[k] = i
		dicofin[i] = k
	if (type(cle)==str):
		for i in cle: dicocrypt.append(dico[i])
	else: dicocrypt.append(cle)
	for i in message:
		if i in dico: mess.append(dico[i])
		else: mess.append(i)
	for i,j in enumerate(mess):
		nya = dicocrypt[i%len(dicocrypt)]
		if type(j) is int:
			if (crypt): fin.append(dicofin[(j+nya)%len(principal)])
			else: fin.append(dicofin[(j-nya)%len(principal)])
		else: fin.append(j)
	return ''.join(fin)

if __name__ == "__main__":
	print("Nya")