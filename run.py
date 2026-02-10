
from flask import Flask
from app.routes import bp
app=Flask(__name__)
app.secret_key="dev"
app.register_blueprint(bp)
app.run(host="0.0.0.0",port=5000)
