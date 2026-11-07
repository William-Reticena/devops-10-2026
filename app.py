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
  lista_somente_id_titulo = []
  
  for tarefa in TAREFAS:
    lista_somente_id_titulo.append({
      tarefa["id"]: tarefa["titulo"] 
    })

  return lista_somente_id_titulo

@APP.get("/tarefas/{id}")
async def tarefa_especifica(id: int):
  for tarefa in TAREFAS:
    if tarefa["id"] == id:
      return tarefa

  return {"message": "Tarefa não existe"}

@APP.post("/tarefas")
async def adicionar_tarefa(titulo: str, descricao: str):
  global TAREFAS
  
  tarefa = criar_tarefa(titulo, descricao)
  TAREFAS.append(tarefa)

  return {"message": "Tarefa adicionada com sucesso!", "tarefa": tarefa}

@APP.get("/")
async def index():
  return {"message": "Hello, World!"}