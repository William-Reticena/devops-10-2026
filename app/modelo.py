"""Modelos para a API de gerenciamento de tarefas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Tarefa(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    concluida: bool = False
    data_criacao: datetime
    data_conclusao: Optional[datetime] = None

    def finalizar(self):
        """Mark the task as completed and set the completion date."""
        self.concluida = True
        self.data_conclusao = datetime.now().isoformat(timespec='seconds')

    def resumir(self):
        """Return a summary of the task."""
        return {self.id: self.titulo}

    def get_id(self):
        """Return the ID of the task."""
        return self.id