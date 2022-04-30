from flask import Blueprint, request
import boto3
import json

bp = Blueprint('main', __name__, url_prefix='/')

# app.config.from_envvar('APP_CONFIG_FILE')

@bp.route('/elb', methods=['GET'])
def serverStatus():
    return "200"

# text generating route
# @bp.route('/generate', methods=['POST'])
# def text_generate():
#     if request.method == 'POST':