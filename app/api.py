"""API for managing tasks."""

from datetime import datetime, timezone
import os
from typing import Annotated, List

import requests
from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session, create_engine, select

from app.modelo import Tarefa


DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("DATABASE_ADDRESS")
DATABASE = os.environ.get("DATABASE")

if DATABASE_USERNAME is None:
    raise ValueError("DATABASE_USERNAME environment variable is not set.")

if DATABASE_PASSWORD is None:
    raise ValueError("DATABASE_PASSWORD environment variable is not set.")

if DATABASE_ADDRESS is None:
    raise ValueError("DATABASE_ADDRESS environment variable is not set.")

if DATABASE is None:
    raise ValueError("DATABASE environment variable is not set.")

DATABASE_URL = (
    f"postgresql+psycopg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}"
    f"@{DATABASE_ADDRESS}/{DATABASE}"
)
ENGINE = create_engine(DATABASE_URL)

def criar_session():
    """Provide a database session for a request."""
    with Session(ENGINE) as s:
        yield s

SESSAO = Annotated[Session, Depends(criar_session)]

async def criar_banco(_app: FastAPI):
    """Create the database tables."""
    SQLModel.metadata.create_all(ENGINE)
    yield

APP = FastAPI(lifespan=criar_banco)
TAREFAS = []
URL_NOTIFICACAO = "http://localhost:8000/notificar"


@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Return each task's ID and title."""
    lista_tarefas = sessao.exec(select(Tarefa)).all()

    return lista_tarefas


@APP.get("/tarefas/{tarefa_id}")
async def tarefa_especifica(tarefa_id: int, sessao: SESSAO):
    """Return a task by ID."""
    tarefa = sessao.get(Tarefa, tarefa_id)
    if tarefa:
        return tarefa

    return {"message": "Tarefa não existe"}


@APP.put("/tarefas/{tarefa_id}")
async def concluir_tarefa(tarefa_id: int, sessao: SESSAO):
    """Mark a task as completed and notify the notification service."""
    tarefa = sessao.get(Tarefa, tarefa_id)
    if tarefa and not tarefa.concluida:
        tarefa.finalizar()
        sessao.add(tarefa)
        sessao.commit()
        sessao.refresh(tarefa)

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
async def apagar_tarefa(tarefa_id: int, sessao: SESSAO):
    """Delete a task by ID."""
    tarefa = sessao.get(Tarefa, tarefa_id)
    if tarefa:
        sessao.delete(tarefa)
        sessao.commit()
        return {"message": "Tarefa excluída com sucesso!"}

    return {"message": "Tarefa não existe"}


@APP.post("/tarefas", status_code=201)
async def adicionar_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Create and store a new task."""
    tarefa = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().astimezone(timezone.utc),
    )
    sessao.add(tarefa)
    sessao.commit()
    sessao.refresh(tarefa)

    return {"message": "Tarefa adicionada com sucesso!", "tarefa": tarefa}


@APP.get("/")
async def index():
    """Return the API greeting."""
    return {"message": "Hello, World!"}


@APP.get("/autor")
async def autor():
    """Return the author's full name."""
    return {"mensagem": "William Reticena"}
