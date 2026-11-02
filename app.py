from flask import Flask
from prof import prof_bp

app = Flask(__name__)
app.register_blueprint(prof_bp)

if __name__ == "__main__":
    app.run(debug=True)