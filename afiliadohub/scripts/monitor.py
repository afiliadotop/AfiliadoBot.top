#!/usr/bin/env python3
"""
Script de monitoramento do AfiliadoHub - Versão Corrigida
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

def check_file_exists(file_path):
    """Verifica se um arquivo existe"""
    return os.path.exists(file_path)

def check_directory_exists(dir_path):
    """Verifica se um diretório existe"""
    return os.path.isdir(dir_path)

def check_python_import(module_name):
    """Verifica se um módulo Python está instalado"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def check_system_health():
    """Verifica a saúde do sistema"""
    print("🔍 Monitorando saúde do sistema AfiliadoHub...")
    print("=" * 60)
    
    checks = []
    
    # 1. Verificação de diretórios essenciais
    essential_dirs = [
        "api",
        "api/handlers",
        "api/utils",
        "api/models",
        "dashboard",
        "dashboard/components",
        "dashboard/pages",
        "dashboard/utils",
        "scripts"
    ]
    
    for dir_path in essential_dirs:
        if check_directory_exists(dir_path):
            checks.append({"item": f"Diretório {dir_path}", "status": "✅ OK"})
        else:
            checks.append({"item": f"Diretório {dir_path}", "status": "❌ FALTANDO"})
    
    # 2. Verificação de arquivos essenciais
    essential_files = [
        "api/main.py",
        "api/handlers/products.py",
        "dashboard/Home.py",
        "requirements.txt",
        ".env.example",
        ".gitignore"
    ]
    
    for file_path in essential_files:
        if check_file_exists(file_path):
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            if file_size > 100:
                checks.append({"item": f"Arquivo {file_path}", "status": "✅ OK"})
            else:
                checks.append({"item": f"Arquivo {file_path}", "status": "⚠️  MUITO PEQUENO"})
        else:
            checks.append({"item": f"Arquivo {file_path}", "status": "❌ FALTANDO"})
    
    # 3. Verificação de dependências Python
    essential_modules = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "pandas",
        "supabase",
        "plotly"
    ]
    
    for module in essential_modules:
        if check_python_import(module):
            checks.append({"item": f"Módulo {module}", "status": "✅ INSTALADO"})
        else:
            checks.append({"item": f"Módulo {module}", "status": "❌ NÃO INSTALADO"})
    
    # 4. Verificação de scripts
    essential_scripts = [
        "scripts/backup.py",
        "scripts/monitor.py",
        "scripts/shopee_scraper.py"
    ]
    
    for script in essential_scripts:
        if check_file_exists(script):
            # Verifica sintaxe Python
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", script],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    checks.append({"item": f"Script {script}", "status": "✅ SINTAXE OK"})
                else:
                    checks.append({"item": f"Script {script}", "status": "❌ ERRO SINTAXE"})
            except:
                checks.append({"item": f"Script {script}", "status": "⚠️  NÃO VERIFICADO"})
        else:
            checks.append({"item": f"Script {script}", "status": "❌ FALTANDO"})
    
    return checks

def generate_report(checks):
    """Gera relatório de monitoramento"""
    print("\n📊 RESULTADO DAS VERIFICAÇÕES:")
    print("=" * 60)
    
    ok_count = 0
    warning_count = 0
    error_count = 0
    
    for check in checks:
        status = check["status"]
        print(f"{status} - {check['item']}")
        
        if "✅" in status:
            ok_count += 1
        elif "⚠️" in status:
            warning_count += 1
        elif "❌" in status:
            error_count += 1
    
    print("\n" + "=" * 60)
    print("📈 ESTATÍSTICAS:")
    print(f"  ✅ OK: {ok_count}")
    print(f"  ⚠️  AVISOS: {warning_count}")
    print(f"  ❌ ERROS: {error_count}")
    
    total = ok_count + warning_count + error_count
    success_rate = (ok_count / total * 100) if total > 0 else 0
    
    print(f"\n  📊 TAXA DE SUCESSO: {success_rate:.1f}%")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "ok": ok_count,
        "warnings": warning_count,
        "errors": error_count,
        "success_rate": success_rate,
        "checks": checks
    }

def save_json_report(report):
    """Salva relatório em JSON"""
    os.makedirs("logs", exist_ok=True)
    
    filename = f"logs/monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo: {filename}")
    return filename

def main():
    """Função principal"""
    print("🚀 AFILIADOHUB MONITOR v1.1")
    print("=" * 60)
    print("Sistema de monitoramento e verificação de integridade")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Executa verificações
        checks = check_system_health()
        
        # Gera relatório
        report = generate_report(checks)
        
        # Salva relatório
        report_file = save_json_report(report)
        
        # Tempo de execução
        elapsed = time.time() - start_time
        print(f"\n⏱️  Tempo total: {elapsed:.2f} segundos")
        
        # Status final
        if report["errors"] == 0:
            print("\n🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
            return 0
        else:
            print(f"\n⚠️  {report['errors']} ERRO(S) ENCONTRADO(S)")
            print("\n🔧 RECOMENDAÇÕES:")
            print("1. Execute: pip install -r requirements.txt")
            print("2. Verifique os arquivos faltantes")
            print("3. Execute o script de verificação novamente")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
