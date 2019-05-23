from datetime import datetime
from flask import Flask,url_for,request,redirect,render_template,session
from time import sleep
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import requests
import bcrypt
import os
import zipfile
import shutil

app = Flask(__name__)
app.secret_key= "<Key>"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def lance(message):
    print(message)
    app.run(debug=True, host="0.0.0.0", port=80)
    exit()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}', '{self.title}')"

class Message(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text,nullable=False)
    to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Message('{self.id}', [ De: '{self.by}', Vers: '{self.to}' ])"

def implemente(user):
    db.session.add(user)
    db.session.commit()

@app.route("/")
def index():
    return render_template("index.html",co="pseudo" in session)

@app.route("/test/<name>")
def setname(name):
    session["pseudo"] = name
    return redirect("/")

@app.route("/message/<id_perso>",methods=["POST","GET"])
def sendmess(id_perso):
    if not "pseudo" in session:
        return redirect(url_for("index"))
    personne = User.query.filter_by(id=id_perso).first()
    me = User.query.filter_by(username=session["pseudo"]).first().id
    if me == personne.id:
        return redirect("/profile")
    if personne:
        if request.method == "GET":
            conv = []
            for i in Message.query.filter(or_((Message.by == me and Message.to == int(id_perso)),(Message.to == me and Message.by == int(id_perso)))):
                conv.append([User.query.filter_by(id=i.by).first().username,i])
            return render_template("sendmess.html",perso=personne,conv=conv[-10:])
        elif request.method == "POST":
            message = Message(content=request.form["contenu"],by=me,to=personne.id)
            implemente(message)
            return redirect("/message/" + id_perso)
    else:
        return redirect("/")

@app.route("/create",methods=["POST","GET"])
def creerpage():
    if not "pseudo" in session:
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("creerpage.html")
    elif request.method == "POST":
        perso_id = User.query.filter_by(username=session["pseudo"]).first().id
        post = Post(title=request.form["titre"],content=request.form["texte"],user_id=perso_id)
        implemente(post)
        return redirect("/locations")

@app.route("/login",methods=["POST","GET"])
def co():
    if request.method == "GET":
        return redirect(url_for("index"))
    elif request.method == "POST":
        if (User.query.filter_by(username=request.form["pseudo"]).first() and bcrypt.checkpw(bytes(request.form["mdp"],"utf-8"),User.query.filter_by(username=request.form["pseudo"]).first().password)):
            session["pseudo"] = request.form["pseudo"]
            return redirect(url_for("profile"))
        else:
            return redirect(url_for("index"))

@app.route("/locations")
def alouer():
    return render_template("locations.html",bdd=Post.query.all())

@app.route("/locations/<num>")
def pagelouer(num):
    offre = Post.query.filter_by(id=int(num)).first()
    if not offre: return render_template("error.html")
    return render_template("pagelouer.html",offre=offre,co="pseudo" in session,num=num)

@app.route("/reserver/<nb>")
def reserver(nb):
    personne = User.query.filter_by(id=nb).first()
    return render_template("payelouer.html",perso = personne)

@app.route("/profile/<perso>")
def persopage(perso):
    nya = User.query.filter_by(username=perso).first()
    if nya:
        offre = Post.query.filter_by(user_id=nya.id).all()
        return render_template("offreperso.html",perso=offre,taille=len(offre),name=perso)
    else: return render_template("error.html")

@app.route("/profile")
def profile():
    if not "pseudo" in session:
        return redirect(url_for("index"))
    conv = []
    me = User.query.filter_by(username=session["pseudo"]).first().id
    for i in Message.query.filter(or_(Message.by == me,Message.to == me)):
        if i.by == me:
            corresp = i.to
        else:
            corresp = i.by
        corresp = User.query.filter_by(id=corresp).first()
        if not corresp in conv:
            conv.append(corresp)
    try:
        offres = User.query.filter_by(username=session["pseudo"]).first().posts
        return render_template("profile.html",name=session["pseudo"],propositions=offres,taille=len(offres),conv=conv)
    except:
        return render_template("profile.html",name=session["pseudo"],propositions=False,conv=conv)

@app.route("/inscription",methods=["POST","GET"])
def inscrire():
    if request.method == "GET":
        return render_template("inscription.html",notif=False)
    elif request.method == "POST":
        if not User.query.filter_by(username=request.form["pseudo"]).first():
            user = User(username=request.form["pseudo"],password=bcrypt.hashpw(bytes(request.form["mot_de_passe"],"utf-8"),bcrypt.gensalt()),email=request.form["mail"])
            implemente(user)
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
        nya = Post.query.filter_by(id=int(num)).first()
        if nya.author.username == session["pseudo"]:
            if request.method == "GET":
                return render_template("modif.html",valeur=nya)
            elif request.method == "POST":
                nya.title = request.form["titre"]
                nya.content = request.form["texte"]
                db.session.commit()
                return redirect("/locations/" + num)
        else: return render_template("error.html")

@app.errorhandler(404)
def page_not_found(e):
    return "<h1 style='color:red;margin-top:100px;text-align:center;'>La page n'a pas été trouvée !</h1>"

if __name__ == "__main__":
    print("Recherche de mise-à-jour...")
    try:
        cherche_version = open("version.info","r")
        version = cherche_version.read()
        cherche_version.close()
    except: lance("Pas de fichiers de version")
    try : r = requests.get("https://raw.githubusercontent.com/Astremy/Guade-Loue/master/version.info")
    except: lance("Aucune connexion")
    if version == r.text: lance("Aucune mise-à-jour")
    else:
        print("Mise-à-jour détectée !")
        print("Téléchargement...")
        try: dl = requests.get("https://github.com/Astremy/Guade-Loue/archive/master.zip")
        except: lance("Aucune connexion")
        for i in os.listdir():
            try: os.remove(i)
            except: shutil.rmtree(i)
        fichier = open("Guade-Loue.zip","wb")
        fichier.write(dl.content)
        fichier.close()
        print("Archive téléchargée, installation..")
        archive = zipfile.ZipFile('Guade-Loue.zip')
        for i in archive.namelist()[1:]:
            archive.extract(i,name=i[len(archive.namelist()[0]):])
        archive.close()
        os.remove("Guade-Loue.zip")
        print("Téléchargement terminé !")
        print("Lancement..")
        os.system("python site.py")
