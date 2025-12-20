import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def create_sales_funnel_chart(data):
    """Cria gráfico de funil de vendas"""
    fig = go.Figure(go.Funnel(
        y=["Produtos Adicionados", "Visualizados", "Clicados", "Vendidos"],
        x=[data.get('products_added', 0), 
           data.get('products_viewed', 0), 
           data.get('products_clicked', 0), 
           data.get('products_sold', 0)],
        textinfo="value+percent initial",
        opacity=0.8,
        marker={"color": ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]}
    ))
    
    fig.update_layout(
        title="Funil de Conversão",
        showlegend=False,
        height=400
    )
    
    return fig

def create_store_performance_chart(store_data):
    """Cria gráfico de barras para performance por loja"""
    stores = list(store_data.keys())
    revenues = [store_data[store].get('total_revenue', 0) for store in stores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=stores,
            y=revenues,
            marker_color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
        )
    ])
    
    fig.update_layout(
        title="Receita por Loja",
        xaxis_title="Loja",
        yaxis_title="Receita (R$)",
        height=400
    )
    
    return fig

def create_daily_trend_chart(daily_data):
    """Cria gráfico de linha para tendências diárias"""
    if not daily_data:
        return go.Figure()
    
    df = pd.DataFrame(daily_data)
    
    fig = go.Figure()
    
    # Adiciona linhas para cada métrica
    if 'products_added' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['products_added'],
            mode='lines+markers',
            name='Produtos Adicionados',
            line=dict(color='#636EFA', width=3)
        ))
    
    if 'products_sold' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['products_sold'],
            mode='lines+markers',
            name='Produtos Vendidos',
            line=dict(color='#EF553B', width=3)
        ))
    
    fig.update_layout(
        title="Tendências Diárias",
        xaxis_title="Data",
        yaxis_title="Quantidade",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_price_distribution_chart(products_data):
    """Cria histograma de distribuição de preços"""
    if not products_data:
        return go.Figure()
    
    prices = [p.get('current_price', 0) for p in products_data]
    
    fig = px.histogram(
        x=prices,
        nbins=30,
        title="Distribuição de Preços",
        labels={'x': 'Preço (R$)', 'y': 'Frequência'},
        color_discrete_sequence=['#00CC96']
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_donut_chart(data, title, color_sequence=None):
    """Cria gráfico de rosca genérico"""
    if not data:
        return go.Figure()
    
    labels = list(data.keys())
    values = list(data.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        textinfo='label+percent',
        marker_colors=color_sequence or px.colors.qualitative.Set3
    )])
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=400
    )
    
    return fig
