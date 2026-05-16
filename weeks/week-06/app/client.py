import httpx

PROJECT_CODE = "logs-s14"
BASE_URL = "http://localhost:8119/graphql"

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


def build_payload(query: str, variables: dict | None = None) -> dict:
    return {
        "query": query,
        "variables": variables or {},
    }


def send(query: str, variables: dict | None = None) -> dict:
    response = httpx.post(BASE_URL, json=build_payload(query, variables))
    response.raise_for_status()
    return response.json()


def show_result(result: dict) -> None:
    if "errors" in result:
        print("Ошибки:")
        for error in result["errors"]:
            print(error.get("message"))

    if "data" in result:
        print("Данные:")
        print(result["data"])


if __name__ == "__main__":
    show_result(send(CREATE_LOG, {"message": "Service started", "level": "INFO"}))
    show_result(send(GET_LOGS))
    show_result(send(GET_LOG, {"id": "1"}))
