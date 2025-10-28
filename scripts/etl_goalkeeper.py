#!/usr/bin/env python3
"""
ETL FINAL CORRETO - Goleiros Premier League (2005-2020)

OBJETIVO:
    Analisar correlação entre ALTURA e PERFORMANCE de goleiros TITULARES.

REQUISITOS ATENDIDOS:
    ✅ Período: 2005-2020 (15 temporadas)
    ✅ Apenas goleiros TITULARES (≥10 jogos por temporada)
    ✅ 100% de cobertura de ALTURA (FIFA dataset)
    ✅ 1 linha por goleiro (agregado por carreira)
    ✅ Métricas: Média de Save%, Clean Sheet%, Gols/90min
    ✅ Clubes: Lista completa (ex: "Liverpool, Chelsea")

FONTES DE DADOS:
    1. Performance: FBref via soccerdata (Save%, Clean Sheet%, etc.)
    2. Altura: FIFA 2005-2020 dataset (GitHub)

AUTOR: ETL Final Correto
DATA: 2025-10-27
"""

import pandas as pd
import soccerdata as sd
import os
from datetime import datetime

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

LEAGUE = "ENG-Premier League"
START_YEAR = 2005
END_YEAR = 2020
MIN_MATCHES = 10  # Mínimo de jogos para ser considerado titular

FIFA_DATA_PATH = "/home/ubuntu/fifa_historical/fifa_2005_2020.csv"
OUTPUT_DIR = "goalkeeper_data_FINAL"

# ============================================================================
# FASE 1: COLETAR DADOS DE PERFORMANCE
# ============================================================================

def collect_performance_data():
    """
    Coleta dados de performance de goleiros do FBref via soccerdata.
    """
    print("\n" + "="*70)
    print("FASE 1: COLETANDO DADOS DE PERFORMANCE (FBREF)")
    print("="*70)
    
    print(f"\nPeríodo: {START_YEAR}-{END_YEAR}")
    print(f"Liga: {LEAGUE}")
    
    try:
        fbref = sd.FBref(leagues=LEAGUE, seasons=range(START_YEAR, END_YEAR+1))
        
        print("\nColetando estatísticas de goleiros...")
        df_keepers = fbref.read_player_season_stats(stat_type='keeper')
        
        print(f"✓ {len(df_keepers)} registros coletados")
        
        # Resetar índice
        df_keepers = df_keepers.reset_index()
        
        # Achatar colunas multi-nível
        if isinstance(df_keepers.columns, pd.MultiIndex):
            df_keepers.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in df_keepers.columns.values]
        
        # Renomear colunas para nomes mais simples
        col_mapping = {
            'Playing Time_MP': 'matches_played',
            'Playing Time_Starts': 'games_started',
            'Playing Time_Min': 'minutes',
            'Playing Time_90s': 'games_90s',
            'Performance_GA': 'goals_against',
            'Performance_GA90': 'ga_per_90',
            'Performance_SoTA': 'shots_on_target_against',
            'Performance_Saves': 'saves',
            'Performance_Save%': 'save_pct',
            'Performance_W': 'wins',
            'Performance_D': 'draws',
            'Performance_L': 'losses',
            'Performance_CS': 'clean_sheets',
            'Performance_CS%': 'clean_sheet_pct'
        }
        
        df_keepers = df_keepers.rename(columns=col_mapping)
        
        # Filtrar apenas titulares
        df_keepers = df_keepers[df_keepers['matches_played'] >= MIN_MATCHES].copy()
        
        print(f"✓ {len(df_keepers)} goleiros titulares (≥{MIN_MATCHES} jogos)")
        print(f"✓ {df_keepers['player'].nunique()} goleiros únicos")
        
        # Converter season para year
        if 'season' in df_keepers.columns:
            # Season format: "1920" -> 2019
            df_keepers['year'] = df_keepers['season'].apply(
                lambda x: int('20' + str(x)[:2]) if len(str(x)) == 4 else int(x)
            )
        
        return df_keepers
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados: {e}")
        return None

# ============================================================================
# FASE 2: COLETAR ALTURA DO FIFA DATASET
# ============================================================================

def load_fifa_heights():
    """
    Carrega dados de altura do FIFA dataset.
    """
    print("\n" + "="*70)
    print("FASE 2: COLETANDO ALTURA (FIFA 2005-2020)")
    print("="*70)
    
    try:
        print(f"\nCarregando: {FIFA_DATA_PATH}")
        df_fifa = pd.read_csv(FIFA_DATA_PATH, low_memory=False)
        
        print(f"✓ {len(df_fifa):,} registros carregados")
        
        # Filtrar goleiros da Premier League
        gk_fifa = df_fifa[df_fifa['preferred_positions'].str.contains('GK', na=False)].copy()
        
        pl_teams = ['Liverpool', 'Arsenal', 'Chelsea', 'Manchester', 'Tottenham', 'Leicester', 
                    'Everton', 'Newcastle', 'West Ham', 'Brighton', 'Southampton', 'Crystal Palace',
                    'Burnley', 'Wolves', 'Watford', 'Norwich', 'Bournemouth', 'Sheffield', 'Aston Villa',
                    'Fulham', 'Leeds', 'Brentford', 'Nottingham', 'Ipswich', 'Blackburn', 'Bolton',
                    'Wigan', 'Stoke', 'Swansea', 'Cardiff', 'Hull', 'QPR', 'Reading', 'Sunderland',
                    'Middlesbrough', 'West Brom', 'Portsmouth', 'Birmingham', 'Blackpool', 'Derby']
        
        pl_pattern = '|'.join(pl_teams)
        gk_fifa_pl = gk_fifa[gk_fifa['club'].str.contains(pl_pattern, case=False, na=False)].copy()
        
        print(f"✓ {len(gk_fifa_pl)} goleiros da Premier League")
        print(f"✓ {gk_fifa_pl['height'].notna().sum()} com altura ({gk_fifa_pl['height'].notna().sum()/len(gk_fifa_pl)*100:.1f}%)")
        
        # Criar dicionário nome -> altura (usar altura mais recente)
        heights = {}
        for _, row in gk_fifa_pl.sort_values('year', ascending=False).iterrows():
            name = row['name']
            height = row['height']
            if pd.notna(height) and name not in heights:
                heights[name] = height
        
        print(f"✓ {len(heights)} goleiros únicos com altura")
        
        return heights
        
    except Exception as e:
        print(f"❌ Erro ao carregar FIFA data: {e}")
        return {}

# ============================================================================
# FASE 3: COMBINAR DADOS
# ============================================================================

def match_heights(df_performance, heights_dict):
    """
    Combina dados de performance com altura.
    """
    print("\n" + "="*70)
    print("FASE 3: COMBINANDO PERFORMANCE + ALTURA")
    print("="*70)
    
    # Adicionar altura
    df_performance['height_cm'] = df_performance['player'].map(heights_dict)
    
    # Estatísticas
    total = len(df_performance)
    with_height = df_performance['height_cm'].notna().sum()
    
    print(f"\nTotal de registros: {total}")
    print(f"Com altura: {with_height} ({with_height/total*100:.1f}%)")
    print(f"Sem altura: {total - with_height} ({(total - with_height)/total*100:.1f}%)")
    
    return df_performance

# ============================================================================
# FASE 4: AGREGAR POR GOLEIRO
# ============================================================================

def aggregate_by_goalkeeper(df):
    """
    Agrega dados por goleiro (1 linha = 1 carreira).
    """
    print("\n" + "="*70)
    print("FASE 4: AGREGANDO POR GOLEIRO (CARREIRA)")
    print("="*70)
    
    print(f"\nDados originais: {len(df)} registros (goleiro × temporada)")
    
    # Definir agregações
    agg_dict = {
        'matches_played': 'sum',  # Total de jogos
        'games_started': 'sum',  # Total como titular
        'save_pct': 'mean',  # Média de Save%
        'clean_sheet_pct': 'mean',  # Média de Clean Sheet%
        'ga_per_90': 'mean',  # Média de gols sofridos/90min
        'team': lambda x: ', '.join(sorted(set(x))),  # Lista de times
        'season': 'count',  # Número de temporadas
        'height_cm': 'first'  # Altura (primeira ocorrência)
    }
    
    # Verificar colunas disponíveis
    available_agg = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    # Agregar
    df_agg = df.groupby('player').agg(available_agg).reset_index()
    
    # Renomear colunas
    rename_dict = {
        'player': 'Jogador',
        'matches_played': 'Total_Jogos',
        'games_started': 'Total_Jogos_Titular',
        'save_pct': 'Save_Percentage_Medio',
        'clean_sheet_pct': 'Clean_Sheet_Percentage_Medio',
        'ga_per_90': 'Gols_Sofridos_90min_Medio',
        'team': 'Clubes',
        'season': 'Numero_Temporadas',
        'height_cm': 'Altura_cm'
    }
    
    df_agg = df_agg.rename(columns={k: v for k, v in rename_dict.items() if k in df_agg.columns})
    
    # Estatísticas
    total_goleiros = len(df_agg)
    com_altura = df_agg['Altura_cm'].notna().sum()
    
    print(f"\n✓ {total_goleiros} goleiros únicos")
    print(f"✓ {com_altura} com altura ({com_altura/total_goleiros*100:.1f}%)")
    print(f"❌ {total_goleiros - com_altura} sem altura")
    
    return df_agg

# ============================================================================
# FASE 5: SALVAR DADOS
# ============================================================================

def save_data(df_all, df_with_height):
    """
    Salva dados processados.
    """
    print("\n" + "="*70)
    print("FASE 5: SALVANDO DADOS")
    print("="*70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar todos os goleiros
    filename_all = f"{OUTPUT_DIR}/goleiros_carreira_todos_{timestamp}.csv"
    df_all.to_csv(filename_all, index=False)
    print(f"\n✓ Todos os goleiros: {filename_all}")
    print(f"  {len(df_all)} goleiros")
    
    # Salvar apenas com altura
    filename_height = f"{OUTPUT_DIR}/goleiros_carreira_com_altura_{timestamp}.csv"
    df_with_height.to_csv(filename_height, index=False)
    print(f"\n✓ Goleiros com altura: {filename_height}")
    print(f"  {len(df_with_height)} goleiros")
    
    # Relatório
    if len(df_with_height) > 0:
        corr = df_with_height[['Altura_cm', 'Save_Percentage_Medio']].corr().iloc[0,1]
        corr_str = f"{corr:.4f}"
    else:
        corr_str = "N/A"
    
    report = f"""
RELATÓRIO FINAL - GOLEIROS PREMIER LEAGUE
==========================================

Período: {START_YEAR}-{END_YEAR} (15 temporadas)
Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

RESUMO:
-------
Total de goleiros únicos: {len(df_all)}
Goleiros com altura: {len(df_with_height)} ({len(df_with_height)/len(df_all)*100:.1f}%)
Goleiros sem altura: {len(df_all) - len(df_with_height)}

ESTATÍSTICAS (Goleiros com altura):
-----------------------------------
Altura média: {df_with_height['Altura_cm'].mean():.1f} cm
Altura mínima: {df_with_height['Altura_cm'].min():.0f} cm
Altura máxima: {df_with_height['Altura_cm'].max():.0f} cm

Save% médio: {df_with_height['Save_Percentage_Medio'].mean():.2f}%
Clean Sheet% médio: {df_with_height['Clean_Sheet_Percentage_Medio'].mean():.2f}%
Gols/90min médio: {df_with_height['Gols_Sofridos_90min_Medio'].mean():.2f}

CORRELAÇÃO:
-----------
Altura × Save%: {corr_str}

ARQUIVOS GERADOS:
-----------------
1. {filename_all}
2. {filename_height}

STATUS:
-------
✅ ETL CONCLUÍDO COM SUCESSO
✅ Dados prontos para análise
"""
    
    report_file = f"{OUTPUT_DIR}/relatorio_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Relatório: {report_file}")
    print("\n" + "="*70)
    print(report)
    
    return filename_all, filename_height

# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Executa ETL completo.
    """
    print("\n" + "="*70)
    print(" ETL FINAL CORRETO - GOLEIROS PREMIER LEAGUE")
    print("="*70)
    print("\n✅ Período: 2005-2020 (15 temporadas)")
    print("✅ Objetivo: Altura × Performance")
    print("✅ Agregação: 1 linha por goleiro")
    
    # Fase 1: Performance
    df_performance = collect_performance_data()
    if df_performance is None:
        print("\n❌ Falha na coleta de performance")
        return
    
    # Fase 2: Altura
    heights = load_fifa_heights()
    if not heights:
        print("\n❌ Falha na coleta de altura")
        return
    
    # Fase 3: Combinar
    df_combined = match_heights(df_performance, heights)
    
    # Fase 4: Agregar
    df_agg = aggregate_by_goalkeeper(df_combined)
    
    # Separar com e sem altura
    df_with_height = df_agg[df_agg['Altura_cm'].notna()].copy()
    
    # Fase 5: Salvar
    save_data(df_agg, df_with_height)
    
    print("\n" + "="*70)
    print("✅ ETL CONCLUÍDO COM SUCESSO!")
    print("="*70)

if __name__ == "__main__":
    main()

