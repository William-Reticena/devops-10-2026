from fastapi import FastAPI
from datetime import datetime

APP = FastAPI()
TAREFAS = []

def criar_tarefa(titulo: str, descricao: str):
  tarefa = {
    "id": len(TAREFAS),
    "titulo": titulo,
    "descricao": descricao,
    "concluida": False,
    "criada_em": datetime.now()
  }
  
  return tarefa

@APP.get("/tarefas")
async def tarefas():
  return TAREFAS

@APP.post("/tarefas")
async def adicionar_tarefa(titulo: str, descricao: str):
  global TAREFAS
  
  tarefa = criar_tarefa(titulo, descricao)
  TAREFAS.append(tarefa)

  return {"message": "Tarefa adicionada com sucesso!", "tarefa": tarefa}

@APP.get("/")
async def index():
  return {"message": "Hello, World!"}