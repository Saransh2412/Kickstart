from pydantic import BaseModel,Field,ConfigDict
from typing import List

class File(BaseModel):
    path: str = Field(
        ...,
        description="Path to the file to be created or modified" )
    purpose: str = Field(
        ...,
        description="Purpose of the file, e.g. 'main application logic', 'data processing module'" )

class Plan(BaseModel):
    name: str = Field(
        ...,
        description="Name of the application to be built"
    )

    description: str = Field(
        ...,
        description="A one-line description of the application"
    )

    techstack: List[str] = Field(
        ...,
        description="The tech stack to be used, e.g. 'Python, React, Flask'"
    )

    features: List[str] = Field(
        ...,
        description="List of features the application should have"
    )

    files: List[File] = Field(
        ...,
        description="List of files to be created (with their purpose in filenames or comments)"
    )

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A detailed description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")
class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")
