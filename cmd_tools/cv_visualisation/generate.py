import json
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Generate CV in HTML format')
    parser.add_argument('-template_path', required=True, type=Path, help='Path to the Jinja2 template file')
    parser.add_argument('-cv_path', required=True, type=Path, help='Path to the CV data file')
    parser.add_argument('-output_path', required=True, type=Path, help='Path to the output HTML file')
    return parser.parse_args()


def generate_cv(template_path, cv_path, output_path):
    with open(cv_path, "r") as f:
        data = json.load(f)

    env = Environment(loader=FileSystemLoader(str(template_path.parents[0])))
    template = env.get_template(str(template_path.name))

    if "profile" in data:
        output = template.render(profile=data["profile"])
    elif "cv" in data:
        output = template.render(profile=data["cv"])


    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(output)


if __name__ == "__main__":
    args = parse_args()
    generate_cv(args.template_path, args.cv_path, args.output_path)
