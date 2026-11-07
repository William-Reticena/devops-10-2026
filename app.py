"""API for managing tasks."""

from datetime import datetime

import requests
from fastapi import FastAPI

APP = FastAPI()
TAREFAS = []
URL_NOTIFICACAO = "http://localhost:8000/notificar"


def criar_tarefa(titulo: str, descricao: str):
    """Create a task from its title and description."""
    tarefa = {
        "id": len(TAREFAS),
        "titulo": titulo,
        "descricao": descricao,
        "concluida": False,
        "criada_em": datetime.now(),
    }

    return tarefa


@APP.get("/tarefas")
async def tarefas():
    """Return each task's ID and title."""
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        lista_somente_id_titulo.append({tarefa["id"]: tarefa["titulo"]})

    return lista_somente_id_titulo


@APP.get("/tarefas/{tarefa_id}")
async def tarefa_especifica(tarefa_id: int):
    """Return a task by ID."""
    for tarefa in TAREFAS:
        if tarefa["id"] == tarefa_id:
            return tarefa

    return {"message": "Tarefa não existe"}


@APP.put("/tarefas/{tarefa_id}")
async def concluir_tarefa(tarefa_id: int):
    """Mark a task as completed and notify the notification service."""
    for tarefa in TAREFAS:
        if tarefa["id"] == tarefa_id:
            tarefa["concluida"] = True
            tarefa["concluida_em"] = datetime.now()
            requests.post(
                URL_NOTIFICACAO,
                params={"_id": tarefa["id"], "titulo": tarefa["titulo"]},
                timeout=5,
            )
            return tarefa

    return {"message": "Tarefa não existe"}


@APP.delete("/tarefas/{tarefa_id}")
async def apagar_tarefa(tarefa_id: int):
    """Delete a task by ID."""
    for indice, tarefa in enumerate(TAREFAS):
        if tarefa["id"] == tarefa_id:
            TAREFAS.pop(indice)
            return {"message": "Tarefa excluída com sucesso!"}

    return {"message": "Tarefa não existe"}


@APP.post("/tarefas", status_code=201)
async def adicionar_tarefa(titulo: str, descricao: str):
    """Create and store a new task."""
    tarefa = criar_tarefa(titulo, descricao)
    TAREFAS.append(tarefa)

    return {"message": "Tarefa adicionada com sucesso!", "tarefa": tarefa}


@APP.get("/")
async def index():
    """Return the API greeting."""
    return {"message": "Hello, World!"}
