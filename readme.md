## installation

### Install [Ollama](https://ollama.com/)
### install [Pytorch](https://pytorch.org/get-started/locally/)

e.g: 
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### install [SBERT](https://sbert.net/)

tested with ONNX version:

```
pip install -U "sentence-transformers[onnx-gpu] @ git+https://github.com/UKPLab/sentence-transformers.git"
```

### install [Jinja2](https://jinja.palletsprojects.com/en/stable/)

```
pip install Jinja2
```

### install local cv-inator packages

in the root project dir:

```
pip install -e cvinatordatamanager
pip install -e cvinatorprocessingtools
```

## Usage

### Scrapper

*Currently the only supported job board is [theprotocol.it](https://theprotocol.it/)*
1. Install scraper-ext as a extension in your favourite web browser (tested in firefox and chrome)
2. Go to one of the supported job boards, select the offer, click 's'
3. Scrapped offer is now in your clipboard


### summarizing offers

```
python summarize.py [-h] -prompt_path PROMPT_PATH -offer_path OFFER_PATH -output_path OUTPUT_PATH [-model MODEL]
```

### comparing offers

to calculate embeddings:

```
python embed.py [-h] -input_dir INPUT_DIR -output_dir OUTPUT_DIR -output_filename OUTPUT_FILENAME
```

to compare offers using calculated embedings:
```
compare.py [-h] -input_path INPUT_PATH -output_dir OUTPUT_DIR
```

### cv generation

```
python .\generate_cv.py -prompt_path .\prompts\cv_generation\prompt_pack_01.json -offer_path .\offers\json\00.json -profile_path .\users_cv_data\01.json -model llama3.2 -output_path generated_cv/02.json
```

### cv visualization

```
python generate.py -template_path TEMPLATE_PATH -cv_path CV_PATH -output_path OUTPUT_PATH
```
