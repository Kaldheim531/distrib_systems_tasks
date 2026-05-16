from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

notifications = []
last_id = 0


class NotificationCreate(BaseModel):
    name: str
    channel: str


class Notification(NotificationCreate):
    id: int


@app.get("/notifications", response_model=list[Notification])
def get_notifications():
    return notifications


@app.post("/notifications", response_model=Notification, status_code=201)
def create_notification(notification: NotificationCreate):
    global last_id

    last_id += 1
    new_notification = notification.model_dump()
    new_notification["id"] = last_id
    notifications.append(new_notification)

    return new_notification


@app.get("/notifications/{notification_id}", response_model=Notification)
def get_notification(notification_id: int):
    for notification in notifications:
        if notification["id"] == notification_id:
            return notification

    raise HTTPException(status_code=404, detail="Notification not found")


@app.put("/notifications/{notification_id}", response_model=Notification)
def update_notification(notification_id: int, notification: NotificationCreate):
    for index, saved_notification in enumerate(notifications):
        if saved_notification["id"] == notification_id:
            updated_notification = notification.model_dump()
            updated_notification["id"] = notification_id
            notifications[index] = updated_notification
            return updated_notification

    raise HTTPException(status_code=404, detail="Notification not found")


@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int):
    for index, notification in enumerate(notifications):
        if notification["id"] == notification_id:
            deleted_notification = notifications.pop(index)
            return deleted_notification

    raise HTTPException(status_code=404, detail="Notification not found")
