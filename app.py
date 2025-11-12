import os
from dotenv import load_dotenv
from flask import Flask,   render_template,  request, redirect, send_from_directory, url_for
from grpc import Status
from openai import OpenAI

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER





documents=[]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/file")    
def file():
    return render_template("file.html", documents=documents)


@app.route("/apropos")    
def apropos():
    return render_template("apropos.html")

@app.route("/contact")    
def contact():
    return render_template("contact.html")

@app.route("/auth")
def auth():
    return render_template("auth.html")
@app.route("/telecharger", methods=["POST"])
def telecharger():
    if "document" not in request.files:
        return "Aucun fichier sélectionné"
    
    file = request.files["document"]
    if file.filename == "":
        return "Nom de fichier vide"
    
    # sauvegarder le fichier dans UPLOAD_FOLDER
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    documents.append(file.filename)
    return redirect(url_for('file'))
    

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory("statique/uploads", filename)

# Charger les variables d'environnement
load_dotenv()




# Initialiser le client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/bloc", methods=["GET", "POST"])
def bloc():
    # 1. Récupérer les fichiers uploadés
    docs = os.listdir(app.config['UPLOAD_FOLDER'])

    # 2. Envoyer à l’IA pour regroupement
    prompt = """
    Analysez ces fichiers et identifiez des groupes logiques basés sur leur contenu, nom, type et contexte d'usage.
    Créez des "intentions" qui regroupent les fichiers similaires ou liés.

    Retournez un JSON avec cette structure:
{
  "intentions": [
    {
      "title": "Titre suggéré pour le groupe",
      "description": "Description de ce que contient ce groupe",
      "confidence": 0.85,
      "fileIndices": [0, 2, 5],
      "reasoning": "Pourquoi ces fichiers vont ensemble",
      "suggestedColor": "#4F8EF7",
      "keywords": ["mot-clé1", "mot-clé2"]
    }
  ]
}

"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0 , 
    )

    # 3. Extraire la réponse de l’IA
    result = response.choices[0].message.content.strip() or '{"intentions": []}'
     # ⚠️ Ici l’IA renvoie du JSON (un dictionnaire)
    import json
    try:
        groupe_fichier = json.loads(result)   
    except:
        groupe_fichier = {"Erreur": docs}  # Si jamais ça plante, on affiche tout brut

    # 4. Envoyer à bloc.html
    return render_template("bloc.html", groupe_fichier=groupe_fichier)
@app.route("/files")
def liste_fichiers():
    query = request.args.get("q", "").lower()
    docs = os.listdir(app.config['UPLOAD_FOLDER'])

    if query:
        docs = [f for f in docs if query in f.lower()]

    return render_template("file.html", fichiers=docs)
@app.route("/bloc/dtail")
def lister_fifhier_bloc():
    # Exemple de blocs organisés
    groupe_fichier = {
        "Documents": ["fichier1.pdf", "fichier2.pdf"],
        "Musique": ["fichier3.mp3"],
    }

    return render_template("bloc.html", groupe_fichier=groupe_fichier)

if __name__ == "__main__":
    app.run(debug=True)