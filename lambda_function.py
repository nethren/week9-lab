from apig_wsgi import make_lambda_handler

from app import app

lambda_handler = make_lambda_handler(app)
