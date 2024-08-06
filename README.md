# smart recipe
![CI](https://github.com/ljw-612/smart_recipe/actions/workflows/main.yml/badge.svg)

## Final Demo Video
[Watch the final demo video here]()

## Project Purpose:
My mom often feels troubled when thinking about what dishes to cook. At the same time, there is a widely recognized concept in traditional Chinese medicine regarding food incompatibility. I want to develop a large model that can recommend recipes while also considering the properties of different foods.

## Architecture Diagram

![Architecture Diagram](.images/architecture.png)


# Model
`Llama-3-Chinese-8B-Instruct-v2-GGUF` is an LLM tuned on `Meta-Llama-3-8B-Instruct`, which can be used for conversation, QA, etc.
https://huggingface.co/hfl/llama-3-chinese-8b-instruct-v2

# Timeline

| Week                | Tasks             |
|---------------------|--------------------|
| Week 0 | Come up with a project idea and timeline |
| Week 1 | Research on food related datasets |
| Week 2 | Turn llama-3-chinese to llamafile |
| Week 3 | Test customized llamafile's performance |
| Week 4 | Collect and preprocess food related data |
| Week 5 | Combine food related data to the local model (RAG maybe?)|
| Week 6 + week 7 | Test the model's performance and start frontend backend development |
| Week 8 | Dorkerize |
| Week 9 | Final test and wrap up |
| week 10 | Documentations and presentation |

# Resources
## convert gguf files to llamafile
```
$ ./llamafile-0.8.8/bin/llamafile-convert Llama3-8B-Chinese-Chat-q8_0-v2_1.gguf
$ chmod +x Llama3-8B-Chinese-Chat-q8_0-v2_1.llamafile
```
## Run llamafile (langchain api)
```
$ ./Llama3-8B-Chinese-Chat-q8_0-v2_1.llamafile -c 2048 --server --nobrowser
```

docker build -t smart-recipe .
docker run -p 8501:8501 smart-recipe  

# References