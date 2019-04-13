from flask import Flask,url_for,request,redirect,render_template,flash,session
import matplotlib.pyplot as plt
import json
import os
from hashlib import sha1
import crypt
from werkzeug.utils import secure_filename
from time import sleep

app = Flask(__name__)
app.secret_key= "Key"

app.config['UPLOAD_FOLDER'] = "C:/Users/Astremy/Desktop/Projet/images"
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg'])

def donnees(recherche,recherche2="",recherche3=""):
	crypt.crypter("bdd.json", sha1(app.secret_key.encode()).hexdigest(), False)
	try:
		load = open("bdd.json","r")
		bdd = json.loads(load.read())
		load.close()
	except:
		return False
	crypt.crypter("bdd.json", sha1(app.secret_key.encode()).hexdigest(), True)
	if recherche2 == "": result = bdd[recherche]
	elif recherche3 == "": result = bdd[recherche][recherche2]
	else: result = bdd[recherche][recherche2][recherche3]
	try: result.reverse()
	except: pass
	return result

def entree(value,endroit,endroit2="",endroit3=""):
	crypt.crypter("bdd.json", sha1(app.secret_key.encode()).hexdigest(), False)
	try:
		load = open("bdd.json","r")
		bdd = json.loads(load.read())
		load.close()
	except:
		return False
	if endroit2 == "": bdd[endroit] = value
	elif endroit3 == "": bdd[endroit][endroit2] = value
	else: bdd[endroit][endroit2][endroit3] = value
	load = open("bdd.json","w")
	load.write(json.dumps(bdd,indent=4))
	load.close()
	crypt.crypter("bdd.json", sha1(app.secret_key.encode()).hexdigest(), True)

def recherche(perso):
	retour = []
	for i in donnees("locations"):
		if i["owner"] == perso: retour.append(i)
	try: retour.reverse()
	except: pass
	return retour

def saveimages(file):
	images = []
	names = []
	load = open("images/photos.json","r")
	donnees = json.loads(load.read())
	load.close()
	for i in range(len(file)):
		if file and allowed_file(file[i].filename):
			filename = secure_filename(file[i].filename)
			names.append(filename)
			file[i].save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			images.append(len(donnees)+i)
	print(names)
	load = open("images/images.json","w")
	load.write(json.dumps(names,indent=4))
	load.close()
	sleep(5)
	return images

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/create",methods=["POST","GET"])
def creerpage():
	if not "pseudo" in session:
		return redirect(url_for("index"))
	if request.method == "GET":
		return render_template("creerpage.html")
	elif request.method == "POST":
		nya = donnees("locations")
		nya.reverse()
		length = len(nya)
		valeur = {"title":request.form["titre"],"text":request.form["texte"],"owner":session["pseudo"],"nb":length}
		if "file" in request.files:
			valeur["images"] = saveimages(request.files.getlist("file"))
		nya.append(valeur)
		entree(nya,"locations")
		return redirect("/locations/" + str(length))

@app.route("/")
def index():
	return render_template("index.html",co="pseudo" in session)

@app.route("/login",methods=["POST","GET"])
def co():
	if request.method == "GET":
		return redirect(url_for("index"))
	elif request.method == "POST":
		if (request.form["pseudo"] in donnees("compte") and donnees("compte",request.form["pseudo"]) == sha1(request.form["mdp"].encode()).hexdigest()):
			session["pseudo"] = request.form["pseudo"]
			return redirect(url_for("profile"))
		else:
			return redirect(url_for("index"))

@app.route("/locations")
def alouer():
	return render_template("locations.html",bdd=donnees("locations"))

@app.route("/locations/<num>")
def pagelouer(num):
	try:
		offre = donnees("locations",int(num))
	except:
		offre = {"title":"Page non trouvée","text":"La page n'existe pas"}
	images = []
	if "images" in offre:
		load = open("images/photos.json","r")
		nya = json.loads(load.read())
		load.close()
		for i in offre["images"]:
			try: images.append(nya[i])
			except: pass
	return render_template("pagelouer.html",offre=offre,images=images)

@app.route("/profile/<perso>")
def persopage(perso):
	offre = recherche(perso)
	if perso in donnees("compte"): return render_template("offreperso.html",perso=offre,taille=len(offre),name=perso)
	else: return render_template("pagelouer.html",offre={"title":"Personne non trouvé","text":"La personne cherchée n'existe pas."})

@app.route("/profile")
def profile():
	if not "pseudo" in session:
		return redirect(url_for("index"))
	try:
		offres = recherche(session["pseudo"])
		return render_template("profile.html",name=session["pseudo"],propositions=offres,taille=len(offres))
	except:
		return render_template("profile.html",name=session["pseudo"],propositions=False)

@app.route("/inscription",methods=["POST","GET"])
def inscrire():
	if request.method == "GET":
		return render_template("inscription.html",notif=False)
	elif request.method == "POST":
		if not (request.form["pseudo"] in donnees("compte")):
			modif = donnees("compte")
			modif[request.form["pseudo"]] = sha1(request.form["mot_de_passe"].encode()).hexdigest()
			entree(modif,"compte")
			session["pseudo"] = request.form["pseudo"]
			return redirect(url_for("profile"))
		else:
			return render_template("inscription.html",notif=True)

@app.route("/deco")
def deco():
	session.pop("pseudo", None)
	return redirect(url_for("index"))

@app.route("/modif/<num>",methods=["POST","GET"])
def modifier(num):
	if not "pseudo" in session:
		return redirect(url_for("index"))
	else:
		if request.method == "GET":
			nya = donnees("locations",int(num))
			if nya["owner"] == session["pseudo"]: return render_template("modif.html",valeur=nya)
			else: return "Vous n'avez pas accès a cette page !"
		elif request.method == "POST":
			modify = donnees("locations",int(num))
			if modify["owner"] == session["pseudo"]:
				if "file" in request.files:
					modify["images"] = saveimages(request.files.getlist("file"))
				modify["title"] = request.form["titre"]
				modify["text"] = request.form["texte"]
				entree(modify,"locations",int(num))
				return redirect("/locations/" + num)
			else: return "Vous n'avez pas accès a cette page !"

@app.errorhandler(404)
def page_not_found(e):
    return "<h1 style='color:red;margin-top:100px;text-align:center;'>La page n'a pas été trouvée !</h1>"

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=80)
