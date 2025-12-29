# Guia do Bot Telegram - AfiliadoHub

## Índice
1. [Visão Geral](#visão-geral)
2. [Configuração Inicial](#configuração-inicial)
3. [CommandHandler: Como Funciona](#commandhandler-como-funciona)
4. [Comandos Disponíveis](#comandos-disponíveis)
5. [Integração com Supabase](#integração-com-supabase)
6. [Testando o Bot](#testando-o-bot)

---

## Visão Geral

O bot Telegram do AfiliadoHub oferece uma interface conversacional para acessar produtos e ofertas dinamicamente da base de dados Supabase. Utiliza a biblioteca `python-telegram-bot` (v20+) com suporte avançado para CommandHandlers e validação de argumentos.

### Recursos Principais
- ✅ **Comandos Dinâmicos** - Acessa lojas e produtos diretamente do banco de dados
- ✅ **Validação de Argumentos** - Usa parâmetro `has_args` para validar comandos
- ✅ **Preferências de Usuário** - Sistema de recomendações personalizadas
- ✅ **Busca Avançada** - Full-text search com filtros múltiplos
- ✅ **Estatís ticas** - Tracking automático de visualizações e cliques

---

## Configuração Inicial

### 1. Criar o Bot no Telegram

1. Abra o Telegram e busque por `@BotFather`
2. Envie `/newbot` e siga as instruções
3. Copie o **token** fornecido (formato: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Configure comandos com `/setcommands`:

```
start - Iniciar o bot
help - Ajuda e comandos disponíveis
lojas - Ver todas as lojas disponíveis
produtos - Ver produtos de uma loja específica
top - Melhores ofertas do momento
cupom - Cupom aleatório
promo - Promoção em destaque
buscar - Buscar produtos
hoje - Novidades de hoje
aleatorio - Produto aleatório
categorias - Ver categorias
preferencias - Gerenciar preferências
recomendar - Produtos recomendados
stats - Estatísticas do bot
```

### 2. Configurar Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Telegram Bot
BOT_TOKEN=seu_token_aqui

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_aqui
```

### 3. Aplicar Migração do Banco de Dados

Execute o SQL no Supabase SQL Editor:

```bash
# Acesse: https://app.supabase.com/project/SEU_PROJETO/sql/new
# Cole e execute o conteúdo de: afiliadohub/sql/user_preferences_migration.sql
```

### 4. Instalar Dependências

```powershell
cd c:\ProjetoAfiliadoTop
.\\venv\\Scripts\\activate
pip install python-telegram-bot supabase
```

---

## CommandHandler: Como Funciona

### Anatomia de um CommandHandler

```python
from telegram.ext import CommandHandler

# Formato básico
CommandHandler(command, callback, filters=None, block=True, has_args=None)
```

### Parâmetros Principais

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `command` | `str \| Collection[str]` | Comando(s) que o handler escuta (sem `/`) |
| `callback` | `coroutine function` | Função async chamada quando comando é recebido |
| `filters` | `BaseFilter` | Filtros adicionais (opcional) |
| `block` | `bool` | Se deve aguardar callback antes do próximo handler |
| `has_args` | `bool \| int` | Valida número de argumentos (v20.5+) |

### Parâmetro `has_args` Explicado

> **Novidade na versão 20.5**: Validação automática de argumentos

```python
# has_args=None (padrão) - Aceita qualquer número de args
CommandHandler("start", start_command)  # /start ✅  /start foo ✅

# has_args=False - NÃO aceita argumentos
CommandHandler("help", help_command, has_args=False)  # /help ✅  /help foo ❌

# has_args=True - REQUER pelo menos 1 argumento  
CommandHandler("search", search_command, has_args=True)  # /search ❌  /search phone ✅

# has_args=int - REQUER exatamente N argumentos
CommandHandler("produtos", produtos_command, has_args=1)  # /produtos ❌  /produtos shopee ✅  /produtos shopee foo ❌
```

### Exemplo Prático: `/produtos` Command

```python
# Definição do handler com has_args=1
self.application.add_handler(
    CommandHandler("produtos", self.produtos_command, has_args=1)
)

async def produtos_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /produtos [loja]"""
    # Se chegou aqui, context.args tem EXATAMENTE 1 elemento
    # A validação é feita automaticamente pelo python-telegram-bot
    
    store_name = context.args[0].lower()  # Seguro acessar args[0]
    
    # Busca loja no banco
    store = await self.supabase.get_store_by_name(store_name)
    
    if not store:
        await update.message.reply_text(
            f"❌ Loja '{store_name}' não encontrada.\\n"
            "Use /lojas para ver lojas disponíveis."
        )
        return
    
    # ... resto da lógica
```

**Comportamento:**
- `/produtos` → ❌ Handler NÃO é chamado (falta argumento)
- `/produtos shopee` → ✅ Handler é chamado com `context.args = ['shopee']`
- `/produtos shopee teste` → ❌ Handler NÃO é chamado (muitos argumentos)

---

## Comandos Disponíveis

### Comandos Básicos

#### `/start`
Mensagem de boas-vindas com menu interativo.

```
Uso: /start
Exemplo: /start
```

#### `/help`
Lista todos os comandos disponíveis.

```
Uso: /help
Exemplo: /help
```

### Comandos de Lojas e Produtos

#### `/lojas`
Lista todas as lojas ativas do banco de dados dinamicamente.

```
Uso: /lojas
Exemplo: /lojas

Retorna:
🏪 Lojas Disponíveis:
🛍️ Shopee
   📦 1,234 produtos disponíveis
   💡 Use: /produtos shopee
...
```

#### `/produtos` ⭐ *Novo com has_args*
Mostra produtos de uma loja específica. **Requer exatamente 1 argumento**.

```
Uso: /produtos <nome_da_loja>
Exemplo: /produtos shopee
         /produtos aliexpress

has_args: 1 (validação automática)
```

### Comandos de Busca e Descoberta

#### `/top`
Melhores ofertas do momento (maior desconto).

```
Uso: /top
Exemplo: /top

Retorna: Top 5 produtos com maior desconto (mínimo 30%)
```

#### `/cupom`
Cupom aleatório com desconto mínimo de 20%.

```
Uso: /cupom
Exemplo: /cupom
```

#### `/promo`
Promoção em destaque (maior desconto disponível).

```
Uso: /promo
Exemplo: /promo
```

#### `/buscar`
Busca produtos por termo.

```
Uso: /buscar <termo_de_busca>
Exemplo: /buscar fone bluetooth
         /buscar smartphone
```

#### `/hoje`
Produtos adicionados hoje.

```
Uso: /hoje
Exemplo: /hoje
```

#### `/aleatorio`
Produto totalmente aleatório.

```
Uso: /aleatorio
Exemplo: /aleatorio
```

#### `/categorias`
Lista categorias disponíveis.

```
Uso: /categorias
Exemplo: /categorias
```

### Comandos de Personalização

#### `/preferencias`
Visualiza preferências do usuário.

```
Uso: /preferencias
Exemplo: /preferencias

Retorna: Lojas preferidas, categorias, desconto mínimo, etc.
```

#### `/recomendar` ⭐ *Novo*
Produtos recomendados baseados em preferências do usuário.

```
Uso: /recomendar
Exemplo: /recomendar

Inteligente: 
- Salva automaticamente informações do usuário
- Aprende com interações
- Filtra por lojas/categorias preferidas
```

### Comandos Administrativos

#### `/stats`
Estatísticas do sistema.

```
Uso: /stats
Exemplo: /stats

Retorna: Total de produtos, produtos por loja, etc.
```

---

## Integração com Supabase

### Arquitetura de Dados

```
┌─────────────────┐
│  Telegram Bot   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  SupabaseManager    │
│  (supabase_client)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Supabase Database           │
├─────────────────────────────────────┤
│  Tables:                            │
│  - products (produtos)              │
│  - stores (lojas)                   │
│  - categories (categorias)          │
│  - product_stats (estatísticas)     │
│  - user_preferences (preferências)  │
│                                     │
│  Functions (RPC):                   │
│  - get_random_product()             │
│  - get_recommended_products()       │
│  - upsert_user_preference()         │
│  - increment_stat()                 │
└─────────────────────────────────────┘
```

### Métodos do SupabaseManager

#### Lojas
```python
# Buscar lojas ativas
stores = await supabase.get_active_stores()

# Buscar loja específica
store = await supabase.get_store_by_name("shopee")

# Lojas com contagem de produtos
stores_with_count = await supabase.get_stores_with_product_count()
```

#### Produtos
```python
# Buscar produtos com filtros
products = await supabase.get_products({
    "store": "shopee",
    "min_discount": 20,
    "limit": 5
})

# Produto aleatório
product = await supabase.get_random_product(min_discount=20)

# Top deals
top_deals = await supabase.get_top_deals(limit=10, min_discount=30)

# Busca full-text
results = await supabase.search_products_fulltext(
    search_term="smartphone",
    store="amazon",
    min_price=100,
    max_price=1000
)
```

#### Preferências de Usuário
```python
# Buscar preferências
prefs = await supabase.get_user_preferences(telegram_user_id)

# Salvar preferências
await supabase.save_user_preference(
    telegram_user_id=12345,
    telegram_username="joao",
    preferred_stores=["shopee", "amazon"],
    min_discount=25
)

# Recomendações personalizadas
recommendations = await supabase.get_recommended_products(
    telegram_user_id=12345,
    limit=5
)
```

---

## Testando o Bot

### Teste Local (Polling)

```powershell
cd c:\ProjetoAfiliadoTop
.\\ venv\\Scripts\\activate
python scripts/test_bot_enhanced.py
```

### Teste de Comandos Manuais

1. **Abra o bot no Telegram**
   - Busque pelo username do seu bot
   - Clique em "Start"

2. **Teste comandos básicos**
   ```
   /start
   /help
   /lojas
   ```

3. **Teste validação has_args**
   ```
   /produtos              → Deve falhar
   /produtos shopee       → Deve funcionar
   /produtos shopee teste → Deve falhar
   ```

4. **Teste preferências**
   ```
   /preferencias
   /recomendar
   ```

5. **Teste busca**
   ```
   /buscar smartphone
   /top
   /cupom
   ```

### Verificar Logs

```powershell
# Logs aparecem no console
# Procure por:
# [OK] - Operações bem-sucedidas
# [ERRO] - Erros
```

### Verificar Database

Acesse Supabase Dashboard:
```
https://app.supabase.com/project/SEU_PROJETO/editor
```

Verifique tabelas:
- `products` - Produtos cadastrados
- `stores` - Lojas ativas
- `user_preferences` - Preferências salvas
- `product_stats` - Estatísticas de uso

---

## Troubleshooting

### Erro: "BOT_TOKEN não encontrado"
**Solução**: Configure `BOT_TOKEN` no arquivo `.env`

### Erro: "SUPABASE_URL e SUPABASE_KEY devem ser configurados"
**Solução**: Configure credenciais do Supabase no `.env`

### Comando não responde
**Solução**: 
1. Verifique se o handler foi registrado em `_register_handlers()`
2. Confirme que o método existe na classe `TelegramBot`
3. Verifique logs de erro

### has_args não funciona
**Solução**: Certifique-se de usar `python-telegram-bot >= 20.5`
```powershell
pip install --upgrade python-telegram-bot
```

### Banco de dados retorna vazio
**Solução**:
1. Verifique se a migração foi executada
2. Confirme que há produtos no banco
3. Teste query diretamente no Supabase SQL Editor

---

## Boas Práticas

### 1. Sempre use `async/await`
```python
# ✅ Correto
await self.supabase.get_products(filters)

# ❌ Incorreto
self.supabase.get_products(filters)  # Sem await
```

### 2. Trate erros apropriadamente
```python
try:
    products = await self.supabase.get_products(filters)
except Exception as e:
    logger.error(f"Erro: {e}")
    await update.message.reply_text("❌ Erro ao buscar produtos")
```

### 3. Use parse_mode correto
```python
# Markdown para mensagens simples
await update.message.reply_text("*Texto em negrito*", parse_mode='Markdown')

# HTML para links
await update.message.reply_text(
    "<a href='https://...'>Link</a>",
    parse_mode='HTML'
)
```

### 4. Incremente estatísticas
```python
await self.supabase.increment_product_stats(
    product["id"],
    "telegram_send_count"
)
```

### 5. Use has_args para validação
```python
# Comando sem argumentos
CommandHandler("help", help_command, has_args=False)

# Comando com exatamente N argumentos
CommandHandler("produtos", produtos_command, has_args=1)

# Comando que aceita argumentos opcionais
CommandHandler("buscar", search_command)  # Valida manualmente context.args
```

---

## Referências

- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [CommandHandler API](https://docs.python-telegram-bot.org/en/latest/telegram.ext.commandhandler.html)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Telegram Bot API](https://core.telegram.org/bots/api)
