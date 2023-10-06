import json

from celery import shared_task
from django.http import JsonResponse
from django.shortcuts import render, redirect
from config.celery import app
import time


@app.task()
def bar():
    time.sleep(20)
    return 'task completed!'


@app.task()
def import_json(task_type):
    time.sleep(task_type * 10)
    return True