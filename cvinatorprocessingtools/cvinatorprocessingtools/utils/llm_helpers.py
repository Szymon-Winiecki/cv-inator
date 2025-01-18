import ollama

def execute_prompt(prompt : str, model : str, LLM_engine : str = "ollama", verbosity : int = 0) -> dict:
    if LLM_engine == "ollama":
       return execute_prompt_ollama(prompt, model, verbosity)
    else:
        raise ValueError(f"LLM_engine '{LLM_engine}' not supported")

def execute_prompt_ollama(prompt : str, model : str, verbosity : int = 0) -> dict:
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
        if verbosity > 1:
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