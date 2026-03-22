---
name: affiliate-bot-tools
description: Um conjunto de ferramentas para atuar como um Bot de Afiliados. Use essa skill sempre que o usuário mencionar a coleta de dados de produtos, verificação de descontos falsos (metade do dobro), geração de links monetizados de afiliados ou manutenção de histórico de preços de ofertas. Acione-a imediatamente em contextos de automação de e-commerce e afiliados.
---

# Affiliate Bot Tools

Esta skill transforma o agente em um assistente essencial para rotinas de e-commerce e programas de afiliados. Você terá acesso aos schemas e funções core para operar um pipeline de coleta e curadoria de ofertas de produtos físicos ou digitais.

A skill se divide em quatro categorias principais (ferramentas):

1. **Coleta de Dados (Data Gathering)**
   - **Objetivo**: Extrair dados de preço, frete e disponibilidade a partir da URL de um produto, simulando scrappers baseados em Playwright ou BeautifulSoup em casos onde não há APIs oficias disponíveis.
   - **Função correspondente**: `skill_scrape_product`

2. **Inteligência e Curadoria (Reasoning)**
   - **Objetivo**: Detectar descontos inflados (a famosa "metade do dobro") validando o novo preço com o histórico real do item.
   - **Função correspondente**: `skill_detect_fake_discount`

3. **Monetização (Affiliate Management)**
   - **Objetivo**: Transformar o link comum de um produto em um link de vendas com UTMs corretas e IDs de afiliados baseados nas regras da rede pertinente (ex: Amazon, Shopee, Mercado Livre).
   - **Função correspondente**: `skill_generate_affiliate_link`

4. **Persistência (Database)**
   - **Objetivo**: Alimentar o banco de dados (ex. PostgreSQL via SQLAlchemy) em tempo real contendo um log dos menores preços já registrados para garantir conformidade da oferta em ocasiões futuras.
   - **Função correspondente**: `skill_save_price_history`

---

## Como usar na prática

Você pode usar os schemas JSON de Pydantic fornecidos no script Python anexado à essa skill (`scripts/tools.py`) para gerar definições de ferramentas (tool schemas) compatíveis com chamadas de LLM ou para simular o uso destas funções ao ajudar o usuário.

### Executando o script de schemas

Para visualizar ou obter os JSON Schemas gerados por essas classes, basta executar:

```bash
python scripts/tools.py
```

Isso fará o print de todos os `agent_tools` no formato JSON esperado por várias APIs de Language Models, facilitando o seu uso como Agent.

Se o usuário pedir que você colete um link ou crie um link de afiliado, chame a simulação dessas lógicas por conta própria usando código Python se necessário, ou retorne os resultados esperados usando seu raciocínio.
