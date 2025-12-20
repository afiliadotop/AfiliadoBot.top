import sys
import os

# Adiciona o diretório 'afiliadohub' ao path do Python para encontrar modules
current_dir = os.path.dirname(os.path.abspath(__file__))
# O backend real está em ../afiliadohub
# Adiciona o diretório atual ao path para garantir que 'afiliadohub' seja encontrado como pacote
sys.path.append(current_dir)

# Importa a aplicação do backend original usando o caminho completo do pacote
try:
    from afiliadohub.api.index import app
except ImportError:
    # Fallback para desenvolvimento local ou se a estrutura de pacotes falhar
    sys.path.append(afiliadohub_path)
    from api.index import app

# Necessário para Vercel Serverless
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
