import pandas as pd
import datetime as dt
import os
import plotly.graph_objects as go
import dash_auth
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import tab1
import tab2
import tab3

class DB:
    def __init__(self):
        self.transactions = DB.transaction_init()
        self.cc = pd.read_csv(r'db\country_codes.csv', index_col=0)
        self.customers = pd.read_csv(r'db\customers.csv', index_col=0)
        self.prod_info = pd.read_csv(r'db\prod_cat_info.csv')
        self.merged = None

    @staticmethod
    def transaction_init():
        src = r'db\transactions'
        transactions = pd.concat(
        [pd.read_csv(os.path.join(src, filename), index_col=0) for filename in os.listdir(src)],
        ignore_index=True
        )

        def convert_dates(x):
            try:
                return dt.datetime.strptime(x, '%d-%m-%Y')
            except:
                return dt.datetime.strptime(x, '%d/%m/%Y')

        transactions['tran_date'] = transactions['tran_date'].apply(convert_dates)
        return transactions


    def merge(self):
        df = self.transactions.join(
            self.prod_info.drop_duplicates(subset=['prod_cat_code'])
            .set_index('prod_cat_code')['prod_cat'],
            on='prod_cat_code',
            how='left'
        )

        df = df.join(
            self.prod_info.drop_duplicates(subset=['prod_sub_cat_code'])
            .set_index('prod_sub_cat_code')['prod_subcat'],
            on='prod_subcat_code',
            how='left'
        )

        df = df.join(
            self.customers.join(self.cc, on='country_code')
            .set_index('customer_Id'),
            on='cust_id'
        )

        self.merged = df

df = DB()
df.merge()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
USERNAME_PASSWORD = [['user','pass']]
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD)

app.layout = html.Div([
    html.Div([
        dcc.Tabs(
            id='tabs',
            value='tab-1',
            children=[
                dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
                dcc.Tab(label='Produkty', value='tab-2'),
                dcc.Tab(label='Kanały sprzedaży', value='tab-3')
            ]
        ),
        html.Div(id='tabs-content')
    ], style={'width':'80%', 'margin':'auto'})
], style={'height':'100%'})


@app.callback(
    Output('tabs-content','children'),
    Input('tabs','value')
)
def render_content(tab):
    if tab == 'tab-1':
        return tab1.render_tab(df.merged)
    elif tab == 'tab-2':
        return tab2.render_tab(df.merged)
    elif tab == 'tab-3':
        return tab3.render_tab(df.merged)

@app.callback(
    Output('bar-sales','figure'),
    [Input('sales-range','start_date'), Input('sales-range','end_date')]
)
def tab1_bar_sales(start_date, end_date):
    truncated = df.merged[(df.merged['tran_date']>=start_date) & (df.merged['tran_date']<=end_date)]
    grouped = truncated[truncated['total_amt']>0].groupby([pd.Grouper(key='tran_date', freq='M'),'Store_type'])['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(go.Bar(
            x=grouped.index,
            y=grouped[col],
            name=col,
            hoverinfo='text',
            hovertext=[f'{y/1e3:.2f}k' for y in grouped[col].values]
        ))

    fig = go.Figure(data=traces, layout=go.Layout(title='Przychody', barmode='stack', legend=dict(x=0, y=-0.5)))
    return fig

@app.callback(
    Output('choropleth-sales','figure'),
    [Input('sales-range','start_date'), Input('sales-range','end_date')]
)
def tab1_choropleth_sales(start_date, end_date):
    truncated = df.merged[(df.merged['tran_date']>=start_date) & (df.merged['tran_date']<=end_date)]
    grouped = truncated[truncated['total_amt']>0].groupby('country')['total_amt'].sum().round(2)

    trace0 = go.Choropleth(
        colorscale='Viridis',
        reversescale=True,
        locations=grouped.index,
        locationmode='country names',
        z=grouped.values,
        colorbar=dict(title='Sales')
    )

    fig = go.Figure(data=[trace0], layout=go.Layout(title='Mapa', geo=dict(showframe=False, projection={'type':'natural earth'})))
    return fig

@app.callback(
    Output('barh-prod-subcat','figure'),
    Input('prod_dropdown','value')
)
def tab2_barh_prod_subcat(chosen_cat):
    grouped = df.merged[(df.merged['total_amt']>0) & (df.merged['prod_cat']==chosen_cat)].pivot_table(
        index='prod_subcat',
        columns='Gender',
        values='total_amt',
        aggfunc='sum'
    ).assign(_sum=lambda x: x['F']+x['M']).sort_values(by='_sum').round(2)

    traces = []
    for col in ['F','M']:
        traces.append(go.Bar(
            x=grouped[col],
            y=grouped.index,
            orientation='h',
            name=col
        ))

    fig = go.Figure(data=traces, layout=go.Layout(barmode='stack', margin={'t':20}))
    return fig

@app.callback(
    Output('store-customer-graph','figure'),
    Input('store-dropdown','value')
)
def update_store_customer_graph(selected_store):
    data = df.merged[df.merged['Store_type'] == selected_store]

    grouped = data.groupby('Gender')['total_amt'].sum()
    fig = go.Figure(data=[go.Bar(
        x=grouped.index,
        y=grouped.values,
        text=[f'{v:,.0f}' for v in grouped.values],
        textposition='auto'
    )])
    fig.update_layout(title=f'Charakterystyka klientów - {selected_store}', yaxis_title='Sprzedaż')
    return fig


if __name__ == '__main__':
    app.run(debug=True)
