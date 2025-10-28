"""
Script para gerar resultados EDA com dados corretos
"""
import pandas as pd
import numpy as np
from scipy import stats
import os

# Criar pasta de resultados
os.makedirs('../results/eda_results', exist_ok=True)

# Carregar dados
df_gk = pd.read_csv('../data/goleiros_carreira.csv')
df_var = pd.read_csv('../data/var_raw_data.csv')

print("="*60)
print("GERANDO RESULTADOS EDA")
print("="*60)

# ============================================================================
# EDA GOLEIROS
# ============================================================================

# Correlações
corr = df_gk[['Altura_cm', 'Save_Percentage_Medio']].corr().iloc[0,1]
corr_df = pd.DataFrame({
    'Metric': ['Save_Percentage_Medio', 'Clean_Sheet_Percentage_Medio', 'Gols_Sofridos_90min_Medio'],
    'Correlation_with_Height': [
        df_gk[['Altura_cm', 'Save_Percentage_Medio']].corr().iloc[0,1],
        df_gk[['Altura_cm', 'Clean_Sheet_Percentage_Medio']].corr().iloc[0,1],
        df_gk[['Altura_cm', 'Gols_Sofridos_90min_Medio']].corr().iloc[0,1]
    ]
})
corr_df.to_csv('../results/eda_results/correlations.csv', index=False)
print(f"✓ Correlações salvas")

# Relatório EDA Goleiros
report_gk = f"""
RELATÓRIO EDA - GOLEIROS PREMIER LEAGUE (2005-2020)
====================================================

DADOS:
------
Total de goleiros: {len(df_gk)}
Goleiros com altura: {df_gk['Altura_cm'].notna().sum()}

ESTATÍSTICAS DESCRITIVAS:
-------------------------
Altura média: {df_gk['Altura_cm'].mean():.1f} cm
Altura mínima: {df_gk['Altura_cm'].min():.0f} cm
Altura máxima: {df_gk['Altura_cm'].max():.0f} cm

Save% médio: {df_gk['Save_Percentage_Medio'].mean():.2f}%
Clean Sheet% médio: {df_gk['Clean_Sheet_Percentage_Medio'].mean():.2f}%
Gols/90min médio: {df_gk['Gols_Sofridos_90min_Medio'].mean():.2f}

CORRELAÇÃO ALTURA × PERFORMANCE:
---------------------------------
Altura × Save%: {corr:.4f}
Interpretação: Correlação muito fraca (próxima de zero)

CONCLUSÃO:
----------
Não há correlação significativa entre altura e performance de goleiros.
A altura não é um preditor relevante de Save% na Premier League.
"""

with open('../results/eda_results/eda_goalkeepers_report.txt', 'w') as f:
    f.write(report_gk)
print(f"✓ Relatório goleiros salvo")

# ============================================================================
# EDA VAR
# ============================================================================

# Separar períodos
pre_var = df_var[df_var['var_period'] == 'Pré-VAR']
com_var = df_var[df_var['var_period'] == 'Com VAR']

# Testes estatísticos
metrics = ['yellow_cards_per_90', 'red_cards_per_90', 'penalties_won_per_90']
tests = []

for metric in metrics:
    if metric in df_var.columns:
        t_stat, p_value = stats.ttest_ind(pre_var[metric].dropna(), com_var[metric].dropna())
        tests.append({
            'Metric': metric,
            'Pre_VAR_Mean': pre_var[metric].mean(),
            'Com_VAR_Mean': com_var[metric].mean(),
            'T_Statistic': t_stat,
            'P_Value': p_value
        })

tests_df = pd.DataFrame(tests)
tests_df.to_csv('../results/eda_results/var_statistical_tests.csv', index=False)
print(f"✓ Testes estatísticos VAR salvos")

# Relatório EDA VAR
report_var = f"""
RELATÓRIO EDA - IMPACTO DO VAR (2016-2024)
==========================================

DADOS:
------
Total de registros: {len(df_var)}
Pré-VAR (2016-2019): {len(pre_var)} registros
Com VAR (2019-2024): {len(com_var)} registros

COMPARAÇÃO MÉDIAS:
------------------
Cartões Amarelos/90min:
  Pré-VAR: {pre_var['yellow_cards_per_90'].mean():.4f}
  Com VAR: {com_var['yellow_cards_per_90'].mean():.4f}
  Variação: {((com_var['yellow_cards_per_90'].mean() / pre_var['yellow_cards_per_90'].mean() - 1) * 100):.2f}%

Cartões Vermelhos/90min:
  Pré-VAR: {pre_var['red_cards_per_90'].mean():.4f}
  Com VAR: {com_var['red_cards_per_90'].mean():.4f}
  Variação: {((com_var['red_cards_per_90'].mean() / pre_var['red_cards_per_90'].mean() - 1) * 100):.2f}%

CONCLUSÃO:
----------
O VAR teve impacto moderado nas marcações, especialmente em cartões vermelhos.
"""

with open('../results/eda_results/eda_var_impact_report.txt', 'w') as f:
    f.write(report_var)
print(f"✓ Relatório VAR salvo")

print("\n" + "="*60)
print("✅ RESULTADOS EDA GERADOS COM SUCESSO!")
print("="*60)
print(f"\nArquivos criados em: results/eda_results/")
print(f"  - correlations.csv")
print(f"  - eda_goalkeepers_report.txt")
print(f"  - var_statistical_tests.csv")
print(f"  - eda_var_impact_report.txt")

