from fastapi import FastAPI


NOTIFICACAO = FastAPI()


def enviar_notificacao(_id: int, titulo: str):
  print(f"Tarefa '{titulo}' (id={_id}) finalizada!")
  return {"mensagem": "OK"}


@NOTIFICACAO.post("/notificar")
async def notificar(_id: int, titulo: str):
  """Rota para notificar."""
  return enviar_notificacao(_id, titulo)
