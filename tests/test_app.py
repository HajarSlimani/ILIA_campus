from io import BytesIO
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import prof
from app import app
from data import COURSES


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    COURSES.clear()
    with app.test_client() as test_client:
        yield test_client
    COURSES.clear()


@pytest.fixture()
def professor(client):
    client.post(
        "/login",
        data={"name": "Prof Test", "role": "professeur"},
    )
    return client


def create_course(client):
    response = client.post(
        "/courses/new",
        data={"title": "Python Flask", "semester": "S1"},
    )
    assert response.status_code == 302
    return COURSES[0]["id"]


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert client.get("/courses").status_code == 302


def test_login_stores_role_and_redirects_to_courses(client):
    response = client.post(
        "/login",
        data={"name": "Etudiant Test", "role": "étudiant"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Liste des cours" in response.get_data(as_text=True)
    with client.session_transaction() as session:
        assert session["name"] == "Etudiant Test"
        assert session["role"] == "étudiant"


def test_student_cannot_create_course(client):
    client.post(
        "/login",
        data={"name": "Etudiant Test", "role": "étudiant"},
    )

    response = client.post(
        "/courses/new",
        data={"title": "Cours interdit", "semester": "S1"},
    )

    assert response.status_code == 403
    assert "seuls les professeurs" in response.get_data(as_text=True)
    assert COURSES == []


def test_professor_must_enter_a_course_title(professor):
    response = professor.post(
        "/courses/new",
        data={"title": "   ", "semester": "S1"},
    )

    assert response.status_code == 200
    assert "Le titre est obligatoire" in response.get_data(as_text=True)
    assert COURSES == []


def test_professor_can_create_and_list_course(professor):
    course_id = create_course(professor)

    response = professor.get("/courses")

    assert response.status_code == 200
    assert "Python Flask" in response.get_data(as_text=True)
    assert str(course_id) in response.get_data(as_text=True)


def test_only_pdf_uploads_are_accepted(professor, tmp_path, monkeypatch):
    monkeypatch.setattr(prof, "__file__", str(tmp_path / "prof.py"))
    course_id = create_course(professor)

    invalid_response = professor.post(
        f"/courses/{course_id}/upload",
        data={"support": (BytesIO(b"plain text"), "notes.txt")},
        content_type="multipart/form-data",
    )
    assert invalid_response.status_code == 200
    assert "Seuls les fichiers PDF" in invalid_response.get_data(as_text=True)

    pdf_content = b"%PDF-test-content"
    valid_response = professor.post(
        f"/courses/{course_id}/upload",
        data={"support": (BytesIO(pdf_content), "cours.pdf")},
        content_type="multipart/form-data",
    )

    assert valid_response.status_code == 302
    assert (tmp_path / "uploads" / "cours.pdf").read_bytes() == pdf_content
    assert COURSES[0]["supports"] == ["cours.pdf"]


def test_logged_in_user_can_download_identical_support(
    professor, tmp_path, monkeypatch
):
    monkeypatch.setattr(prof, "__file__", str(tmp_path / "prof.py"))
    course_id = create_course(professor)
    pdf_content = b"%PDF-download-content"
    professor.post(
        f"/courses/{course_id}/upload",
        data={"support": (BytesIO(pdf_content), "support.pdf")},
        content_type="multipart/form-data",
    )

    professor.get("/logout")
    professor.post(
        "/login",
        data={"name": "Etudiant Test", "role": "étudiant"},
    )
    response = professor.get(f"/courses/{course_id}/download/support.pdf")

    assert response.status_code == 200
    assert response.data == pdf_content


def test_upload_over_five_megabytes_is_rejected(professor, tmp_path, monkeypatch):
    monkeypatch.setattr(prof, "__file__", str(tmp_path / "prof.py"))
    course_id = create_course(professor)
    oversized_file = b"x" * (5 * 1024 * 1024 + 1)

    response = professor.post(
        f"/courses/{course_id}/upload",
        data={"support": (BytesIO(oversized_file), "large.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert "5 Mo" in response.get_data(as_text=True)


def test_professor_can_upload_pdf(professor, tmp_path, monkeypatch):
    """Un professeur peut déposer un fichier PDF dans un cours."""
    monkeypatch.setattr(prof, "__file__", str(tmp_path / "prof.py"))
    course_id = create_course(professor)

    response = professor.post(
        f"/courses/{course_id}/upload",
        data={"support": (BytesIO(b"%PDF-valid-content"), "support.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert (tmp_path / "uploads" / "support.pdf").read_bytes() == b"%PDF-valid-content"
    assert COURSES[0]["supports"] == ["support.pdf"]
