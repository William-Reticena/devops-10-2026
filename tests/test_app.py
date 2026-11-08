"""Test the task management API."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, delete

from app import api
from app.api import APP, criar_session
from app.modelo import Tarefa
from notificacao import NOTIFICACAO


NOTIFICACAO_CLIENT = TestClient(NOTIFICACAO)
BANCO = create_engine("sqlite:///banco.db", connect_args={"check_same_thread": False})


@pytest.fixture(name="sessao")
def fixture_sessao():
    """Fixture to provide a database session for testing."""
    SQLModel.metadata.create_all(BANCO)

    with Session(BANCO) as sessao:
        sessao.exec(delete(Tarefa))
        sessao.commit()
        yield sessao

    SQLModel.metadata.drop_all(BANCO)


@pytest.fixture(name="client")
def fixture_client(sessao: Session):
    """Fixture to provide a TestClient for testing."""
    def get_test_session():
        return sessao

    APP.dependency_overrides[criar_session] = get_test_session

    client = TestClient(APP)
    yield client

    APP.dependency_overrides.clear()


def criar_tarefa_teste(sessao: Session) -> Tarefa:
    """Create a task in the test database."""
    tarefa = Tarefa(
        titulo="Estudar",
        descricao="FastAPI",
        data_criacao="2026-01-01T00:00:00+00:00",
    )
    sessao.add(tarefa)
    sessao.commit()
    sessao.refresh(tarefa)
    return tarefa



def test_index(client: TestClient):
    """Return the API greeting."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}



def test_author(client: TestClient):
    """Return the API author."""
    response = client.get("/autor")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "William Reticena"}


def test_list_tasks(client: TestClient, sessao: Session):
    """List tasks stored in the database."""
    criar_tarefa_teste(sessao)
    response = client.get("/tarefas")

    assert response.status_code == 200
    assert response.json()[0]["titulo"] == "Estudar"



def test_get_task(client: TestClient, sessao: Session):
    """Return a task by ID."""
    tarefa = criar_tarefa_teste(sessao)
    response = client.get(f"/tarefas/{tarefa.id}")

    assert response.status_code == 200
    assert response.json()["id"] == tarefa.id
    assert response.json()["titulo"] == "Estudar"
    assert response.json()["descricao"] == "FastAPI"



def test_get_nonexistent_task(client: TestClient):
    """Return a message for an unknown task."""
    response = client.get("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}


def test_complete_task(client: TestClient, sessao: Session, monkeypatch):
    """Complete a task and notify the service."""
    tarefa = criar_tarefa_teste(sessao)
    notified = {}

    def fake_post(url, params, timeout):
        notified.update(url=url, params=params, timeout=timeout)

    monkeypatch.setattr(api.requests, "post", fake_post)

    response = client.put(f"/tarefas/{tarefa.id}")

    assert response.status_code == 200
    assert response.json()["concluida"] is True
    assert notified == {
        "url": api.URL_NOTIFICACAO,
        "params": {"_id": tarefa.id, "titulo": "Estudar"},
        "timeout": 5,
    }



def test_complete_nonexistent_task(client: TestClient, monkeypatch):
    """Return a message without notifying for an unknown task."""
    post = Mock()
    monkeypatch.setattr(api.requests, "post", post)

    response = client.put("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}
    post.assert_not_called()



def test_delete_task(client: TestClient, sessao: Session):
    """Delete a task from the database."""
    tarefa = criar_tarefa_teste(sessao)

    response = client.delete(f"/tarefas/{tarefa.id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa excluída com sucesso!"}
    assert sessao.get(Tarefa, tarefa.id) is None



def test_delete_nonexistent_task(client: TestClient):
    """Return a message for an unknown deletion."""
    response = client.delete("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}



def test_add_task(client: TestClient):
    """Create a task in the database."""
    response = client.post("/tarefas", params={"titulo": "Estudar", "descricao": "FastAPI"})

    assert response.status_code == 201
    assert response.json()["message"] == "Tarefa adicionada com sucesso!"
    assert response.json()["tarefa"]["titulo"] == "Estudar"
    assert response.json()["tarefa"]["descricao"] == "FastAPI"


def test_notify():
    """Notify the notification service."""
    response = NOTIFICACAO_CLIENT.post(
        "/notificar",
        params={"_id": 1, "titulo": "Estudar"},
    )

    assert response.status_code == 200
    assert response.json() == {"mensagem": "OK"}
