#!/usr/bin/env python3
"""
ETL - Análise do Impacto do VAR na Premier League (2000-2024)

OBJETIVO:
    Extrair dados de cartões (amarelos e vermelhos) e pênaltis marcados
    para analisar se o VAR mudou os padrões de marcação na Premier League.

CONTEXTO:
    O VAR (Video Assistant Referee) foi introduzido na Premier League
    na temporada 2019-20. Este ETL compara:
    - Período PRÉ-VAR: 2016-2019 (3 temporadas)
    - Período COM VAR: 2019-2024 (5 temporadas)
    
    NOTA: Dados de cartões e pênaltis no FBref estão disponíveis apenas
    a partir da temporada 2016-17. Temporadas anteriores não possuem
    essas estatísticas no formato 'misc'.

ARQUITETURA:
    ┌─────────────────────────────────────────────────────────────┐
    │                        EXTRACT                              │
    │  ┌──────────────┐         ┌─────────────────────┐          │
    │  │   FBref      │────────>│  Estatísticas de    │          │
    │  │ (soccerdata) │         │  Disciplina         │          │
    │  └──────────────┘         │  - Cartões Amarelos │          │
    │                           │  - Cartões Vermelhos│          │
    │                           │  - Pênaltis         │          │
    │                           │  - Faltas           │          │
    │                           └─────────────────────┘          │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                      TRANSFORM                              │
    │  - Classificar temporadas (Pré-VAR vs Com VAR)             │
    │  - Calcular médias por temporada                            │
    │  - Normalizar por número de jogos                           │
    │  - Agregar estatísticas por período                         │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                         LOAD                                │
    │  - CSV com dados brutos                                     │
    │  - CSV com análise comparativa                              │
    │  - Relatório de impacto do VAR                              │
    └─────────────────────────────────────────────────────────────┘

FERRAMENTAS:
    - Python 3.11
    - pandas: Manipulação de dados
    - soccerdata: Scraping de dados do FBref

AUTOR: ETL para Análise de Impacto do VAR
DATA: 2025-10-27
"""

import pandas as pd
import soccerdata as sd
import time
import os
from datetime import datetime

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

LEAGUE = "ENG-Premier League"
START_YEAR = 2000
END_YEAR = 2024
VAR_INTRODUCTION_YEAR = 2019  # VAR introduzido na temporada 2019-20
OUTPUT_DIR = "/home/ubuntu/goalkeeper_data"  # Mesma pasta, arquivos diferentes

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# FUNÇÕES DE EXTRAÇÃO (EXTRACT)
# ============================================================================

def generate_seasons(start_year, end_year):
    """
    Gera lista de temporadas no formato aceito pelo soccerdata.
    
    Args:
        start_year: Ano inicial (ex: 2000)
        end_year: Ano final (ex: 2024)
    
    Returns:
        Lista de strings no formato "YY-YY" (ex: ["00-01", "01-02"])
    """
    seasons = []
    for year in range(start_year, end_year + 1):
        season_str = f"{str(year)[-2:]}-{str(year+1)[-2:]}"
        seasons.append(season_str)
    return seasons

def extract_discipline_stats(league, seasons):
    """
    EXTRACT: Extrai estatísticas de disciplina (cartões e pênaltis) do FBref.
    
    Utiliza a biblioteca soccerdata para fazer scraping do FBref,
    coletando dados de cartões amarelos, vermelhos e pênaltis.
    
    Args:
        league: Nome da liga
        seasons: Lista de temporadas
    
    Returns:
        DataFrame com estatísticas de disciplina por time e temporada
    """
    all_data = []
    
    print(f"\n{'='*60}")
    print(f"EXTRACT: Coletando dados de {len(seasons)} temporadas")
    print(f"{'='*60}")
    
    for i, season in enumerate(seasons, 1):
        try:
            print(f"\n[{i}/{len(seasons)}] Temporada {season}...", end=" ")
            
            # Inicializar scraper FBref
            fbref = sd.FBref(leagues=league, seasons=season)
            
            # Obter estatísticas miscelâneas (incluem cartões e pênaltis)
            misc_stats = fbref.read_team_season_stats(stat_type="misc")
            
            if misc_stats.empty:
                print("⚠ Sem dados")
                continue
            
            # Resetar índice para facilitar manipulação
            misc_stats = misc_stats.reset_index()
            print(f"✓ {len(misc_stats)} times")
            
            all_data.append(misc_stats)
            
            # Delay para não sobrecarregar servidor
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            continue
    
    if not all_data:
        raise Exception("Nenhum dado foi extraído")
    
    # Concatenar todos os dados
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ Total: {len(combined_df)} registros extraídos")
    
    return combined_df

# ============================================================================
# FUNÇÕES DE TRANSFORMAÇÃO (TRANSFORM)
# ============================================================================

def transform_discipline_data(df, var_year=2019):
    """
    TRANSFORM: Limpa e transforma dados de disciplina.
    
    Operações:
    - Flatten de colunas MultiIndex
    - Renomeação de colunas
    - Classificação de períodos (Pré-VAR vs Com VAR)
    - Conversão de tipos
    - Cálculo de métricas normalizadas
    
    Args:
        df: DataFrame bruto
        var_year: Ano de introdução do VAR
    
    Returns:
        DataFrame transformado
    """
    print(f"\n{'='*60}")
    print(f"TRANSFORM: Limpeza e transformação dos dados")
    print(f"{'='*60}")
    
    df_clean = df.copy()
    
    # Flatten column names (MultiIndex -> string simples)
    if isinstance(df_clean.columns, pd.MultiIndex):
        df_clean.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                           for col in df_clean.columns.values]
    
    # Renomear colunas para maior clareza
    column_mapping = {
        'Performance_CrdY': 'yellow_cards',
        'Performance_CrdR': 'red_cards',
        'Performance_2CrdY': 'second_yellow_red',
        'Performance_Fls': 'fouls_committed',
        'Performance_Fld': 'fouls_drawn',
        'Performance_PKwon': 'penalties_won',
        'Performance_PKcon': 'penalties_conceded',
        'Performance_Off': 'offsides',
        'Performance_Crs': 'crosses',
        'Performance_Int': 'interceptions',
        'Performance_TklW': 'tackles_won',
        'Performance_OG': 'own_goals',
        'Performance_Recov': 'recoveries',
        'Aerial Duels_Won': 'aerial_duels_won',
        'Aerial Duels_Lost': 'aerial_duels_lost',
        'Aerial Duels_Won%': 'aerial_duels_won_pct'
    }
    
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Selecionar colunas relevantes
    relevant_columns = ['league', 'season', 'team', 'players_used', '90s',
                       'yellow_cards', 'red_cards', 'second_yellow_red',
                       'fouls_committed', 'fouls_drawn',
                       'penalties_won', 'penalties_conceded']
    
    available_cols = [col for col in relevant_columns if col in df_clean.columns]
    df_clean = df_clean[available_cols]
    
    # Converter tipos numéricos
    numeric_cols = ['players_used', '90s', 'yellow_cards', 'red_cards', 
                   'second_yellow_red', 'fouls_committed', 'fouls_drawn',
                   'penalties_won', 'penalties_conceded']
    
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Adicionar coluna de ano da temporada
    df_clean['season_year'] = df_clean['season'].apply(
        lambda x: int(f"20{x.split('-')[0]}") if len(x.split('-')[0]) == 2 else int(x.split('-')[0])
    )
    
    # Classificar período (Pré-VAR vs Com VAR)
    df_clean['var_period'] = df_clean['season_year'].apply(
        lambda year: 'Com VAR' if year >= var_year else 'Pré-VAR'
    )
    
    # Calcular total de cartões vermelhos (diretos + segundo amarelo)
    df_clean['total_red_cards'] = df_clean['red_cards'] + df_clean['second_yellow_red']
    
    # Calcular métricas normalizadas (por 90 minutos)
    df_clean['yellow_cards_per_90'] = df_clean['yellow_cards'] / df_clean['90s']
    df_clean['red_cards_per_90'] = df_clean['total_red_cards'] / df_clean['90s']
    df_clean['penalties_won_per_90'] = df_clean['penalties_won'] / df_clean['90s']
    df_clean['penalties_conceded_per_90'] = df_clean['penalties_conceded'] / df_clean['90s']
    df_clean['fouls_committed_per_90'] = df_clean['fouls_committed'] / df_clean['90s']
    
    # Remover linhas com valores nulos nas métricas principais
    df_clean = df_clean.dropna(subset=['yellow_cards', 'red_cards', 'penalties_won'])
    
    print(f"\n✓ Dados transformados: {len(df_clean)} registros")
    print(f"  Temporadas Pré-VAR: {len(df_clean[df_clean['var_period'] == 'Pré-VAR']['season'].unique())}")
    print(f"  Temporadas Com VAR: {len(df_clean[df_clean['var_period'] == 'Com VAR']['season'].unique())}")
    
    return df_clean

def create_comparative_analysis(df):
    """
    TRANSFORM: Cria análise comparativa entre períodos Pré-VAR e Com VAR.
    
    Args:
        df: DataFrame transformado
    
    Returns:
        DataFrame com estatísticas agregadas por período
    """
    print(f"\n{'='*60}")
    print(f"TRANSFORM: Criando análise comparativa")
    print(f"{'='*60}")
    
    # Agrupar por período VAR
    comparison = df.groupby('var_period').agg({
        'season': 'nunique',
        'team': 'count',
        'yellow_cards': 'sum',
        'total_red_cards': 'sum',
        'penalties_won': 'sum',
        'penalties_conceded': 'sum',
        'fouls_committed': 'sum',
        'yellow_cards_per_90': 'mean',
        'red_cards_per_90': 'mean',
        'penalties_won_per_90': 'mean',
        'penalties_conceded_per_90': 'mean',
        'fouls_committed_per_90': 'mean'
    }).reset_index()
    
    # Renomear colunas para clareza
    comparison.columns = [
        'Período', 'Temporadas', 'Total de Registros',
        'Total Cartões Amarelos', 'Total Cartões Vermelhos',
        'Total Pênaltis a Favor', 'Total Pênaltis Contra',
        'Total Faltas Cometidas',
        'Média Amarelos/90min', 'Média Vermelhos/90min',
        'Média Pênaltis a Favor/90min', 'Média Pênaltis Contra/90min',
        'Média Faltas/90min'
    ]
    
    print(f"\n✓ Análise comparativa criada")
    print(f"\n{comparison.to_string(index=False)}")
    
    return comparison

def calculate_var_impact(df):
    """
    TRANSFORM: Calcula o impacto percentual do VAR nas métricas.
    
    Args:
        df: DataFrame com análise comparativa
    
    Returns:
        DataFrame com variações percentuais
    """
    print(f"\n{'='*60}")
    print(f"TRANSFORM: Calculando impacto do VAR")
    print(f"{'='*60}")
    
    # Separar dados pré e pós VAR
    pre_var = df[df['Período'] == 'Pré-VAR'].iloc[0]
    with_var = df[df['Período'] == 'Com VAR'].iloc[0]
    
    # Calcular variações percentuais
    metrics = [
        'Média Amarelos/90min',
        'Média Vermelhos/90min',
        'Média Pênaltis a Favor/90min',
        'Média Pênaltis Contra/90min',
        'Média Faltas/90min'
    ]
    
    impact_data = []
    for metric in metrics:
        pre_value = pre_var[metric]
        with_value = with_var[metric]
        change = with_value - pre_value
        pct_change = (change / pre_value) * 100 if pre_value != 0 else 0
        
        impact_data.append({
            'Métrica': metric.replace('Média ', '').replace('/90min', ''),
            'Pré-VAR': round(pre_value, 4),
            'Com VAR': round(with_value, 4),
            'Variação Absoluta': round(change, 4),
            'Variação %': round(pct_change, 2)
        })
    
    impact_df = pd.DataFrame(impact_data)
    
    print(f"\n✓ Impacto calculado:")
    print(f"\n{impact_df.to_string(index=False)}")
    
    return impact_df

# ============================================================================
# FUNÇÕES DE CARGA (LOAD)
# ============================================================================

def load_data(df_raw, df_comparison, df_impact, output_dir):
    """
    LOAD: Salva dados processados em arquivos CSV e relatório.
    
    Args:
        df_raw: DataFrame com dados brutos transformados
        df_comparison: DataFrame com análise comparativa
        df_impact: DataFrame com impacto do VAR
        output_dir: Diretório de saída
    
    Returns:
        Tupla com caminhos dos arquivos criados
    """
    print(f"\n{'='*60}")
    print(f"LOAD: Salvando dados processados")
    print(f"{'='*60}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Dados brutos transformados
    raw_file = os.path.join(output_dir, f"var_impact_raw_data_{timestamp}.csv")
    df_raw.to_csv(raw_file, index=False, encoding='utf-8')
    print(f"\n✓ Dados brutos: {raw_file}")
    
    # 2. Análise comparativa
    comparison_file = os.path.join(output_dir, f"var_impact_comparison_{timestamp}.csv")
    df_comparison.to_csv(comparison_file, index=False, encoding='utf-8')
    print(f"✓ Análise comparativa: {comparison_file}")
    
    # 3. Impacto do VAR
    impact_file = os.path.join(output_dir, f"var_impact_analysis_{timestamp}.csv")
    df_impact.to_csv(impact_file, index=False, encoding='utf-8')
    print(f"✓ Análise de impacto: {impact_file}")
    
    # 4. Relatório detalhado
    report_file = os.path.join(output_dir, f"var_impact_report_{timestamp}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RELATÓRIO DE IMPACTO DO VAR NA PREMIER LEAGUE\n")
        f.write("="*60 + "\n\n")
        f.write(f"Data de extração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Liga: {LEAGUE}\n")
        f.write(f"Período: {START_YEAR}-{END_YEAR}\n")
        f.write(f"Introdução do VAR: Temporada {VAR_INTRODUCTION_YEAR}-{VAR_INTRODUCTION_YEAR+1}\n\n")
        
        f.write("CONTEXTO\n")
        f.write("-"*60 + "\n")
        f.write("O VAR (Video Assistant Referee) foi introduzido na Premier League\n")
        f.write("na temporada 2019-20 com o objetivo de auxiliar os árbitros em\n")
        f.write("decisões cruciais, incluindo:\n")
        f.write("  - Gols e infrações que levam a gols\n")
        f.write("  - Pênaltis\n")
        f.write("  - Cartões vermelhos diretos\n")
        f.write("  - Confusão de identidade de jogadores\n\n")
        
        f.write("ESTATÍSTICAS GERAIS\n")
        f.write("-"*60 + "\n")
        f.write(f"Total de registros: {len(df_raw)}\n")
        f.write(f"Temporadas analisadas: {df_raw['season'].nunique()}\n")
        f.write(f"Times únicos: {df_raw['team'].nunique()}\n\n")
        
        # Estatísticas por período
        pre_var = df_comparison[df_comparison['Período'] == 'Pré-VAR'].iloc[0]
        with_var = df_comparison[df_comparison['Período'] == 'Com VAR'].iloc[0]
        
        f.write("PERÍODO PRÉ-VAR (2000-2019)\n")
        f.write("-"*60 + "\n")
        f.write(f"Temporadas: {int(pre_var['Temporadas'])}\n")
        f.write(f"Total de cartões amarelos: {int(pre_var['Total Cartões Amarelos'])}\n")
        f.write(f"Total de cartões vermelhos: {int(pre_var['Total Cartões Vermelhos'])}\n")
        f.write(f"Total de pênaltis marcados: {int(pre_var['Total Pênaltis a Favor'])}\n")
        f.write(f"Média de amarelos por 90min: {pre_var['Média Amarelos/90min']:.4f}\n")
        f.write(f"Média de vermelhos por 90min: {pre_var['Média Vermelhos/90min']:.4f}\n")
        f.write(f"Média de pênaltis por 90min: {pre_var['Média Pênaltis a Favor/90min']:.4f}\n\n")
        
        f.write("PERÍODO COM VAR (2019-2024)\n")
        f.write("-"*60 + "\n")
        f.write(f"Temporadas: {int(with_var['Temporadas'])}\n")
        f.write(f"Total de cartões amarelos: {int(with_var['Total Cartões Amarelos'])}\n")
        f.write(f"Total de cartões vermelhos: {int(with_var['Total Cartões Vermelhos'])}\n")
        f.write(f"Total de pênaltis marcados: {int(with_var['Total Pênaltis a Favor'])}\n")
        f.write(f"Média de amarelos por 90min: {with_var['Média Amarelos/90min']:.4f}\n")
        f.write(f"Média de vermelhos por 90min: {with_var['Média Vermelhos/90min']:.4f}\n")
        f.write(f"Média de pênaltis por 90min: {with_var['Média Pênaltis a Favor/90min']:.4f}\n\n")
        
        f.write("IMPACTO DO VAR\n")
        f.write("-"*60 + "\n")
        for _, row in df_impact.iterrows():
            f.write(f"\n{row['Métrica']}:\n")
            f.write(f"  Pré-VAR: {row['Pré-VAR']:.4f}\n")
            f.write(f"  Com VAR: {row['Com VAR']:.4f}\n")
            f.write(f"  Variação: {row['Variação Absoluta']:+.4f} ({row['Variação %']:+.2f}%)\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("CONCLUSÕES\n")
        f.write("="*60 + "\n\n")
        
        # Análise automática das variações
        for _, row in df_impact.iterrows():
            metric = row['Métrica']
            pct = row['Variação %']
            
            if abs(pct) < 5:
                trend = "permaneceu praticamente estável"
            elif pct > 0:
                trend = f"aumentou {pct:.1f}%"
            else:
                trend = f"diminuiu {abs(pct):.1f}%"
            
            f.write(f"• {metric}: {trend}\n")
    
    print(f"✓ Relatório: {report_file}")
    
    return raw_file, comparison_file, impact_file, report_file

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Orquestra o processo ETL completo.
    """
    print("\n" + "="*60)
    print("ETL - IMPACTO DO VAR NA PREMIER LEAGUE")
    print("="*60)
    print(f"Liga: {LEAGUE}")
    print(f"Período: {START_YEAR}-{END_YEAR}")
    print(f"Introdução do VAR: {VAR_INTRODUCTION_YEAR}-{VAR_INTRODUCTION_YEAR+1}")
    print("="*60)
    
    try:
        # EXTRACT
        seasons = generate_seasons(START_YEAR, END_YEAR)
        df_raw = extract_discipline_stats(LEAGUE, seasons)
        
        # TRANSFORM
        df_clean = transform_discipline_data(df_raw, var_year=VAR_INTRODUCTION_YEAR)
        df_comparison = create_comparative_analysis(df_clean)
        df_impact = calculate_var_impact(df_comparison)
        
        # LOAD
        files = load_data(df_clean, df_comparison, df_impact, OUTPUT_DIR)
        
        print("\n" + "="*60)
        print("✓ ETL CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\nArquivos gerados:")
        for f in files:
            print(f"  - {f}")
        
        return df_clean, df_comparison, df_impact
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    df_data, df_comp, df_impact = main()

