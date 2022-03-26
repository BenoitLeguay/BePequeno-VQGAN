import openai
import json
import logging

def set():
    with open('.openai/credentials.json') as json_file:
        credentials = json.load(json_file)
    openai.api_key = credentials["API_key"]

def ask(in_sentence):
    logger = logging.getLogger('BePequenoVQGAN')
    response = openai.Completion.create(
        engine="davinci",
        prompt=in_sentence,
        max_tokens=40,
        temperature=0.95,
        stop=['.', '?', '!'],
        best_of=5

    )
    logger.info(response)
    out_sentence = response["choices"][0]["text"]
    #out_sentence = out_sentence.replace("\n", "")
    
    return out_sentence