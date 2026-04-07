web: uvicorn afiliadohub.api.index:app --host 0.0.0.0 --port $PORT
worker_awin: python -m afiliadohub.scripts.awin_daily_worker
worker_telegram: python -m afiliadohub.scripts.telethon_worker
