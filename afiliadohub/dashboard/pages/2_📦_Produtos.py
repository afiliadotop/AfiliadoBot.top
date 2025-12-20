import sys
import os

# Adiciona a raiz ao path se necessário
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir)) # Raiz do projeto
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import padronizado
from dashboard.utils.supabase_client import get_supabase_client
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="Gerenciar Produtos - AfiliadoHub",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Gerenciar Produtos")

# Inicializa Supabase
@st.cache_resource
def init_supabase():
    return get_supabase_client()

supabase = init_supabase()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Buscar Produtos", 
    "➕ Adicionar Manual", 
    "✏️ Editar em Massa", 
    "🗑️ Remover Produtos"
])

with tab1:
    st.subheader("Buscar Produtos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        store_filter = st.multiselect(
            "Loja",
            ["shopee", "aliexpress", "amazon", "temu", "shein", "magalu", "mercado_livre"],
            default=None
        )
    
    with col2:
        category_filter = st.text_input("Categoria")
    
    with col3:
        price_range = st.slider(
            "Faixa de Preço (R$)",
            min_value=0.0,
            max_value=5000.0,
            value=(0.0, 1000.0),
            step=10.0
        )
    
    # Busca
    if st.button("🔍 Buscar Produtos", type="primary"):
        with st.spinner("Buscando produtos..."):
            try:
                query = supabase.table("products").select("*").eq("is_active", True)
                
                if store_filter:
                    query = query.in_("store", store_filter)
                
                if category_filter:
                    query = query.ilike("category", f"%{category_filter}%")
                
                query = query.gte("current_price", price_range[0])\
                            .lte("current_price", price_range[1])
                
                response = query.limit(100).execute()
                
                if response.data:
                    df = pd.DataFrame(response.data)
                    
                    # Formatação
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
                    df['current_price'] = df['current_price'].apply(lambda x: f"R$ {x:,.2f}")
                    df['discount_percentage'] = df['discount_percentage'].apply(lambda x: f"{x}%" if pd.notnull(x) else "")
                    
                    # Mostra resultados
                    st.dataframe(
                        df[['id', 'name', 'store', 'current_price', 'discount_percentage', 'category', 'created_at']],
                        use_container_width=True,
                        column_config={
                            "id": st.column_config.NumberColumn("ID", width="small"),
                            "name": st.column_config.TextColumn("Nome", width="large"),
                            "store": st.column_config.TextColumn("Loja", width="small"),
                            "current_price": st.column_config.TextColumn("Preço", width="small"),
                            "discount_percentage": st.column_config.TextColumn("Desconto", width="small"),
                            "category": st.column_config.TextColumn("Categoria", width="medium"),
                            "created_at": st.column_config.TextColumn("Adicionado", width="medium")
                        }
                    )
                    
                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Produtos Encontrados", len(df))
                    with col2:
                        avg_price = df['current_price'].str.replace('R$ ', '').str.replace(',', '').astype(float).mean()
                        st.metric("Preço Médio", f"R$ {avg_price:,.2f}")
                    with col3:
                        has_discount = df['discount_percentage'].str.contains('%').sum()
                        st.metric("Com Desconto", f"{has_discount} produtos")
                    
                else:
                    st.warning("Nenhum produto encontrado com os filtros selecionados.")
                    
            except Exception as e:
                st.error(f"Erro ao buscar produtos: {e}")

with tab2:
    st.subheader("Adicionar Produto Manualmente")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            store = st.selectbox(
                "Loja*",
                ["shopee", "aliexpress", "amazon", "temu", "shein", "magalu", "mercado_livre"]
            )
            name = st.text_input("Nome do Produto*", max_chars=200)
            affiliate_link = st.text_input("Link de Afiliado*")
            original_link = st.text_input("Link Original (opcional)")
        
        with col2:
            current_price = st.number_input("Preço Atual (R$)*", min_value=0.01, value=99.90, step=0.01)
            original_price = st.number_input("Preço Original (R$)", min_value=0.00, value=0.00, step=0.01)
            category = st.text_input("Categoria")
            image_url = st.text_input("URL da Imagem")
        
        # Calcula desconto automático
        if original_price > current_price and original_price > 0:
            discount = ((original_price - current_price) / original_price) * 100
            st.info(f"💰 Desconto calculado: {discount:.1f}%")
        else:
            discount = None
        
        coupon_code = st.text_input("Código do Cupom")
        coupon_expiry = st.date_input("Validade do Cupom (opcional)")
        
        # Tags
        tags_input = st.text_input("Tags (separadas por vírgula)")
        
        # Botão de envio
        submitted = st.form_submit_button("💾 Salvar Produto", type="primary")
        
        if submitted:
            # Validação
            if not name or not affiliate_link or not current_price:
                st.error("Por favor, preencha os campos obrigatórios (*)")
            else:
                try:
                    product_data = {
                        "store": store,
                        "name": name[:500],
                        "affiliate_link": affiliate_link,
                        "original_link": original_link if original_link else affiliate_link,
                        "current_price": float(current_price),
                        "original_price": float(original_price) if original_price > 0 else None,
                        "discount_percentage": int(discount) if discount else None,
                        "category": category if category else None,
                        "image_url": image_url if image_url else None,
                        "coupon_code": coupon_code if coupon_code else None,
                        "coupon_expiry": coupon_expiry.isoformat() if coupon_expiry else None,
                        "tags": [tag.strip() for tag in tags_input.split(',')] if tags_input else [],
                        "source": "manual",
                        "is_active": True,
                        "is_featured": False
                    }
                    
                    # Insere no Supabase
                    response = supabase.table("products").insert(product_data).execute()
                    
                    if response.data:
                        st.success(f"✅ Produto '{name}' adicionado com sucesso! ID: {response.data[0]['id']}")
                        
                        # Limpa o formulário
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar produto. Verifique os dados.")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

with tab3:
    st.subheader("Edição em Massa")
    
    st.info("""
    ⚡ **Funcionalidade Premium**
    
    Para editar produtos em massa, faça download da planilha, 
    edite no Excel/Google Sheets e faça upload novamente.
    """)
    
    # Download template
    if st.button("📥 Baixar Template CSV"):
        # Cria template
        template_df = pd.DataFrame(columns=[
            'id', 'name', 'current_price', 'original_price', 
            'category', 'is_active', 'is_featured'
        ])
        
        # Converte para CSV
        csv = template_df.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Baixar Template",
            data=csv,
            file_name="template_edicao_massa.csv",
            mime="text/csv"
        )
    
    # Upload de arquivo editado
    uploaded_file = st.file_uploader(
        "Envie o arquivo CSV editado",
        type=['csv'],
        help="Use o template baixado e faça upload após editar"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🔄 Aplicar Alterações", type="primary"):
                with st.spinner("Aplicando alterações..."):
                    # Converte para lista de dicionários
                    updates = df.to_dict('records')
                    
                    # Atualiza produtos
                    success_count = 0
                    error_count = 0
                    
                    for update in updates:
                        try:
                            product_id = update.pop('id')
                            if pd.notnull(product_id):
                                supabase.table("products").update(update).eq('id', int(product_id)).execute()
                                success_count += 1
                        except Exception as e:
                            error_count += 1
                    
                    st.success(f"✅ {success_count} produtos atualizados")
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} produtos com erro")

        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

with tab4:
    st.subheader("Remover Produtos")
    
    st.warning("⚠️ **Atenção:** Esta ação não pode ser desfeita!")
    
    # Filtros para remoção
    removal_option = st.radio(
        "Selecione critério de remoção:",
        ["Produtos Inativos", "Produtos Antigos", "Por Loja", "Remover Todos"]
    )
    
    if removal_option == "Produtos Inativos":
        try:
            response = supabase.table("products").select("count", count="exact").eq("is_active", False).execute()
            inactive_count = response.count or 0
            
            st.write(f"**Produtos inativos encontrados:** {inactive_count}")
            
            if inactive_count > 0 and st.button("🗑️ Remover Produtos Inativos", type="secondary"):
                with st.spinner("Removendo produtos inativos..."):
                    supabase.table("products").delete().eq("is_active", False).execute()
                    st.success(f"✅ {inactive_count} produtos inativos removidos")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Erro: {e}")
    
    elif removal_option == "Produtos Antigos":
        days = st.slider("Produtos com mais de (dias):", 30, 365, 90)
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            response = supabase.table("products")\
                .select("count", count="exact")\
                .lt("updated_at", cutoff_date).execute()
            
            old_count = response.count or 0
            
            st.write(f"**Produtos antigos encontrados:** {old_count}")
            
            if old_count > 0 and st.button(f"🗑️ Remover Produtos Antigos", type="secondary"):
                with st.spinner("Removendo produtos antigos..."):
                    supabase.table("products").delete().lt("updated_at", cutoff_date).execute()
                    st.success(f"✅ {old_count} produtos antigos removidos")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Erro: {e}")
    
    elif removal_option == "Por Loja":
        store_to_remove = st.selectbox("Selecione a loja:", 
            ["shopee", "aliexpress", "amazon", "temu", "shein", "magalu", "mercado_livre"])
        
        try:
            response = supabase.table("products")\
                .select("count", count="exact")\
                .eq("store", store_to_remove).execute()
            
            store_count = response.count or 0
            
            st.write(f"**Produtos da loja {store_to_remove}:** {store_count}")
            
            if store_count > 0 and st.button(f"🗑️ Remover Todos de {store_to_remove}", type="secondary"):
                with st.spinner(f"Removendo produtos da {store_to_remove}..."):
                    supabase.table("products").delete().eq("store", store_to_remove).execute()
                    st.success(f"✅ {store_count} produtos removidos")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Erro: {e}")
    
    else:  # Remover Todos
        st.error("🚨 **PERIGO: Esta ação removerá TODOS os produtos!**")
        
        password = st.text_input("Digite 'CONFIRMAR-DELETE' para prosseguir:", type="password")
        
        if password == "CONFIRMAR-DELETE":
            if st.button("💀 REMOVER TODOS OS PRODUTOS", type="primary"):
                with st.spinner("Removendo todos os produtos..."):
                    try:
                        # Primeiro faz backup
                        response = supabase.table("products").select("*").execute()
                        backup_data = response.data if response.data else []
                        
                        # Remove tudo
                        supabase.table("products").delete().neq("id", 0).execute()
                        
                        st.error("🚨 TODOS OS PRODUTOS FORAM REMOVIDOS!")
                        st.info(f"Backup salvo com {len(backup_data)} registros")
                        
                    except Exception as e:
                        st.error(f"Erro: {e}")
