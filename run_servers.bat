@echo off
start cmd /k "cd /d D:\api\api && python manage.py runserver 8088"
start cmd /k "cd /d D:\api\api && uvicorn aap_api.fast_api:app --reload --port 8000"