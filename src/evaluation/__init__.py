"""Evaluation module - task schemas and metrics."""

from .task_schema import Task, TaskSuite, TaskCategory, Difficulty, TestCase
from .prompt_schema import PromptTemplate, PromptGenerator

__all__ = [
    "Task",
    "TaskSuite", 
    "TaskCategory",
    "Difficulty",
    "TestCase",
    "PromptTemplate",
    "PromptGenerator",
]
