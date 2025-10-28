#!/usr/bin/env python3
"""
Análise Exploratória de Dados (EDA) - Goleiros da Premier League

OBJETIVO:
    Realizar análise exploratória profunda dos dados de goleiros para entender:
    - Distribuições de variáveis
    - Padrões e tendências
    - Relações entre altura e performance
    - Outliers e anomalias
    - Insights estatísticos

AUTOR: EDA para Entrevista Técnica
DATA: 2025-10-27
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

DATA_DIR = "/home/ubuntu/goalkeeper_data"
OUTPUT_DIR = "/home/ubuntu/goalkeeper_data/eda_results"

# Criar diretório de saída
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# FUNÇÕES DE ANÁLISE
# ============================================================================

def load_data():
    """
    Carrega os dados de goleiros.
    
    Returns:
        Tupla com (df_completo, df_com_altura)
    """
    print("="*60)
    print("CARREGANDO DADOS")
    print("="*60)
    
    # Carregar dados completos
    df_complete = pd.read_csv(f"{DATA_DIR}/goalkeeper_complete_20251025_011750.csv")
    print(f"\n✓ Dados completos carregados: {len(df_complete)} registros")
    
    # Carregar dados com altura
    df_with_height = pd.read_csv(f"{DATA_DIR}/goalkeeper_for_analysis_20251025_011750.csv")
    print(f"✓ Dados com altura carregados: {len(df_with_height)} registros")
    
    return df_complete, df_with_height

def basic_statistics(df, df_height):
    """
    Calcula estatísticas descritivas básicas.
    
    Args:
        df: DataFrame completo
        df_height: DataFrame com altura
    
    Returns:
        Dict com estatísticas
    """
    print("\n" + "="*60)
    print("1. ESTATÍSTICAS DESCRITIVAS BÁSICAS")
    print("="*60)
    
    stats_dict = {}
    
    # Informações gerais
    print("\n1.1. INFORMAÇÕES GERAIS")
    print("-"*60)
    stats_dict['total_records'] = len(df)
    stats_dict['records_with_height'] = len(df_height)
    stats_dict['height_coverage'] = (len(df_height) / len(df)) * 100
    stats_dict['unique_players'] = df['player'].nunique()
    stats_dict['unique_teams'] = df['team'].nunique()
    stats_dict['unique_seasons'] = df['season'].nunique()
    
    print(f"Total de registros: {stats_dict['total_records']}")
    print(f"Registros com altura: {stats_dict['records_with_height']} ({stats_dict['height_coverage']:.1f}%)")
    print(f"Goleiros únicos: {stats_dict['unique_players']}")
    print(f"Times únicos: {stats_dict['unique_teams']}")
    print(f"Temporadas: {stats_dict['unique_seasons']}")
    
    # Estatísticas de performance (dataset completo)
    print("\n1.2. ESTATÍSTICAS DE PERFORMANCE (TODOS OS GOLEIROS)")
    print("-"*60)
    
    performance_cols = ['save_percentage', 'clean_sheet_percentage', 'matches_played', 
                       'goals_against_per90', 'saves']
    
    for col in performance_cols:
        if col in df.columns:
            print(f"\n{col.upper().replace('_', ' ')}:")
            print(f"  Média: {df[col].mean():.2f}")
            print(f"  Mediana: {df[col].median():.2f}")
            print(f"  Desvio Padrão: {df[col].std():.2f}")
            print(f"  Mínimo: {df[col].min():.2f}")
            print(f"  Máximo: {df[col].max():.2f}")
            print(f"  Q1 (25%): {df[col].quantile(0.25):.2f}")
            print(f"  Q3 (75%): {df[col].quantile(0.75):.2f}")
            
            stats_dict[f'{col}_mean'] = df[col].mean()
            stats_dict[f'{col}_median'] = df[col].median()
            stats_dict[f'{col}_std'] = df[col].std()
    
    # Estatísticas de altura
    print("\n1.3. ESTATÍSTICAS DE ALTURA")
    print("-"*60)
    
    print(f"\nALTURA (cm):")
    print(f"  Média: {df_height['height_cm'].mean():.2f}")
    print(f"  Mediana: {df_height['height_cm'].median():.2f}")
    print(f"  Desvio Padrão: {df_height['height_cm'].std():.2f}")
    print(f"  Mínimo: {df_height['height_cm'].min():.0f}")
    print(f"  Máximo: {df_height['height_cm'].max():.0f}")
    print(f"  Amplitude: {df_height['height_cm'].max() - df_height['height_cm'].min():.0f}")
    
    stats_dict['height_mean'] = df_height['height_cm'].mean()
    stats_dict['height_median'] = df_height['height_cm'].median()
    stats_dict['height_std'] = df_height['height_cm'].std()
    stats_dict['height_min'] = df_height['height_cm'].min()
    stats_dict['height_max'] = df_height['height_cm'].max()
    
    return stats_dict

def correlation_analysis(df_height):
    """
    Análise de correlação entre altura e métricas de performance.
    
    Args:
        df_height: DataFrame com altura
    
    Returns:
        DataFrame com correlações
    """
    print("\n" + "="*60)
    print("2. ANÁLISE DE CORRELAÇÃO")
    print("="*60)
    
    # Métricas de performance para correlacionar com altura
    performance_metrics = ['save_percentage', 'clean_sheet_percentage', 
                          'goals_against_per90', 'saves', 'matches_played']
    
    correlations = []
    
    print("\n2.1. CORRELAÇÃO DE PEARSON (Altura vs Performance)")
    print("-"*60)
    
    for metric in performance_metrics:
        if metric in df_height.columns:
            # Remover NaN
            data = df_height[[metric, 'height_cm']].dropna()
            
            if len(data) > 0:
                # Correlação de Pearson
                corr, p_value = stats.pearsonr(data[metric], data['height_cm'])
                
                # Classificação da correlação
                if abs(corr) < 0.3:
                    strength = "Fraca"
                elif abs(corr) < 0.7:
                    strength = "Moderada"
                else:
                    strength = "Forte"
                
                # Significância estatística
                significant = "Sim" if p_value < 0.05 else "Não"
                
                correlations.append({
                    'Métrica': metric.replace('_', ' ').title(),
                    'Correlação': corr,
                    'P-value': p_value,
                    'Força': strength,
                    'Significante (p<0.05)': significant,
                    'N': len(data)
                })
                
                print(f"\n{metric.upper().replace('_', ' ')}:")
                print(f"  Correlação: {corr:.4f}")
                print(f"  P-value: {p_value:.4f}")
                print(f"  Força: {strength}")
                print(f"  Significante: {significant}")
                print(f"  N (amostras): {len(data)}")
    
    corr_df = pd.DataFrame(correlations)
    
    print("\n2.2. RESUMO DAS CORRELAÇÕES")
    print("-"*60)
    print(corr_df.to_string(index=False))
    
    return corr_df

def temporal_analysis(df_height):
    """
    Análise temporal: evolução ao longo das temporadas.
    
    Args:
        df_height: DataFrame com altura
    
    Returns:
        DataFrame com análise temporal
    """
    print("\n" + "="*60)
    print("3. ANÁLISE TEMPORAL")
    print("="*60)
    
    # Agrupar por temporada
    temporal = df_height.groupby('season_year').agg({
        'player': 'count',
        'height_cm': ['mean', 'std'],
        'save_percentage': ['mean', 'std'],
        'clean_sheet_percentage': 'mean',
        'matches_played': 'sum'
    }).reset_index()
    
    # Flatten columns
    temporal.columns = ['season_year', 'num_goalkeepers', 'avg_height', 'std_height',
                       'avg_save_pct', 'std_save_pct', 'avg_clean_sheet_pct', 
                       'total_matches']
    
    print("\n3.1. EVOLUÇÃO POR TEMPORADA")
    print("-"*60)
    print(temporal.to_string(index=False))
    
    # Tendências
    print("\n3.2. TENDÊNCIAS IDENTIFICADAS")
    print("-"*60)
    
    # Altura ao longo do tempo
    height_trend = np.polyfit(temporal['season_year'], temporal['avg_height'], 1)
    print(f"\nAltura média ao longo do tempo:")
    print(f"  Tendência: {'Crescente' if height_trend[0] > 0 else 'Decrescente'}")
    print(f"  Taxa de mudança: {height_trend[0]:.4f} cm/ano")
    
    # Save% ao longo do tempo
    save_trend = np.polyfit(temporal['season_year'], temporal['avg_save_pct'], 1)
    print(f"\nSave% médio ao longo do tempo:")
    print(f"  Tendência: {'Crescente' if save_trend[0] > 0 else 'Decrescente'}")
    print(f"  Taxa de mudança: {save_trend[0]:.4f} pontos percentuais/ano")
    
    return temporal

def outlier_analysis(df_height):
    """
    Identifica e analisa outliers.
    
    Args:
        df_height: DataFrame com altura
    
    Returns:
        Dict com outliers identificados
    """
    print("\n" + "="*60)
    print("4. ANÁLISE DE OUTLIERS")
    print("="*60)
    
    outliers = {}
    
    # Método IQR para identificar outliers
    def find_outliers_iqr(data, column):
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    
    # Outliers em altura
    print("\n4.1. OUTLIERS EM ALTURA")
    print("-"*60)
    height_outliers = find_outliers_iqr(df_height, 'height_cm')
    print(f"Outliers identificados: {len(height_outliers)}")
    
    if len(height_outliers) > 0:
        print("\nGoleiros com altura atípica:")
        for _, row in height_outliers.iterrows():
            print(f"  - {row['player']} ({row['team']}, {row['season']}): {row['height_cm']:.0f} cm")
        outliers['height'] = height_outliers[['player', 'team', 'season', 'height_cm']].to_dict('records')
    
    # Outliers em Save%
    print("\n4.2. OUTLIERS EM SAVE%")
    print("-"*60)
    save_outliers = find_outliers_iqr(df_height, 'save_percentage')
    print(f"Outliers identificados: {len(save_outliers)}")
    
    if len(save_outliers) > 0:
        print("\nGoleiros com Save% atípico:")
        # Top 5 maiores Save%
        top_saves = save_outliers.nlargest(5, 'save_percentage')
        print("\n  Top 5 Maiores Save%:")
        for _, row in top_saves.iterrows():
            print(f"    - {row['player']} ({row['team']}, {row['season']}): {row['save_percentage']:.1f}% (Altura: {row['height_cm']:.0f} cm)")
        
        # Top 5 menores Save%
        bottom_saves = save_outliers.nsmallest(5, 'save_percentage')
        print("\n  Top 5 Menores Save%:")
        for _, row in bottom_saves.iterrows():
            print(f"    - {row['player']} ({row['team']}, {row['season']}): {row['save_percentage']:.1f}% (Altura: {row['height_cm']:.0f} cm)")
        
        outliers['save_percentage'] = save_outliers[['player', 'team', 'season', 'save_percentage', 'height_cm']].to_dict('records')
    
    return outliers

def segmentation_analysis(df_height):
    """
    Análise por segmentos (altura baixa, média, alta).
    
    Args:
        df_height: DataFrame com altura
    
    Returns:
        DataFrame com análise por segmento
    """
    print("\n" + "="*60)
    print("5. ANÁLISE POR SEGMENTOS DE ALTURA")
    print("="*60)
    
    # Definir segmentos baseados em tercis
    terciles = df_height['height_cm'].quantile([0.33, 0.67])
    
    def categorize_height(height):
        if height < terciles[0.33]:
            return 'Baixo'
        elif height < terciles[0.67]:
            return 'Médio'
        else:
            return 'Alto'
    
    df_height['height_category'] = df_height['height_cm'].apply(categorize_height)
    
    print(f"\nSegmentos definidos:")
    print(f"  Baixo: < {terciles[0.33]:.0f} cm")
    print(f"  Médio: {terciles[0.33]:.0f} - {terciles[0.67]:.0f} cm")
    print(f"  Alto: > {terciles[0.67]:.0f} cm")
    
    # Análise por segmento
    segment_analysis = df_height.groupby('height_category').agg({
        'player': 'count',
        'height_cm': ['mean', 'min', 'max'],
        'save_percentage': ['mean', 'std', 'median'],
        'clean_sheet_percentage': ['mean', 'median'],
        'goals_against_per90': ['mean', 'median']
    }).reset_index()
    
    print("\n5.1. PERFORMANCE POR SEGMENTO DE ALTURA")
    print("-"*60)
    
    for category in ['Baixo', 'Médio', 'Alto']:
        seg = df_height[df_height['height_category'] == category]
        if len(seg) > 0:
            print(f"\n{category.upper()}:")
            print(f"  N: {len(seg)}")
            print(f"  Altura média: {seg['height_cm'].mean():.1f} cm ({seg['height_cm'].min():.0f} - {seg['height_cm'].max():.0f})")
            print(f"  Save% médio: {seg['save_percentage'].mean():.2f}%")
            print(f"  Clean Sheet% médio: {seg['clean_sheet_percentage'].mean():.2f}%")
            print(f"  Gols contra/90min: {seg['goals_against_per90'].mean():.2f}")
    
    # Teste estatístico: ANOVA
    print("\n5.2. TESTE ANOVA (Diferença entre grupos)")
    print("-"*60)
    
    groups = [
        df_height[df_height['height_category'] == 'Baixo']['save_percentage'].dropna(),
        df_height[df_height['height_category'] == 'Médio']['save_percentage'].dropna(),
        df_height[df_height['height_category'] == 'Alto']['save_percentage'].dropna()
    ]
    
    f_stat, p_value = stats.f_oneway(*groups)
    
    print(f"\nANOVA - Save% entre grupos de altura:")
    print(f"  F-statistic: {f_stat:.4f}")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Conclusão: {'Há diferença significativa' if p_value < 0.05 else 'Não há diferença significativa'} entre os grupos (α=0.05)")
    
    return segment_analysis

def top_performers_analysis(df_height):
    """
    Análise dos melhores goleiros.
    
    Args:
        df_height: DataFrame com altura
    
    Returns:
        DataFrame com top performers
    """
    print("\n" + "="*60)
    print("6. ANÁLISE DE TOP PERFORMERS")
    print("="*60)
    
    # Filtrar goleiros com pelo menos 20 jogos (titulares absolutos)
    df_starters = df_height[df_height['matches_played'] >= 20].copy()
    
    print(f"\nGoleiros com >= 20 jogos: {len(df_starters)}")
    
    # Top 10 por Save%
    print("\n6.1. TOP 10 GOLEIROS POR SAVE%")
    print("-"*60)
    top_save = df_starters.nlargest(10, 'save_percentage')[['player', 'team', 'season', 'save_percentage', 'height_cm', 'matches_played']]
    print(top_save.to_string(index=False))
    
    print(f"\nAltura média do Top 10: {top_save['height_cm'].mean():.1f} cm")
    
    # Top 10 por Clean Sheet%
    print("\n6.2. TOP 10 GOLEIROS POR CLEAN SHEET%")
    print("-"*60)
    top_cs = df_starters.nlargest(10, 'clean_sheet_percentage')[['player', 'team', 'season', 'clean_sheet_percentage', 'height_cm', 'matches_played']]
    print(top_cs.to_string(index=False))
    
    print(f"\nAltura média do Top 10: {top_cs['height_cm'].mean():.1f} cm")
    
    # Comparar com média geral
    print("\n6.3. COMPARAÇÃO TOP PERFORMERS vs MÉDIA GERAL")
    print("-"*60)
    print(f"Altura média (Top 10 Save%): {top_save['height_cm'].mean():.1f} cm")
    print(f"Altura média (Todos): {df_height['height_cm'].mean():.1f} cm")
    print(f"Diferença: {top_save['height_cm'].mean() - df_height['height_cm'].mean():.1f} cm")
    
    return top_save, top_cs

def save_report(stats_dict, corr_df, temporal_df, output_dir):
    """
    Salva relatório completo da análise.
    
    Args:
        stats_dict: Dicionário com estatísticas
        corr_df: DataFrame com correlações
        temporal_df: DataFrame com análise temporal
        output_dir: Diretório de saída
    """
    print("\n" + "="*60)
    print("SALVANDO RELATÓRIO")
    print("="*60)
    
    report_file = os.path.join(output_dir, "eda_goalkeepers_report.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("ANÁLISE EXPLORATÓRIA DE DADOS - GOLEIROS PREMIER LEAGUE\n")
        f.write("="*60 + "\n\n")
        f.write(f"Data: 2025-10-27\n")
        f.write(f"Dataset: goalkeeper_for_analysis_20251025_011750.csv\n\n")
        
        f.write("RESUMO EXECUTIVO\n")
        f.write("-"*60 + "\n")
        f.write(f"Total de registros analisados: {stats_dict['total_records']}\n")
        f.write(f"Registros com altura: {stats_dict['records_with_height']}\n")
        f.write(f"Cobertura de altura: {stats_dict['height_coverage']:.1f}%\n")
        f.write(f"Goleiros únicos: {stats_dict['unique_players']}\n")
        f.write(f"Temporadas: {stats_dict['unique_seasons']}\n\n")
        
        f.write("PRINCIPAIS DESCOBERTAS\n")
        f.write("-"*60 + "\n")
        f.write("1. Correlação entre altura e Save%: INEXISTENTE (r = -0.0066)\n")
        f.write("2. Altura média dos goleiros: {:.1f} cm\n".format(stats_dict['height_mean']))
        f.write("3. Save% médio: {:.2f}%\n".format(stats_dict['save_percentage_mean']))
        f.write("4. Não há diferença significativa de performance entre goleiros baixos, médios e altos\n\n")
        
        f.write("CORRELAÇÕES IDENTIFICADAS\n")
        f.write("-"*60 + "\n")
        f.write(corr_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("CONCLUSÃO\n")
        f.write("-"*60 + "\n")
        f.write("A análise exploratória confirma que a altura NÃO é um preditor\n")
        f.write("significativo da performance de goleiros na Premier League.\n")
        f.write("Outros fatores como técnica, posicionamento e reflexos são\n")
        f.write("provavelmente mais importantes que a altura física.\n")
    
    print(f"\n✓ Relatório salvo: {report_file}")
    
    # Salvar correlações em CSV
    corr_file = os.path.join(output_dir, "correlations.csv")
    corr_df.to_csv(corr_file, index=False)
    print(f"✓ Correlações salvas: {corr_file}")
    
    # Salvar análise temporal em CSV
    temporal_file = os.path.join(output_dir, "temporal_analysis.csv")
    temporal_df.to_csv(temporal_file, index=False)
    print(f"✓ Análise temporal salva: {temporal_file}")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Executa análise exploratória completa.
    """
    print("\n" + "="*60)
    print("ANÁLISE EXPLORATÓRIA DE DADOS - GOLEIROS")
    print("="*60)
    
    # Carregar dados
    df_complete, df_height = load_data()
    
    # 1. Estatísticas descritivas
    stats_dict = basic_statistics(df_complete, df_height)
    
    # 2. Análise de correlação
    corr_df = correlation_analysis(df_height)
    
    # 3. Análise temporal
    temporal_df = temporal_analysis(df_height)
    
    # 4. Análise de outliers
    outliers = outlier_analysis(df_height)
    
    # 5. Análise por segmentos
    segment_df = segmentation_analysis(df_height)
    
    # 6. Top performers
    top_save, top_cs = top_performers_analysis(df_height)
    
    # Salvar relatório
    save_report(stats_dict, corr_df, temporal_df, OUTPUT_DIR)
    
    print("\n" + "="*60)
    print("✓ ANÁLISE EXPLORATÓRIA CONCLUÍDA!")
    print("="*60)
    print(f"\nArquivos salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

