# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

### IMPORTS ###
from collections import Counter
import re

import dash
import dash_d3cloud
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


### INITIAL CONFIGS ###
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


### FUNCTIONS ###
def prepare_input(text_data):
    tokens = re.split("\W+", text_data)
    tokens_with_counts = Counter(tokens)
    return tokens_with_counts


def shape_text(shape, df_byshape):
    df_shape = None
    for i in df_byshape:
        if i[0] == shape:
            df_shape = i[1]
            break
    if df_shape is None:
        print('Shape not found.')
        return
    words = list(df_shape['description'])
    words = [str(w) for w in words]
    text = '\n'.join(words)
    return prepare_input(text)


def word_for_wordclouds(n, shape, df_byshape):
    tokens_with_counts = shape_text(shape, df_byshape)
    tokens_wordcloud = [{"text": a, "value": b} for a, b in
                        tokens_with_counts.most_common(n)]
    return tokens_wordcloud


### CHARTS ###
def create_scatter_map(data):
    scatter_map = px.scatter_mapbox(data, lat="latitude", lon="longitude",
                                    hover_name='city',
                                    hover_data=['Date_time',
                                                'state/province',
                                                'country',
                                                'UFO_shape'],
                                    color_discrete_sequence=[colors['text']],
                                    height=350,
                                    title='Distribuição Geográfica de'
                                          ' Avistamentos de OVNIs'
                                    )

    scatter_map.update_layout(mapbox_style="dark", mapbox_accesstoken=token,
                              paper_bgcolor=colors['background'],
                              font_color=colors['text'],
                              title={'xanchor': 'center', 'yanchor': 'top',
                                     'y': 0.9, 'x': 0.5})
    scatter_map.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0},
                              mapbox={'accesstoken': token, 'zoom': 1.5,
                              'center': dict(lat=38, lon=-50)})
    return scatter_map


def create_hbar_shapes(data):
    fig = px.bar(x=list(reversed(data))[-10::],
                 y=list(map(lambda x: x.capitalize(),
                            list(reversed(data.index))))[-10::],
                 orientation='h',
                 color_discrete_sequence=[colors['text']],
                 title='Frequência de Aparições por Formato da Nave (Top 10)',
                 labels={'x': 'Aparições', 'y': 'Formatos de Nave'},
                 opacity=0.75)

    fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            title={'xanchor': 'center', 'yanchor': 'top', 'y': 0.9,
                   'x': 0.5},
            margin={"r": 0, "t": 50, "l": 50, "b": 50}
    )
    return fig


def create_density_map(data, data2):
    fig3 = px.density_mapbox(data, lat='latitude', lon='longitude',
                             radius=10,
                             center=dict(lat=0, lon=180), zoom=0,
                             mapbox_style="stamen-terrain",
                             height=350,
                             title='Densidade de Avistamentos de OVNIs')

    fig3.add_trace(go.Scattermapbox(
        lat=data2['Latitude'],
        lon=data2['Longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=5,
            color='rgb(255, 0, 0)',
            opacity=0.7
        ),
        text=data2['Name'],
        hoverinfo='text'
    ))

    fig3.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0},
                       paper_bgcolor=colors['background'],
                       font_color=colors['text'],
                       title={'xanchor': 'center', 'yanchor': 'top',
                              'y': 0.9, 'x': 0.5},
                       mapbox={'accesstoken': token, 'zoom': 9,
                               'center': dict(lat=40.7, lon=-73.9)})
    return fig3


def create_histogram(data):
    fig4 = px.histogram(data, x='Date_time',
                        nbins=70,
                        color_discrete_sequence=[colors['text']],
                        title='Frequência de Aparições por Intervalo de Tempo',
                        opacity=0.75)

    fig4.update_xaxes(rangeslider_visible=True)
    fig4.update_layout(
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            plot_bgcolor=colors['background'],
            xaxis_title_text='Tempo',
            yaxis_title_text='Aparições',
            bargap=0.1,
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            title={'xanchor': 'center', 'yanchor': 'bottom', 'y': 0.85,
                   'x': 0.5},
            margin={"r": 10, "t": 50, "l": 50, "b": 50}
    )
    fig4.update_layout(clickmode='event+select')
    return fig4


### STYLING ###
colors = {
    'background': '#101820',
    'text': '#F2AA4C'
}

wordcloud_colors = ['#f2aa4c', '#da9944', '#c2883d', '#a97735', '#91662e',
                    '#795526', '#61441e', '#493317']

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


### DATA PROCESSING ###
data = pd.read_csv('ufo_sighting_data.csv', low_memory=False)
airports = pd.read_csv('airports.csv')
df_byshape = list(data.groupby(['UFO_shape']))
ufo_shape_freq = data['UFO_shape'].value_counts()
data = data.drop(43782)
data['Date_time'] = pd.to_datetime(data['Date_time'], errors='coerce')
data["latitude"] = pd.to_numeric(data["latitude"], downcast="float")
data["longitude"] = pd.to_numeric(data["longitude"], downcast="float")


### MAPBOX SETTINGS ###
token = 'pk.eyJ1IjoibWRlbGltYWZyZWlyZSIsImEiOiJja2U3d2xmamgxcmJnMnN1bGptOXl2'\
        'bDh0In0.MGCK7cRRKpmA6Fi_O8sFTw'
px.set_mapbox_access_token(token)


### LAYOUT ###
app.layout = html.Div(style={'backgroundColor': colors['background']},
                      children=[
    html.H1(
        children='UFO Sightings Around the World',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dashboard para análise de dados de OVNIs', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='hbar_time',
        figure=create_histogram(data),
        style={'height': 300, 'width': '48%', 'display': 'inline-block'}
    ),

    dcc.Graph(
        id='hbar_shapes',
        figure=create_hbar_shapes(ufo_shape_freq),
        style={'height': 300, 'width': '48%', 'display': 'inline-block'}
    ),

    dcc.Dropdown(
        id='ddown',
        options=[{'label': 'Scatter Plot', 'value': 'scatter'},
                 {'label': 'Heatmap', 'value': 'heat'}],
        value='scatter',
        clearable=False,
        style={'width': '30%',
               'backgroundColor': colors['background'],
               'color': colors['text']
               }
        ),

    dcc.Graph(
        id='scatter_map',
        figure=create_scatter_map(data),
        style={'width': '48%', 'display': 'inline-block'}),

    html.Div(dash_d3cloud.WordCloud(
            id='wordcloud',
            words=[{"text": 'Selecione aparições', "value": 100}],
            options={'spiral': 'archimedean',
                     'scale': 'linear',
                     'rotations': 4,
                     'rotationAngles': [0, 0],
                     'fontSizes': [15, 40],
                     'colors': wordcloud_colors,
                     'padding': 2
                     }
        ),   style={'width': '48%', 'display': 'inline-block'}
    ),
])


### CALLBACKS ###
@app.callback(
    Output('wordcloud', 'words'),
    [Input('scatter_map', 'selectedData')])
def display_selected_data(selectedData):

    if selectedData and selectedData['points']:
        if len(selectedData['points']) > 15000:
            return [{"text": 'Muitos pontos', "value": 100}]
        words = []
        for x in selectedData['points']:
            index = int(x['pointNumber']) + 1
            words.append(data.iloc[index]['description'])

        words = [str(w) for w in words]
        text = '\n'.join(words)
        tokens_with_counts = prepare_input(text)
        tokens_wordcloud = [{"text": a, "value": b} for a, b in
                            tokens_with_counts.most_common(50)]

        return tokens_wordcloud
    else:
        return [{"text": 'Selecione aparições', "value": 100}]


@app.callback([
    Output('scatter_map', 'figure'),
    Output('hbar_shapes', 'figure')],
    [Input('hbar_time', 'selectedData'),
     Input('ddown', 'value')])
def update_graphs(selectedData, ddown_v):
    if ddown_v == 'heat':
        return create_density_map(data, airports), create_hbar_shapes(
                ufo_shape_freq)
    else:
        if selectedData and selectedData['points']:
            indexs = []
            for x in selectedData['points']:
                indexs = indexs + x['pointNumbers']
            new_sdata = data[data.index.isin(indexs)]
            ufo_shape_freq_up = new_sdata['UFO_shape'].value_counts()
            return create_scatter_map(new_sdata),\
                create_hbar_shapes(ufo_shape_freq_up)
        else:
            return create_scatter_map(data),\
                create_hbar_shapes(ufo_shape_freq)


if __name__ == '__main__':
    app.run_server(debug=True)
