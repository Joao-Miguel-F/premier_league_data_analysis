# Stage 2: ETL - Extração, Transformação e Carga

## Projeto Goleiros (2005-2020)

### Fontes de Dados
1. **Performance**: FBref via biblioteca `soccerdata`
2. **Altura**: FIFA 2005-2020 dataset (GitHub)

### Processo
1. Coleta de estatísticas de goleiros (Save%, Clean Sheet%, etc.)
2. Filtro de titulares (≥10 jogos/temporada)
3. Match de altura via nome do jogador
4. Agregação por carreira (1 linha = 1 goleiro)

### Resultados
- **125 goleiros únicos**
- **111 com altura** (88.8%)
- **404 registros** agregados em 111 carreiras

## Projeto VAR (2016-2024)

### Fonte de Dados
- **FBref** via biblioteca `soccerdata`

### Processo
1. Coleta de estatísticas disciplinares por time
2. Classificação em Pré-VAR (2016-2019) e Com VAR (2019-2024)
3. Cálculo de médias e variações

### Resultados
- **160 registros** (time × temporada)
- **Pré-VAR**: 60 registros
- **Com VAR**: 100 registros
