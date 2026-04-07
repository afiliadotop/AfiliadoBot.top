import os
import sys
import asyncio
import logging
import random
import time
from dotenv import load_dotenv



try:
    from telethon import TelegramClient, errors
except ImportError:
    print("❌ Telethon não detectado. Execute: pip install telethon")
    sys.exit(1)

from afiliadohub.api.utils.supabase_client import get_supabase_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TelethonGhostWorker")

# === CONFIGURAÇÕES GHOST PROTOCOL ===
load_dotenv()

API_ID = os.getenv("TELETHON_API_ID")
API_HASH = os.getenv("TELETHON_API_HASH")
PHONE = os.getenv("TELETHON_PHONE")

SESSION_NAME = 'userbot_afiliadotop'
TARGET_CHATS = ['@toplifegrupo', '@divulgar900', '@frasesestickers', '@Divulgacao4', '@brasileirosnaeuropa1'] # Podem ser IDs ou @ usernames

# Limites Seguros
BLOCOS_POR_DIA_LIMIT = 15  # Não exceda! Limite o envio total por dia (Cota Telegram)
MAX_MSGS_POR_LOTE = 2      # Quantas ofertas por rajada (Pequeno para disfarce)

ABERTURAS = [
    "🔥 Oferta Imperdível!",
    "⚡ Corre que o preço caiu:",
    "🚨 Achado do Dia!",
    "🎯 Promoção Especial detectada:",
    "🛒 Preço de banana:",
    "💣 Explodiu de Desconto:",
    "🏆 Top oferta passando na sua tela:"
]

def buscar_produtos_frescos(supabase, limit=5):
    """
    Busca produtos do Supabase que NUNCA foram enviados para o Telegram.
    (telegram_send_count == 0 ou ausente).
    """
    # 1. Pega os produtos ativos mais recentes e com algum desconto
    logger.info("🔍 Minerando Supabase por produtos virgens...")
    res = supabase.client.table("products").select("id, name, affiliate_link, current_price, discount_percentage").eq("is_active", True).gt("discount_percentage", 0).order("created_at", desc=True).limit(80).execute()
    
    if not res.data:
        return []

    produtos = res.data
    p_ids = [p["id"] for p in produtos]

    # 2. Pega as métricas do histórico para bater com nossa cota
    stats_res = supabase.client.table("product_stats").select("product_id, telegram_send_count").in_("product_id", p_ids).execute()
    
    enviados_count = { s["product_id"]: s.get("telegram_send_count", 0) for s in (stats_res.data or []) }
    
    nao_enviados = []
    for p in produtos:
        c = enviados_count.get(p["id"], 0)
        if c == 0:
            nao_enviados.append(p)
            if len(nao_enviados) >= limit:
                break
                
    return nao_enviados

def montar_mensagem(produto):
    abertura = random.choice(ABERTURAS)
    nome = produto.get("name", "Produto Oculto")
    preco = produto.get("current_price", 0.0)
    link = produto.get("affiliate_link", "")
    desconto = produto.get("discount_percentage", 0)
    
    texto = f"{abertura}\n\n"
    texto += f"📌 {nome}\n\n"
    
    if desconto > 0:
        texto += f"💸 Desconto de {desconto}%\n"
        
    texto += f"💰 Apenas R$ {preco:.2f}!\n\n"
    texto += f"🔗 Acesse: {link}"
    
    return texto

async def enviar_como_humano(client, chat, mensagem):
    """Simula ações humanas antes de postar"""
    try:
        tempo_digitacao = min(max(len(mensagem) / 60.0, 1.5), 5.0)
        
        async with client.action(chat, 'typing'):
            await asyncio.sleep(tempo_digitacao)  
            
        await client.send_message(chat, mensagem, link_preview=True)
        return True, "success"
        
    except errors.FloodWaitError as e:
        logger.warning(f"🛑 [Telegram] Alerta de Flood. Dormindo compulsoriamente por {e.seconds}s...")
        await asyncio.sleep(e.seconds)
        return False, "flood"
        
    except errors.UserBannedInChannelError:
        logger.error(f"❌ [Telegram] Fomos banidos no chat {chat}. Verifique seu envio.")
        return False, "banned"
        
    except errors.ChatWriteForbiddenError:
        logger.error(f"❌ [Telegram] Chat {chat} não permite envio (restrito). Pulando este chat.")
        return False, "restricted"
        
    except errors.rpcerrorerrors.ChatRestrictedError:
        logger.error(f"❌ [Telegram] Chat {chat} está restrito. Pulando este chat.")
        return False, "restricted"
        
    except Exception as e:
        error_str = str(e).lower()
        if "restricted" in error_str or "cannot be used" in error_str:
            logger.error(f"⚠️ Chat {chat} restrito. Pulando: {e}")
            return False, "restricted"
        logger.error(f"⚠️ Erro silencioso ({chat}): {e}")
        return False, "error"

async def daemon_telegram_worker():
    if not API_ID or not API_HASH or not PHONE:
        logger.error("🛑 Faltam as variáveis TELETHON_API_ID, TELETHON_API_HASH ou TELETHON_PHONE no .env")
        return

    supabase = get_supabase_manager()
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    logger.info("📱 Conectando ao Telegram...")
    await client.start(phone=PHONE)
    logger.info("✔️ Autenticação do Telegram bem sucedida!")

    logger.info("🛡️ Ghost Protocol Worker Inicializado! Aguardando janelas de tempo.")

    blocos_hoje = 0

    while True:
        # Busca produtos que ainda não foram postados
        tamanho_lote = random.randint(1, MAX_MSGS_POR_LOTE)
        lote_produtos = buscar_produtos_frescos(supabase, limit=tamanho_lote)
        
        if not lote_produtos:
            logger.info("📭 Nenhum produto novo com desconto e `is_active=True` detectado no BD.")
            pausa = 600  # Dorme 10 minutos se n tiver nada
        else:
            # Embaralha ordem dos chats
            chats_ativos = TARGET_CHATS.copy()
            random.shuffle(chats_ativos)

            sucesso_no_lote = False

            for chat in chats_ativos:
                for prod in lote_produtos:
                    msg = montar_mensagem(prod)
                    logger.info(f"[{time.strftime('%H:%M:%S')}] Tentando via Userbot -> {chat} (Prod ID: {prod['id']})")
                    enviado, status = await enviar_como_humano(client, chat, msg)
                    
                    if status == "restricted":
                        logger.warning(f"  ⏭️ Chat {chat} restrito, removendo da lista...")
                        if chat in TARGET_CHATS:
                            TARGET_CHATS.remove(chat)
                        continue
                    
                    if enviado:
                        sucesso_no_lote = True
                        await supabase.increment_product_stats(prod['id'], "telegram_send_count")
                        
                        pausa_curta = random.uniform(25.0, 72.0)
                        logger.info(f"   [Jitter] Dormindo {pausa_curta:.1f}s.")
                        await asyncio.sleep(pausa_curta)

            blocos_hoje += 1

            if blocos_hoje >= BLOCOS_POR_DIA_LIMIT:
                logger.info("Zzz... Sistema parando para não bater limite diário seguro de Spams Telegram (12-24h sleep).")
                await asyncio.sleep(86400 / 2) # Dorme 12h
                blocos_hoje = 0
            
            pausa = random.randint(1800, 3300) # Entre 30 a 55 mins

        logger.info(f"[{time.strftime('%H:%M:%S')}] Ghost protocol repousando por ({pausa/60:.1f} minutos)...")
        await asyncio.sleep(pausa)

if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(daemon_telegram_worker())
    except KeyboardInterrupt:
        print("\n[Worker] Desligado com segurança pelo Usuário.")
