# Premier League Data Analysis

Análise de dados da Premier League com foco em dois projetos principais: correlação entre altura e performance de goleiros, e impacto do VAR nas marcações disciplinares.

---

## 📊 Projetos

### 1. Goleiros: Altura vs Performance (2005-2020)
**Objetivo**: Analisar se existe correlação entre altura de goleiros e sua performance em defesas.

**Principais Descobertas**:
- ✅ **111 goleiros titulares** analisados
- ✅ **88.8% de cobertura de altura** (FIFA dataset)
- ✅ **Correlação: r = 0.0654** (fraca positiva)
- ✅ **Conclusão**: Altura NÃO é preditor significativo de performance

**Dados**:
- Período: 2005-2020 (15 temporadas)
- Fonte Performance: FBref via soccerdata
- Fonte Altura: FIFA 2005-2020 dataset
- Métricas: Save%, Clean Sheet%, Gols/90min

### 2. VAR: Impacto nas Marcações (2016-2024)
**Objetivo**: Avaliar se o VAR mudou as marcações de cartões e pênaltis na Premier League.

**Principais Descobertas**:
- ✅ **Cartões Vermelhos**: +21.45% com VAR
- ✅ **Cartões Amarelos**: +6.44% com VAR
- ✅ **Pênaltis**: +1-2% (praticamente estável)
- ✅ **Conclusão**: VAR teve impacto moderado, principalmente em expulsões

**Dados**:
- Pré-VAR: 2016-2019 (3 temporadas, 60 registros)
- Com VAR: 2019-2024 (5 temporadas, 100 registros)
- Fonte: FBref via soccerdata

---

## 🗂️ Estrutura do Repositório

```
premier_league_data_analysis/
│
├── 📂 scripts/              # Scripts Python
│   ├── etl_goalkeeper.py            # ETL: Goleiros (2005-2020)
│   ├── etl_var_impact.py            # ETL: VAR (2016-2024)
│   ├── eda_goalkeepers.py           # Análise Exploratória: Goleiros
│   ├── eda_var_impact.py            # Análise Exploratória: VAR
│   ├── ai_integration_goalkeepers.py # IA: Goleiros
│   └── ai_integration_var.py        # IA: VAR
│
├── 📂 data/                 # Dados processados
│   ├── goleiros_carreira.csv        # 111 goleiros com altura
│   ├── var_raw_data.csv             # Dados brutos VAR
│   ├── var_comparison.csv           # Comparação Pré-VAR vs Com VAR
│   └── var_analysis.csv             # Análise agregada VAR
│
├── 📂 docs/                 # Documentação
│   ├── STAGE2_ETL_SUMMARY.md        # Resumo Stage 2: ETL
│   ├── STAGE3_EDA_SUMMARY.md        # Resumo Stage 3: EDA
│   ├── STAGE4_AI_SUMMARY.md         # Resumo Stage 4: IA
│   └── EXECUTIVE_SUMMARY.md         # Resumo Executivo Geral
│
├── 📂 dashboards/           # Dashboards (Looker Studio)
│   └── LOOKER_GUIDE.md              # Guia de criação no Looker
│
├── 📄 README.md             # Este arquivo
├── 📄 requirements.txt      # Dependências Python
└── 📄 .gitignore            # Arquivos a ignorar no Git
```

---

## 🚀 Quick Start

### 1. Clonar Repositório
```bash
git clone https://github.com/Joao-Miguel-F/premier-league-data-analysis.git
cd premier-league-data-analysis
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Executar ETL
```bash
# Goleiros (demora ~5min)
python scripts/etl_goalkeeper.py

# VAR (demora ~3min)
python scripts/etl_var_impact.py
```

### 4. Análise Exploratória
```bash
# Goleiros
python scripts/eda_goalkeepers.py

# VAR
python scripts/eda_var_impact.py
```

### 5. Integração IA
```bash
# Goleiros
python scripts/ai_integration_goalkeepers.py

# VAR
python scripts/ai_integration_var.py
```

---

## 📈 Principais Resultados

### Goleiros (2005-2020)

| Métrica | Valor |
|---------|-------|
| Goleiros analisados | 111 |
| Altura média | 190.7 cm |
| Save% médio | 70.76% |
| **Correlação Altura × Save%** | **0.0654** |

**Interpretação**: Correlação muito fraca. Altura não prediz performance.

### VAR (2016-2024)

| Métrica | Pré-VAR | Com VAR | Variação |
|---------|---------|---------|----------|
| Cartões Vermelhos/90min | 0.0724 | 0.0879 | **+21.45%** |
| Cartões Amarelos/90min | 1.7583 | 1.8716 | +6.44% |
| Pênaltis/90min | 0.1217 | 0.1239 | +1.80% |

**Interpretação**: VAR teve impacto moderado, principalmente em expulsões.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11**
- **pandas** - Manipulação de dados
- **soccerdata** - Coleta de dados do FBref
- **scipy** - Testes estatísticos
- **numpy** - Operações numéricas
- **openai** - Integração com GPT-4

---

## 📚 Documentação Completa

- [Stage 2: ETL](docs/STAGE2_ETL_SUMMARY.md) - Processo de extração e transformação
- [Stage 3: EDA](docs/STAGE3_EDA_SUMMARY.md) - Análise exploratória detalhada
- [Stage 4: IA](docs/STAGE4_AI_SUMMARY.md) - Integração com IA
- [Resumo Executivo](docs/EXECUTIVE_SUMMARY.md) - Visão geral de todos os stages

---

## 🎯 Case Técnico

Este projeto foi desenvolvido como parte de um case técnico para entrevista, demonstrando habilidades em:

1. ✅ **ETL** - Extração, transformação e carga de dados
2. ✅ **EDA** - Análise exploratória e estatística
3. ✅ **IA** - Integração com modelos de linguagem
4. ✅ **Comunicação** - Documentação técnica e executiva

---

## 📞 Contato

**João Miguel Freitas**  
E-mail: Freitasjoamiguel3@gmail.com
Linkedin: https://www.linkedin.com/in/jo%C3%A3o-miguel-freitas-525b0529b/

---

## 📄 Licença

Este projeto é de código aberto para fins educacionais e de portfólio.

---

**Desenvolvido com 📊 e ☕ para análise de dados da Premier League**

