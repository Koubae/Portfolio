from flask import Flask, render_template, request, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = b''
app.config['ENV'] = 'production'


# =============== < BLUEPRINTS > =============== # 

from .projects.scraper_image import scrap_proj
app.register_blueprint(scrap_proj)


@app.route('/')
def index():
    return render_template('index.html')




