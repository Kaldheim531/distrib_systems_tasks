from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import re

app = FastAPI(title="Users GraphQL Service")

# ── In-memory store ───────────────────────────────────────────────────────────

_next_id: int = 1
_db: dict[int, dict] = {}


# ── GraphiQL UI ───────────────────────────────────────────────────────────────

GRAPHIQL_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>GraphiQL</title>
  <link href="https://unpkg.com/graphiql/graphiql.min.css" rel="stylesheet" />
</head>
<body style="margin:0">
  <div id="graphiql" style="height:100vh"></div>
  <script crossorigin src="https://unpkg.com/react/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom/umd/react-dom.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/graphiql/graphiql.min.js"></script>
  <script>
    const fetcher = GraphiQL.createFetcher({ url: '/graphql' });
    ReactDOM.render(React.createElement(GraphiQL, { fetcher }), document.getElementById('graphiql'));
  </script>
</body>
</html>"""


# ── Resolvers ─────────────────────────────────────────────────────────────────

def resolve_users() -> list[dict]:
    return list(_db.values())


def resolve_user(id: str) -> Optional[dict]:
    return _db.get(int(id))


def resolve_create_user(name: str, email: str) -> dict:
    global _next_id
    user = {"id": str(_next_id), "name": name, "email": email}
    _db[_next_id] = user
    _next_id += 1
    return user


# ── Query executor ────────────────────────────────────────────────────────────

def pick_fields(obj: dict, selection: list[str]) -> dict:
    if not selection:
        return obj
    return {k: v for k, v in obj.items() if k in selection}


def extract_fields(block: str) -> list[str]:
    inner = re.search(r'\{([^{}]*)\}', block)
    if not inner:
        return []
    return re.findall(r'\b(id|name|email)\b', inner.group(1))


def resolve_arg(name: str, raw_args: str, variables: dict) -> Optional[str]:
    var_m = re.search(rf'{name}\s*:\s*\$(\w+)', raw_args)
    if var_m:
        return str(variables.get(var_m.group(1), ""))
    str_m = re.search(rf'{name}\s*:\s*["\']([^"\']*)["\']', raw_args)
    if str_m:
        return str_m.group(1)
    num_m = re.search(rf'{name}\s*:\s*(\d+)', raw_args)
    if num_m:
        return num_m.group(1)
    return None


def execute(query: str, variables: dict) -> dict:
    q = query.strip()
    is_mutation = bool(re.match(r'\s*mutation', q, re.IGNORECASE))

    if is_mutation:
        m = re.search(r'createUser\s*\(([^)]*)\)', q, re.IGNORECASE)
        if not m:
            return {"errors": [{"message": "Unknown mutation"}]}
        raw_args = m.group(1)
        name_val = resolve_arg("name", raw_args, variables)
        email_val = resolve_arg("email", raw_args, variables)
        if name_val is None or email_val is None:
            return {"errors": [{"message": "createUser requires name and email"}]}
        user = resolve_create_user(name_val, email_val)
        fields = extract_fields(q)
        return {"data": {"createUser": pick_fields(user, fields)}}

    # single user
    m = re.search(r'\buser\s*\(([^)]*)\)', q, re.IGNORECASE)
    if m:
        id_val = resolve_arg("id", m.group(1), variables)
        if id_val is None:
            return {"errors": [{"message": "user() requires id argument"}]}
        user = resolve_user(id_val)
        fields = extract_fields(q)
        return {"data": {"user": pick_fields(user, fields) if user else None}}

    # list
    if re.search(r'\busers\b', q, re.IGNORECASE):
        fields = extract_fields(q)
        return {"data": {"users": [pick_fields(u, fields) for u in resolve_users()]}}

    return {"errors": [{"message": "Unknown query"}]}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/graphql", response_class=HTMLResponse)
async def graphiql():
    return GRAPHIQL_HTML


@app.post("/graphql")
async def graphql_endpoint(request: Request):
    body = await request.json()
    query = body.get("query", "")
    variables = body.get("variables") or {}
    result = execute(query, variables)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8119 )