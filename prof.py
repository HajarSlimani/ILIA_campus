import os
from flask import Blueprint, request, redirect, render_template_string
from werkzeug.utils import secure_filename
from data import COURSES

prof_bp = Blueprint("prof", __name__)

FORM = """
<h2>Nouveau cours</h2>
<form method="post" enctype="multipart/form-data">
  <input name="title" placeholder="Intitulé"><br>
  <input name="semester" placeholder="Semestre"><br>
  <input type="file" name="support" accept=".pdf"><br>
  <button>Créer</button>
</form>
"""

@prof_bp.route("/prof/courses/new", methods=["GET", "POST"])
def new_course():
    if request.method == "POST":
        f = request.files["support"]
        filename = secure_filename(f.filename)
        os.makedirs("uploads", exist_ok=True)
        f.save(os.path.join("uploads", filename))
        COURSES.append({
            "id": len(COURSES) + 1,
            "title": request.form["title"],
            "semester": request.form["semester"],
            "file": filename,
        })
        return "Cours créé"
    return render_template_string(FORM)