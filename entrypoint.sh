#!/bin/bash
python chatbot.py
flask --app keepAlive run --host 0.0.0.0 --port 80