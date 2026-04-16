/**
 * Vercel Serverless Function — Mercado Livre Search Proxy
 *
 * Resolve o 403 do ML adicionando Bearer token em todas as requests.
 * Conforme doc oficial ML (linha 830):
 *   "forbidden (403): o IP está bloqueado ou faltam scopes"
 *   "Em toda chamada, enviar o access token em todas elas"
 *
 * Fluxo:
 *   Browser → /api/ml-search?q=notebook (Vercel Function)
 *             ↓ adiciona Authorization: Bearer <ML_ACCESS_TOKEN>
 *             https://api.mercadolibre.com/sites/MLB/search
 *             ↓ 200 OK (autenticado)
 *   Browser ← JSON com produtos
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';

const ML_BASE = 'https://api.mercadolibre.com';
// Token configurado em Vercel > Settings > Environment Variables
const ML_TOKEN = process.env.ML_ACCESS_TOKEN || '';

export default async function handler(req: VercelRequest, res: VercelResponse) {
    // CORS para afiliadobot.top
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // Repassa todos os query params para o ML
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(req.query)) {
            if (typeof value === 'string') {
                queryParams.append(key, value);
            }
        }

        const mlUrl = `${ML_BASE}/sites/MLB/search?${queryParams.toString()}`;

        const headers: HeadersInit = {
            'Accept': 'application/json',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'User-Agent': 'Mozilla/5.0 (compatible; AfiliadoBot/1.0)',
        };

        // Token obrigatório — ML bloqueia IPs de datacenter sem auth
        if (ML_TOKEN) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${ML_TOKEN}`;
        }

        const mlResponse = await fetch(mlUrl, { headers });

        if (!mlResponse.ok) {
            const errorBody = await mlResponse.text();
            console.error(`[ML Proxy] ${mlResponse.status}: ${errorBody.slice(0, 200)}`);
            return res.status(mlResponse.status).json({
                error: `ML API error: ${mlResponse.status}`,
                detail: errorBody.slice(0, 200),
            });
        }

        const data = await mlResponse.json();

        // Cache de 60s para reduzir requests ao ML
        res.setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=120');
        return res.status(200).json(data);

    } catch (error) {
        console.error('[ML Proxy] Unexpected error:', error);
        return res.status(500).json({ error: 'Internal proxy error' });
    }
}
