from datetime import datetime
from app.modelo import Tarefa

def test_nova_tarefa():
    """Test creating a new task."""
    tarefa = Tarefa(
        id=0,
        titulo="Test Task",
        data_criacao=datetime.now().isoformat(timespec='seconds')
    )

    assert tarefa.id == 0
    assert tarefa.titulo == "Test Task"
    assert tarefa.descricao == None
    assert tarefa.data_criacao.isoformat(timespec='seconds') == datetime.now().isoformat(timespec='seconds')
    assert tarefa.data_conclusao == None
    assert tarefa.concluida == False


def test_concluir_tarefa():
    tarefa = Tarefa(
        id=0,
        titulo="Test Task",
        data_criacao=datetime.now().isoformat(timespec='seconds')
    )

    tarefa.finalizar()

    assert tarefa.concluida == True
    assert tarefa.data_conclusao is not None