import pandas as pd
import io
from datetime import datetime
from typing import Dict, List
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ReportExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    async def export_to_excel(self, data: Dict, report_type: str) -> bytes:
        """Exporta dados para Excel"""
        try:
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Página de resumo
                if 'summary' in data:
                    summary_df = pd.DataFrame([data['summary']])
                    summary_df.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Página de produtos
                if 'products' in data and data['products']:
                    products_df = pd.DataFrame(data['products'])
                    products_df.to_excel(writer, sheet_name='Produtos', index=False)
                
                # Página de estatísticas
                if 'statistics' in data and data['statistics']:
                    stats_df = pd.DataFrame([data['statistics']])
                    stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
                
                # Página por loja
                if 'by_store' in data and data['by_store']:
                    store_data = []
                    for store, metrics in data['by_store'].items():
                        metrics['loja'] = store
                        store_data.append(metrics)
                    
                    store_df = pd.DataFrame(store_data)
                    store_df.to_excel(writer, sheet_name='Por Loja', index=False)
                
                writer._save()
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Erro ao exportar para Excel: {str(e)}")
    
    async def export_to_pdf(self, data: Dict, report_type: str) -> bytes:
        """Exporta dados para PDF"""
        try:
            buffer = io.BytesIO()
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            elements = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#1E3A8A')
            )
            
            elements.append(Paragraph(f"Relatório AfiliadoHub - {report_type}", title_style))
            elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Resumo
            if 'summary' in data:
                elements.append(Paragraph("📊 Resumo Geral", self.styles['Heading2']))
                
                summary_data = [
                    ['Métrica', 'Valor']
                ]
                
                for key, value in data['summary'].items():
                    if isinstance(value, (int, float)):
                        if 'percent' in key.lower() or 'rate' in key.lower():
                            value = f"{value:.2f}%"
                        elif 'price' in key.lower() or 'amount' in key.lower():
                            value = f"R$ {value:,.2f}"
                        else:
                            value = f"{value:,}"
                    
                    summary_data.append([key.replace('_', ' ').title(), str(value)])
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 30))
            
            # Produtos (limitado)
            if 'products' in data and data['products']:
                elements.append(Paragraph("📦 Produtos", self.styles['Heading2']))
                
                # Limita a 50 produtos no PDF
                products_data = [['ID', 'Nome', 'Loja', 'Preço', 'Desconto']]
                
                for product in data['products'][:50]:
                    products_data.append([
                        str(product.get('id', '')),
                        str(product.get('name', ''))[:30],
                        str(product.get('store', '')),
                        f"R$ {product.get('current_price', 0):,.2f}",
                        f"{product.get('discount_percentage', 0)}%" if product.get('discount_percentage') else ''
                    ])
                
                products_table = Table(products_data, colWidths=[0.5*inch, 3*inch, inch, inch, inch])
                products_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))
                
                elements.append(products_table)
                
                if len(data['products']) > 50:
                    elements.append(Paragraph(f"... e mais {len(data['products']) - 50} produtos", self.styles['Italic']))
                
                elements.append(Spacer(1, 30))
            
            # Por loja
            if 'by_store' in data and data['by_store']:
                elements.append(Paragraph("🏪 Análise por Loja", self.styles['Heading2']))
                
                store_data = [['Loja', 'Produtos', 'Vendas (R$)', 'Taxa Conversão']]
                
                for store, metrics in data['by_store'].items():
                    store_data.append([
                        store.title(),
                        str(metrics.get('product_count', 0)),
                        f"R$ {metrics.get('total_revenue', 0):,.2f}",
                        f"{metrics.get('click_through_rate', 0):.1f}%"
                    ])
                
                store_table = Table(store_data, colWidths=[1.5*inch, inch, 1.5*inch, 1.5*inch])
                store_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                
                elements.append(store_table)
                elements.append(Spacer(1, 30))
            
            # Rodapé
            elements.append(Paragraph("---", self.styles['Normal']))
            elements.append(Paragraph("AfiliadoHub - Relatório Gerado Automaticamente", self.styles['Italic']))
            elements.append(Paragraph(f"Página 1", self.styles['Italic']))
            
            # Gera PDF
            doc.build(elements)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Erro ao exportar para PDF: {str(e)}")
    
    async def export_to_csv(self, data: Dict, report_type: str) -> bytes:
        """Exporta dados para CSV"""
        try:
            output = io.StringIO()
            
            # Exporta produtos se existirem
            if 'products' in data and data['products']:
                df = pd.DataFrame(data['products'])
                df.to_csv(output, index=False)
            elif 'summary' in data:
                # Exporta resumo
                df = pd.DataFrame([data['summary']])
                df.to_csv(output, index=False)
            else:
                # Exporta dados brutos
                df = pd.DataFrame([data])
                df.to_csv(output, index=False)
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            raise Exception(f"Erro ao exportar para CSV: {str(e)}")
    
    async def generate_comprehensive_report(self, start_date: str, end_date: str, format: str = 'excel') -> Dict:
        """Gera relatório completo em múltiplos formatos"""
        try:
            from api.handlers.advanced_analytics import AdvancedAnalytics
            
            analytics = AdvancedAnalytics()
            report_data = await analytics.generate_performance_report(start_date, end_date)
            
            if 'error' in report_data:
                return report_data
            
            # Exporta no formato solicitado
            if format == 'excel':
                content = await self.export_to_excel(report_data, 'Completo')
                filename = f"relatorio_completo_{start_date[:10]}_{end_date[:10]}.xlsx"
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            elif format == 'pdf':
                content = await self.export_to_pdf(report_data, 'Completo')
                filename = f"relatorio_completo_{start_date[:10]}_{end_date[:10]}.pdf"
                content_type = 'application/pdf'
            
            elif format == 'csv':
                content = await self.export_to_csv(report_data, 'Completo')
                filename = f"relatorio_completo_{start_date[:10]}_{end_date[:10]}.csv"
                content_type = 'text/csv'
            
            else:
                return {"error": "Formato não suportado"}
            
            return {
                "filename": filename,
                "content": content,
                "content_type": content_type,
                "report_data": report_data
            }
            
        except Exception as e:
            return {"error": str(e)}
