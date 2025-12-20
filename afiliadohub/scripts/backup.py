#!/usr/bin/env python3
"""
Script de backup automático para o AfiliadoHub
"""
import os
import json
import csv
import gzip
from datetime import datetime, timedelta
from pathlib import Path
import sys
import asyncio

# Adiciona o diretório raiz ao path
# Assumes script is running from root or scripts folder
sys.path.append(str(Path(__file__).parent.parent))

try:
    from api.utils.supabase_client import get_supabase_manager
except ImportError:
    # Try alternate path if running from root
    from afiliadohub.api.utils.supabase_client import get_supabase_manager


class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.supabase = get_supabase_manager()
    
    async def create_full_backup(self):
        """Cria backup completo do banco"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_full_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        print(f"💾 Criando backup completo: {backup_name}")
        
        # Tabelas para backup
        tables = [
            "products", "product_stats", "product_logs",
            "commissions", "settings", "import_logs"
        ]
        
        backup_data = {}
        
        for table in tables:
            try:
                print(f"  📋 Exportando {table}...")
                
                # Busca todos os dados da tabela
                response = self.supabase.client.table(table).select("*").execute()
                
                if response.data:
                    # Salva como JSON
                    json_file = backup_path / f"{table}.json"
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(response.data, f, ensure_ascii=False, indent=2)
                    
                    # Salva como CSV
                    csv_file = backup_path / f"{table}.csv"
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=response.data[0].keys())
                        writer.writeheader()
                        writer.writerows(response.data)
                    
                    backup_data[table] = {
                        "rows": len(response.data),
                        "json_size": json_file.stat().st_size,
                        "csv_size": csv_file.stat().st_size
                    }
                    
                    print(f"    ✅ {table}: {len(response.data)} registros")
                else:
                    print(f"    📭 {table}: vazia")
                    
            except Exception as e:
                print(f"    ❌ Erro em {table}: {e}")
        
        # Cria arquivo de metadados
        metadata = {
            "backup_type": "full",
            "timestamp": timestamp,
            "tables": backup_data,
            "total_rows": sum(data["rows"] for data in backup_data.values()),
            "version": "1.0.0",
            "created_by": "AfiliadoHub Backup Manager"
        }
        
        metadata_file = backup_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Compacta backup
        archive_path = self._compress_backup(backup_path)
        
        # Remove diretório temporário
        import shutil
        shutil.rmtree(backup_path)
        
        print(f"✅ Backup criado: {archive_path}")
        print(f"📊 Estatísticas: {metadata['total_rows']} registros em {len(tables)} tabelas")
        
        return archive_path
    
    async def create_incremental_backup(self, days: int = 1):
        """Cria backup incremental dos últimos dias"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_incremental_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        print(f"🔄 Criando backup incremental (últimos {days} dias)...")
        
        # Backup apenas de produtos recentes
        try:
            response = self.supabase.client.table("products")\
                .select("*")\
                .gte("created_at", cutoff_date)\
                .execute()
            
            if response.data:
                products_file = backup_path / "products_recent.json"
                with open(products_file, 'w', encoding='utf-8') as f:
                    json.dump(response.data, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ Produtos recentes: {len(response.data)} registros")
            else:
                print("  📭 Nenhum produto recente")
                
        except Exception as e:
            print(f"  ❌ Erro ao buscar produtos recentes: {e}")
        
        # Backup de estatísticas recentes
        try:
            response = self.supabase.client.table("product_stats")\
                .select("*")\
                .gte("last_sent", cutoff_date)\
                .execute()
            
            if response.data:
                stats_file = backup_path / "stats_recent.json"
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(response.data, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ Estatísticas recentes: {len(response.data)} registros")
                
        except Exception as e:
            print(f"  ❌ Erro ao buscar estatísticas: {e}")
        
        # Compacta backup
        if any(backup_path.iterdir()):
            archive_path = self._compress_backup(backup_path)
            print(f"✅ Backup incremental criado: {archive_path}")
            
            # Remove diretório temporário
            import shutil
            shutil.rmtree(backup_path)
            
            return archive_path
        else:
            print("📭 Nenhum dado para backup incremental")
            shutil.rmtree(backup_path)
            return None
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Compacta o diretório de backup"""
        import tarfile
        
        archive_name = f"{backup_path.name}.tar.gz"
        archive_path = self.backup_dir / archive_name
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_path, arcname=backup_path.name)
        
        return archive_path
    
    async def list_backups(self):
        """Lista backups disponíveis"""
        backups = []
        
        for file in self.backup_dir.glob("*.tar.gz"):
            stat = file.stat()
            
            # Extrai informações do nome
            name_parts = file.stem.split('_')
            backup_type = name_parts[1] if len(name_parts) > 1 else "unknown"
            timestamp_str = name_parts[2] if len(name_parts) > 2 else ""
            
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            except:
                timestamp = datetime.fromtimestamp(stat.st_mtime)
            
            backups.append({
                "name": file.name,
                "type": backup_type,
                "size_mb": stat.st_size / (1024 * 1024),
                "created": timestamp,
                "path": file
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    async def restore_backup(self, backup_file: Path, restore_type: str = "all"):
        """Restaura um backup"""
        print(f"🔄 Restaurando backup: {backup_file.name}")
        
        # Extrai backup
        extract_dir = self.backup_dir / backup_file.stem
        import tarfile
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(extract_dir)
        
        # Encontra arquivos JSON
        json_files = list(extract_dir.rglob("*.json"))
        
        restored_tables = 0
        restored_rows = 0
        
        for json_file in json_files:
            if json_file.name == "metadata.json":
                continue
            
            table_name = json_file.stem.replace('_recent', '')
            
            if restore_type == "all" or table_name in restore_type:
                print(f"  📋 Restaurando {table_name}...")
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data:
                        # Remove dados existentes se for backup completo
                        if "_recent" not in json_file.stem:
                            self.supabase.client.table(table_name).delete().neq("id", 0).execute()
                        
                        # Insere em lotes
                        batch_size = 1000
                        for i in range(0, len(data), batch_size):
                            batch = data[i:i + batch_size]
                            self.supabase.client.table(table_name).insert(batch).execute()
                        
                        restored_tables += 1
                        restored_rows += len(data)
                        
                        print(f"    ✅ {table_name}: {len(data)} registros")
                        
                except Exception as e:
                    print(f"    ❌ Erro ao restaurar {table_name}: {e}")
        
        # Limpa diretório extraído
        import shutil
        shutil.rmtree(extract_dir)
        
        print(f"✅ Restauração concluída: {restored_rows} registros em {restored_tables} tabelas")
        
        return {
            "tables": restored_tables,
            "rows": restored_rows,
            "backup_file": backup_file.name
        }
    
    async def cleanup_old_backups(self, keep_last: int = 10, max_age_days: int = 30):
        """Remove backups antigos"""
        backups = await self.list_backups()
        
        if len(backups) <= keep_last:
            print(f"📭 Apenas {len(backups)} backups, mantendo todos")
            return 0
        
        # Filtra backups antigos
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        old_backups = [
            b for b in backups[keep_last:]
            if b["created"] < cutoff_date
        ]
        
        # Remove backups
        removed_count = 0
        for backup in old_backups:
            try:
                backup["path"].unlink()
                removed_count += 1
                print(f"  🗑️  Removido: {backup['name']}")
            except Exception as e:
                print(f"  ❌ Erro ao remover {backup['name']}: {e}")
        
        print(f"✅ {removed_count} backups antigos removidos")
        return removed_count

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciador de backups do AfiliadoHub")
    parser.add_argument(
        "action",
        choices=["create", "create-incremental", "list", "restore", "cleanup"],
        help="Ação a executar"
    )
    parser.add_argument("--days", type=int, default=1, help="Dias para backup incremental")
    parser.add_argument("--file", help="Arquivo de backup para restaurar")
    parser.add_argument("--type", choices=["all", "products", "stats"], default="all", 
                       help="Tipo de dados para restaurar")
    parser.add_argument("--keep", type=int, default=10, help="Backups a manter no cleanup")
    parser.add_argument("--max-age", type=int, default=30, help="Idade máxima em dias para cleanup")
    
    args = parser.parse_args()
    
    backup_manager = BackupManager()
    
    if args.action == "create":
        await backup_manager.create_full_backup()
    
    elif args.action == "create-incremental":
        await backup_manager.create_incremental_backup(args.days)
    
    elif args.action == "list":
        backups = await backup_manager.list_backups()
        
        print("\n📋 Backups disponíveis:")
        print("-" * 80)
        for backup in backups:
            print(f"📁 {backup['name']}")
            print(f"   Tipo: {backup['type']}")
            print(f"   Tamanho: {backup['size_mb']:.2f} MB")
            print(f"   Criado: {backup['created'].strftime('%d/%m/%Y %H:%M')}")
            print()
    
    elif args.action == "restore":
        if not args.file:
            print("❌ É necessário especificar o arquivo de backup com --file")
            return
        
        backup_file = Path(args.file)
        if not backup_file.exists():
            print(f"❌ Arquivo não encontrado: {backup_file}")
            return
        
        # confirm = input("⚠️  Esta ação irá substituir dados existentes. Continuar? (s/n): ")
        # In automation mode, we skip confirmation or assume yes carefully. 
        # For now, keeping logic but commenting out interactive input to avoid blocking, 
        # assuming user runs this manually.
        await backup_manager.restore_backup(backup_file, args.type)

    
    elif args.action == "cleanup":
        removed = await backup_manager.cleanup_old_backups(args.keep, args.max_age)
        print(f"\n🧹 {removed} backups removidos")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
