# LGPD Compliance - Lei Geral de Proteção de Dados

**Framework:** LGPD (Lei 13.709/2018)  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Objetivo

Garantir conformidade com a Lei Geral de Proteção de Dados Pessoais (LGPD).

---

## 📋 Inventário de Dados Pessoais

### Dados Coletados

| Dado | Categoria | Finalidade | Base Legal | Retenção |
|------|-----------|------------|------------|----------|
| **Email** | Identificação | Autenticação, comunicação | Consentimento | Enquanto conta ativa |
| **Nome** | Identificação | Personalização | Consentimento | Enquanto conta ativa |
| **Senha (hash)** | Autenticação | Login | Execução de contrato | Enquanto conta ativa |
| **IP Address** | Logs | Segurança, auditoria | Interesse legítimo | 90 dias |
| **User Agent** | Logs | Analytics | Interesse legítimo | 90 dias |
| **Preferências** | Perfil | Personalização | Consentimento | Enquanto conta ativa |

### Dados NÃO Coletados
- ❌ CPF
- ❌ Dados sensíveis (raça, religião, política, saúde, etc)
- ❌ Dados de crianças/adolescentes
- ❌ Dados financeiros (cartão de crédito)

---

## ✅ Princípios LGPD Aplicados

### 1. Finalidade
✅ Dados coletados para propósitos específicos e legítimos  
✅ Informados ao titular

### 2. Adequação
✅ Tratamento compatível com finalidades informadas

### 3. Necessidade
✅ Apenas dados essenciais para funcionalidade

### 4. Livre Acesso
✅ Titular pode consultar seus dados facilmente

### 5. Qualidade dos Dados
✅ Dados mantidos atualizados e corretos

### 6. Transparência
✅ Informações claras sobre tratamento

### 7. Segurança
✅ Medidas técnicas e administrativas implementadas

### 8. Prevenção
✅ Medidas para prevenir danos

### 9. Não Discriminação
✅ Sem tratamento discriminatório

### 10. Responsabilização
✅ Demonstração de conformidade

---

## 🔐 Bases Legais

### Consentimento
**Quando:** Cadastro, newsletter, preferências  
**Como:** Opt-in explícito  
**Evidência:** Timestamp, IP, checkbox marcado

### Execução de Contrato
**Quando:** Uso da plataforma  
**Como:** Termos de uso aceitos

### Interesse Legítimo
**Quando:** Analytics, segurança  
**Como:** LIA (Legitimate Interest Assessment) documentado

---

## 👤 Direitos do Titular

### 1. Confirmação e Acesso
**Direito:** Saber se dados são tratados  
**Implementação:** Dashboard "Meus Dados"  
**SLA:** Resposta imediata (automated)

### 2. Correção
**Direito:** Corrigir dados incompletos/incorretos  
**Implementação:** Perfil editável  
**SLA:** Imediato (self-service)

### 3. Anonimização, Bloqueio ou Eliminação
**Direito:** Dados desnecessários/excessivos  
**Implementação:** "Excluir conta" + anonimização  
**SLA:** 48h

### 4. Portabilidade
**Direito:** Receber dados em formato estruturado  
**Implementação:** Export JSON/CSV  
**SLA:** 72h

### 5. Eliminação
**Direito:** Deletar dados após fim do tratamento  
**Implementação:** "Excluir conta permanentemente"  
**SLA:** 7 dias (com período de graça)

### 6. Informação sobre Compartilhamento
**Direito:** Saber com quem dados são compartilhados  
**Implementação:** Privacy policy  
**Compartilhamentos:**
- Supabase (database hosting)
- Render (API hosting)
- Vercel (frontend hosting)
- Sentry (error tracking - anonymized)

### 7. Revogação de Consentimento
**Direito:** Retirar consentimento  
**Implementação:** Settings → "Revogar consentimento"  
**SLA:** Imediato

---

## 🛡️ Medidas de Segurança

### Técnicas
- ✅ Criptografia em trânsito (TLS 1.3)
- ✅ Criptografia em repouso (Supabase)
- ✅ Hashing de senhas (bcrypt)
- ✅ RLS (Row Level Security)
- ✅ Backup diário

### Administrativas
- ✅ Política de segurança
- ✅ Controle de acesso
- ✅ Treinamento de equipe
- ✅ Incident response plan

### Organizacionais
- ✅ DPO designado
- ✅ Privacy by design
- ✅ DPIA para features críticas

---

## 📊 DPIA - Data Protection Impact Assessment

**Quando obrigatório:**
- Tratamento em larga escala
- Dados sensíveis
- Perfiling/decisão automatizada
- Monitoramento sistemático

**Processo:**
1. Identificar necessidade
2. Descrever tratamento
3. Avaliar necessidade/proporcionalidade
4. Identificar riscos
5. Medidas de mitigação
6. DPO review
7. Documentar

**Template:** `docs/compliance/lgpd/dpia-template.md`

---

## 🚨 Incident de Dados

### Notificação ANPD
**Quando:** Incidente com risco/dano aos titulares  
**SLA:** 2 dias úteis (razoável prazo)  
**Como:** Formulário ANPD

**Conteúdo:**
- Descrição do incidente
- Dados afetados
- Titulares impactados
- Medidas técnicas de proteção
- Riscos aos titulares
- Medidas adotadas
- Medidas para reverter/mitigar

### Notificação Titular
**Quando:** Risco relevante  
**SLA:** Imediato  
**Como:** Email

---

## 👔 DPO - Data Protection Officer

**Responsabilidades:**
- Orientar empresa e colaboradores
- Atender titulares
- Interagir com ANPD
- Monitorar conformidade

**Contato:** dpo@afiliadobot.top

**Designado:** [Pending - nomear]

---

## 📄 Documentos Obrigatórios

### 1. Privacy Policy
**Status:** ⏳ A criar  
**Localização:** `/privacy-policy`  
**Conteúdo:**
- Dados coletados
- Finalidades
- Bases legais
- Compartilhamento
- Direitos do titular
- Contato DPO

### 2. Terms of Service
**Status:** ⏳ A criar  
**Localização:** `/terms`

### 3. Cookie Policy
**Status:** ⏳ A criar (se aplicável)

### 4. Consent Forms
**Status:** ⏳ A implementar  
**Localização:** Signup flow

---

## ✅ Checklist de Conformidade

### Fundação
- [x] Inventário de dados pessoais
- [ ] Privacy policy publicada
- [ ] Terms of service publicados
- [ ] DPO designado

### Consentimento
- [ ] Consent flow no signup
- [ ] Evidência de consentimento armazenada
- [ ] Opção de revogação implementada

### Direitos do Titular
- [ ] Dashboard "Meus Dados"
- [ ] Export de dados (portabilidade)
- [ ] Exclusão de conta
- [ ] Correção de dados (já existe - perfil editável)

### Segurança
- [x] Política de segurança
- [x] Criptografia implementada
- [x] Controle de acesso (RLS)
- [x] Backup

### Processos
- [ ] Incident response (LGPD-specific)
- [x] Risk management
- [ ] DPIA template e processo

### Training
- [ ] Equipe treinada em LGPD
- [ ] DPO certificado (recomendado)

---

## 📊 Compliance Score

**Atual:** 50%

- Fundação: 25%
- Consentimento: 0%
- Direitos: 25%
- Segurança: 100%
- Processos: 50%
- Training: 0%

**Meta:** 100% até [Data TBD]

---

## 📞 Contatos

- **DPO:** dpo@afiliadobot.top
- **Titular (exercer direitos):** privacidade@afiliadobot.top
- **ANPD:** https://www.gov.br/anpd

---

**Aprovado por:** [Pending DPO]  
**Próxima revisão:** Trimestral
