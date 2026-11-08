from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock

import app.api as api
from app.modelo import Tarefa
from notificacao import NOTIFICACAO


CLIENT = TestClient(api.APP)
NOTIFICACAO_CLIENT = TestClient(NOTIFICACAO)


@pytest.fixture(autouse=True)
def reset_tasks():
    api.TAREFAS.clear()


def test_index():
    response = CLIENT.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_author():
    response = CLIENT.get("/autor")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "William Reticena"}


def test_list_tasks():
    api.TAREFAS.append(
        Tarefa(
            id=0,
            titulo="Estudar",
            descricao="FastAPI",
            data_criacao="2026-01-01T00:00:00",
        )
    )

    response = CLIENT.get("/tarefas")

    assert response.status_code == 200
    assert response.json() == [{"0": "Estudar"}]


def test_get_task():
    api.TAREFAS.append(
        Tarefa(
            id=0,
            titulo="Estudar",
            descricao="FastAPI",
            data_criacao="2026-01-01T00:00:00",
        )
    )

    response = CLIENT.get("/tarefas/0")

    assert response.status_code == 200
    assert response.json()["id"] == 0
    assert response.json()["titulo"] == "Estudar"
    assert response.json()["descricao"] == "FastAPI"


def test_get_nonexistent_task():
    response = CLIENT.get("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}


def test_complete_task(monkeypatch):
    api.TAREFAS.append(
        Tarefa(
            id=0,
            titulo="Estudar",
            descricao="FastAPI",
            data_criacao="2026-01-01T00:00:00",
        )
    )
    notified = {}

    def fake_post(url, params, timeout):
        notified.update(url=url, params=params, timeout=timeout)

    monkeypatch.setattr(api.requests, "post", fake_post)

    response = CLIENT.put("/tarefas/0")

    assert response.status_code == 200
    assert response.json()["concluida"] is True
    assert notified == {
        "url": api.URL_NOTIFICACAO,
        "params": {"_id": 0, "titulo": "Estudar"},
        "timeout": 5,
    }


def test_complete_nonexistent_task(monkeypatch):
    post = Mock()
    monkeypatch.setattr(api.requests, "post", post)

    response = CLIENT.put("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}
    post.assert_not_called()


def test_delete_task():
    api.TAREFAS.append(
        Tarefa(
            id=0,
            titulo="Estudar",
            descricao="FastAPI",
            data_criacao="2026-01-01T00:00:00",
        )
    )

    response = CLIENT.delete("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa excluída com sucesso!"}
    assert api.TAREFAS == []


def test_delete_nonexistent_task():
    response = CLIENT.delete("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}


def test_add_task():
    response = CLIENT.post("/tarefas", params={"titulo": "Estudar", "descricao": "FastAPI"})

    assert response.status_code == 201
    assert response.json()["message"] == "Tarefa adicionada com sucesso!"
    assert response.json()["tarefa"]["titulo"] == "Estudar"
    assert response.json()["tarefa"]["descricao"] == "FastAPI"


def test_notify():
    response = NOTIFICACAO_CLIENT.post(
        "/notificar",
        params={"_id": 1, "titulo": "Estudar"},
    )

    assert response.status_code == 200
    assert response.json() == {"mensagem": "OK"}