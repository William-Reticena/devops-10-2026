"""Modelos para a API de gerenciamento de tarefas."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Tarefa(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)
    titulo: str
    descricao: Optional[str] = None
    concluida: bool = False
    data_criacao: datetime
    data_conclusao: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        if isinstance(self.data_criacao, str):
            self.data_criacao = datetime.fromisoformat(self.data_criacao)
        if isinstance(self.data_conclusao, str):
            self.data_conclusao = datetime.fromisoformat(self.data_conclusao)

    def finalizar(self):
        """Mark the task as completed and set the completion date."""
        self.concluida = True
        self.data_conclusao = datetime.now().astimezone()

    def resumir(self):
        """Return a summary of the task."""
        return {self.id: self.titulo}

    def get_id(self):
        """Return the ID of the task."""
        return self.id