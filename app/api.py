"""API for managing tasks."""

from datetime import datetime

import requests
from fastapi import FastAPI
from .modelo import Tarefa

APP = FastAPI()
TAREFAS = []
URL_NOTIFICACAO = "http://localhost:8000/notificar"


@APP.get("/tarefas")
async def tarefas():
    """Return each task's ID and title."""
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        lista_somente_id_titulo.append({tarefa.id: tarefa.titulo})

    return lista_somente_id_titulo


@APP.get("/tarefas/{tarefa_id}")
async def tarefa_especifica(tarefa_id: int):
    """Return a task by ID."""
    for tarefa in TAREFAS:
        if tarefa.id == tarefa_id:
            return tarefa

    return {"message": "Tarefa não existe"}


@APP.put("/tarefas/{tarefa_id}")
async def concluir_tarefa(tarefa_id: int):
    """Mark a task as completed and notify the notification service."""
    for tarefa in TAREFAS:
        if tarefa.id == tarefa_id and not tarefa.concluida:
            tarefa.finalizar()

            try:
                requests.post(
                    URL_NOTIFICACAO,
                    params={"_id": tarefa.id, "titulo": tarefa.titulo},
                    timeout=5,
                )
            except requests.RequestException as e:
                print(f"Error notifying: {e}")

            return tarefa

    return {"message": "Tarefa não existe"}


@APP.delete("/tarefas/{tarefa_id}")
async def apagar_tarefa(tarefa_id: int):
    """Delete a task by ID."""
    for indice, tarefa in enumerate(TAREFAS):
        if tarefa.id == tarefa_id:
            TAREFAS.pop(indice)
            return {"message": "Tarefa excluída com sucesso!"}

    return {"message": "Tarefa não existe"}


@APP.post("/tarefas", status_code=201)
async def adicionar_tarefa(titulo: str, descricao: str = None):
    """Create and store a new task."""
    tarefa = Tarefa(
        id=len(TAREFAS),
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().isoformat(timespec='seconds')
    )
    TAREFAS.append(tarefa)

    return {"message": "Tarefa adicionada com sucesso!", "tarefa": tarefa}


@APP.get("/")
async def index():
    """Return the API greeting."""
    return {"message": "Hello, World!"}


@APP.get("/autor")
async def autor():
    """Return the author's full name."""
    return {"mensagem": "William Reticena"}
