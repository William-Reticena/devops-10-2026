"""API for managing tasks."""

from datetime import datetime, timezone
import os
import sys
import logging
from typing import Annotated, List

import requests
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Session, create_engine, select

from app.modelo import Tarefa

LOGGER = logging.getLogger("applogger")
LOGGER.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
file_handler = logging.FileHandler("app.log", encoding="utf-8")

formatter = logging.Formatter("%(name)s - %(asctime)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

LOGGER.addHandler(handler)
LOGGER.addHandler(file_handler)


DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("DATABASE_ADDRESS")
DATABASE = os.environ.get("DATABASE")

if DATABASE_USERNAME is None:
    LOGGER.critical("DATABASE_USERNAME environment variable is not set.")
    sys.exit(1)

if DATABASE_PASSWORD is None:
    LOGGER.critical("DATABASE_PASSWORD environment variable is not set.")
    sys.exit(1)

if DATABASE_ADDRESS is None:
    LOGGER.critical("DATABASE_ADDRESS environment variable is not set.")
    sys.exit(1)

if DATABASE is None:
    LOGGER.critical("DATABASE environment variable is not set.")
    sys.exit(1)

DATABASE_URL = (
    f"postgresql+psycopg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}"
    f"@{DATABASE_ADDRESS}/{DATABASE}"
)
LOGGER.debug(
    "Configuring database connection to %s for database %s.",
    DATABASE_ADDRESS,
    DATABASE,
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

@APP.exception_handler(404)
async def trata_404(_, __):
    """Handle 404 errors."""
    LOGGER.warning("404 error encountered.")
    return JSONResponse(status_code=404, content={"message": "Recurso não encontrado"})

@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Return each task's ID and title."""
    LOGGER.debug("Starting task list query.")
    lista_tarefas = sessao.exec(select(Tarefa)).all()

    LOGGER.info("Retrieved %s tasks from the database.", len(lista_tarefas))

    return lista_tarefas


@APP.get("/tarefas/{tarefa_id}")
async def tarefa_especifica(tarefa_id: int, sessao: SESSAO):
    """Return a task by ID."""
    LOGGER.debug("Loading task with ID %s from the database.", tarefa_id)
    LOGGER.info("Retrieving task %s.", tarefa_id)
    tarefa = sessao.get(Tarefa, tarefa_id)
    if tarefa:
        LOGGER.info("Task %s found.", tarefa_id)
        return tarefa

    LOGGER.warning("Task %s does not exist.", tarefa_id)
    return {"message": "Tarefa não existe"}


@APP.put("/tarefas/{tarefa_id}")
async def concluir_tarefa(tarefa_id: int, sessao: SESSAO):
    """Mark a task as completed and notify the notification service."""
    LOGGER.debug("Checking whether task %s can be completed.", tarefa_id)
    LOGGER.info("Completing task %s.", tarefa_id)
    tarefa = sessao.get(Tarefa, tarefa_id)
    if tarefa and not tarefa.concluida:
        tarefa.finalizar()
        sessao.add(tarefa)
        sessao.commit()
        sessao.refresh(tarefa)
        LOGGER.debug("Task %s refreshed after commit.", tarefa_id)
        LOGGER.info("Task %s completed.", tarefa_id)

        try:
            LOGGER.debug("Sending completion notification for task %s.", tarefa_id)
            requests.post(
                URL_NOTIFICACAO,
                params={"_id": tarefa.id, "titulo": tarefa.titulo},
                timeout=5,
            )
        except requests.RequestException as e:
            LOGGER.error("Error notifying about task %s: %s", tarefa_id, e)

        return tarefa

    LOGGER.warning(
        "Task %s does not exist or is already completed.", tarefa_id
    )
    return {"message": "Tarefa não existe"}


@APP.delete("/tarefas/{tarefa_id}")
async def apagar_tarefa(tarefa_id: int, sessao: SESSAO):
    """Delete a task by ID."""
    LOGGER.debug("Loading task %s before deletion.", tarefa_id)
    LOGGER.info("Deleting task %s.", tarefa_id)
    tarefa = sessao.get(Tarefa, tarefa_id)
    if tarefa:
        sessao.delete(tarefa)
        sessao.commit()
        LOGGER.debug("Delete transaction committed for task %s.", tarefa_id)
        LOGGER.info("Task %s deleted.", tarefa_id)
        return {"message": "Tarefa excluída com sucesso!"}

    LOGGER.warning("Task %s does not exist.", tarefa_id)
    return {"message": "Tarefa não existe"}


@APP.post("/tarefas", status_code=201)
async def adicionar_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Create and store a new task."""
    LOGGER.debug("Preparing new task with description provided: %s.", descricao is not None)
    LOGGER.info("Creating task with title '%s'.", titulo)
    tarefa = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().astimezone(timezone.utc),
    )
    sessao.add(tarefa)
    sessao.commit()
    sessao.refresh(tarefa)
    LOGGER.debug("New task received database ID %s.", tarefa.id)
    LOGGER.info("Task %s created.", tarefa.id)

    return {"message": "Tarefa adicionada com sucesso!", "tarefa": tarefa}


@APP.get("/")
async def index():
    """Return the API greeting."""
    LOGGER.info("Root endpoint accessed.")
    return {"message": "Hello, World!"}


@APP.get("/autor")
async def autor():
    """Return the author's full name."""
    LOGGER.info("Author endpoint accessed.")
    return {"mensagem": "William Reticena"}
