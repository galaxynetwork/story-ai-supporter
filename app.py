from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import boto3
import json

app = FastAPI()

origins = [
    "https://ai.galaxychain.zone",
    "https://galaxychain.zone",
    "http://localhost:3000",
    "https://galaxychain.zone",
    "https://ai-api.galaxychain.zone",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Amazon SageMaker Runtime Client
session = boto3.Session()
sagemaker_runtime = session.client('sagemaker-runtime')

# Sagemaker endpoint name.
endpoint_name = 'sm-endpoint-gpt-j-6b'


class DataIn(BaseModel):
    text: str
    datas: dict


@app.get("/elb")
async def server_status():
    response_body = {
        'status': 200,
        'data': "Healthy"
    }

    return jsonable_encoder(response_body)


@app.post('/gen-text')
async def text_generate(ai_params: DataIn):
    response_body = {
        'status': 100,
        'data': ""
    }

    payload = {
        'inputs': "",
        'parameters': {
            'max_length': 100,
            'do_sample': True,
            'no_repeat_ngram_size': 2,
            'temperature': 0.75,
            'top_k': 10,
            'top_p': 0.95,
            'early_stopping': True,
        }
    }

    user_text = ai_params.dict()['text']
    if user_text == "":
        response_body['status'] = 400
        response_body['data'] = "Please enter text."

        return jsonable_encoder(response_body)

    tempr_param = float(ai_params.dict()['datas']['randomness'])
    if tempr_param < 0.01:
        tempr_param = 0.01

    top_k_param = int(ai_params.dict()['datas']['fluency'])
    if top_k_param < 1:
        top_k_param = 1

    payload['inputs'] = user_text
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
        res_text = str(raw_text).replace(user_text, "").replace("\n", " ").replace('"', "")

        response_body['status'] = 200
        response_body['data'] = res_text

        return jsonable_encoder(response_body)
    except:
        response_body['status'] = 503
        response_body['data'] = "AI server is overloaded"

        return jsonable_encoder(response_body)