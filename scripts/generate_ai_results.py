"""
Script para gerar resultados de IA com dados corretos
"""
import pandas as pd
import os
from openai import OpenAI

# Criar pasta de resultados
os.makedirs('../results/ai_results', exist_ok=True)

# Inicializar OpenAI
client = OpenAI()

# Carregar dados
df_gk = pd.read_csv('../data/goleiros_carreira.csv')
df_var_comp = pd.read_csv('../data/var_comparison.csv')

print("="*60)
print("GERANDO RESULTADOS IA")
print("="*60)

# ============================================================================
# IA GOLEIROS
# ============================================================================

# Calcular estatísticas
corr = df_gk[['Altura_cm', 'Save_Percentage_Medio']].corr().iloc[0,1]
altura_media = df_gk['Altura_cm'].mean()
save_medio = df_gk['Save_Percentage_Medio'].mean()

# Prompt para relatório executivo
prompt_exec = f"""
Você é um analista de dados esportivos. Analise os seguintes dados de {len(df_gk)} goleiros da Premier League (2005-2020):

- Altura média: {altura_media:.1f} cm
- Save% médio: {save_medio:.2f}%
- Correlação Altura × Save%: {corr:.4f}

Gere um RELATÓRIO EXECUTIVO de 3-4 parágrafos para diretores de clube, explicando:
1. O que os dados mostram
2. Implicações para recrutamento
3. Recomendações práticas

Seja direto, profissional e acionável.
"""

print("Gerando relatório executivo...")
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": prompt_exec}],
    temperature=0.7,
    max_tokens=500
)

exec_summary = response.choices[0].message.content

with open('../results/ai_results/ai_executive_summary.txt', 'w') as f:
    f.write(exec_summary)
print("✓ Relatório executivo salvo")

# Prompt para recomendações de recrutamento
prompt_recruit = f"""
Com base na análise de {len(df_gk)} goleiros da Premier League mostrando correlação de {corr:.4f} entre altura e Save%, 
gere 5 RECOMENDAÇÕES PRÁTICAS para scouts e diretores de futebol sobre recrutamento de goleiros.

Seja específico e acionável.
"""

print("Gerando recomendações de recrutamento...")
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": prompt_recruit}],
    temperature=0.7,
    max_tokens=400
)

recruit_rec = response.choices[0].message.content

with open('../results/ai_results/ai_recruitment_recommendations.txt', 'w') as f:
    f.write(recruit_rec)
print("✓ Recomendações de recrutamento salvas")

# ============================================================================
# IA VAR
# ============================================================================

# Extrair dados de comparação
if len(df_var_comp) >= 2:
    pre_var_row = df_var_comp[df_var_comp['Período'] == 'Pré-VAR'].iloc[0]
    com_var_row = df_var_comp[df_var_comp['Período'] == 'Com VAR'].iloc[0]
    
    var_red = ((com_var_row['Média Vermelhos/90min'] / pre_var_row['Média Vermelhos/90min'] - 1) * 100)
    var_yellow = ((com_var_row['Média Amarelos/90min'] / pre_var_row['Média Amarelos/90min'] - 1) * 100)
    
    # Prompt para relatório VAR
    prompt_var = f"""
Você é um analista de políticas esportivas. Analise o impacto do VAR na Premier League:

- Cartões Vermelhos: +{var_red:.1f}%
- Cartões Amarelos: +{var_yellow:.1f}%

Gere um RELATÓRIO para stakeholders (3-4 parágrafos) explicando:
1. O que mudou com o VAR
2. Implicações para clubes e jogadores
3. Recomendações estratégicas

Seja profissional e baseado em dados.
"""

    print("Gerando relatório VAR...")
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt_var}],
        temperature=0.7,
        max_tokens=500
    )
    
    var_report = response.choices[0].message.content
    
    with open('../results/ai_results/ai_var_stakeholder_report.txt', 'w') as f:
        f.write(var_report)
    print("✓ Relatório VAR salvo")

print("\n" + "="*60)
print("✅ RESULTADOS IA GERADOS COM SUCESSO!")
print("="*60)
print(f"\nArquivos criados em: results/ai_results/")
print(f"  - ai_executive_summary.txt")
print(f"  - ai_recruitment_recommendations.txt")
print(f"  - ai_var_stakeholder_report.txt")

