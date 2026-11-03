import os
from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename
from data import COURSES

prof_bp = Blueprint("prof", __name__)


def logged_in(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "role" not in session:
            flash("Veuillez vous connecter pour accéder à cette page.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def professor_only(view):
    @wraps(view)
    @logged_in
    def wrapped_view(*args, **kwargs):
        if session["role"] != "professeur":
            return "Accès refusé : seuls les professeurs peuvent effectuer cette action.", 403
        return view(*args, **kwargs)

    return wrapped_view


def find_course(course_id):
    return next((course for course in COURSES if course["id"] == course_id), None)


@prof_bp.route("/courses", methods=["GET"])
@logged_in
def courses():
    return render_template("courses.html", courses=COURSES)


@prof_bp.route("/courses/new", methods=["GET", "POST"])
@professor_only
def new_course():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        semester = request.form.get("semester", "").strip()
        if not title:
            flash("Le titre est obligatoire", "error")
            return render_template("new_course.html")

        COURSES.append({
            "id": max((course["id"] for course in COURSES), default=0) + 1,
            "title": title,
            "semester": semester,
            "supports": [],
        })
        flash("Cours créé.", "success")
        return redirect(url_for("prof.courses"))

    return render_template("new_course.html")


@prof_bp.route("/courses/<int:course_id>", methods=["GET"])
@logged_in
def course_detail(course_id):
    course = find_course(course_id)
    if course is None:
        abort(404)
    return render_template("course_detail.html", course=course)


@prof_bp.route("/courses/<int:course_id>/upload", methods=["GET", "POST"])
@professor_only
def upload_support(course_id):
    course = find_course(course_id)
    if course is None:
        abort(404)

    if request.method == "POST":
        support = request.files.get("support")
        if support is None or not support.filename:
            flash("Veuillez sélectionner un fichier PDF.", "error")
            return render_template("upload.html", course=course)
        if not support.filename.lower().endswith(".pdf"):
            flash("Seuls les fichiers PDF sont autorisés.", "error")
            return render_template("upload.html", course=course)

        filename = secure_filename(support.filename)
        if not filename:
            flash("Le nom du fichier est invalide.", "error")
            return render_template("upload.html", course=course)

        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        support.save(os.path.join(upload_dir, filename))
        if "supports" not in course:
            course["supports"] = []
        if filename not in course["supports"]:
            course["supports"].append(filename)
        flash("Support ajouté.", "success")
        return redirect(url_for("prof.course_detail", course_id=course_id))

    return render_template("upload.html", course=course)


@prof_bp.route("/courses/<int:course_id>/download/<path:filename>", methods=["GET"])
@logged_in
def download_support(course_id, filename):
    course = find_course(course_id)
    if course is None or filename not in course.get("supports", []):
        abort(404)

    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    return send_from_directory(upload_dir, filename, as_attachment=True)