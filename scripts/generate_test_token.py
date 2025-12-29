"""
Script para gerar token de autenticação para testes
Uso: python scripts/generate_test_token.py
"""

import requests
import json
from datetime import datetime

# Configuração
API_URL = "http://localhost:8000/api"
TEST_USER = {
    "email": "teste@afiliado.top",
    "password": "Teste123!",
    "name": "Usuário Teste"
}

def create_test_user():
    """Cria usuário de teste se não existir"""
    print("📝 Tentando criar usuário de teste...")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Usuário criado com sucesso!")
            return True
        elif response.status_code == 400:
            print("ℹ️  Usuário já existe")
            return True
        else:
            print(f"⚠️  Erro ao criar usuário: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print("⚠️  Certifique-se de que o backend está rodando!")
        return False

def login_and_get_token():
    """Faz login e retorna o token"""
    print("\n🔐 Fazendo login...")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            
            print("✅ Login bem-sucedido!")
            print(f"\n👤 Usuário: {user.get('name')} ({user.get('email')})")
            print(f"🔑 Role: {user.get('role', 'client')}")
            
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def test_token(token):
    """Testa o token em um endpoint protegido"""
    print("\n🧪 Testando token no endpoint /shopee/products...")
    
    try:
        response = requests.get(
            f"{API_URL}/shopee/products?limit=5",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            pagination = data.get("pagination", {})
            
            print("✅ Token válido!")
            print(f"📦 Produtos retornados: {len(products)}")
            print(f"📊 Total disponível: {pagination.get('total', 0)}")
            return True
        else:
            print(f"❌ Erro ao testar: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 GERADOR DE TOKEN DE TESTE - AfiliadoBot")
    print("=" * 60)
    
    # Criar usuário se necessário
    if not create_test_user():
        print("\n⚠️  Não foi possível criar/verificar usuário")
        return
    
    # Fazer login
    token = login_and_get_token()
    if not token:
        print("\n❌ Não foi possível obter token")
        return
    
    # Testar token
    test_token(token)
    
    # Exibir token
    print("\n" + "=" * 60)
    print("🎯 SEU TOKEN DE ACESSO:")
    print("=" * 60)
    print(f"\n{token}\n")
    
    print("=" * 60)
    print("📋 COMO USAR:")
    print("=" * 60)
    print("\n1️⃣  No Swagger (http://localhost:8000/docs):")
    print("   - Clique em 'Authorize' (cadeado)")
    print("   - Cole o token acima")
    print("   - Clique em 'Authorize'")
    
    print("\n2️⃣  No Console do Navegador (F12):")
    print(f"   localStorage.setItem('afiliadobot_token', '{token}')")
    
    print("\n3️⃣  Em requisições cURL:")
    print(f"   -H 'Authorization: Bearer {token}'")
    
    print("\n4️⃣  No Postman/Insomnia:")
    print("   Auth Type: Bearer Token")
    print(f"   Token: {token}")
    
    print("\n✨ Token válido até expirar (configurado no Supabase)")
    print("=" * 60)
    
    # Salvar em arquivo
    with open("scripts/test_token.txt", "w") as f:
        f.write(f"Token gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Usuário: {TEST_USER['email']}\n")
        f.write(f"Token: {token}\n")
    
    print("\n💾 Token salvo em: scripts/test_token.txt")

if __name__ == "__main__":
    main()
