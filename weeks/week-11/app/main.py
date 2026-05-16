from fastapi import FastAPI, HTTPException

app = FastAPI()

reviews = []
last_id = 0


@app.get("/")
def root():
    return {"project": "reviews-s14", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reviews")
def get_reviews():
    return reviews


@app.post("/reviews", status_code=201)
def create_review(review: dict):
    global last_id

    last_id += 1
    new_review = {
        "id": last_id,
        "name": review.get("name", ""),
        "rating": int(review.get("rating", 0)),
    }
    reviews.append(new_review)
    return new_review


@app.get("/reviews/{review_id}")
def get_review(review_id: int):
    for review in reviews:
        if review["id"] == review_id:
            return review

    raise HTTPException(status_code=404, detail="Review not found")
