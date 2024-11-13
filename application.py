# Note we imported request!
from flask import Flask, render_template, request, g, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
import sqlite3

app = Flask(__name__)
# Configurer une clé secrete
# Il y a une meilleure manière de le faire sans la mettre dans le code
app.config['SECRET_KEY'] ="Clé difficile à deviner"
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_SECRET_KEY'] = 'WTF'
#Fonctions de gestion de la bdd
def connecter_bdd():
    conn = sqlite3.connect('base_jouets.db')
    conn.row_factory = sqlite3.Row
    return conn

def obtenir_bdd():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connecter_bdd()
    return g.sqlite_db

@app.teardown_appcontext
def fermer_bdd(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Maintenant, nous allons créer une classe WTForm
# Beaucoup de champs sont disponibles sur:
# http://wtforms.readthedocs.io/en/stable/fields.html
class CategorieForm(FlaskForm):
    '''
    Cette classe générale reçoit beaucoup de formulaires
    à propos des catégories de jouets
    On va créer trois champs WTForms.
    '''
    nom_cat = StringField('Nom Catégorie:            ', validators=[
        DataRequired(message="Ce champ est obligatoire"),
        Length(min=3, max=50, message="La longueur doit être entre 3 et 50 caractères")
    ])
    desc_cat = TextAreaField("Description Catégorie: ")
    envoyer = SubmitField('Envoyer')


#On spécifie dans la route les méthodes acceptées par HTTP: POST et GET
#Si les méthodes ne sont pas ajoutées, c'est GET par défaut
@app.route('/', methods=['GET', 'POST'])
def index():
    # Mettre nom_cat et desc_cat comme flag, 
    # on les utilisera dans les tests. Au début, elles sont inconnues
    nom_cat = None
    desc_cat = None
    
    bdd = obtenir_bdd()    
    curseur = bdd.execute("""SELECT nom, description FROM
                           categories""")
    ttes_categ = curseur.fetchall()
    
    # On crée une instance de formulaire.
    form = CategorieForm()
    # Si le formulaire est valide et les données des champs sont acceptées
    # à la soumission, validate_on_submit() renvoie True, 
    # sinon, elle renvoie 
    if form.validate_on_submit():
        # Récupérer les données sur la catégorie
        nom_cat = form.nom_cat.data
        desc_cat = form.desc_cat.data
        #insertion dans la bdd
        
        bdd.execute("""INSERT INTO categories(nom, description) VALUES
                    (?, ?)""", (nom_cat, desc_cat))
        bdd.commit()
        # Rénitialiser les champs du formulaire
        form.nom_cat.data = ''
        form.desc_cat.data = ''
        redirect(url_for('index'))
    return render_template('index.html', form=form, nom_cat=nom_cat,
                           desc_cat=desc_cat, ttes_categ=ttes_categ)
    

@app.route('/categorie/<id_cat>', methods=['GET', 'POST'])
def supprimer_categ(id_cat):
    bdd = obtenir_bdd()
    
    curseur = bdd.execute("""
    SELECT id, nom, description FROM categories WHERE id= ? ;""", (id_cat,))

    categ = curseur.fetchone()

    #print(categ[0]) # Appel par l'index
    #print(type(categ)) # Regardons le type
    #print(categ["description"]) # Regardons la catégorie 

    #return f"La catégorie est {categ["nom"]}."

    if categ: # si catégorie existant
        # Exécution de la requête de suppression
        bdd.execute("DELETE FROM categories WHERE id=?", 
        (categ["id"],))

        bdd.commit() # Pour les requêtes INSERT, UPDATE et DELETE.

        return "<h1>Catégorie N°"+ str(categ["id"]) +" a été supprimée </h1>"

    else :
        return "<h1>La catégorie demandée est introuvable</h1>"

if __name__ == '__main__':
    app.run(debug=True)
