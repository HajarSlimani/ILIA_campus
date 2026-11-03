import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from prof import prof_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "demo-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.register_blueprint(prof_bp)


@app.route("/", methods=["GET"])
def home():
    if "role" in session:
        return redirect(url_for("prof.courses"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "")
        if not name or role not in {"professeur", "étudiant"}:
            flash("Veuillez choisir un rôle et entrer votre nom.", "error")
            return render_template("login.html")

        session["name"] = name
        session["role"] = role
        flash("Connexion réussie.", "success")
        return redirect(url_for("prof.courses"))

    return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("login"))


@app.errorhandler(413)
def request_entity_too_large(error):
    del error
    flash("Le fichier dépasse la taille maximale de 5 Mo.", "error")
    return render_template("message.html", title="Fichier trop volumineux"), 413


if __name__ == "__main__":
    app.run(debug=True)