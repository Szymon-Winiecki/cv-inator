import ollama
import pathlib
import argparse
import json
import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-prompt_path', required=True, type=str, help='Path to the prompt file')
    parser.add_argument('-offer_path', required=True, type=str, help='Path to the offer file')
    parser.add_argument('-output_path', required=True, type=str, help='Output path for the summary')
    parser.add_argument('-model', required=False, type=str, default='qwen2.5:0.5b', help='Model to use for summarization')
    return parser.parse_args()

def summarize_offer(prompt, offer, model, offer_placeholder="${OFFER}", verbose=False):

    prompt = prompt.replace(offer_placeholder, offer)

    stream = ollama.generate(
        model=model,
        prompt=prompt,
        stream=True,
    )

    info = {}
    response = ""
    for chunk in stream:
        response += chunk['response']
        if verbose:
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

def handle_summarization(prompt_path, offer_path, output_path, model, offer_placeholder="${OFFER}", verbose=False):
    prompt = open(prompt_path, 'r').read()
    offer = open(offer_path, 'r').read()

    summarization_result = summarize_offer(prompt, offer, model, offer_placeholder, verbose)

    response = json.loads(summarization_result["response"])

    result = {
        'offer_summary': response,
        'info': summarization_result['info'],
        'model': model,
        'prompt_path': prompt_path,
        'offer_path': offer_path,
        'timestamp' : datetime.datetime.now().isoformat(' '),
        'LLM_engine': 'ollama',
    }

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as file:
        file.write(json.dumps(result, indent=4))

if __name__ == '__main__':

    parsed_args = parse_args()

    handle_summarization(parsed_args.prompt_path, parsed_args.offer_path, parsed_args.output_path, parsed_args.model, verbose=True)