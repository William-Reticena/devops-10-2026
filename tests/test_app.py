from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock

import app
from notificacao import NOTIFICACAO


CLIENT = TestClient(app.APP)
NOTIFICACAO_CLIENT = TestClient(NOTIFICACAO)


@pytest.fixture(autouse=True)
def reset_tasks():
    app.TAREFAS.clear()


def test_index():
    response = CLIENT.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_list_tasks():
    app.TAREFAS.append({"id": 0, "titulo": "Estudar", "descricao": "FastAPI"})

    response = CLIENT.get("/tarefas")

    assert response.status_code == 200
    assert response.json() == [{"0": "Estudar"}]


def test_get_task():
    app.TAREFAS.append({"id": 0, "titulo": "Estudar", "descricao": "FastAPI"})

    response = CLIENT.get("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {
        "id": 0,
        "titulo": "Estudar",
        "descricao": "FastAPI",
    }


def test_get_nonexistent_task():
    response = CLIENT.get("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}


def test_complete_task(monkeypatch):
    app.TAREFAS.append({"id": 0, "titulo": "Estudar", "descricao": "FastAPI", "concluida": False})
    notified = {}

    def fake_post(url, params, timeout):
        notified.update(url=url, params=params, timeout=timeout)

    monkeypatch.setattr(app.requests, "post", fake_post)

    response = CLIENT.put("/tarefas/0")

    assert response.status_code == 200
    assert response.json()["concluida"] is True
    assert notified == {
        "url": app.URL_NOTIFICACAO,
        "params": {"_id": 0, "titulo": "Estudar"},
        "timeout": 5,
    }


def test_complete_nonexistent_task(monkeypatch):
    post = Mock()
    monkeypatch.setattr(app.requests, "post", post)

    response = CLIENT.put("/tarefas/999")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa não existe"}
    post.assert_not_called()


def test_delete_task():
    app.TAREFAS.append({"id": 0, "titulo": "Estudar", "descricao": "FastAPI"})

    response = CLIENT.delete("/tarefas/0")

    assert response.status_code == 200
    assert response.json() == {"message": "Tarefa excluída com sucesso!"}
    assert app.TAREFAS == []


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