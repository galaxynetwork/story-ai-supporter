from flask import Blueprint, request, jsonify
import boto3
import json

bp = Blueprint('main', __name__, url_prefix='/')

# Amazon SageMaker Runtime Client
session = boto3.Session()
sagemaker_runtime = session.client('sagemaker-runtime')

# Sagemaker endpoint name.
endpoint_name = 'sm-endpoint-gpt-j-6b'


@bp.route('/elb', methods=['GET'])
def serverStatus():
    return "200"


@bp.route('/gen-text', methods=['POST'])
def text_generate():
    response_body = {
        'status': [],
        'data': None
    }

    if request.method == 'POST':
        user_text = request.json['text']
        payload = {
            "inputs": user_text,
            "parameters": {
                "max_length": 64,
                "temperature": 0.9,
                "top_k": 50,
                "top_p": 0.95,
                "num_return_sequence": 2,
            }
        }

        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(payload)
        )

        result = json.loads(response['Body'].read().decode())

        text = result[0]['generated_text']
        response_body['status'] = 200
        response_body['data'] = text

        return jsonify(response_body), 200
    else:
        response_body['status'] = 405
        response_body['data'] = "GET Method Not Allowed. Please Try POST Method."

        return jsonify(response_body), 405