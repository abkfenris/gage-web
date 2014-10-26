from flask import Blueprint, render_template
from datetime import datetime

main = Blueprint('main', __name__)

from . import views, errors

#@main.route('/')
#@main.route('/index')
#def index():
#	user = {'nickname':datetime.now()} # fake user
#	return render_template('index.tmp.html',
#						   title='Home',
#						   user = user)