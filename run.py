#!flask/bin/python
from app import create_app
import config

app = create_app(config.Config)

app.run(debug=True)