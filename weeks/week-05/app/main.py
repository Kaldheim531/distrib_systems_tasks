import re

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

users = []
last_id = 0

GRAPHIQL_PAGE = """
<!doctype html>
<html>
<head>
  <title>GraphQL Console</title>
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f6f7f9;
      color: #202124;
    }
    header {
      padding: 14px 18px;
      background: #ffffff;
      border-bottom: 1px solid #ddd;
      font-weight: 700;
    }
    main {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      padding: 16px;
      height: calc(100vh - 62px);
      box-sizing: border-box;
    }
    textarea, pre {
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      border: 1px solid #ccc;
      border-radius: 6px;
      padding: 12px;
      background: #ffffff;
      font-family: monospace;
      font-size: 14px;
      resize: none;
      overflow: auto;
    }
    .panel {
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 8px;
      min-height: 0;
    }
    button {
      width: 120px;
      height: 36px;
      border: 0;
      border-radius: 6px;
      background: #1a73e8;
      color: white;
      cursor: pointer;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <header>GraphQL Console</header>
  <main>
    <section class="panel">
      <button onclick="sendQuery()">Run</button>
      <textarea id="query">mutation {
  createUser(name: "Alex", email: "alex@example.com") {
    id
    name
    email
  }
}</textarea>
    </section>
    <section class="panel">
      <div>Response</div>
      <pre id="result">{}</pre>
    </section>
  </main>
  <script>
    async function sendQuery() {
      const query = document.getElementById("query").value;
      const response = await fetch("/graphql", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query})
      });
      const data = await response.json();
      document.getElementById("result").textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
"""


def get_fields(query: str):
    matches = re.findall(r"\{([^{}]*)\}", query)
    if not matches:
        return ["id", "name", "email"]

    fields = re.findall(r"\b(id|name|email)\b", matches[-1])
    return fields or ["id", "name", "email"]


def get_argument(name: str, text: str, variables: dict):
    variable = re.search(rf"{name}\s*:\s*\$(\w+)", text)
    if variable:
        return variables.get(variable.group(1))

    string_value = re.search(rf'{name}\s*:\s*"([^"]*)"', text)
    if string_value:
        return string_value.group(1)

    number_value = re.search(rf"{name}\s*:\s*(\d+)", text)
    if number_value:
        return number_value.group(1)

    return None


def only_fields(item: dict, fields: list[str]):
    return {field: item[field] for field in fields if field in item}


def create_user(name: str, email: str):
    global last_id

    last_id += 1
    user = {"id": str(last_id), "name": name, "email": email}
    users.append(user)
    return user


def execute_graphql(query: str, variables: dict):
    fields = get_fields(query)

    if "createUser" in query:
        arguments = re.search(r"createUser\s*\(([^)]*)\)", query)
        if not arguments:
            return {"errors": [{"message": "createUser arguments not found"}]}

        name = get_argument("name", arguments.group(1), variables)
        email = get_argument("email", arguments.group(1), variables)
        if name is None or email is None:
            return {"errors": [{"message": "name and email are required"}]}

        user = create_user(str(name), str(email))
        return {"data": {"createUser": only_fields(user, fields)}}

    if re.search(r"\buser\s*\(", query):
        arguments = re.search(r"user\s*\(([^)]*)\)", query)
        user_id = get_argument("id", arguments.group(1), variables) if arguments else None
        user = next((item for item in users if item["id"] == str(user_id)), None)
        return {"data": {"user": only_fields(user, fields) if user else None}}

    if re.search(r"\busers\b", query):
        return {"data": {"users": [only_fields(user, fields) for user in users]}}

    return {"errors": [{"message": "unknown query"}]}


@app.get("/graphql", response_class=HTMLResponse)
def graphql_page():
    return GRAPHIQL_PAGE


@app.post("/graphql")
async def graphql(request: Request):
    body = await request.json()
    query = body.get("query", "")
    variables = body.get("variables") or {}
    return JSONResponse(execute_graphql(query, variables))
