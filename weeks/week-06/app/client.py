import httpx

PROJECT_CODE = "logs-s14"
BASE_URL = "http://localhost:8119/graphql"


def build_payload(query: str, variables: dict) -> dict:
    """
    Формирует словарь для отправки GraphQL запроса.

    :param query: Текст запроса (query или mutation).
    :param variables: Словарь с переменными.
    :return: Словарь с ключами "query" и "variables".
    """
    return {"query": query, "variables": variables}


def send(query: str, variables: dict | None = None) -> dict:
    """Отправляет GraphQL запрос и возвращает распарсенный ответ."""
    payload = build_payload(query, variables or {})
    response = httpx.post(BASE_URL, json=payload)
    response.raise_for_status()
    return response.json()


def handle(result: dict) -> None:
    """Выводит данные или ошибки из ответа."""
    if errors := result.get("errors"):
        print("Ошибки:")
        for e in errors:
            print(f"  - {e.get('message')}")
    if data := result.get("data"):
        print("Данные:", data)


# ── Запросы ───────────────────────────────────────────────────────────────────

CREATE_LOG = """
mutation($message: String!, $level: String!) {
  createLog(message: $message, level: $level) {
    id
    message
    level
  }
}
"""

GET_LOGS = """
query {
  logs {
    id
    message
    level
  }
}
"""

GET_LOG = """
query($id: ID!) {
  log(id: $id) {
    id
    message
    level
  }
}
"""


if __name__ == "__main__":
    print("=== Создаём лог ===")
    handle(send(CREATE_LOG, {"message": "Service started", "level": "INFO"}))

    print("\n=== Создаём ещё один лог ===")
    handle(send(CREATE_LOG, {"message": "Something went wrong", "level": "ERROR"}))

    print("\n=== Получаем все логи ===")
    handle(send(GET_LOGS))

    print("\n=== Получаем лог по id=1 ===")
    handle(send(GET_LOG, {"id": "1"}))