# tab3.py
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

def render_tab(df):
    df['weekday'] = df['tran_date'].dt.day_name()

    grouped = df[df['total_amt']>0].groupby(['Store_type', 'weekday'])['total_amt'].sum().unstack(fill_value=0)

    traces = []
    for store in grouped.index:
        traces.append(go.Bar(
            x=grouped.columns,
            y=grouped.loc[store],
            name=store
        ))
    
    fig_sales_by_weekday = go.Figure(data=traces, layout=go.Layout(
        title="Sprzedaż wg dni tygodnia i kanałów",
        barmode='group'
    ))

    store_options = [{'label': s, 'value': s} for s in df['Store_type'].unique()]
    default_store = df['Store_type'].unique()[0]

    layout = html.Div([
        html.H1("Kanały sprzedaży", style={'text-align':'center'}),

        html.Div([dcc.Graph(id='sales-weekday-bar', figure=fig_sales_by_weekday)], style={'width':'100%'}),

        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='store-dropdown',
                    options=store_options,
                    value=default_store
                ),
                dcc.Graph(id='store-customer-graph')
            ], style={'width':'50%'})
        ], style={'display':'flex'})
    ])

    return layout
