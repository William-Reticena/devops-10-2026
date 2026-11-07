from fastapi import FastAPI
from datetime import datetime
import requests

APP = FastAPI()
TAREFAS = []
URL_NOTIFICACAO = "http://localhost:8002/notificar"

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

@APP.put("/tarefas/{id}")
async def concluir_tarefa(id: int):
  for tarefa in TAREFAS:
    if tarefa["id"] == id:
      tarefa["concluida"] = True
      tarefa["concluida_em"] = datetime.now()
      requests.post(
        URL_NOTIFICACAO,
        params={"_id": tarefa["id"], "titulo": tarefa["titulo"]}
      )
      return tarefa

  return {"message": "Tarefa não existe"}

@APP.delete("/tarefas/{id}")
async def apagar_tarefa(id: int):
  for indice, tarefa in enumerate(TAREFAS):
    if tarefa["id"] == id:
      TAREFAS.pop(indice)
      return {"message": "Tarefa excluída com sucesso!"}

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