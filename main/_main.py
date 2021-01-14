from flask import Flask, render_template, request, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xf18\x16\xd5\xe4\xae\xab\xb9\xe4\xa3\x19\xc9!\x86\xffk\x82vp\x15\xb8#\x8boo`\x0c\xa7\x1e\x98U\xc51\xcf\x8d\xae'
app.config['ENV'] = 'production'


# =============== < BLUEPRINTS > =============== # 

from .projects.scraper_image import scrap_proj
app.register_blueprint(scrap_proj)


@app.route('/')
def index():
    return render_template('index.html')




