# ⚽ Premier League Data Analysis 📊

**Análise de dados da Premier League com foco em dois projetos principais:**
1. **Goleiros:** Correlação entre altura e performance (2005-2020).
2. **VAR:** Impacto nas marcações disciplinares (2016-2024).

---

## 🔍 Projetos de Análise

### 1\. Goleiros: Altura vs Performance (2005-2020)

**Objetivo**: Analisar se existe correlação estatisticamente significativa entre a altura de goleiros e sua performance em defesas na Premier League.

| Métrica | Valor | Interpretação |
| :--- | :--- | :--- |
| Goleiros analisados | 111 | Goleiros titulares com dados completos. |
| Altura média | 190.7 cm | Altura média dos goleiros analisados. |
| Save% médio | 70.76% | Porcentagem média de defesas. |
| **Correlação Altura × Save%** | **0.0654** | Correlação muito fraca e positiva. |

**Conclusão Principal**: A altura **NÃO** é um preditor significativo da performance de um goleiro em termos de Save% no período analisado.

**Detalhes da Análise:**
*   **Período:** 2005-2020 (15 temporadas)
*   **Fontes:** FBref (via `soccerdata`) para performance, FIFA dataset para altura.
*   **Métricas:** Save%, Clean Sheet%, Gols Sofridos/90min.

### 2\. VAR: Impacto nas Marcações Disciplinares (2016-2024)

**Objetivo**: Avaliar o impacto da introdução do Video Assistant Referee (VAR) nas marcações de cartões e pênaltis na Premier League.

| Métrica | Pré-VAR (2016-2019) | Com VAR (2019-2024) | Variação |
| :--- | :--- | :--- | :--- |
| Cartões Vermelhos/90min | 0.0724 | 0.0879 | **+21.45%** |
| Cartões Amarelos/90min | 1.7583 | 1.8716 | +6.44% |
| Pênaltis/90min | 0.1217 | 0.1239 | +1.80% |

**Conclusão Principal**: O VAR teve um **impacto moderado**, sendo mais notável no aumento das marcações de **Cartões Vermelhos** (expulsões).

**Detalhes da Análise:**
*   **Períodos:** Pré-VAR (3 temporadas) e Com VAR (5 temporadas).
*   **Fonte:** FBref (via `soccerdata`).

---

## 🛠️ Tecnologias e Dependências

O projeto foi desenvolvido em Python e utiliza as seguintes bibliotecas principais:

*   **Python 3.11**
*   **pandas**: Manipulação e análise de dados.
*   **soccerdata**: Coleta de dados estatísticos do FBref.
*   **scipy**: Testes estatísticos e cálculos de correlação.
*   **openai**: Integração com modelos de linguagem (GPT-4) para sumarização e insights.

As dependências completas estão listadas no arquivo `requirements.txt`.

---

## 🚀 Guia de Início Rápido (Quick Start)

Siga os passos abaixo para replicar a análise.

### 1\. Clonar o Repositório

```bash
git clone https://github.com/Joao-Miguel-F/premier_league_data_analysis.git
cd premier_league_data_analysis
```

### 2\. Instalar Dependências

É altamente recomendável usar um ambiente virtual (`venv` ou `conda`).

```bash
pip install -r requirements.txt
```

### 3\. Executar o Processo ETL (Extração, Transformação e Carga)

Estes scripts coletam e processam os dados brutos.

```bash
# ETL Goleiros (demora aproximadamente 5 minutos)
python scripts/etl_goalkeeper.py

# ETL VAR (demora aproximadamente 3 minutos)
python scripts/etl_var_impact.py
```

### 4\. Análise Exploratória de Dados (EDA)

Execute para gerar gráficos e estatísticas descritivas.

```bash
# EDA Goleiros
python scripts/eda_goalkeepers.py

# EDA VAR
python scripts/eda_var_impact.py
```

### 5\. Integração com IA (Opcional)

Estes scripts utilizam a API da OpenAI para gerar sumarizações e análises avançadas.

```bash
# Integração IA Goleiros
python scripts/ai_integration_goalkeepers.py

# Integração IA VAR
python scripts/ai_integration_var.py
```

---

## 🗂️ Estrutura do Repositório

```
premier_league_data_analysis/
│
├── 📂 scripts/              # Scripts Python para ETL, EDA e IA
├── 📂 data/                 # Dados processados e resultados intermediários
├── 📂 docs/                 # Documentação e resumos de cada etapa
│   ├── EXECUTIVE_SUMMARY.md # Resumo Executivo Geral
│   └── ...                  # Outros resumos de etapas (ETL, EDA, IA)
├── 📂 dashboards/           # Arquivos e guias para dashboards (Looker Studio)
├── 📄 README.md             # Este arquivo
├── 📄 requirements.txt      # Dependências do projeto
└── 📄 QUICK_START.md        # Guia de início rápido (conteúdo duplicado, será removido)
```

---

## 📚 Documentação Completa e Resumos

A documentação detalhada de cada etapa do projeto pode ser encontrada na pasta `docs/`:

*   [Resumo Executivo Geral](docs/EXECUTIVE_SUMMARY.md)
*   [Stage 2: ETL - Resumo do Processo](docs/STAGE2_ETL_SUMMARY.md)
*   [Stage 3: EDA - Análise Exploratória Detalhada](docs/STAGE3_EDA_SUMMARY.md)
*   [Stage 4: IA - Integração com Modelos de Linguagem](docs/STAGE4_AI_SUMMARY.md)

---

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido como parte de um **Case Técnico** para demonstrar proficiência em:

1.  **ETL** (Extração, Transformação e Carga)
2.  **EDA** (Análise Exploratória e Estatística)
3.  **Integração com IA** (Utilizando OpenAI/GPT-4)
4.  **Comunicação Técnica** (Documentação e Resumos Executivos)

**Desenvolvido com 📊 e ☕ para análise de dados da Premier League.**

---

## 📞 Contato

**João Miguel Freitas**  
E-mail: `Freitasjoamiguel3@gmail.com`  
LinkedIn: [https://www.linkedin.com/in/jo%C3%A3o-miguel-freitas-525b0529b/](https://www.linkedin.com/in/jo%C3%A3o-miguel-freitas-525b0529b/)

## 📄 Licença

Este projeto é de código aberto para fins educacionais e de portfólio.
