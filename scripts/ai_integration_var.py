#!/usr/bin/env python3
"""
Integração de IA - Impacto do VAR na Premier League

OBJETIVO:
    Aplicar modelos de IA para enriquecer a análise do impacto do VAR:
    1. Geração de relatório executivo para stakeholders
    2. Análise preditiva de marcações futuras
    3. Geração de insights narrativos

MODELOS UTILIZADOS:
    - OpenAI GPT (via API) para geração de texto e análise
    - Regressão linear simples para predição

AUTOR: AI Integration para Entrevista Técnica
DATA: 2025-10-27
"""

import pandas as pd
import numpy as np
import os
from openai import OpenAI

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

DATA_DIR = "../data"
OUTPUT_DIR = "../data/ai_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Inicializar cliente OpenAI
client = OpenAI()

# ============================================================================
# FUNÇÕES DE IA
# ============================================================================

def load_var_data():
    """
    Carrega dados de análise do VAR.
    
    Returns:
        Tuple com (df_raw, df_comparison, df_analysis)
    """
    print("="*60)
    print("CARREGANDO DADOS DE ANÁLISE DO VAR")
    print("="*60)
    
    df_raw = pd.read_csv(f"{DATA_DIR}/var_raw_data.csv")
    df_comparison = pd.read_csv(f"{DATA_DIR}/var_comparison.csv")
    df_analysis = pd.read_csv(f"{DATA_DIR}/var_analysis.csv")
    
    print(f"\n✓ Dados brutos carregados: {len(df_raw)} registros")
    print(f"✓ Análise comparativa carregada")
    print(f"✓ Análise de impacto carregada")
    
    return df_raw, df_comparison, df_analysis

def generate_stakeholder_report(df_comparison, df_analysis):
    """
    Gera relatório executivo para stakeholders (dirigentes, mídia).
    
    Args:
        df_comparison: DataFrame com comparação de períodos
        df_analysis: DataFrame com análise de impacto
    
    Returns:
        Tuple (relatório, prompt)
    """
    print("\n" + "="*60)
    print("1. RELATÓRIO EXECUTIVO PARA STAKEHOLDERS")
    print("="*60)
    
    # Preparar contexto
    context = f"""
ANÁLISE DO IMPACTO DO VAR NA PREMIER LEAGUE

DADOS COMPARATIVOS:
{df_comparison.to_string(index=False)}

VARIAÇÕES IDENTIFICADAS:
{df_analysis.to_string(index=False)}

CONTEXTO:
- O VAR foi introduzido na temporada 2019-20
- Período analisado: 2016-2024 (3 temporadas pré-VAR, 5 com VAR)
- Total de 160 registros de times analisados
"""
    
    prompt = f"""Você é um analista de dados esportivos da Premier League.

Crie um RELATÓRIO EXECUTIVO de 3-4 parágrafos sobre o impacto do VAR para apresentar aos dirigentes da liga e à mídia esportiva.

{context}

O relatório deve:
1. Resumir os principais achados de forma clara e objetiva
2. Destacar o impacto mais significativo (cartões vermelhos +21.45%)
3. Explicar por que pênaltis permaneceram estáveis
4. Concluir se o VAR está cumprindo seu objetivo

Use linguagem profissional mas acessível. Gere em português do Brasil."""
    
    print("\n📝 PROMPT ENVIADO AO LLM:")
    print("-"*60)
    print(prompt[:500] + "...")
    
    print("\n🤖 GERANDO RELATÓRIO...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um analista de dados esportivos da Premier League."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        
        report = response.choices[0].message.content
        
        print("\n✅ RELATÓRIO GERADO:")
        print("-"*60)
        print(report)
        
        return report, prompt
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar relatório: {e}")
        return None, prompt

def predict_future_trends(df_raw):
    """
    Usa análise preditiva simples para estimar tendências futuras.
    
    Args:
        df_raw: DataFrame com dados brutos
    
    Returns:
        Dict com predições
    """
    print("\n" + "="*60)
    print("2. ANÁLISE PREDITIVA DE TENDÊNCIAS")
    print("="*60)
    
    # Filtrar período Com VAR
    df_var = df_raw[df_raw['var_period'] == 'Com VAR'].copy()
    
    # Agrupar por temporada
    temporal = df_var.groupby('season_year').agg({
        'yellow_cards_per_90': 'mean',
        'red_cards_per_90': 'mean',
        'penalties_won_per_90': 'mean'
    }).reset_index()
    
    temporal = temporal.sort_values('season_year')
    
    print("\n2.1. DADOS HISTÓRICOS (COM VAR)")
    print("-"*60)
    print(temporal.to_string(index=False))
    
    # Predições simples usando regressão linear
    predictions = {}
    
    for metric in ['yellow_cards_per_90', 'red_cards_per_90', 'penalties_won_per_90']:
        # Criar índice numérico
        X = np.arange(len(temporal)).reshape(-1, 1)
        y = temporal[metric].values
        
        # Regressão linear simples
        coeffs = np.polyfit(X.flatten(), y, 1)
        
        # Predição para próximas 2 temporadas
        next_seasons = np.array([len(temporal), len(temporal) + 1]).reshape(-1, 1)
        predictions[metric] = {
            'current_avg': y.mean(),
            'trend': 'crescente' if coeffs[0] > 0 else 'decrescente',
            'rate': coeffs[0],
            'next_season': coeffs[0] * next_seasons[0][0] + coeffs[1],
            'season_after': coeffs[0] * next_seasons[1][0] + coeffs[1]
        }
    
    print("\n2.2. PREDIÇÕES PARA PRÓXIMAS TEMPORADAS")
    print("-"*60)
    
    for metric, pred in predictions.items():
        metric_name = metric.replace('_', ' ').title()
        print(f"\n{metric_name}:")
        print(f"  Média atual: {pred['current_avg']:.4f}")
        print(f"  Tendência: {pred['trend']}")
        print(f"  Taxa de mudança: {pred['rate']:.4f} por temporada")
        print(f"  Predição 2024-25: {pred['next_season']:.4f}")
        print(f"  Predição 2025-26: {pred['season_after']:.4f}")
    
    return predictions

def generate_ai_insights(df_comparison, df_analysis, predictions):
    """
    Usa LLM para gerar insights narrativos sobre as predições.
    
    Args:
        df_comparison: DataFrame com comparação
        df_analysis: DataFrame com análise
        predictions: Dict com predições
    
    Returns:
        Tuple (insights, prompt)
    """
    print("\n" + "="*60)
    print("3. GERAÇÃO DE INSIGHTS NARRATIVOS COM IA")
    print("="*60)
    
    # Preparar contexto
    pred_summary = f"""
PREDIÇÕES PARA PRÓXIMAS TEMPORADAS:

Cartões Amarelos/90min:
- Tendência: {predictions['yellow_cards_per_90']['trend']}
- Predição 2024-25: {predictions['yellow_cards_per_90']['next_season']:.4f}
- Predição 2025-26: {predictions['yellow_cards_per_90']['season_after']:.4f}

Cartões Vermelhos/90min:
- Tendência: {predictions['red_cards_per_90']['trend']}
- Predição 2024-25: {predictions['red_cards_per_90']['next_season']:.4f}
- Predição 2025-26: {predictions['red_cards_per_90']['season_after']:.4f}

Pênaltis a Favor/90min:
- Tendência: {predictions['penalties_won_per_90']['trend']}
- Predição 2024-25: {predictions['penalties_won_per_90']['next_season']:.4f}
- Predição 2025-26: {predictions['penalties_won_per_90']['season_after']:.4f}

IMPACTO HISTÓRICO DO VAR:
{df_analysis.to_string(index=False)}
"""
    
    prompt = f"""Você é um analista preditivo de futebol especializado em arbitragem.

Com base nas predições abaixo, gere 3 INSIGHTS ESTRATÉGICOS sobre o futuro do VAR na Premier League.

{pred_summary}

Os insights devem:
1. Interpretar as tendências identificadas
2. Explicar possíveis causas (ex: árbitros ficando mais rigorosos)
3. Sugerir implicações para clubes e jogadores
4. Ser acionáveis e práticos

Gere em formato de lista numerada, em português do Brasil."""
    
    print("\n📝 PROMPT ENVIADO AO LLM:")
    print("-"*60)
    print(prompt[:400] + "...")
    
    print("\n🤖 GERANDO INSIGHTS...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um analista preditivo de futebol."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        insights = response.choices[0].message.content
        
        print("\n✅ INSIGHTS GERADOS:")
        print("-"*60)
        print(insights)
        
        return insights, prompt
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar insights: {e}")
        return None, prompt

def generate_policy_recommendations(df_analysis):
    """
    Gera recomendações de política para a liga usando LLM.
    
    Args:
        df_analysis: DataFrame com análise de impacto
    
    Returns:
        Tuple (recomendações, prompt)
    """
    print("\n" + "="*60)
    print("4. RECOMENDAÇÕES DE POLÍTICA PARA A LIGA")
    print("="*60)
    
    context = f"""
IMPACTO DO VAR IDENTIFICADO:
{df_analysis.to_string(index=False)}

DESCOBERTAS PRINCIPAIS:
- Cartões vermelhos aumentaram 21.45% (impacto significativo)
- Cartões amarelos aumentaram 6.44% (impacto moderado)
- Pênaltis permaneceram estáveis (+1-2%)
- Faltas não mudaram

CONTEXTO:
- O VAR foi introduzido para corrigir "erros claros e óbvios"
- Há debates sobre tempo de jogo perdido com revisões
- Alguns criticam excesso de intervenções, outros pedem mais
"""
    
    prompt = f"""Você é um consultor de políticas esportivas da IFAB (International Football Association Board).

Com base na análise do impacto do VAR na Premier League, crie 3 RECOMENDAÇÕES DE POLÍTICA para otimizar o uso do VAR.

{context}

As recomendações devem:
1. Ser baseadas em evidências dos dados
2. Equilibrar precisão e fluidez do jogo
3. Considerar a percepção de jogadores, técnicos e torcedores
4. Ser implementáveis na prática

Gere em formato de lista numerada com justificativa, em português do Brasil."""
    
    print("\n📝 PROMPT ENVIADO AO LLM:")
    print("-"*60)
    print(prompt[:400] + "...")
    
    print("\n🤖 GERANDO RECOMENDAÇÕES...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um consultor de políticas esportivas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        
        recommendations = response.choices[0].message.content
        
        print("\n✅ RECOMENDAÇÕES GERADAS:")
        print("-"*60)
        print(recommendations)
        
        return recommendations, prompt
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar recomendações: {e}")
        return None, prompt

def save_ai_outputs(outputs, output_dir):
    """
    Salva todos os outputs de IA.
    
    Args:
        outputs: Dict com outputs gerados
        output_dir: Diretório de saída
    """
    print("\n" + "="*60)
    print("SALVANDO OUTPUTS DE IA")
    print("="*60)
    
    # Relatório para stakeholders
    if outputs.get('stakeholder_report'):
        with open(f"{output_dir}/ai_var_stakeholder_report.txt", 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RELATÓRIO EXECUTIVO VAR - GERADO POR IA\n")
            f.write("="*60 + "\n\n")
            f.write("PROMPT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['stakeholder_prompt'] + "\n\n")
            f.write("OUTPUT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['stakeholder_report'])
        print(f"✓ Relatório para stakeholders salvo")
    
    # Predições
    if outputs.get('predictions'):
        pred_df = pd.DataFrame(outputs['predictions']).T
        pred_df.to_csv(f"{output_dir}/ai_var_predictions.csv")
        print(f"✓ Predições salvas")
    
    # Insights
    if outputs.get('insights'):
        with open(f"{output_dir}/ai_var_insights.txt", 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("INSIGHTS ESTRATÉGICOS - GERADOS POR IA\n")
            f.write("="*60 + "\n\n")
            f.write("PROMPT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['insights_prompt'] + "\n\n")
            f.write("OUTPUT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['insights'])
        print(f"✓ Insights estratégicos salvos")
    
    # Recomendações de política
    if outputs.get('policy_recommendations'):
        with open(f"{output_dir}/ai_var_policy_recommendations.txt", 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RECOMENDAÇÕES DE POLÍTICA - GERADAS POR IA\n")
            f.write("="*60 + "\n\n")
            f.write("PROMPT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['policy_prompt'] + "\n\n")
            f.write("OUTPUT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['policy_recommendations'])
        print(f"✓ Recomendações de política salvas")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Executa integração de IA completa para análise do VAR.
    """
    print("\n" + "="*60)
    print("INTEGRAÇÃO DE IA - IMPACTO DO VAR")
    print("="*60)
    
    outputs = {}
    
    # Carregar dados
    df_raw, df_comparison, df_analysis = load_var_data()
    
    # 1. Gerar relatório para stakeholders
    report, report_prompt = generate_stakeholder_report(df_comparison, df_analysis)
    outputs['stakeholder_report'] = report
    outputs['stakeholder_prompt'] = report_prompt
    
    # 2. Análise preditiva
    predictions = predict_future_trends(df_raw)
    outputs['predictions'] = predictions
    
    # 3. Gerar insights narrativos
    insights, insights_prompt = generate_ai_insights(df_comparison, df_analysis, predictions)
    outputs['insights'] = insights
    outputs['insights_prompt'] = insights_prompt
    
    # 4. Gerar recomendações de política
    policy, policy_prompt = generate_policy_recommendations(df_analysis)
    outputs['policy_recommendations'] = policy
    outputs['policy_prompt'] = policy_prompt
    
    # Salvar outputs
    save_ai_outputs(outputs, OUTPUT_DIR)
    
    print("\n" + "="*60)
    print("✓ INTEGRAÇÃO DE IA CONCLUÍDA!")
    print("="*60)
    print(f"\nArquivos salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

