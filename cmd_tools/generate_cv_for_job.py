import pathlib
import argparse
import json
import datetime
from collections import defaultdict
from pathlib import Path

from utils import calculate_file_hash, execute_prompt

def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-prompt_path', required=True, type=Path, help='Path to the prompt file')
    parser.add_argument('-offer_path', required=True, type=Path, help='Path to the offer file')
    parser.add_argument('-profile_path', required=True, type=Path, help='Path to the cv data file')
    parser.add_argument('-output_path', required=True, type=Path, help='Output path for the summary')
    parser.add_argument('-model', required=False, type=str, default='qwen2.5:0.5b', help='Model to use for summarization')
    parser.add_argument('-verbosity', required=False, type=int, default=False, help='Verbose mode: 0 - silent, 1 - print system messages, 2 - print system messages and model outputs')
    return parser.parse_args()



def generate_single_section(prompt, offer, profile, model, offer_placeholder="${OFFER}", profile_placeholder="${PROFILE}", verbosity=0):

    prompt = prompt.replace(offer_placeholder, offer)
    prompt = prompt.replace(profile_placeholder, profile)

    return execute_prompt(prompt, model, verbosity)

def generate_section_in_context(prompt, offer, profile, cv_draft, model, offer_placeholder="${OFFER}", profile_placeholder="${PROFILE}", draft_placeholder="${DRAFT}", verbosity=0):
        prompt = prompt.replace(offer_placeholder, offer)
        prompt = prompt.replace(profile_placeholder, profile)
        prompt = prompt.replace(draft_placeholder, cv_draft)
    
        return execute_prompt(prompt, model, verbosity)


def handle_generation(prompt_path, offer_id, offer_path, profile_path, output_path, model, offer_placeholder="${OFFER}", profile_placeholder="${PROFILE}", draft_placeholder="${DRAFT}", verbosity=0):
    prompts = json.loads(open(prompt_path, 'r').read())
    for p in prompts:
        prompts[p] = open(prompt_path.parents[0] / prompts[p], 'r', encoding="utf8").read()


    offer = open(offer_path, 'r', encoding="utf8").read()
    offer = json.dumps(json.loads(offer)['offer'])
    profile = open(profile_path, 'r', encoding="utf8").read()
    profile = json.loads(profile)['profile']
    
    # rewrite parts not generated by the LLM
    cv = {
        "personal_info": profile["personal_info"],
        "education": profile["education"],
        "certifications": profile["certifications"],
        "languages": profile["languages"],
    }

    stages_all = 6
    stages_done = 0


    profile = json.dumps(profile)
    info_acc = defaultdict(int)

    for p in ["tech_stack", "soft_stack", "work_experience", "projects"]:
        if p not in prompts:
            print(f"Warning: Missing {p} prompt!")
            cv[p] = []
        else:
            generated = generate_single_section(prompts[p], offer, profile, model, offer_placeholder, profile_placeholder, verbosity)
            cv.update(json.loads(generated["response"]))
            for key in generated["info"]:
                info_acc[key] += generated["info"][key]

        stages_done += 1
        if(verbosity > 0):
            print(f"Stage {stages_done}/{stages_all} done")

    for p in ["about_me"]:
        if p not in prompts:
            print(f"Warning: Missing {p} prompt!")
            cv[p] = ""
        else:
            generated = generate_section_in_context(prompts[p], offer, profile, json.dumps(cv), model, offer_placeholder, profile_placeholder, draft_placeholder, verbosity)
            cv.update(json.loads(generated["response"]))
            for key in generated["info"]:
                info_acc[key] += generated["info"][key]

        stages_done += 1
        if(verbosity > 0):
            print(f"Stage {stages_done}/{stages_all} done")


    supplement = {}
    for p in ["review"]:
        if p not in prompts:
            print(f"Warning: Missing {p} prompt!")
        else:
            generated = generate_section_in_context(prompts[p], offer, profile, json.dumps(cv), model, offer_placeholder, profile_placeholder, draft_placeholder, verbosity)
            supplement[p] = generated["response"]
            for key in generated["info"]:
                info_acc[key] += generated["info"][key]
        
        stages_done += 1
        if(verbosity > 0):
            print(f"Stage {stages_done}/{stages_all} done")

    

    result = {
        'cv': cv,
        'supplement': supplement,
        'info': generated['info'],
        'model': model,
        'prompt_path': str(prompt_path),
        'prompt_hash': calculate_file_hash(prompt_path),
        'offer_id': offer_id,
        'offer_path': str(offer_path),
        'offer_hash': calculate_file_hash(offer_path),
        'profile_path': str(profile_path),
        'profile_hash': calculate_file_hash(profile_path),
        'timestamp' : datetime.datetime.now().isoformat(' '),
        'LLM_engine': 'ollama',
    }

    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as file:
        file.write(json.dumps(result, indent=4))

if __name__ == '__main__':

    parsed_args = parse_args()

    handle_generation(parsed_args.prompt_path, 999999999999, parsed_args.offer_path, parsed_args.profile_path, parsed_args.output_path, parsed_args.model, verbosity=parsed_args.verbosity)