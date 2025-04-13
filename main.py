from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, Base, get_db

# Initialize FastAPI app and database tables
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ✅ Root route for "/"
@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API!"}

# Fetch all tasks
@app.get("/api/todos/", response_model=List[schemas.TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

# Create a new task
@app.post("/api/todos/", response_model=schemas.TodoResponse)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(**todo.dict())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# Update task completion status or title
@app.patch("/api/todos/{todo_id}/", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    existing_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in todo.dict().items():
        setattr(existing_todo, key, value)
    
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

# Delete a task by ID
@app.delete("/api/todos/{todo_id}/")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(existing_todo)
    db.commit() 
    return {"detail": "Todo deleted successfully"}
