"""
Versão melhorada do comando shopee_buscar
Esconde comissões em grupos públicos, mostra apenas em chats privados
"""

async def shopee_buscar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /shopee_buscar - Busca produtos na Shopee"""
    try:
        keyword = ' '.join(context.args) if context.args else None
        
        if not keyword:
            await update.message.reply_text(
                "🔍 *Como usar:*\n\n"
                "`/shopee_buscar [palavra-chave]`\n\n"
                "*Exemplos:*\n"
                "• `/shopee_buscar fone bluetooth`\n"
                "• `/shopee_buscar capa iphone`",
                parse_mode='Markdown'
            )
            return
        
        # Detecta se é grupo ou privado
        is_private = update.message.chat.type == 'private'
        
        await update.message.reply_text(
            f"🔍 Buscando: *{keyword}*...",
            parse_mode='Markdown'
        )
        
        from ..utils.shopee_client import create_shopee_client
        
        client = create_shopee_client()
        async with client:
            result = await client.get_products(
                keyword=keyword,
                sort_type=5,  # Maior comissão (interno)
                limit=5
            )
        
        nodes = result.get("nodes", [])
        
        if nodes:
            await update.message.reply_text(
                f"✅ Encontrei {len(nodes)} produtos!",
                parse_mode='Markdown'
            )
            
            for idx, product in enumerate(nodes, 1):
                name = product.get('productName', 'N/A')
                price_min = product.get('priceMin', '0')
                price_max = product.get('priceMax', price_min)
                sales = product.get('sales', 0)
                rating = product.get('ratingStar', 'N/A')
                discount = product.get('priceDiscountRate', 0)
                offer_link = product.get('offerLink', '')
                
                # VERSÃO PÚBLICA (Grupo) - SEM comissão
                if not is_private:
                    message = f"*{idx}. {name[:50]}{'...' if len(name) > 50 else ''}*\n\n"
                    
                    # Destaca desconto se houver
                    if discount > 0:
                        message += f"🔥 *{discount}% OFF!*\n\n"
                    
                    # Preço
                    if price_min == price_max:
                        message += f"💰 R$ {price_min}\n"
                    else:
                        message += f"💰 R$ {price_min} - R$ {price_max}\n"
                    
                    message += f"📦 {sales:,} vendidos\n"
                    message += f"⭐ {rating}/5\n"
                    message += f"\n🔗 [Comprar com Desconto]({offer_link})"
                
                # VERSÃO PRIVADA (DM) - COM comissão
                else:
                    commission_rate = float(product.get('commissionRate', 0)) * 100
                    seller_comm = float(product.get('sellerCommissionRate', 0)) * 100 if product.get('sellerCommissionRate') else 0
                    
                    message = f"*#{idx} - {name[:45]}{'...' if len(name) > 45 else ''}*\n\n"
                    
                    # Mostra comissão APENAS em privado
                    if commission_rate >= 50:
                        message += f"🔥 *ALTA COMISSÃO: {commission_rate:.1f}%* 🔥\n"
                    else:
                        message += f"💰 Comissão: *{commission_rate:.1f}%*\n"
                    
                    if seller_comm > 0:
                        message += f"   └ Vendedor: {seller_comm:.1f}%\n"
                    
                    message += f"\n"
                    
                    if discount > 0:
                        message += f"🏷️ Desconto: {discount}%\n"
                    
                    if price_min == price_max:
                        message += f"💵 Preço: R$ {price_min}\n"
                    else:
                        message += f"💵 Preço: R$ {price_min} - R$ {price_max}\n"
                    
                    message += f"📦 Vendas: {sales:,}\n"
                    message += f"⭐ Rating: {rating}/5\n"
                    message += f"\n🔗 [Ver Produto]({offer_link})"
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                
                import asyncio
                await asyncio.sleep(0.7)
            
            # Mensagem final diferente
            if is_private:
                await update.message.reply_text(
                    "💡 *Dica:* Use `/shopee_link [url]` para gerar link personalizado!",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                f"😕 Nenhum produto encontrado com: *{keyword}*",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Erro no comando /shopee_buscar: {e}")
        await update.message.reply_text("❌ Erro ao buscar produtos.")
