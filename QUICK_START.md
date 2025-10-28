# Quick Start - Navegação Rápida

## 📁 Estrutura em 30 Segundos

- **scripts/** - Códigos Python (ETL, EDA, IA)
- **data/** - Dados processados (CSVs)
- **docs/** - Documentação completa
- **dashboards/** - Guia Looker Studio

## 🎯 O Que Ver Primeiro?

### 1. Resultados Principais
- [README.md](README.md) - Visão geral

### 2. Dados
- `data/goleiros_carreira.csv` - 111 goleiros
- `data/var_comparison.csv` - Comparação VAR

### 3. Documentação
- [Stage 2: ETL](docs/STAGE2_ETL_SUMMARY.md)
- [Stage 3: EDA](docs/STAGE3_EDA_SUMMARY.md)
- [Stage 4: IA](docs/STAGE4_AI_SUMMARY.md)

### 4. Código
- `scripts/etl_goalkeeper.py` - ETL Goleiros
- `scripts/etl_var_impact.py` - ETL VAR

## ⚡ Executar Análises

```bash
# Instalar
pip install -r requirements.txt

# ETL
python scripts/etl_goalkeeper.py

# EDA
python scripts/eda_goalkeepers.py

# IA
python scripts/ai_integration_goalkeepers.py
```

## 📊 Principais Descobertas

**Goleiros**: Altura NÃO prediz performance (r=0.0654)  
**VAR**: +21% cartões vermelhos, +6% amarelos
