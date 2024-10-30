import ollama
import pathlib
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-prompt_path', required=True, type=str, help='Path to the prompt file')
    parser.add_argument('-offer_path', required=True, type=str, help='Path to the offer file')
    parser.add_argument('-output_path', required=True, type=str, help='Output path for the summary')
    parser.add_argument('-model', required=False, type=str, default='qwen2.5:0.5b', help='Model to use for summarization')
    return parser.parse_args()

def summarize_offer(prompt, offer, model, offer_placeholder="${OFFER}", verbose=False):
    prompt = prompt.replace(offer_placeholder, offer)
    response = ""
    stream = ollama.generate(
        model=model,
        prompt=prompt,
        stream=True,
    )

    for chunk in stream:
        response += chunk['response']
        if verbose:
            print(chunk['response'], end='', flush=True)

    return response

def handle_summarization(prompt_path, offer_path, output_path, model, offer_placeholder="${OFFER}", verbose=False):
    prompt = open(prompt_path, 'r').read()
    offer = open(offer_path, 'r').read()

    response = summarize_offer(prompt, offer, model, offer_placeholder, verbose)

    response = json.loads(response)

    result = {
        'offer_summary': response
    }

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as file:
        file.write(json.dumps(result, indent=4))

if __name__ == '__main__':

    parsed_args = parse_args()

    handle_summarization(parsed_args.prompt_path, parsed_args.offer_path, parsed_args.output_path, parsed_args.model, verbose=True)