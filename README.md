# gen-ai-tutorials

Repositório para exemplos e tutoriais (e boas práticas) a serem em projetos de Genarative AI

# Poetry

## Instalação da aplicação
Para instalação de novos bibliotecas no poetry, segue alguns exemplo de libs já instaladas para este projeto.

```shell
cd ./app
poetry install
```

### Para inclusão de novos pacotes
```shell
poetry add python-dotenv pydantic pydantic-settings
poetry add langchain langchain langchain-core langchain-community langchain-openai
poetry add tavily-python
poetry add langgraph
poetry add langsmith langserve[all]
```

# Cloud
## Google Colab
No diretório ```./app/google-colab```, existe a configuração de scripts a serem utilizados no Google Colab

| Framework| filename |
| :---     | :--- |
| Ollama   | *Ollama_ngrok.ipynb* |


# Docker

## Frameworks
```shell
# Ollama
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Databases
```shell
# Qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```