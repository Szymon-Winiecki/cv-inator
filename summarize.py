import ollama
import pathlib
import argparse
import json
import datetime

from utils import calculate_file_hash

def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-prompt_path', required=True, type=str, help='Path to the prompt file')
    parser.add_argument('-offer_path', required=True, type=str, help='Path to the offer file')
    parser.add_argument('-output_path', required=True, type=str, help='Output path for the summary')
    parser.add_argument('-model', required=False, type=str, default='qwen2.5:0.5b', help='Model to use for summarization')
    parser.add_argument('-verobosity', required=False, type=int, default=False, help='Verbose mode: 0 - silent, 1 - print system messages, 2 - print system messages and model outputs')
    return parser.parse_args()
    

def summarize_offer(prompt, offer, model, offer_placeholder="${OFFER}", verobosity=0):

    prompt = prompt.replace(offer_placeholder, offer)

    stream = ollama.generate(
        model=model,
        prompt=prompt,
        format="json",
        stream=True,
    )

    info = {}
    response = ""
    for chunk in stream:
        response += chunk['response']
        if verobosity > 1:
            print(chunk['response'], end='', flush=True)
        
        if chunk['done']:
            info['total_duration'] = chunk['total_duration']
            info['load_duration'] = chunk['load_duration']
            info['prompt_eval_count'] = chunk['prompt_eval_count']
            info['prompt_eval_duration'] = chunk['prompt_eval_duration']
            info['eval_count'] = chunk['eval_count']
            info['eval_duration'] = chunk['eval_duration']

    return {
            "response": response, 
            "info": info ,
            }

def handle_summarization(prompt_path, offer_id, offer_path, output_path, model, offer_placeholder="${OFFER}", verbosity=0):
    prompt = open(prompt_path, 'r').read()
    offer = open(offer_path, 'r', encoding="utf8").read()
    offer = json.dumps(json.loads(offer)['offer'])

    summarization_result = summarize_offer(prompt, offer, model, offer_placeholder, verbosity)

    response = json.loads(summarization_result["response"])

    result = {
        'offer_summary': response,
        'info': summarization_result['info'],
        'model': model,
        'prompt_path': str(prompt_path),
        'prompt_hash': calculate_file_hash(prompt_path),
        'offer_id': offer_id,
        'offer_path': str(offer_path),
        'offer_hash': calculate_file_hash(offer_path),
        'timestamp' : datetime.datetime.now().isoformat(' '),
        'LLM_engine': 'ollama',
    }

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as file:
        file.write(json.dumps(result, indent=4))

if __name__ == '__main__':

    parsed_args = parse_args()

    handle_summarization(parsed_args.prompt_path, 999999999999, parsed_args.offer_path, parsed_args.output_path, parsed_args.model, verbosity=parsed_args.verobosity)