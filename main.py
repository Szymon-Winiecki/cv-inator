import ollama
import os

# read prompt and offer  scheme from filesystem
prompt = open('prompt.txt', 'r').read()
scheme = open('offer_scheme.txt', 'r').read()

# read offers from filesystem
offers = []
for filename in os.listdir('offers'):
    with open('offers/' + filename, 'r') as file:
        offers.append(file.read())

prommpt_header = prompt + '\n' + scheme + '\n' + 'Offer:\n'

i = 0
for offer in offers:
    full_prompt = prommpt_header + offer
    response = ollama.generate(
        model='llama3.2',
        prompt=full_prompt,
        stream=False,
    )

    with open(f'out/offer_{i}.txt', 'w') as file:
        file.write(response['response'])
    i += 1

print('Done!')

# stream = ollama.generate(
#     model='mistral',
#     prompt='Why is the sky blue?',
#     stream=True,
# )

# for chunk in stream:
#   print(chunk['response'], end='', flush=True)