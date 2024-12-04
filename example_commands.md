# Examples of usage

below you will find examples how to run each part of this tool

### cv generation

```
python .\generate_cv.py -prompt_path .\prompts\cv_generation\prompt_pack_01.json -offer_path .\offers\json\00.json -profile_path .\users_cv_data\01.json -model llama3.2 -output_path generated_cv/02.json
```

### cv visualization

```
python .\cv_visualisation\generate.py -template_path .\cv_visualisation\templates\template.html -cv_path .\generated_cv\01.json -output_path .\cv_visualisation\output\01.html
```