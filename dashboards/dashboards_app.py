"""
Premier League Data Analysis Dashboard
Built with Plotly Dash
Replicates the design and structure of the Champions League Analysis Dashboard
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# --- Data Loading and Processing ---
def load_data():
    goleiros_df = pd.read_csv("data/goleiros_carreira.csv")
    var_analysis_df = pd.read_csv("data/var_analysis.csv")
    var_comparison_df = pd.read_csv("data/var_comparison.csv")
    
    # Rename columns for consistency
    goleiros_df.rename(columns={
        'Altura_cm': 'Altura (cm)',
        'Save_Percentage_Medio': 'Save % Médio',
        'Gols_Sofridos_90min_Medio': 'Gols Sofridos / 90min'
    }, inplace=True)
    
    return goleiros_df, var_analysis_df, var_comparison_df

goleiros_df, var_analysis_df, var_comparison_df = load_data()

# --- Calculate KPIs ---
avg_height = goleiros_df['Altura (cm)'].mean()
min_height = goleiros_df['Altura (cm)'].min()
max_height = goleiros_df['Altura (cm)'].max()
avg_save_percent = goleiros_df['Save % Médio'].mean()
correlation_save = goleiros_df['Altura (cm)'].corr(goleiros_df['Save % Médio'])

tallest_gk = goleiros_df.loc[goleiros_df['Altura (cm)'].idxmax()]
shortest_gk = goleiros_df.loc[goleiros_df['Altura (cm)'].idxmin()]

var_red_cards_change = var_analysis_df[var_analysis_df['Métrica'] == 'Vermelhos']['Variação %'].iloc[0]

# --- Initialize Dash App ---
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Premier League Data Analysis Dashboard"

# --- Define Color Scheme ---
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'secondary': '#7f7f7f'
}

# --- Create Figures ---

# 1. Save Percentage vs Height Scatter Plot
fig_scatter = go.Figure()
fig_scatter.add_trace(go.Scatter(
    x=goleiros_df['Altura (cm)'],
    y=goleiros_df['Save % Médio'],
    mode='markers',
    marker=dict(size=8, color=COLORS['primary'], opacity=0.6, line=dict(width=1, color='white')),
    text=goleiros_df['Jogador'],
    hovertemplate='<b>%{text}</b><br>Altura: %{x} cm<br>Save%: %{y:.2f}%<extra></extra>',
    name='Goleiros'
))

# Add trend line
z = np.polyfit(goleiros_df['Altura (cm)'], goleiros_df['Save % Médio'], 1)
p = np.poly1d(z)
x_trend = np.linspace(goleiros_df['Altura (cm)'].min(), goleiros_df['Altura (cm)'].max(), 100)
fig_scatter.add_trace(go.Scatter(
    x=x_trend,
    y=p(x_trend),
    mode='lines',
    line=dict(color=COLORS['danger'], dash='dash', width=2),
    name='Tendência',
    hovertemplate='Tendência<extra></extra>'
))

# Highlight tallest and shortest
fig_scatter.add_trace(go.Scatter(
    x=[tallest_gk['Altura (cm)']],
    y=[tallest_gk['Save % Médio']],
    mode='markers',
    marker=dict(size=15, color=COLORS['danger'], symbol='star'),
    name='Mais Alto',
    hovertemplate='<b>Mais Alto: %s</b><extra></extra>' % tallest_gk['Jogador']
))

fig_scatter.add_trace(go.Scatter(
    x=[shortest_gk['Altura (cm)']],
    y=[shortest_gk['Save % Médio']],
    mode='markers',
    marker=dict(size=15, color=COLORS['success'], symbol='star'),
    name='Mais Baixo',
    hovertemplate='<b>Mais Baixo: %s</b><extra></extra>' % shortest_gk['Jogador']
))

fig_scatter.update_layout(
    title=f'Save Percentage vs Height (Correlação: r={correlation_save:.3f})',
    xaxis_title='Altura (cm)',
    yaxis_title='Save % Médio',
    template='plotly_white',
    height=500,
    hovermode='closest'
)

# 2. Tallest vs Shortest Comparison
comparison_data = {
    'Métrica': ['Altura (cm)', 'Save %', 'Gols/90min'],
    'Mais Alto': [tallest_gk['Altura (cm)'], tallest_gk['Save % Médio'], tallest_gk['Gols Sofridos / 90min']],
    'Mais Baixo': [shortest_gk['Altura (cm)'], shortest_gk['Save % Médio'], shortest_gk['Gols Sofridos / 90min']]
}

fig_comparison = go.Figure()
fig_comparison.add_trace(go.Bar(
    x=comparison_data['Métrica'],
    y=comparison_data['Mais Alto'],
    name='Mais Alto',
    marker=dict(color=COLORS['danger']),
    text=[f"{v:.1f}" for v in comparison_data['Mais Alto']],
    textposition='auto'
))

fig_comparison.add_trace(go.Bar(
    x=comparison_data['Métrica'],
    y=comparison_data['Mais Baixo'],
    name='Mais Baixo',
    marker=dict(color=COLORS['success']),
    text=[f"{v:.1f}" for v in comparison_data['Mais Baixo']],
    textposition='auto'
))

fig_comparison.update_layout(
    title='Tallest vs Shortest Goalkeeper Comparison',
    barmode='group',
    template='plotly_white',
    height=500,
    hovermode='closest'
)

# 3. Height Distribution
fig_height_dist = go.Figure()
fig_height_dist.add_trace(go.Box(
    y=goleiros_df['Altura (cm)'],
    name='Altura',
    marker=dict(color=COLORS['primary']),
    boxmean='sd'
))

fig_height_dist.update_layout(
    title='Height Distribution',
    yaxis_title='Altura (cm)',
    template='plotly_white',
    height=500,
    showlegend=False
)

# 4. Top 10 Goalkeepers by Save Percentage
top_10_gk = goleiros_df.nlargest(10, 'Save % Médio').sort_values('Save % Médio', ascending=True)
fig_top_10 = px.bar(
    top_10_gk,
    x='Save % Médio',
    y='Jogador',
    orientation='h',
    title='Top 10 Goalkeepers by Save Percentage',
    color='Save % Médio',
    color_continuous_scale=px.colors.sequential.Greens,
    text='Save % Médio'
)
fig_top_10.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
fig_top_10.update_layout(
    height=500,
    showlegend=False,
    template='plotly_white'
)

# 5. VAR Impact - Variation Percentage
var_metrics = var_analysis_df[var_analysis_df['Métrica'].isin(['Amarelos', 'Vermelhos', 'Pênaltis a Favor', 'Pênaltis Contra'])]
fig_var_impact = go.Figure()
fig_var_impact.add_trace(go.Bar(
    x=var_metrics['Métrica'],
    y=var_metrics['Variação %'],
    marker=dict(color=['#FFD700', '#FF4500', '#1E90FF', '#1E90FF']),
    text=var_metrics['Variação %'].apply(lambda x: f'{x:.2f}%'),
    textposition='auto',
    hovertemplate='%{x}<br>Variação: %{y:.2f}%<extra></extra>'
))

fig_var_impact.update_layout(
    title='VAR Impact - Variation Percentage (Mean / 90min)',
    xaxis_title='Métrica',
    yaxis_title='Variação %',
    template='plotly_white',
    height=500
)

# 6. VAR Comparison - Pre-VAR vs Com VAR
metrics_cols = ['Média Amarelos/90min', 'Média Vermelhos/90min']
pre_var_values = var_comparison_df[var_comparison_df['Período'] == 'Pré-VAR'][metrics_cols].values[0]
com_var_values = var_comparison_df[var_comparison_df['Período'] == 'Com VAR'][metrics_cols].values[0]

fig_var_comparison = go.Figure()
fig_var_comparison.add_trace(go.Bar(
    x=metrics_cols,
    y=pre_var_values,
    name='Pré-VAR',
    marker=dict(color=COLORS['secondary']),
    hovertemplate='%{x}<br>Pré-VAR: %{y:.2f}<extra></extra>'
))

fig_var_comparison.add_trace(go.Bar(
    x=metrics_cols,
    y=com_var_values,
    name='Com VAR',
    marker=dict(color=COLORS['danger']),
    hovertemplate='%{x}<br>Com VAR: %{y:.2f}<extra></extra>'
))

fig_var_comparison.update_layout(
    title='VAR Comparison - Pre-VAR vs Com VAR (Mean / 90min)',
    xaxis_title='Métrica',
    yaxis_title='Média / 90min',
    barmode='group',
    template='plotly_white',
    height=500
)

# --- App Layout ---
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Premier League Data Analysis", className="text-primary fw-bold mt-4 mb-2"),
            html.P("Interactive Dashboard: Goalkeeper Evolution & VAR Impact Analysis", className="text-muted mb-4")
        ])
    ]),
    
    # Navigation Tabs
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id='tabs', value='tab-1', children=[
                # TAB 1: Executive Overview
                dcc.Tab(label='📊 Executive Overview', value='tab-1', children=[
                    dbc.Container([
                        # KPI Cards
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H2(f"{avg_height:.1f} cm", className="text-primary fw-bold"),
                                        html.P("Average Goalkeeper Height", className="text-muted"),
                                        html.P(f"Range: {min_height:.0f}-{max_height:.0f} cm", className="small text-muted")
                                    ])
                                ], className="mb-3")
                            ], md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H2(f"{avg_save_percent:.1f}%", className="text-success fw-bold"),
                                        html.P("Average Save Percentage", className="text-muted"),
                                        html.P(f"{len(goleiros_df)} elite goalkeepers", className="small text-muted")
                                    ])
                                ], className="mb-3")
                            ], md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H2(f"r = +{correlation_save:.3f}", className="text-warning fw-bold"),
                                        html.P("Height-Save % Correlation", className="text-muted"),
                                        html.P("Weak positive correlation", className="small text-muted")
                                    ])
                                ], className="mb-3")
                            ], md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H2(f"{var_red_cards_change:+.1f}%", className="text-danger fw-bold"),
                                        html.P("Red Cards Change (VAR)", className="text-muted"),
                                        html.P("Post-VAR vs Pre-VAR", className="small text-muted")
                                    ])
                                ], className="mb-3")
                            ], md=3)
                        ], className="mb-4"),
                        
                        # Key Findings
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("🎯 Key Findings", className="fw-bold mb-3"),
                                        
                                        html.H6("Thesis 1: Goalkeeper Height & Performance", className="text-primary fw-bold"),
                                        html.P("Heights stable at ~190cm, but save % shows weak positive correlation (r=0.0653) with height. Top performers include both tall and short goalkeepers.", className="mb-3"),
                                        
                                        html.Hr(),
                                        
                                        html.H6("Thesis 2: VAR Impact", className="text-primary fw-bold"),
                                        html.P(f"VAR changed red cards by {var_red_cards_change:+.2f}%, penalties by {var_analysis_df[var_analysis_df['Métrica'] == 'Pênaltis a Favor']['Variação %'].iloc[0]:+.2f}%, and yellow cards by {var_analysis_df[var_analysis_df['Métrica'] == 'Amarelos']['Variação %'].iloc[0]:+.2f}%.", className="mb-3"),
                                        
                                        html.Hr(),
                                        
                                        html.H6("Implications", className="text-success fw-bold"),
                                        html.Ul([
                                            html.Li("Height provides slight advantage but isn't decisive"),
                                            html.Li("Technical skills and positioning matter more than physical attributes"),
                                            html.Li("VAR's impact varies significantly by decision type")
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ], fluid=True, className="mt-4 mb-4")
                ]),
                
                # TAB 2: Goalkeeper Analysis
                dcc.Tab(label='📏 Goalkeeper Analysis', value='tab-2', children=[
                    dbc.Container([
                        # Tallest and Shortest Cards
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("🏆 Tallest Goalkeeper", className="text-warning fw-bold"),
                                        html.H3(tallest_gk['Jogador'], className="fw-bold"),
                                        html.H4(f"{tallest_gk['Altura (cm)']:.0f} cm", className="text-primary fw-bold"),
                                        html.P(f"Save %: {tallest_gk['Save % Médio']:.1f}%"),
                                        html.P(f"Gols/90min: {tallest_gk['Gols Sofridos / 90min']:.1f}")
                                    ])
                                ], className="mb-3")
                            ], md=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("🔴 Shortest Goalkeeper", className="text-success fw-bold"),
                                        html.H3(shortest_gk['Jogador'], className="fw-bold"),
                                        html.H4(f"{shortest_gk['Altura (cm)']:.0f} cm", className="text-success fw-bold"),
                                        html.P(f"Save %: {shortest_gk['Save % Médio']:.1f}%"),
                                        html.P(f"Gols/90min: {shortest_gk['Gols Sofridos / 90min']:.1f}")
                                    ])
                                ], className="mb-3")
                            ], md=6)
                        ], className="mb-4"),
                        
                        # Charts
                        dbc.Row([
                            dbc.Col([dcc.Graph(figure=fig_scatter)], md=6),
                            dbc.Col([dcc.Graph(figure=fig_comparison)], md=6)
                        ], className="mb-4"),
                        
                        dbc.Row([
                            dbc.Col([dcc.Graph(figure=fig_height_dist)], md=6),
                            dbc.Col([dcc.Graph(figure=fig_top_10)], md=6)
                        ], className="mb-4")
                    ], fluid=True, className="mt-4 mb-4")
                ]),
                
                # TAB 3: VAR Impact
                dcc.Tab(label='🎥 VAR Impact', value='tab-3', children=[
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([dcc.Graph(figure=fig_var_impact)], md=6),
                            dbc.Col([dcc.Graph(figure=fig_var_comparison)], md=6)
                        ], className="mb-4")
                    ], fluid=True, className="mt-4 mb-4")
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P(
                "Premier League Data Analysis Dashboard | 100% Real Data | Built with Plotly Dash",
                className="text-center text-muted small"
            )
        ])
    ], className="mb-4")
], fluid=True, style={'backgroundColor': '#f8f9fa'})

# --- Run the app ---
# Para deployment no Render/Gunicorn, o servidor deve ser exposto como 'server'
server = app.server

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
