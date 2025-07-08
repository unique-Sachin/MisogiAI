from fastapi import FastAPI, HTTPException,status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Task Management API",version="1.0.0")

# In-memory storage
tasks = []
task_counter = 1

# Pydantic models
class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    completed: bool = False

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# API Endpoints
@app.get("/tasks",response_model=List[Task])
async def get_tasks():
    return tasks

@app.post("/tasks",response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Create a new task"""
    global task_counter
    new_task = Task(id=task_counter,**task.model_dump())
    tasks.append(new_task)
    task_counter += 1
    return new_task

@app.get("/tasks/{task_id}",response_model=Task)
async def get_task(task_id: int):
    """Get a task by ID"""
    task = next((task for task in tasks if task.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
    

@app.put("/tasks/{task_id}",response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task"""

    # Find the task
    task_index = next((i for i, task in enumerate(tasks) if task.id == task_id), None)

    if task_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Update the task
    task = tasks[task_index]
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.completed is not None:
        task.completed = task_update.completed
    
    return task

@app.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    """Delete a task"""

    # Find and remove the task
    task_index = next((i for i, task in enumerate(tasks) if task.id == task_id), None)

    if task_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    deleted_task = tasks.pop(task_index)
    return {"message": f"Task {deleted_task.title} deleted successfully"}

# Serve the web UI

@app.get("/",response_class=HTMLResponse)
async def get_ui():
    """Serve the web UI"""
    with open("static/index.html", "r") as file:
        return file.read()

# Health check endpoint
@app.get("/health",status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)