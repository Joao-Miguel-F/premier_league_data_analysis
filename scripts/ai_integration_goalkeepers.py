#!/usr/bin/env python3
"""
Integração de IA - Análise de Goleiros da Premier League

OBJETIVO:
    Aplicar modelos de IA para enriquecer a análise de goleiros:
    1. Geração de insights narrativos via LLM
    2. Classificação de perfis de goleiros
    3. Sistema de recomendação para recrutamento

MODELOS UTILIZADOS:
    - OpenAI GPT (via API) para geração de texto
    - Análise estatística para classificação

AUTOR: AI Integration para Entrevista Técnica
DATA: 2025-10-27
"""

import pandas as pd
import numpy as np
import json
import os
from openai import OpenAI

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

DATA_DIR = "../data"
OUTPUT_DIR = "../data/ai_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Inicializar cliente OpenAI (API key já configurada em variável de ambiente)
client = OpenAI()

# ============================================================================
# FUNÇÕES DE IA
# ============================================================================

def load_analysis_data():
    """
    Carrega dados de análise exploratória.
    
    Returns:
        Tuple com (df_goleiros, correlações, estatísticas)
    """
    print("="*60)
    print("CARREGANDO DADOS DE ANÁLISE")
    print("="*60)
    
    df = pd.read_csv(f"{DATA_DIR}/goleiros_carreira.csv")
    
    # Calcular correlações básicas
    if 'Altura_cm' in df.columns and 'Save_Percentage_Medio' in df.columns:
        corr = df[['Altura_cm', 'Save_Percentage_Medio']].corr().iloc[0,1]
        corr_df = pd.DataFrame({
            'Metric': ['Save_Percentage_Medio'],
            'Correlation_with_Height': [corr]
        })
    else:
        corr_df = pd.DataFrame()
    
    print(f"\n✓ Dados de goleiros carregados: {len(df)} registros")
    print(f"✓ Correlações carregadas: {len(corr_df)} métricas")
    
    return df, corr_df

def generate_executive_summary(df, corr_df):
    """
    Usa LLM para gerar relatório executivo baseado nos dados.
    
    Args:
        df: DataFrame com dados de goleiros
        corr_df: DataFrame com correlações
    
    Returns:
        String com relatório gerado
    """
    print("\n" + "="*60)
    print("1. GERAÇÃO DE RELATÓRIO EXECUTIVO VIA LLM")
    print("="*60)
    
    # Preparar contexto para o LLM
    stats_summary = f"""
DADOS ANALISADOS:
- Total de goleiros: {len(df)}
- Altura média: {df['height_cm'].mean():.1f} cm
- Save% médio: {df['save_percentage'].mean():.2f}%
- Clean Sheet% médio: {df['clean_sheet_percentage'].mean():.2f}%

CORRELAÇÕES ENCONTRADAS:
{corr_df.to_string(index=False)}

INSIGHTS PRINCIPAIS:
- Correlação altura × Save%: {corr_df[corr_df['Métrica'] == 'Save Percentage']['Correlação'].values[0]:.4f}
- Nenhuma correlação significativa (todos p-values > 0.05)
- Goleiros mais baixos (< 190 cm) têm Clean Sheet% de 31.26%
- Goleiros mais altos (> 192 cm) têm Clean Sheet% de 24.16%
"""
    
    prompt = f"""Você é um analista de dados esportivos especializado em futebol. 

Analise os seguintes dados sobre goleiros da Premier League e gere um RELATÓRIO EXECUTIVO de 3-4 parágrafos para apresentar aos diretores de um clube de futebol.

{stats_summary}

O relatório deve:
1. Resumir as principais descobertas de forma clara
2. Explicar por que altura NÃO é um bom preditor de performance
3. Sugerir implicações práticas para recrutamento
4. Usar linguagem profissional mas acessível

Gere o relatório em português do Brasil."""
    
    print("\n📝 PROMPT ENVIADO AO LLM:")
    print("-"*60)
    print(prompt)
    
    print("\n🤖 GERANDO RELATÓRIO...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um analista de dados esportivos especializado em futebol."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        report = response.choices[0].message.content
        
        print("\n✅ RELATÓRIO GERADO:")
        print("-"*60)
        print(report)
        
        return report, prompt
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar relatório: {e}")
        return None, prompt

def classify_goalkeeper_profiles(df):
    """
    Classifica goleiros em perfis baseado em suas características.
    
    Args:
        df: DataFrame com dados de goleiros
    
    Returns:
        DataFrame com classificações
    """
    print("\n" + "="*60)
    print("2. CLASSIFICAÇÃO DE PERFIS DE GOLEIROS")
    print("="*60)
    
    # Criar cópia para não modificar original
    df_classified = df.copy()
    
    # Definir perfis baseados em métricas
    def classify_profile(row):
        save_pct = row['save_percentage']
        cs_pct = row['clean_sheet_percentage']
        height = row['height_cm']
        
        # Classificação baseada em performance
        if save_pct >= 75 and cs_pct >= 35:
            performance = "Elite"
        elif save_pct >= 72 and cs_pct >= 28:
            performance = "Acima da Média"
        elif save_pct >= 68:
            performance = "Média"
        else:
            performance = "Abaixo da Média"
        
        # Classificação baseada em altura
        if height < 188:
            height_class = "Baixo"
        elif height < 193:
            height_class = "Médio"
        else:
            height_class = "Alto"
        
        # Perfil combinado
        if performance == "Elite":
            if height_class == "Baixo":
                profile = "Técnico de Elite"
            elif height_class == "Alto":
                profile = "Completo de Elite"
            else:
                profile = "Equilibrado de Elite"
        elif performance == "Acima da Média":
            profile = f"Sólido ({height_class})"
        else:
            profile = f"Em Desenvolvimento ({height_class})"
        
        return pd.Series({
            'performance_level': performance,
            'height_class': height_class,
            'profile': profile
        })
    
    # Aplicar classificação
    classifications = df_classified.apply(classify_profile, axis=1)
    df_classified = pd.concat([df_classified, classifications], axis=1)
    
    # Estatísticas por perfil
    print("\n2.1. DISTRIBUIÇÃO DE PERFIS")
    print("-"*60)
    profile_counts = df_classified['profile'].value_counts()
    print(profile_counts)
    
    print("\n2.2. EXEMPLOS DE CADA PERFIL")
    print("-"*60)
    
    for profile in df_classified['profile'].unique()[:5]:  # Top 5 perfis
        examples = df_classified[df_classified['profile'] == profile].nlargest(2, 'save_percentage')
        if len(examples) > 0:
            print(f"\n{profile}:")
            for _, row in examples.iterrows():
                print(f"  - {row['player']} ({row['team']}, {row['season']}): "
                      f"Save% {row['save_percentage']:.1f}%, "
                      f"CS% {row['clean_sheet_percentage']:.1f}%, "
                      f"Altura {row['height_cm']:.0f}cm")
    
    return df_classified

def generate_recruitment_recommendations(df_classified):
    """
    Usa LLM para gerar recomendações de recrutamento baseadas nos perfis.
    
    Args:
        df_classified: DataFrame com goleiros classificados
    
    Returns:
        String com recomendações
    """
    print("\n" + "="*60)
    print("3. SISTEMA DE RECOMENDAÇÃO PARA RECRUTAMENTO")
    print("="*60)
    
    # Identificar top performers por perfil
    elite_goalkeepers = df_classified[
        df_classified['performance_level'] == 'Elite'
    ].nlargest(10, 'save_percentage')
    
    # Preparar contexto
    context = f"""
ANÁLISE DE MERCADO - GOLEIROS DE ELITE:

Top 10 Goleiros por Performance:
{elite_goalkeepers[['player', 'team', 'season', 'height_cm', 'save_percentage', 'clean_sheet_percentage', 'profile']].to_string(index=False)}

DESCOBERTA CHAVE:
- Não há correlação entre altura e performance (r = -0.0066)
- Goleiros "baixos" (< 190cm) têm melhor Clean Sheet% que "altos"
- Perfis técnicos são tão eficazes quanto perfis físicos
"""
    
    prompt = f"""Você é um diretor de futebol especializado em recrutamento de goleiros.

Com base na análise abaixo, crie um GUIA DE RECRUTAMENTO com 3 recomendações práticas para identificar goleiros de alto potencial, considerando que altura NÃO é um preditor confiável.

{context}

As recomendações devem:
1. Focar em métricas objetivas (Save%, Clean Sheet%)
2. Desafiar o mito da altura
3. Sugerir critérios alternativos
4. Ser acionáveis para scouts

Gere em português do Brasil, formato de lista numerada."""
    
    print("\n📝 PROMPT ENVIADO AO LLM:")
    print("-"*60)
    print(prompt[:500] + "...")
    
    print("\n🤖 GERANDO RECOMENDAÇÕES...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um diretor de futebol especializado em recrutamento."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        
        recommendations = response.choices[0].message.content
        
        print("\n✅ RECOMENDAÇÕES GERADAS:")
        print("-"*60)
        print(recommendations)
        
        return recommendations, prompt
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar recomendações: {e}")
        return None, prompt

def generate_player_scouting_report(df_classified, player_name):
    """
    Gera relatório de scouting individual usando LLM.
    
    Args:
        df_classified: DataFrame com goleiros classificados
        player_name: Nome do jogador
    
    Returns:
        String com relatório
    """
    print("\n" + "="*60)
    print(f"4. RELATÓRIO DE SCOUTING INDIVIDUAL - {player_name}")
    print("="*60)
    
    # Buscar dados do jogador
    player_data = df_classified[df_classified['player'] == player_name]
    
    if len(player_data) == 0:
        print(f"\n❌ Jogador '{player_name}' não encontrado")
        return None, None
    
    # Pegar melhor temporada
    best_season = player_data.nlargest(1, 'save_percentage').iloc[0]
    
    # Comparar com média
    avg_save = df_classified['save_percentage'].mean()
    avg_cs = df_classified['clean_sheet_percentage'].mean()
    avg_height = df_classified['height_cm'].mean()
    
    context = f"""
RELATÓRIO DE SCOUTING:

Jogador: {best_season['player']}
Time: {best_season['team']}
Temporada: {best_season['season']}
Idade: {best_season['age']} anos
Altura: {best_season['height_cm']:.0f} cm (Média da liga: {avg_height:.0f} cm)

ESTATÍSTICAS:
- Save%: {best_season['save_percentage']:.1f}% (Média da liga: {avg_save:.1f}%)
- Clean Sheet%: {best_season['clean_sheet_percentage']:.1f}% (Média da liga: {avg_cs:.1f}%)
- Jogos: {best_season['matches_played']:.0f}
- Gols sofridos/90min: {best_season['goals_against_per90']:.2f}

PERFIL: {best_season['profile']}
NÍVEL: {best_season['performance_level']}
"""
    
    prompt = f"""Você é um scout profissional de futebol.

Analise o seguinte goleiro e crie um RELATÓRIO DE SCOUTING de 2-3 parágrafos para apresentar ao diretor técnico.

{context}

O relatório deve:
1. Avaliar pontos fortes baseado nas estatísticas
2. Comentar sobre a altura (se relevante ou não)
3. Comparar com a média da liga
4. Dar uma recomendação final (contratar, monitorar, ou passar)

Use linguagem profissional de scouting. Gere em português do Brasil."""
    
    print("\n📝 PROMPT ENVIADO AO LLM:")
    print("-"*60)
    print(prompt[:400] + "...")
    
    print("\n🤖 GERANDO RELATÓRIO...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um scout profissional de futebol."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        report = response.choices[0].message.content
        
        print("\n✅ RELATÓRIO GERADO:")
        print("-"*60)
        print(report)
        
        return report, prompt
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar relatório: {e}")
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
    
    # Salvar relatório executivo
    if outputs.get('executive_summary'):
        with open(f"{output_dir}/ai_executive_summary.txt", 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RELATÓRIO EXECUTIVO GERADO POR IA\n")
            f.write("="*60 + "\n\n")
            f.write("PROMPT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['executive_summary_prompt'] + "\n\n")
            f.write("OUTPUT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['executive_summary'])
        print(f"✓ Relatório executivo salvo")
    
    # Salvar recomendações
    if outputs.get('recommendations'):
        with open(f"{output_dir}/ai_recruitment_recommendations.txt", 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RECOMENDAÇÕES DE RECRUTAMENTO GERADAS POR IA\n")
            f.write("="*60 + "\n\n")
            f.write("PROMPT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['recommendations_prompt'] + "\n\n")
            f.write("OUTPUT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['recommendations'])
        print(f"✓ Recomendações salvas")
    
    # Salvar relatório de scouting
    if outputs.get('scouting_report'):
        with open(f"{output_dir}/ai_scouting_report.txt", 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RELATÓRIO DE SCOUTING GERADO POR IA\n")
            f.write("="*60 + "\n\n")
            f.write("PROMPT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['scouting_prompt'] + "\n\n")
            f.write("OUTPUT:\n")
            f.write("-"*60 + "\n")
            f.write(outputs['scouting_report'])
        print(f"✓ Relatório de scouting salvo")
    
    # Salvar classificações
    if 'classifications' in outputs and outputs['classifications'] is not None:
        outputs['classifications'].to_csv(
            f"{output_dir}/goalkeeper_classifications.csv",
            index=False
        )
        print(f"✓ Classificações salvas")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Executa integração de IA completa.
    """
    print("\n" + "="*60)
    print("INTEGRAÇÃO DE IA - ANÁLISE DE GOLEIROS")
    print("="*60)
    
    outputs = {}
    
    # Carregar dados
    df, corr_df = load_analysis_data()
    
    # 1. Gerar relatório executivo
    summary, summary_prompt = generate_executive_summary(df, corr_df)
    outputs['executive_summary'] = summary
    outputs['executive_summary_prompt'] = summary_prompt
    
    # 2. Classificar perfis
    df_classified = classify_goalkeeper_profiles(df)
    outputs['classifications'] = df_classified
    
    # 3. Gerar recomendações de recrutamento
    recommendations, rec_prompt = generate_recruitment_recommendations(df_classified)
    outputs['recommendations'] = recommendations
    outputs['recommendations_prompt'] = rec_prompt
    
    # 4. Gerar relatório de scouting individual
    # Escolher um top performer
    top_player = df_classified.nlargest(1, 'save_percentage').iloc[0]['player']
    scouting, scout_prompt = generate_player_scouting_report(df_classified, top_player)
    outputs['scouting_report'] = scouting
    outputs['scouting_prompt'] = scout_prompt
    
    # Salvar outputs
    save_ai_outputs(outputs, OUTPUT_DIR)
    
    print("\n" + "="*60)
    print("✓ INTEGRAÇÃO DE IA CONCLUÍDA!")
    print("="*60)
    print(f"\nArquivos salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

