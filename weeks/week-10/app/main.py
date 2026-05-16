from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = []
last_id = 0


@app.get("/")
def root():
    return {"project": "tasks-s14", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task: dict):
    global last_id

    last_id += 1
    new_task = {
        "id": last_id,
        "name": task.get("name", ""),
        "due": task.get("due", ""),
    }
    tasks.append(new_task)
    return new_task


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")
