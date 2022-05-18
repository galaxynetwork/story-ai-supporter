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
        'data': ""
    }

    if request.method == 'POST':
        user_text = request.json['text']
        max_lenth = len(user_text) + 100
        tempr_param = float(request.json['datas']['randomness'])
        top_k_param = int(request.json['datas']['fluency'])

        payload = {
            'inputs': user_text,
            'parameters': {
                'max_length': max_lenth,
                'do_sample': True,
                'no_repeat_ngram_size': 2,
                'temperature': 0.75,
                'top_k': 10,
                'top_p': 0.95,
                'early_stopping': True,
            }
        }

        payload['parameters']['temperature'] = tempr_param
        payload['parameters']['top_k'] = top_k_param

        try:
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )

            result = json.loads(response['Body'].read().decode())

            raw_text = result[0]['generated_text']
            res_text = str(raw_text).replace("\n", " ").replace('"', "")

            response_body['status'] = 200
            response_body['data'] = res_text

            return jsonify(response_body), 200
        except:
            response_body['status'] = 503
            response_body['data'] = "AI server is overloaded"

            return jsonify(response_body), 503

    else:
        response_body['status'] = 405
        response_body['data'] = "GET Method Not Allowed. Please Try POST Method."

        return jsonify(response_body), 405