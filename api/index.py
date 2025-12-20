import sys
import os

# Adiciona o diretório 'afiliadohub' ao path do Python para encontrar modules
current_dir = os.path.dirname(os.path.abspath(__file__))
# O backend real está em ../afiliadohub
afiliadohub_path = os.path.join(current_dir, '..', 'afiliadohub')
sys.path.append(afiliadohub_path)

# Importa a aplicação do backend original
from api.index import app

# Necessário para Vercel Serverless
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
