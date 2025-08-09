
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 14:40:20 2022

@author: martinmi
"""

import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
from dash.dash import no_update  # ,callback_context
from PIL import Image
import plotly.express as px
import json
import io
import base64
import datetime
import functools
import time
# import pickle
import flask
import random
import string
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
# import bjoern

# from uuid import uuid4
# from dash.long_callback import DiskcacheLongCallbackManager
# import diskcache
# launch_uid = uuid4()
# cache = diskcache.Cache("./cache")
# long_callback_manager = DiskcacheLongCallbackManager(
#     cache, cache_by=[lambda: launch_uid], expire=60,
# )
with open('ros_livarna_v1.txt', 'r') as f:
    lines = f.read()
decoded_data_list_dicts = json.loads(lines)

server = flask.Flask(__name__) # define flask app.server
lth_livarna_layout = Image.open("lth_livarna_layout_mod.png")


# from scipy import stats
# import dash_draggable
colors_list = px.colors.qualitative.Plotly +px.colors.qualitative.Light24 + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet + px.colors.qualitative.Light24 + px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet
no_of_colors=400
random_colors_list=["#"+''.join([random.choice('0123456789ABCDEF') for i in range(6)])
       for j in range(no_of_colors)]

colors_list = colors_list + random_colors_list
pd.options.mode.chained_assignment = None
lightblue = 'rgb(236, 248, 255)'
lightbluewhiter = 'rgb(250, 253, 255)'
lightblueborder = 'rgb(230, 242, 249)'
white = 'rgb(255, 255, 255)'
marker_color = px.colors.qualitative.Plotly[5]
laptop_screen = {'height': 641, 'width': 1422}
# PC_screen = {'height': 802, 'width': 1707}
# widths!
# xs Extra small<576px
# sm Small≥576px
# md Medium≥768px
# lg Large≥992px
# xl Extra large≥1200px
# (xs, sm, md, lg, xl, xxl)

# piechart_paper_bgcolor = 'rgb(236, 248, 255)'
piechart_paper_bgcolor = white
uppercase_indicators = ['X', 'x', 'Y', 'Y',
                        'Q', 'q', 'w', 'W', 'ABB', 'abb', '-']
uppercase_indicators_exceptions = ['kg', 'mm']

# app = dash.Dash(__name__)
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], server=server,title='Transportne poti LTH')

# with open(r'C:\Working Directory Investicije Ljubljana 2021-22\dash_podatki\spaghetti_layout_img.pickle', 'wb') as handle:
#     pickle.dump(spaghetti_fig_dict['layout']['images'][0], handle, protocol=pickle.HIGHEST_PROTOCOL)
# with open('df_pripadnost_strojev_filled.pickle', 'rb') as handle:
#     df_pripadnost_strojev = pickle.load(handle)

# %% funkcije

def redistribute_vertices(geom, distance,tracename):
    # if tracename == '200:200_srednja':
    #     breakpoint()
    if geom.geom_type == 'LineString':
        num_vert = int(round(geom.length / distance)) # + 20
        # num_vert = int(round(geom.length / distance * 1 / geom.length**0.56)) # inverzno proporcionalno dolzini poti
        if num_vert == 0:
            num_vert = 1
        return LineString(
            [geom.interpolate(float(n) / num_vert, normalized=True)
             for n in range(num_vert + 1)])
    elif geom.geom_type == 'MultiLineString':
        parts = [redistribute_vertices(part, distance)
                 for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise ValueError('unhandled geometry %s', (geom.geom_type,))

def get_dictionary_from_df_pripadnost_columns(input_column, output_column, target, mapping_source):
    # breakpoint()
    mapping_dict = mapping_source[[input_column, output_column]].set_index(input_column).T.to_dict('index')
    return [mapping_dict[output_column][x] if x in mapping_dict[output_column].keys() else 'Ni def.' for x in
            target[input_column].values]

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print("Finished {} in {} secs".format(repr(func.__name__), round(run_time, 3)))
        return value
    return wrapper

def merge_dicts(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif isinstance(a[key], int) and isinstance(b[key], int): #number_of_traces
                a[key] += b[key]
            elif isinstance(a[key], list) and isinstance(b[key], list): #traces_list
                a[key] += b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None, width=100,
                      paper_bgcolor=lightblue,
                      plot_bgcolor=lightblue,
                      height=100)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value)
        else:
            yield (key, value)

# %% Modals Content
top_left_toast_offset = 154

Modal_Shrani_Content = html.Div([
    dbc.Card(
        [
            dbc.CardBody(
                [
                    html.I(
                        'Ime datoteke: ', className="opacity-100 p-1 mb-1 text-black fw-light fst-normal rounded bg-gradient"),
                    dcc.Input(id='save_file_name', type='text', placeholder='', size='20', style={'marginRight': '1px', 'padding': '1px', 'display': 'inline'}, value='',
                              className="opacity-100 p-1 mx-1 bg-white fw-bold text-primary fst-normal rounded"),
                    html.Hr(''),
                    html.Button('💾 Shrani',id='download_data_button'),
                    dcc.Download(id = 'download_spaghetti_graph'),
                    # dcc.Download(id = 'download_traces_mapping'),
                    # dcc.Download(id='download_datatable'),
                    html.P(''),
                ]
            ),
        ],
        color='light',   # https://bootswatch.com/default/ for more card colors
        inverse=False,   # change color of text (black or white)
        outline=False,  # True = remove the block colors from the background and header
    )
], style={})


Modal_shrani = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("💾 Shrani")),

                            dbc.ModalBody([
                                Modal_Shrani_Content
                                ]),
                dbc.ModalFooter(
                    # dbc.Button(
                    #     "Zapri", id="modal_shrani_close", className="ms-auto", n_clicks=0
                    # )
                ),
            ],
            id="modal_shrani",
            is_open=False,
        )
# %% Navigation Bar NAV BAR
inputs1 = html.Div(
    [
        # dbc.CardHeader([
            # html.Div(style={'margin-right':10}),
            dbc.DropdownMenu(
                children=[
                 dcc.Upload(
                     dbc.Button('📂 Odpri',
                                color='light',id='upload_data_button',
                                className='p-1 my-1 mx-2 me-1 fw-light border-1',
                                n_clicks=0,
                                size="sm",
                                style={'margin-left': '0px'},
                                )
                     ,id = 'upload_data'),
             dbc.Button(
                 '💾 Shrani',
                 color='light',
                 id='shrani_button',
                 className='p-1 my-1 mx-2 me-1 fw-light border-2',
                 n_clicks=0,
                 size="sm",
                 style={'margin-left': '0px'},
             ),
             # dcc.RadioItems( id = "radio_viewmode",
             #                   options=[
             #                       {'label': 'View Mode', 'value': 'View Mode'},
             #                       {'label': 'Draw Mode', 'value': 'Draw Mode'},
             #                   ],
             #                   value='Draw Mode',
             #                   style={'display': 'inline-block'},
             #                   className='fw-light',
             #                   inputStyle={"margin-right": "6px"},
             #                ),
             dbc.Button(
                 '↔️ Pozicioniraj',
                 color='light',
                 id='pozicioniraj_button',
                 className='p-1 my-1 mx-1 me-1 fw-light border-1',
                 n_clicks=0,
                 size="sm",
                 style={'margin-left': '0px'},
             ),
                ],
                nav=True,
                in_navbar=True,
                label="📁",
                # color= "success",
                className="mx-2 border border-warning rounded",
                style={'display': 'inline-block', "width":"60px", "height":"40px"}
            ),
            dbc.Button(
                '↩️',
                color='light',
                id='undo_button',
                className='p-1 my-1 mx-1 me-1 fw-light border border-primary rounded',
                n_clicks=0,
                size="md",
                style={'margin-left': '0px'},
            ),
            dbc.Button(
                '🗑️',
                color='secondary',
                id='izbrisi_vnos',
                className='p-1 my-1 mx-1 me-1 fw-light text-white fs-normal border border-white rounded',
                size='md',
                n_clicks=0,
                # style = {'display':'inline'},
            )
        ],className='p-0 g-0 m-0', style={"align-items":"center", "display":"flex"})


inputs2 =  html.Div([
                    
                    html.I('Kategorija: ',className="mx-1 px-1",style={"font-size":"12px"}),
                    dcc.Input(id="input_kategorija", type="text", placeholder="", style={
                              'width': 85, 'marginRight': '5',"font-size":"12px"}),
                    html.I('Otok:',className="mx-1 px-1",style={"font-size":"12px"}),
                    dcc.Input(id="input_groupname", type="text", placeholder="", style={
                              'width': 70, 'marginRight': '5',"font-size":"12px"}),
                    html.I('Atribut: ',className="mx-1 px-1",style={"font-size":"12px"}),
                    dcc.Input(id="input_name", type="text", placeholder="",
                              style={'width': 200, 'marginRight': '5px',"font-size":"12px"}),
            ])


inputs3 = html.Div(
    [
        # dbc.CardBody([
                dcc.Dropdown(
                    id='dropdown_kategorija',
                    options=[],
                    value=None,
                    placeholder="Kategorija",
                    # search_value = 'uj'
                    style={'width': 130,"float" : "left", "font-size":"12px"},
                    optionHeight = 45,
                    # className='mx-3'
                    # clearable=False
                    ),
                dcc.Dropdown(
                    id='dropdown_name',
                    options=[],
                    value=None,
                    placeholder="Atribut",
                    style={'width': 150, "float" : "right", "font-size":"12px"},
                    # optionHeight = 45,
                    # clearable=False
                    ),
                dcc.Dropdown(
                    id='dropdown_groupname',
                    options=[],
                    value=None,
                    placeholder="Otok",
                    # optionHeight = 45,
                    # clearable=False,
                    style={'width': 100,
                            "float" : "right", 
                            "font-size":"12px"
                           },
                    # className='mx-3'
                    ),
        ],className='',
        style={"float" : "right" })

title_navbar = html.Span([html.A('Transportne poti',style={"font-size":"16px"}),
                          html.Sup('v0.41',style={"font-size":"12px","marginLeft":"6px"})])

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url('Logo_160px160px_offset_top_right_no_napis.png'),
                                         width=50, style={"float": "left", "position": "relative"}, className='')),
                        dbc.Col(dbc.NavbarBrand(
                            title_navbar, className="mx-2 mt-3 fw-bold rounded"), align="center"),
                    ],
                    # align="left",
                    justify="start",
                    className="g-0 m-0 p-0",
                ),
                # href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            # osnovne_nastavitve,
            inputs1,
            inputs2,
            inputs3,


        ],
        style={
            'margin-left': '30px',
            'width':"115%"
        },
        className="",
        fluid=True
    ),
    color="light",
    # dark=True,
    className="g-0 p-0 mx-0 mt-0 fw-bold rounded",
    style={"position": "fixed",
           'zIndex': 999,
           'align-items': 'center',
            'width':"115%",
           # 'margin-left':'30px'
           }
)

# %% SideBar
tab2_content = dbc.Card(
    [

        dbc.CardBody([
            dcc.RadioItems(
                id='radioitems_poti_rubrike',
                options=[
                    {'label': 'Po poteh', 'value': 'Po poteh'},
                    {'label': 'Po otokih', 'value': 'Po otokih'},
                    # {'label': 'Top 6', 'value': 'Po otokih'}
                ],
                value='Po poteh',
                className="px-2 mx-2 text-primary fs-6 text",
                labelStyle={'padding': '5px'},
                style={'display':'inline'},
                inputStyle={"margin-right": "6px"},
            ),
            html.Hr(className="bg-primary"),

            dbc.Row(
                [
                    dbc.Col([
                        # html.Div([
                        # collapse_button_sunburst_oddelek

                        dbc.Collapse([
                            # html.P(""),
                            dcc.Graph(id='spaghetti_plot_lengths', figure=blank_figure(),
                                      config={
                                'displayModeBar': False,
                            },
                                # style = {"position": "relative",'zIndex': 3}
                            ),
                            html.Div([
                            dcc.Input(id='save_file_name_download_graf_dolžine_izpis', type='text', placeholder='Ime datoteke',
                                      size='20', 
                                      style={'float':'left','marginRight': '1px', 'padding': '1px', 'display': 'inline-block'}, value='',
                                      className="opacity-100 p-1 mx-1 fw-bold text-primary fst-normal"),
                            html.I('.xlsx',
                                   className="opacity-100 p-1 mx-1 mt-2 text-black",
                                   style={'marginTop': '5px',
                                   # 'float':'right'
                                   }),
                            dbc.Button(
                                '🔽 Snemi izpis',
                                color='light',
                                id='graf_dolžine_izpis_xlsx',
                                className='p-1 my-1 mx-2 me-1 fw-primary border-2 border-primary',
                                n_clicks=0,
                                size="sm",
                                style={'margin-left': '0px',
                                       'float':'right'},
                            ),
                            ],style={'align-content': 'center',
                                     'display':'flex',
                                     'flex-wrap':'wrap',
                                   # 'float':'right'
                                   },
                             className="p-1 m-1",),
                            dcc.Download(id = 'download_graf_dolžine_izpis_xlsx'),
                            dcc.Download(id = 'download_graf_dolžine_izpis_xlsx_vsi_stolpci'),
                            # html.P(''),
                            
                        ],
                            id='collapse_button_sunburst_oddelek',
                            is_open=True,
                        )

                    ], className="g-1 opacity-100 p-1 m-1 text-primary border border-light border-2 text-primary",
                        id="sunburst_div"),

                ],

            )
        ]),
    ],
    style={"width": "1600px",'zIndex': 7,
    "z-index": 7},
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=False,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
    className="p-0 mx-0 g-0"
)


# %% Spaghetti Bar Plot

# spaghetti_fig = go.Figure(data = [{'x': [], 'y': [],'name': 'Pot'+str(i)} for i in range(25)])
# TV
# width = 1250
# height = 1600
# PC_
width = 2000
height = 2560

x_img_loc = 0.6
y_img_loc = 3.7
scale_img_loc = 4.8

# spaghetti_fig = go.Figure(data = [{'x': [], 'y': [],'name': 'Pot'+str(i)} for i in range(25)])
spaghetti_fig = go.Figure()

spaghetti_fig.add_layout_image(
    dict(
        source=lth_livarna_layout,
        xref="x",
        yref="y",
        # x=0.6,
        # y=3.7,
        # sizex=4.8,
        # sizey=4.8,
        x=x_img_loc,
        y=y_img_loc,
        sizex=scale_img_loc,
        sizey=scale_img_loc,
        # sizing="stretch",
        opacity=1,
        layer="below")
)

# Set templates
# spaghetti_fig.update_layout(template="simple_white")
spaghetti_fig.update_yaxes(range=[0, 4])
spaghetti_fig.update_xaxes(range=[1, 6])
spaghetti_fig.update_xaxes(visible=False)
spaghetti_fig.update_yaxes(visible=False)

spaghetti_fig.update_layout(
    # dragmode='drawopenpath',
    # style of new shapes
    newshape=dict(line_color=marker_color,
                  # fillcolor='white',
                  opacity=1),
    width=width, height=height,
    paper_bgcolor=white,
    plot_bgcolor=white,
    # plot_bgcolor='rgb(251, 251, 251)',
    # margin=dict(t=10, b=10, l=0, r=0),
    # paper_bgcolor=lightbluewhiter,
    # title="Plot Title",
    # xaxis_title="Otok",
    # yaxis_title="Število pozivov",
    # legend_title="Vrsta stroška",
    # font= {'family': 'Bahnschrift'},
    # showlegend=True,
    legend=dict(bgcolor='rgb(245, 245, 245)',
                orientation="v",
                yanchor="top",
                # y=0.8,
                # x= 1.5,
                xanchor="right"
                ),
    # legend_font_size = 16,
    modebar_orientation='h'
)
spaghetti_fig.layout.template = None
# src=app.get_asset_url('Logo_160px160px_offset_top_right_no_napis.png'
# source=r"C:\Working Directory Investicije Ljubljana 2021-22\dash_podatki\lth_livarna_layout_mod.png",


spaghetti_graph = dcc.Graph(id='spaghetti_graph', figure=spaghetti_fig,
                            config={
                                # 'modeBarButtonsToRemove': ['pan2d', 'lasso2d','zoom2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d'],
                                'modeBarButtonsToRemove': ['lasso2d', 'autoScale2d', 'select2d'],
                                'modeBarButtonsToAdd': ['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ],
                                # 'displaylogo': 'hover',
                                'displayModeBar': True,
                                'scrollZoom': True,
                                'displaylogo': False,
                                # "editable": True,
                                # 'legendText': True,
                                # 'setBackground': white
                                # 'autosizable': True,
                                  'toImageButtonOptions': {
                                    'format': 'png', # one of png, svg, jpeg, webp
                                    'filename': 'Transportne_poti',
                                    'height': None,
                                    'width': None,
                                    'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
                                  }
                            },
                            # style = {"position": "relative",'zIndex': 3}
                            )


# %% Tab 1 Content

tab1_content = dbc.Card([

                    dbc.Row(
                        [

                            dbc.Col([

                                spaghetti_graph
                            ],
                                className='my-1 p-0 g-0'), 
                ]
            ),
], 
    style={"width": "1800px", "z-index": '5','zIndex': '5',"position": "relative"},
    id="graphs_charts_div_tab1",
    color='info',   # https://bootswatch.com/default/ for more card colors
    inverse=False,   # change color of text (black or white)
    outline=False,  # True = remove the block colors from the background and header
    className="p-0 m-0 g-0"
)



#%% Sunburst definition
data_tabela = {
    'Kategorija': 'Liv',
    'Otok': 'L1401',
    'Atribut poti': 'Prazna INT',
    'Dolžina [m]': 'Dolžina [m]',
    'Delovno mesto': 'Delovno mesto',
    'I/O': 'I/O',
    'Prazne/Polne': 'Prazne/Polne',
    'Tip': 'Tip',
    'Število enot': 'Število enot',
}

editable_columns = ['Otok','Delovno mesto','I/O','Prazne/Polne', 'Tip','Število enot']
# Creates pandas DataFrame.
df_data_tabela = pd.DataFrame(data_tabela,index=[0])

datatable_data_tabela = df_data_tabela.to_dict('records')
datatable_columns_tabela = [{'name': i, 'id': i, 'editable':True} if i in editable_columns else {'name': i, 'id': i} for i in df_data_tabela.columns]

datatable_sunburst = html.Div([dash_table.DataTable(
    id='datatable_sunburst',
    columns=datatable_columns_tabela,
    # data=datatable_data_tabela,  # the contents of the table
    # editable=True,  # allow editing of data inside all cells
    # allow filtering of data by user ('native') or not ('none')
    filter_action='native',
    # enables data to be sorted per-column by user or not ('none')
    sort_action='native',
    export_format="xlsx",
    fill_width=True,
    sort_mode='single',
    # sort_mode='single',         # sort across 'multi' or 'single' columns
    # column_selectable='multi',  # allow users to select 'multi' or 'single' columns
    # row_selectable='multi',     # allow users to select 'multi' or 'single' rows
    # row_deletable=True,  # choose if user can delete a row (True) or not (False)
    # selected_columns=[],        # ids of columns that user selects
    # selected_rows=[],           # indices of rows that user selects
    # # page_action='native',       # all data is passed to the table up-front or not ('none')
    page_current=0,  # page number that user is on
    page_size=13,  # number of rows visible per page
    style_cell={  # ensure adequate header width when text is shorter than cell's text
        'minWidth': 85, 'maxWidth': 125,
        'width': 95,
        # 'max-height' : 14, 'height' : 10,
        'fontSize': 13, 'font-family': 'calibri',  # % Calibri,
        'textAlign': 'center'
    },
    # style_cell_conditional=[    # align text columns to left. By default they are aligned to right
    #     {
    #         'if': {'column_id': c},
    #         'textAlign': 'left'
    #     } for c in ['country', 'iso_alpha3']
    # ],
    style_data={  # overflow cells' content into multiple lines
        'whiteSpace': 'normal',
        'width': 'auto',
        'backgroundColor': white,
        'color': 'black',
        'border': '1px solid gainsboro'
    },
    style_table={'overflowX': 'auto'},
    style_header={
        'whiteSpace': 'normal',
        'height': 'auto',
        'backgroundColor': 'rgb(245,245,245)',
        'color': 'black',
        'font-family': 'calibri',
        'fontSize': 14,
        'fontWeight': 'normal',
        'border': '1px solid gainsboro',
        'textAlign': 'center'
    },

    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': lightblue,
        },
        {
            'if': {'column_id': 'Opis artikla'},
            'textAlign': 'left'
        }

    ]
),
],
    className="opacity-100 p-0 m-0 text-primary fw-normal fst-normal rounded bg-gradient"
)



#%% Toast Datatable
barplots_config = {
    'modeBarButtonsToRemove': ['lasso2d', 'autoScale2d', 'select2d', 'resetScale2d', 'zoom2d', 'zoomIn2d',
                               'zoomOut2d', ],
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png',  # one of png, svg, jpeg, webp
        # 'filename': 'Transportne_poti',
        'height': None,
        'width': None,
        'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
    }}

sunburst_graph = dcc.Graph(id='sunburst_poti', figure=blank_figure(),
                               className="opacity-100 p-0 mt-2 bg-white",
                               config={'displayModeBar': False})


checklist_kategorije = html.Div([
    html.P(
        'Kategorije: ', className="opacity-100 p-1 mb-1 text-black fw-light text-primary fst-normal rounded bg-gradient text-decoration-underline fs-6"),
    # html.Hr(),
    # dcc.Checklist(
    #     id='all_or_none_checklist_kategorije',
    #     options=[
    #         {'label': 'Izberi vse', 'value': 'All'}],
    #     # value=['All'],
    #     labelStyle={'display': 'block'},
    #     # multi=True,
    #     # placeholder="Select a city",
    # ),
    dcc.Dropdown(
        id='checklist_kategorije',
        # labelStyle={'display': 'block'},
        style={'shape': 'rectangle',
               "font-size":"11px",
                # 'padding-left': '0px', 'padding': '0px',
                # 'min-width':'120px',
                # 'max-width':'130px',
                # 'max-height':'150px'
                },
        multi=True,
        placeholder=""
    ),
],style={
        'max-width':'270px',
        # 'max-height':'50px',
        # 'margin-right': '20px',
        'display':'inline-block'},
    # className="g-1 p-1 m-1"
    )

checklist_otoki = html.Div([
    html.P(
        'Otoki: ', className="opacity-100 p-1 mb-1 text-black fw-light text-primary fst-normal rounded bg-gradient text-decoration-underline fs-6"),
    # html.Hr(),
    # dcc.Checklist(
    #     id='all_or_none_checklist_otoki',
    #     options=[
    #         {'label': 'Izberi vse', 'value': 'All'}],
    #     value=['All'],
    #     labelStyle={'display': 'block'},
    #     inputStyle={"margin-right": "6px"},
    #     # multi=True,
    #     # placeholder="Select a city",
    # ),
    dcc.Dropdown(
        id='checklist_otoki',
        # labelStyle={'display': 'block'},
        style={'shape': 'rectangle',
                'padding-left': '0px', 'padding': '0px',
                'min-width':'270px',
                "font-size":"11px"
                },
        multi=True,
        placeholder="",
    ),
],style={
       'max-width':'280px',
        'display':'inline-block',
        # 'float':'left'
        }
    # ,   className = "border border-warning"
    )

checklist_atributi = html.Div([
    html.P(
        'Atributi poti - iskalni niz: ', className="opacity-100 p-1 mb-1 text-black text-primary fw-light fst-normal rounded bg-gradient text-decoration-underline fs-6"),
    # html.Hr(),
    # dcc.Checklist(
    #     id='all_or_none_checklist_atributi',
    #     options=[
    #         {'label': 'Izberi vse', 'value': 'All'}],
    #     value=['All'],
    #     labelStyle={'display': 'block'},
    #     inputStyle={"margin-right": "6px"},
    #     # multi=True,
    #     # placeholder="Select a city",
    # ),
    # dcc.Dropdown(
    #     id='checklist_atributi',
    #     # labelStyle={'display': 'block'},
    #     style={'shape': 'rectangle',
    #             'padding-left': '0px', 'padding': '0px',
    #             'min-width':'270px',
    #             "font-size":"11px"
    #             },
    #     multi=True,
    #     placeholder="",
    # ),
    dcc.Input(
        id='checklist_atributi',
        # labelStyle={'display': 'block'},
        style={'shape': 'rectangle',
                'padding-left': '0px', 'padding': '0px',
                'min-width':'270px',
                "font-size":"11px"
                },
        multiple=False,
        # type="email",
        placeholder="Vsebuje: ",
    ),
    dcc.Input(
        id='checklist_atributi_secondary',
        # labelStyle={'display': 'block'},
        style={'shape': 'rectangle',
                'padding-left': '0px', 'padding': '0px',
                'min-width':'270px',
                "font-size":"11px"
                },
        multiple=False,
        # type="email",
        placeholder="Vsebuje: ",
    ),
    dcc.Input(
        id='checklist_atributi_tertiary',
        # labelStyle={'display': 'block'},
        style={'shape': 'rectangle',
                'padding-left': '0px', 'padding': '0px',
                'min-width':'270px',
                "font-size":"11px"
                },
        multiple=False,
        # type="email",
        placeholder="Vsebuje: ",
    ),
    html.Br(),
    html.Br(),
],style={
        'max-width':'280px',
        'display':'inline-block',
        # 'float':'left'
        })



toast_sunburst = dbc.Toast(
            [
                html.Div([
                # toast_sunburst_content,
                dbc.Row([
                        dbc.Col([
                                sunburst_graph
                                ]),
                        dbc.Col([
                                checklist_kategorije
                                ]),
                        dbc.Col([
                                checklist_otoki
                                ]),
                        dbc.Col([
                                checklist_atributi
                                ]),
                    
                        ]),
                # html.Hr(),
                ],
                    style={"max-height":"600px","overflow-y":"scroll","width":"310px","overflow-x":"hidden"},
                    className="g-0 p-0 m-0"),
             ],
            id="toast_sunburst",
            header="Izbor poti",
            is_open=False,
            dismissable=True,
            icon="primary",
            style={"position": "fixed", "top": 57, "right": 0, "width": "auto",  'zIndex': 5,
                   "z-index": 5},
            # top: 66 positions the toast below the navbar
            # style={'zIndex': '4'},
            # className = "opacity 70"
        )


toast_pozicioniraj = dbc.Toast(
            [
                html.I('x: '),
                dcc.Input(id='x_pozicioniraj', type='text', placeholder=' od 0 do 10',
                          size='4', 
                          style={'marginRight': '1px', 'padding': '1px', 'display': 'inline-block'}, value='',
                          className="opacity-100 p-1 mx-1 fw-bold text-primary fst-normal"),
                html.I('y: '),
                dcc.Input(id='y_pozicioniraj', type='text', placeholder=' od 0 do 10',
                          size='4', 
                          style={'marginRight': '1px', 'padding': '1px', 'display': 'inline-block'}, value='',
                          className="opacity-100 p-1 mx-1 fw-bold text-primary fst-normal"),
                html.I('scale x: '),
                dcc.Input(id='x_scale_pozicioniraj', type='text', placeholder=' od 0 do 10',
                          size='4', 
                          style={'marginRight': '1px', 'padding': '1px', 'display': 'inline-block'}, value='',
                          className="opacity-100 p-1 mx-1 fw-bold text-primary fst-normal"),
                html.I('scale y: '),
                dcc.Input(id='y_scale_pozicioniraj', type='text', placeholder=' od 0 do 10',
                          size='4', 
                          style={'marginRight': '1px', 'padding': '1px', 'display': 'inline-block'}, value='',
                          className="opacity-100 p-1 mx-1 fw-bold text-primary fst-normal"),
                dbc.Button(
                    '↔️ Premakni',
                    color='info',
                    id='premakni_sliko',
                    size="sm",
                    className="opacity-100 g-1 p-1 m-1 fw-light text-white fs-normal")
             ],
            id="toast_pozicioniraj",
            header="Pozicioniraj sliko",
            is_open=False,
            dismissable=True,
            # icon="primary",
            style={"position": "absolute", "top": 55, "left": 600, "width": 650,  'zIndex': 5,
                   "z-index": 5},
            # top: 66 positions the toast below the navbar
            # style={'zIndex': '4'},
            className = "opacity 100 bg-white"
        )

# top_sidebar = 80
top_sidebar_icon_minimize = 23
left_sidebar_icon_minimize = 265

toast_izbor_poti =  dbc.Toast([
        dbc.Button(
            '🔎 Izbor poti',
            color='info',
            id='toggle_sunburst_button',
            n_clicks=0,
            size="sm",
            className="opacity-100 g-0 p-0 m-1 fw-light text-white fs-normal",
            style={"position": "absolute",
                   "font-size":"12px",
                   'zIndex': 3,
                   "z-index": 3,
                   "visibility": "visible",
                   "width": 120,
                   "height": 30})],
              # datatable_card,
              # "This toast is placed in the top right",

              # id="toast_izbor_poti",
              # header="Tabelarični izpis",
              is_open=True,
              dismissable=False,
              # icon="danger",
              # top: 66 positions the toast below the navbar
              style={"position": "absolute", "top": top_sidebar_icon_minimize, "left": left_sidebar_icon_minimize, "width": 20,  'zIndex': 3,
                     "z-index": 3, "visibility": "hidden"},
              className="g-0 p-0 m-0 fw-light text-white fs-normal",
              )

top_sidebar_icon_minimize = 23
left_sidebar_icon_minimize = 390

sunburst_tabela_data =  dbc.Toast([
       dbc.Button(
           '✏️ Preimenuj poti',
           color='info',
           size="sm",
           id='toggle_sunburst_settings_content',
            className="opacity-100 g-0 p-0 m-1 fw-light text-white fs-normal",
            style={"position": "absolute",
                   "font-size":"12px",
                   'zIndex': 3,
                   "z-index": 3,
                   "visibility": "visible",
                   "width": 120,
                   "height": 30})],
              # datatable_card,
              # "This toast is placed in the top right",

              # id="toast_izbor_poti",
              # header="Tabelarični izpis",
              is_open=True,
              dismissable=False,
              # icon="danger",
              # top: 66 positions the toast below the navbar
              style={"position": "absolute", "top": top_sidebar_icon_minimize, "left": left_sidebar_icon_minimize, "width": 20,  'zIndex': 3,
                     "z-index": 3, "visibility": "hidden"},
              className="g-0 p-0 m-0 fw-light text-white fs-normal",
              )

top_sidebar_icon_minimize = 23
left_sidebar_icon_minimize = 515

toggle_legenda_toast =  dbc.Toast([
       dbc.Button(
           '🔘 Legenda',
           color='light',
           size="sm",
           id='toggle_legenda',
            className="opacity-100 g-0 p-0 m-1 fw-light text-primary fs-normal",
            style={"position": "absolute",
                   "font-size":"12px",
                   'zIndex': 3,
                   "z-index": 3,
                   "visibility": "visible",
                   "width": 120,
                   "height": 30})],
              # datatable_card,
              # "This toast is placed in the top right",

              # id="toast_izbor_poti",
              # header="Tabelarični izpis",
              is_open=True,
              dismissable=False,
              # icon="danger",
              # top: 66 positions the toast below the navbar
              style={"position": "absolute", "top": top_sidebar_icon_minimize, "left": left_sidebar_icon_minimize, "width": 20,  'zIndex': 3,
                     "z-index": 3, "visibility": "hidden"},
              className="g-0 p-0 m-0 fw-light text-white fs-normal",
              )

top_sidebar_icon_minimize = 73
left_sidebar_icon_minimize = -10

toggle_heatmap =  dbc.Toast([
        dbc.Button(
            '🔥',
            color='warning',
            size="sm",
            id='toggle_heatmap',
            className="opacity-100 g-0 p-0 m-1 fw-light text-primary fs-normal",
            style={"position": "absolute",
                    "font-size":"24px",
                    'zIndex': 6,
                    "z-index": 6,
                    "visibility": "visible",
                    "width": 35,
                    "height": 40
                    })],
              # datatable_card,
              # "This toast is placed in the top right",

              # id="toast_izbor_poti",
              # header="Tabelarični izpis",
              is_open=True,
              dismissable=False,
              # icon="danger",
              # top: 66 positions the toast below the navbar
              style={"position": "fixed", "top": top_sidebar_icon_minimize, "left": left_sidebar_icon_minimize, "width": 20,  'zIndex': 6,
                      "z-index": 6, "visibility": "hidden"},
              className="g-0 p-0 m-0 fw-light text-white fs-normal",
              )

top_sidebar_icon_minimize = 116
left_sidebar_icon_minimize = -10

toggle_poti =  dbc.Toast([
        dbc.Button(
            '💫',
            color='info',
            size="sm",
            id='toggle_poti',
            className="opacity-100 g-0 p-0 m-1 fw-light text-primary fs-normal",
            style={"position": "absolute",
                    "font-size":"24px",
                    'zIndex': 6,
                    "z-index": 6,
                    "visibility": "visible",
                    "width": 35,
                    "height": 40
                    })],
              # datatable_card,
              # "This toast is placed in the top right",

              # id="toast_izbor_poti",
              # header="Tabelarični izpis",
              is_open=True,
              dismissable=False,
              # icon="danger",
              # top: 66 positions the toast below the navbar
              style={"position": "fixed", "top": top_sidebar_icon_minimize, "left": left_sidebar_icon_minimize, "width": 20,  'zIndex': 6,
                      "z-index": 6, "visibility": "hidden"},
              className="g-0 p-0 m-0 fw-light text-white fs-normal",
              )

toast_floating = html.Div([toast_izbor_poti, sunburst_tabela_data,toggle_legenda_toast,toggle_heatmap,toggle_poti])
#%% Sunburst Settings Content
sunburst_settings_content = html.Div([
    dbc.Card(
        [
            dbc.CardHeader(
                [html.H4('Tabela transportnih poti', style={'display': 'inline', 'margin-right': '30px'},
                         className="p-1 mb-2 fst-normal rounded"),
                 html.Div([
                 dcc.Upload(
                     dbc.Button('📂 Odpri xlsx',
                                color='light',id='upload_datatable_button',
                                className='p-1 my-1 mx-2 me-1 fw-light border-1',
                                n_clicks=0,
                                size="sm",
                                style={'margin-left': '0px'},
                                ),
                     id = 'upload_datatable')],style={'display': 'inline','float':'right'}),
                
                 dcc.Input(id='preimenuj_atribute_input', type='text', placeholder='', size='20', style={"float":"right",'marginRight': '10px', 'marginLeft': '1px', 'padding': '1px', 'display': 'inline'}, value='',
                           className="opacity-100 p-1 mx-1 bg-white fw-bold text-primary fst-normal rounded"),
                 html.I('Dev window: ', className ='me-4', style={"float":"right"}),
                 # dbc.Button(
                 #     'breakpoint',
                 #     color='secondary',
                 #     id='breakpoint',
                 #     className='p-1 my-1 mx-1 me-1 fw-light text-white fs-normal border border-white rounded',
                 #     size='md',
                 #     n_clicks=0,
                 #     # style = {'display':'inline'},
                 # )
        
                 ], style={'backgroundColor': lightbluewhiter}),

            # dbc.CardImg(src='/assets/ball_of_sun.jpg', top=True, bottom=False, shrani_nalozi
            #             title='Image by Kevin Dinkel', alt='Learn Dash Bootstrap Card Component'),
            dbc.CardBody(
                [
                    dbc.Row(
                        [

                            dbc.Col([
                                html.I('Po spreminanju tabele: ', className ='me-5'),
                                dbc.Button('🔄 Posodobi atribute poti',id='posodobi_atribute', color="info"),
                                html.I('', className ='mx-3'),
                                dbc.Button('✏️ Izvedi preimenovanje',id='izvedi_preimenovanje', color="success"),
                                html.Hr(),
                                

                                datatable_sunburst,
                                html.Br(),

                                dcc.Store(id='datatable_sunburst_store'
                                          # , storage_type='local'
                                          ),
                                dcc.Store(id='image_layout_store'
                                           , storage_type='local'
                                          ),
                                dcc.Store(id='datatable_sunburst_active_cell_store'
                                            # , storage_type='local'
                                          ),
                                dcc.Store(id='datatable_initial_data'
                                            # , storage_type='local'
                                          ),
                            ],
                                style={'zIndex': 3},
                                className='m-1 p-1 g-1'),

                        ],
                        align="start",
                        justify="start",
                        style={
                            # "position": "relative",
                            'zIndex': 3}
                    )
                ]
            ),
        ],
        color=lightbluewhiter,  # https://bootswatch.com/default/ for more card colors
        inverse=False,  # change color of text (black or white)
        outline=False,  # True = remove the block colors from the background and header
        # style={"width": "120%"},
        className="py-1 my-1 g-0",
        # width = 6,
    ),

], style={"width": "95%", 'backgroundColor': white}, className="p-0 m-0 g-0")


Modal_sunburst_settings_content = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("⚙️ Sunburst")),
                dbc.ModalBody([
                    sunburst_settings_content
                ],            
                    # style={'width': '1200px'}
                    ),
                dbc.ModalFooter(
                    # dbc.Button(
                    #     "Zapri", id="modal_load_close", className="ms-auto", n_clicks=0
                    # )
                ),
            ],
            id="modal_sunburst_settings_content",
            is_open=False,
            size="xl",
            # style={'width': '1200px'},
        )

# %% App Layout
tab_height = '6vh'

tabs = dbc.Tabs(
                [
                    dbc.Tab(children=tab1_content, label='Transportne poti',
                            tab_id="tab1", className="p-0 m-0 g-0 text-primary",
                            style = {"font-size":"12px",'line-height': tab_height}),
                    dbc.Tab(children=tab2_content, label='Graf dolžin',
                            tab_id="tab2", className="p-0 m-0 g-0 text-primary",
                            style = {"font-size":"12px",'line-height': tab_height}
                            ,),
                    # dbc.Tab(label='Zaloga skladišča vzd.',tab_id="tab3")
                ],
                active_tab="tab1",
                id="tabs",
                style = {
                    # "width": "3000px",
                           "margin-top":"10px"
                          },
        #         className="p-1 m-1 g-1"
        )
# tabs = html.Div(
#     [
#         # dbc.CardHeader(
#             dcc.Tabs(
#                 [
#                     dcc.Tab(children=tab1_content, label='Transportne poti',
#                             value="tab1", className="p-0 m-0 g-0 fw-bold text-primary",style = {"font-size":"12px"}),
#                     dcc.Tab(children=tab2_content, label='Graf dolžin',
#                             value="tab2", className="p-0 m-0 g-0 fw-bold text-primary",
#                             style = {"font-size":"12px"}
#                             ,),
#                     # dbc.Tab(label='Zaloga skladišča vzd.',tab_id="tab3")
#                 ],
#                 # active_tab="tab1",
#                 id="tabs",
#                 style = {
#                     # "width":"100%",
#                           # "margin-top":"45px"
#                           },
#                 className="p-1 m-1 g-1"
#             # ),
#             # className="p-0 m-0 g-0 bg-white"
#         ),
#         # dbc.CardBody(id="tab_card_content",className="p-0 m-0 g-0 bg-white"),
#     ],
#     # color="light",
#     className="p-0 mx-1 g-0 mt-3",
#     style = {
#         # "width":"200%",
#                 "margin-top":"10px"
#                 }
# )
# xs Extra small<576px
# sm Small≥576px
# md Medium≥768px
# lg Large≥992px
# xl Extra large≥1200px
# (xs, sm, md, lg, xl, xxl)

stores = html.Div([dcc.Store(id='sidebar_state'),
                  dcc.Store(id='traces_mapping'),
                   dcc.Store(id='lengths_store'),
                   dcc.Store(id='izbrisi_vnos_iz_undo')
                  ])


app.layout = html.Div(
    [
        dbc.Row([
            navbar,
            # sidebar
        ]),
        dbc.Row([
            dbc.Col([
                # html.Div(
                    # [
                        dbc.Row([
                            stores,
                            # dcc.Store(id='datatable_state'),
                            html.Br(),
                            html.Br(),
                            toast_floating,
                            # navbar,
                            # sidebar,
                            # html.P(''),
                            # Modal_load,
                            # toast_izbor_poti,
                            Modal_shrani,
                            Modal_sunburst_settings_content,
                            tabs,
                            toast_sunburst,
                            toast_pozicioniraj,
                            # toasts,
                            # html.Div([
                            #     dcc.Location(id='url'),
                            #     html.Div(id='viewport_container')
                            # ], style={"visibility": "hidden"}, className='p-0 m-0 mt-2 g-0'),
                            # html.Div('', id='Tooltips_bin'),
                        ])
                        ], width=4),

        ])],
    # style = {"width":"90%","z-index": 3},
    id="app_layout_div")

# app.layout = tabs 

# %% Modals
# @app.callback(
#     Output("modal_load", "is_open"),
#     Input("odpri_button", "n_clicks"), 
#      # Input("modal_load_close", "n_clicks"),
#     [State("modal_load", "is_open")],
# )
# def toggle_modal_load(n1, is_open):
#     if n1:
#         return not is_open
#     return is_open


@app.callback(
    Output("modal_shrani", "is_open"),
    Input("shrani_button", "n_clicks"), 
    # Input("modal_shrani_close", "n_clicks"),
    [State("modal_shrani", "is_open")],
)
def toggle_modal_shrani(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("modal_sunburst_settings_content", "is_open"),
    Input("toggle_sunburst_settings_content", "n_clicks"), 
     # Input("modal_load_close", "n_clicks"),
    [State("modal_sunburst_settings_content", "is_open")],
)
def modal_sunburst_settings_content(n1, is_open):
    # breakpoint()
    if n1:
        if is_open:
            return False
        else:
            return True
    return False

#%% Toast Sunburst
@app.callback(
    Output('toast_sunburst', 'is_open'),
    [Input('toggle_sunburst_button', 'n_clicks')],
    [State("toast_sunburst", "is_open")]
)
def toast_sunburst(n, is_open):
    if n:
        if is_open:
            return False
        else:
            return True
    return False
#%% Toast pozicioniraj
@app.callback(
    Output('toast_pozicioniraj', 'is_open'),
    [Input('pozicioniraj_button', 'n_clicks')],
    [State("toast_pozicioniraj", "is_open")]
)
def toast_pozicioniraj(n, is_open):
    if n:
        if is_open:
            return False
        else:
            return True
    return False

#%% Shrani nalozi

@app.callback(
    Output("download_spaghetti_graph", "data"),
    # Output("download_traces_mapping", "data"),
    # Output("download_datatable", "data"),
    Input("download_data_button", "n_clicks"),
    State("save_file_name", "value"),
    State('spaghetti_graph', 'figure'),
    State('traces_mapping', 'data'),
    State('datatable_sunburst', 'data'),
    prevent_initial_call=True,
)
def shrani(n_click_button,filename,spaghetti_fig,traces_mapping_dict,datatable_sunburst_data):
    # breakpoint()
    filename_fig = filename +'.txt'
    spaghetti_fig['layout']['images']=None
    # filename_traces = filename +'_traces' +'.txt'
    # filename_sunburst = filename +'_sunburst' +'.txt'
    # filename_fig = filename +'.pickle'
    # with open(r'C:\Users\martinmi\Downloads\v20_pick_default.pickle', 'wb') as handle:
    #     pickle.dump([spaghetti_fig,traces_mapping_dict,datatable_sunburst_data], handle, protocol=pickle.HIGHEST_PROTOCOL)
    #     return dict(content=pickle.dump([spaghetti_fig,traces_mapping_dict,datatable_sunburst_data], handle, protocol=pickle.HIGHEST_PROTOCOL), filename=filename_fig)
    return dict(content=json.dumps([spaghetti_fig,traces_mapping_dict,datatable_sunburst_data]), filename=filename_fig)

#%% SideBar

@app.callback(
    Output('spaghetti_graph', 'figure',allow_duplicate=True),
    Output('traces_mapping', 'data',allow_duplicate=True),
    Input('upload_data', 'contents'),
    State('upload_data', 'filename'),
    State('upload_data', 'last_modified'),
    prevent_initial_call=True,
)

# @timer
def update_spagheti_bar(
                        contents_graph,
                        filename_graph,
                        last_modified_graph,
                        ):
    scaler = 58.077784760408484
    invalid_entry = False
    # breakpoint()
    content_type, content_string = contents_graph.split(',')
    decoded = base64.b64decode(content_string)
    decoded_data_list_dicts = json.loads(decoded)
    
    datatable_df = pd.DataFrame(decoded_data_list_dicts[2])
    datatable_df['name'] = datatable_df['Otok'] +":"+ datatable_df['Atribut poti']
    poti_dolzine_dict = pd.Series(datatable_df['Dolžina [m]'].values,index=datatable_df['name']).to_dict()
    decoded_dict_fig = decoded_data_list_dicts[0]
    traces_mapping_dict = decoded_data_list_dicts[1]
    
    breakpoint()
    
    for ind,trace in enumerate(decoded_dict_fig['data']):
        # breakpoint()
        if trace['type'] == 'histogram2dcontour':
            # breakpoint()
            del decoded_dict_fig['data'][ind]
        if trace['name'] == 'markers':
            # breakpoint()
            del decoded_dict_fig['data'][ind]
        
        if trace['name'] in poti_dolzine_dict.keys():
            trace['text'] = np.array([poti_dolzine_dict[trace['name']]]*len(trace['x']),dtype=object)
            trace['customdata'] = np.array([trace['name']]*len(trace['x']),dtype=object)
        else:
            trace['text'] = np.array(["Nan"]*len(trace['x']),dtype=object)
            
    spaghetti_fig = go.Figure(decoded_dict_fig)

    spaghetti_fig.add_layout_image(
        dict(
            source=lth_livarna_layout,
            xref="x",
            yref="y",
            # x=0.6,
            # y=3.7,
            # sizex=4.8,
            # sizey=4.8,
            x=x_img_loc,
            y=y_img_loc,
            sizex=scale_img_loc,
            sizey=scale_img_loc,
            # sizing="stretch",
            opacity=1,
            layer="below")
    )

    spaghetti_fig.update_layout(
        # dragmode='drawopenpath',
        width=width, height=height,
        # style of new shapes
        newshape=dict(line_color=marker_color,
                      opacity=1),
        
        legend_traceorder="reversed",
        legend=dict(bgcolor=lightbluewhiter,
                    orientation="v",
                    # bordercolor="Gray",
                    # borderwidth=1
                    yanchor="top",
                    # y=0.8,
                    x= 1,
                    # xanchor="left"
                    )
    )
    spaghetti_fig.layout.template = None
    spaghetti_fig.update_layout(hovermode='closest')
    spaghetti_fig.update_traces(hovertemplate=
                                '%{customdata}<br>Dolžina: %{text} [m]<extra></extra>',
                                )

    return spaghetti_fig, traces_mapping_dict
# %% drawlines output figure

@app.callback(
    Output('spaghetti_graph', 'figure'),
    Output('traces_mapping', 'data'),
    Output('izbrisi_vnos_iz_undo', 'data'),
    State('dropdown_name', 'options'),
    State('dropdown_groupname', 'options'),
    State('dropdown_kategorija', 'options'),
    State('spaghetti_graph','figure'),
    State('input_name', 'value'),
    State('input_groupname','value'),
    State('input_kategorija','value'),
    State('traces_mapping','data'),
    State('traces_mapping','modified_timestamp'),
    Input('izbrisi_vnos','n_clicks'),
    Input('undo_button','n_clicks'),
    Input('spaghetti_graph','relayoutData'),
    Input('upload_data', 'contents'),
    State('upload_data', 'filename'),
    State('upload_data', 'last_modified'),
    Input('checklist_kategorije', 'value'),
    Input('checklist_otoki', 'value'),
    Input('checklist_atributi', 'value'),
    State('datatable_sunburst_store', 'data'),
    State('image_layout_store','data'),
    # State('radio_viewmode', 'value'),
    Input('premakni_sliko','n_clicks'),
    State('x_pozicioniraj','value'),
    State('y_pozicioniraj','value'),
    State('x_scale_pozicioniraj','value'),
    State('y_scale_pozicioniraj','value'),
    Input('toggle_legenda','n_clicks'),
    State('datatable_initial_data', 'data'),
    Input('izvedi_preimenovanje', 'n_clicks'),
    State('datatable_sunburst', 'data'),
    Input('toggle_heatmap', 'n_clicks'),
    Input('toggle_poti', 'n_clicks'),
    Input('checklist_atributi_secondary', 'value'),
    Input('checklist_atributi_tertiary', 'value'),
    # State(component_id='all_or_none_checklist_otoki', component_property='value'),
    
    # State(component_id='all_or_none_checklist_atributi', component_property='value'),
    # Input('izvedi_preimenovanje', 'n_clicks'),
    # Input('datatable_sunburst', 'data'),
    # Input('datatable_sunburst', 'data_previous'),
    
)

# @timer
def update_spagheti_bar(
                        # spaghetti_restyledata,
                        input_name_options, input_groupname_options, input_kategorija_options, 
                        spaghetti_fig_dict, input_name_entitiy, input_groupname, input_kategorija,
                        traces_mapping_dict, traces_mapping_timestamp,
                        izbrisi_vnos_click, undo_click,relayoutData,
                        contents_graph,filename_graph,last_modified_graph,
                        checklist_kategorije,checklist_otoki,checklist_atributi,
                        datatable_sunburst_store,
                        image_layout_store,
                        # radio_viewmode_value,
                        premakni_sliko_button,
                        x_pozicioniraj_val,y_pozicioniraj_val,x_scale_pozicioniraj_val,y_scale_pozicioniraj_val,
                        toggle_legenda_click,
                        datatable_initial_data,
                        izvedi_preimenovanje_click,
                        datatable_sunburst_data,
                        toggle_heatmap,
                        toggle_poti,
                        checklist_atributi_secondary,
                        checklist_atributi_tertiary
                        # all_or_none_checklist_otoki,
                        # all_or_none_checklist_atributi
                        # legend_instances_groupname_dict
                        ):
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    ctx_triggered_property = ctx.triggered[0]['prop_id'].split('.')[1]
    scaler = 58.077784760408484
    invalid_entry = False
    if (ctx_triggered_info == 'spaghetti_graph' and ctx_triggered_property == 'relayoutData') and 'shapes' not in relayoutData.keys():
        raise dash.exceptions.PreventUpdate
    # if ctx_triggered_info == 'izbrisi_vnos' and input_name == 'break':
        # breakpoint()
    # breakpoint()
    if ctx_triggered_info == 'izvedi_preimenovanje':
        # breakpoint()
        datatable_data_new_df = pd.DataFrame(datatable_sunburst_data)
        datatable_data_old_df = pd.DataFrame(datatable_initial_data)
        datatable_data_old_df['Otok NEW'] = datatable_data_new_df['Otok']
        datatable_data_old_df['Atribut poti NEW'] = datatable_data_new_df['Atribut poti']
        datatable_data_old_df['ID_old'] = datatable_data_old_df['Otok']+':'+datatable_data_old_df['Atribut poti']
        datatable_data_old_df['ID_new'] = datatable_data_old_df['Otok NEW']+':'+datatable_data_old_df['Atribut poti NEW']
        # breakpoint()
        newnames = {k:v for k,v in zip(datatable_data_old_df['ID_old'],datatable_data_old_df['ID_new']) if not k == v}
        unmod_trace_IDs = []
        # renamed_trace_IDS = []
        # breakpoint()
        for trace in spaghetti_fig_dict['data']:
            if trace['name'] in newnames.keys():
                trace['name'] = newnames[trace['name']]
            else:
                unmod_trace_IDs.append(trace['name'])
        traces_mapping_dict_colors = {newnames.get(k, k): v for k, v in traces_mapping_dict['colors'].items()}
        # traces_mapping_dict_temp = traces_mapping_dict.copy()
        # traces_mapping_dict = traces_mapping_dict_temp.copy()
        # breakpoint()
        for old_otok,old_atribut,new_otok,new_atribut in zip(datatable_data_old_df['Otok'],datatable_data_old_df['Atribut poti'],
                                                         datatable_data_old_df['Otok NEW'],datatable_data_old_df['Atribut poti NEW']):
            # if 'LBJ' in old_atribut:
            #     breakpoint()
            if old_otok == new_otok and not old_atribut == new_atribut: #update atribut
                try:
                    traces_mapping_dict[old_otok][new_atribut] = traces_mapping_dict[old_otok][old_atribut]
                    del traces_mapping_dict[old_otok][old_atribut]
                except:
                    old_atribut = str(old_otok)+':'+str(old_atribut)
                    traces_mapping_dict[old_otok][new_atribut] = traces_mapping_dict[old_otok][old_atribut]
                    del traces_mapping_dict[old_otok][old_atribut]
                    # breakpoint()
                # traces_mapping_dict[old_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
                # del traces_mapping_dict[old_otok][old_atribut]
            elif old_atribut == new_atribut and not old_otok == new_otok: #update otok
                try:
                    if new_otok not in traces_mapping_dict.keys():
                        traces_mapping_dict[new_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
                    else:
                        traces_mapping_dict[new_otok].update({str(new_atribut): traces_mapping_dict[old_otok][old_atribut]})
                    del traces_mapping_dict[old_otok][old_atribut]
                except:
                    old_atribut = str(old_otok)+':'+str(old_atribut)
                    if new_otok not in traces_mapping_dict.keys():
                        traces_mapping_dict[new_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
                    else:
                        # breakpoint()
                        traces_mapping_dict[new_otok].update({str(new_atribut): traces_mapping_dict[old_otok][old_atribut]})
                    del traces_mapping_dict[old_otok][old_atribut] 
                    # breakpoint()
            elif not old_atribut == new_atribut and old_otok == new_otok: #oboje preimenovano
                try:
                    if new_otok not in traces_mapping_dict.keys():
                        traces_mapping_dict[new_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
                    else:
                        traces_mapping_dict[new_otok].update({str(new_atribut): traces_mapping_dict[old_otok][old_atribut]})
                    del traces_mapping_dict[old_otok]
                except:
                    old_atribut = str(old_otok)+':'+str(old_atribut)
                    if new_otok not in traces_mapping_dict.keys():
                        traces_mapping_dict[new_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
                    else:
                        traces_mapping_dict[new_otok].update({str(new_atribut): traces_mapping_dict[old_otok][old_atribut]})
                    del traces_mapping_dict[old_otok]
                    # breakpoint()
            # elif old_atribut == new_atribut and old_otok == new_otok: # ni preimenovanja
            #     # breakpoint()
            #     # old_atribut = str(old_otok)+':'+str(old_atribut)
            #     # old_atribut = old_atribut
            #     # new_atribut = new_atribut
            #     try:
            #         if new_otok not in traces_mapping_dict.keys():
            #             traces_mapping_dict[new_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
            #         else:
            #             traces_mapping_dict[new_otok].update({str(new_atribut): traces_mapping_dict[old_otok][old_atribut]})
            #         del traces_mapping_dict[old_otok][old_atribut]
            #     except:
            #         old_atribut = str(old_otok)+':'+str(old_atribut)
            #         if new_otok not in traces_mapping_dict.keys():
            #             traces_mapping_dict[new_otok] = {str(new_atribut): traces_mapping_dict[old_otok][old_atribut]}
            #         else:
            #             # breakpoint()
            #             if old_atribut in traces_mapping_dict[old_otok].keys():
            #                 breakpoint()
            #                 traces_mapping_dict[new_otok].update({str(new_atribut): traces_mapping_dict[old_otok][old_atribut]})
            #                 del traces_mapping_dict[old_otok][old_atribut]
            #             else:
            #                 breakpoint()
 
                
        traces_mapping_dict_legend_instances = {newnames.get(k, k): v for k, v in traces_mapping_dict['legend_instances'].items()}
        i = 0
        for ID in traces_mapping_dict['traces_list']:
            if ID in newnames.keys():
                traces_mapping_dict['traces_list'][i] = newnames[ID]
            i += 1
        traces_mapping_dict['legend_instances'] = traces_mapping_dict_legend_instances
        traces_mapping_dict['colors'] = traces_mapping_dict_colors
        spaghetti_fig_dict['layout']['shapes'] = None
                         
        for trace in spaghetti_fig_dict['data']:
            if trace['name'] in newnames.values():
                trace['customdata'] = np.array([trace['name']]*len(trace['x']),dtype=object)
                
        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        spaghetti_fig.update_layout(newshape=dict(line_color=marker_color,opacity=1),legend_traceorder="reversed")
        spaghetti_fig.layout.template = None
        # breakpoint()
        return spaghetti_fig, traces_mapping_dict, no_update
    
    if input_name_entitiy == None or input_groupname == None or input_kategorija == None:
        invalid_entry = True
        
    else:
        if len(input_name_entitiy) == 0 or len(input_groupname) == 0 or len(input_kategorija) == 0:
            invalid_entry = True
    # breakpoint()
    if (ctx_triggered_info == 'spaghetti_graph' and ctx_triggered_property == 'relayoutData') and invalid_entry: #ne narisi crte
        spaghetti_fig_dict['layout']['shapes'] = None
        # spaghetti_fig_dict['layout']['images'] = [image_layout_store]
        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        if not 'images' in spaghetti_fig_dict['layout'].keys():
            spaghetti_fig.add_layout_image(
                dict(
                    source=lth_livarna_layout,
                    xref="x",
                    yref="y",
                    # x=0.6,
                    # y=3.7,
                    # sizex=4.8,
                    # sizey=4.8,
                    x=x_img_loc,
                    y=y_img_loc,
                    sizex=scale_img_loc,
                    sizey=scale_img_loc,
                    # sizing="stretch",
                    opacity=1,
                    layer="below")
            )
        else:
            type(spaghetti_fig_dict['layout']['images']) == list
            if len(spaghetti_fig_dict['layout']['images']) >= 2:
                spaghetti_fig_dict['layout']['images'] = [spaghetti_fig_dict['layout']['images'][0]]
        spaghetti_fig.update_layout(
            # dragmode='drawopenpath',
            width=width, height=height,
            # style of new shapes
            newshape=dict(line_color=marker_color,
                          opacity=1),
            
            legend_traceorder="reversed"
        )
        spaghetti_fig.layout.template = None
        return spaghetti_fig, no_update, no_update
    
    if ctx_triggered_info == 'toggle_legenda':
        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        if spaghetti_fig.layout.showlegend == True:
            spaghetti_fig.update_layout(
                showlegend=False,
            )
        elif spaghetti_fig.layout.showlegend == False:
            spaghetti_fig.update_layout(
                showlegend=True,
            )
        return spaghetti_fig, no_update, no_update
    
    if ctx_triggered_info == 'premakni_sliko':
        # breakpoint()
        spaghetti_fig_dict['layout']['shapes'] = None
        spaghetti_fig_dict['layout']['images'][0]['x'] = float(x_pozicioniraj_val)
        spaghetti_fig_dict['layout']['images'][0]['y'] = float(y_pozicioniraj_val)
        spaghetti_fig_dict['layout']['images'][0]['sizex'] = float(x_scale_pozicioniraj_val)
        spaghetti_fig_dict['layout']['images'][0]['sizey'] = float(y_scale_pozicioniraj_val)
        # spaghetti_fig_dict['layout']['images'] = [image_layout_store]
        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        spaghetti_fig.update_layout(
            # dragmode='drawopenpath',
            width=width, height=height,
            # style of new shapes
            newshape=dict(line_color=marker_color,
                          opacity=1),
            
            legend_traceorder="reversed"
        )
        spaghetti_fig.layout.template = None
        return spaghetti_fig, traces_mapping_dict, no_update
               
    if len(input_name_options) == 0:
        input_name_options = [
            {'label': input_name_entitiy, 'value': input_name_entitiy}]
    else:
        input_name_options_vals = [
            v[-1] for x, v in [element.items() for element in input_name_options]]
        if not input_name_entitiy in input_name_options_vals:
            input_name_options.append(
                {'label': input_name_entitiy, 'value': input_name_entitiy})
            
    if len(input_groupname_options) == 0:
        input_groupname_options = [
            {'label': input_groupname, 'value': input_groupname}]
    else:
        input_groupname_options_vals = [
            v[-1] for x, v in [element.items() for element in input_groupname_options]]
        # input_groupname_options_vals = [x['label'] for x in input_groupname_options]
        if not input_groupname in input_groupname_options_vals:
            input_groupname_options.append(
                {'label': input_groupname, 'value': input_groupname})
            
    if len(input_kategorija_options) == 0:
        input_kategorija_options = [
            {'label': input_kategorija, 'value': input_kategorija}]
    else:
        input_kategorija_options_vals = [
            v[-1] for x, v in [element.items() for element in input_kategorija_options]]
        # input_kategorija_options_vals = [x['label'] for x in input_kategorija_options]
        if not input_kategorija in input_kategorija_options_vals:
            input_kategorija_options.append(
                {'label': input_kategorija, 'value': input_kategorija})
            
    # breakpoint()
    if traces_mapping_dict == None:
        traces_mapping_dict = dict()
        trace_id = -1
        traces_mapping_dict['number_of_traces'] = trace_id
        traces_mapping_dict['traces_list'] = list()
        traces_mapping_dict['legend_instances'] = {}
        traces_mapping_dict['colors'] = {}
        # breakpoint()
    elif traces_mapping_dict['number_of_traces'] > -1:
        traces_inds = []
        for key, value in recursive_items(traces_mapping_dict):
            if key == 'trace_id':
                traces_inds.append(value)
        trace_id = max(traces_inds)
        # traces_mapping_dict.update({'legend_instances':legend_instances_groupname_dict})
        # breakpoint()
    if ctx_triggered_info == 'undo_button':
        # breakpoint()
        trace_id_list = traces_mapping_dict['traces_list']
        # spaghetti_fig_dict['layout']['shapes'] = None
        # spaghetti_fig_dict['layout']['images'] = [image_layout_store]
        # breakpoint()
        
        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        if not 'images' in spaghetti_fig_dict['layout'].keys():
            spaghetti_fig.add_layout_image(
                dict(
                    source=lth_livarna_layout,
                    xref="x",
                    yref="y",
                    # x=0.6,
                    # y=3.7,
                    # sizex=4.8,
                    # sizey=4.8,
                    x=x_img_loc,
                    y=y_img_loc,
                    sizex=scale_img_loc,
                    sizey=scale_img_loc,
                    # sizing="stretch",
                    opacity=1,
                    layer="below")
            )
        else:
            type(spaghetti_fig_dict['layout']['images']) == list
            if len(spaghetti_fig_dict['layout']['images']) >= 2:
                spaghetti_fig_dict['layout']['images'] = [spaghetti_fig_dict['layout']['images'][0]]

        spaghetti_fig.update_layout(
            # dragmode='drawopenpath',
            width=width, height=height,
            # style of new shapes
            newshape=dict(line_color=marker_color,
                          opacity=1),
            
            legend_traceorder="reversed"
        )
        spaghetti_fig.layout.template = None
        if input_groupname in traces_mapping_dict.keys():
            if input_name_entitiy in traces_mapping_dict[input_groupname]:
                # breakpoint()
                last_step_number = str(max(
                    [int(x) for x in traces_mapping_dict[input_groupname][input_name_entitiy]['steps'].keys()]))
                number_of_points_to_remove = len(
                    traces_mapping_dict[input_groupname][input_name_entitiy]['steps'][last_step_number]['x'])
                trace_id_to_trim = str(input_groupname) + \
                    ':'+str(input_name_entitiy)
                ind_to_trim = trace_id_list.index(trace_id_to_trim)
                # breakpoint()
                spaghetti_fig.data[ind_to_trim].x = [
                    x for x in spaghetti_fig.data[ind_to_trim].x][:-number_of_points_to_remove]
                spaghetti_fig.data[ind_to_trim].y = [
                    y for y in spaghetti_fig.data[ind_to_trim].y][:-number_of_points_to_remove]
                del traces_mapping_dict[input_groupname][input_name_entitiy]['steps'][last_step_number]
                if len(traces_mapping_dict[input_groupname][input_name_entitiy]['steps']) ==0: #izbrisi_vnos
                    trace_id_list = traces_mapping_dict['traces_list']
                    trace_id_to_remove = str(input_groupname)+':'+str(input_name_entitiy)
                    # ind_to_remove = trace_id_list.index(trace_id_to_remove)
                    traces_mapping_dict['number_of_traces'] = traces_mapping_dict['number_of_traces'] - 1
                    # instances_list = traces_mapping_dict['legend_instances'][input_groupname]['instances']
                    # show_hide_list = traces_mapping_dict['legend_instances'][input_groupname]['visible']

                    for idx,trace in enumerate(spaghetti_fig_dict['data']):
                        if trace['name'] == trace_id_to_remove:
                            del spaghetti_fig_dict['data'][idx]
                    del traces_mapping_dict[input_groupname][input_name_entitiy]
                    del traces_mapping_dict['legend_instances'][input_groupname+':'+input_name_entitiy]
                    del traces_mapping_dict['colors'][trace_id_to_remove]
                    if len(traces_mapping_dict[input_groupname].keys()) == 0:
                        del traces_mapping_dict[input_groupname]
                    trace_id_list.remove(trace_id_to_remove)

                    spaghetti_fig = go.Figure(spaghetti_fig_dict)
                    return spaghetti_fig, traces_mapping_dict, datetime.datetime.now()
                return spaghetti_fig, traces_mapping_dict, no_update

    if ctx_triggered_info == 'izbrisi_vnos':
        trace_id_list = traces_mapping_dict['traces_list']
        trace_id_to_remove = str(input_groupname)+':'+str(input_name_entitiy)
        # ind_to_remove = trace_id_list.index(trace_id_to_remove)
        traces_mapping_dict['number_of_traces'] = traces_mapping_dict['number_of_traces'] - 1
        del traces_mapping_dict[input_groupname][input_name_entitiy]
        del traces_mapping_dict['legend_instances'][input_groupname+':'+input_name_entitiy]
        del traces_mapping_dict['colors'][trace_id_to_remove]
        if len(traces_mapping_dict[input_groupname].keys()) == 0:
            del traces_mapping_dict[input_groupname]
        trace_id_list.remove(trace_id_to_remove)
        # breakpoint()
        for idx,trace in enumerate(spaghetti_fig_dict['data']):
            if trace['name'] == trace_id_to_remove:
                del spaghetti_fig_dict['data'][idx]
        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        # breakpoint()
        return spaghetti_fig, traces_mapping_dict, no_update
    # breakpoint()
    if ctx_triggered_info == 'spaghetti_graph' and not ctx_triggered_property == 'restyleData' and 'shapes' in relayoutData.keys(): #rises
        # time.sleep(0.2)
    
        trace_id_list = traces_mapping_dict['traces_list']
        if input_groupname in traces_mapping_dict.keys():
            if input_name_entitiy in traces_mapping_dict[input_groupname]:
                trace_id = traces_mapping_dict['number_of_traces']
                traces_mapping_dict['number_of_traces'] = trace_id
            else:
                trace_id = traces_mapping_dict['number_of_traces'] + 1
                traces_mapping_dict['number_of_traces'] = trace_id
        else:
            trace_id = traces_mapping_dict['number_of_traces'] + 1
            traces_mapping_dict['number_of_traces'] = trace_id

        if not relayoutData == None:
            shape_type = relayoutData['shapes'][0]['type']
            
            if shape_type == 'rect':
                coords_x = [relayoutData['shapes'][0]['x0'], relayoutData['shapes'][0]['x1'], relayoutData['shapes'][0]['x1'], relayoutData['shapes'][0]['x0'],relayoutData['shapes'][0]['x0']]
                coords_y = [relayoutData['shapes'][0]['y0'], relayoutData['shapes'][0]['y0'], relayoutData['shapes'][0]['y1'], relayoutData['shapes'][0]['y1'],relayoutData['shapes'][0]['y0']]
            elif shape_type == 'line':
                coords_x = [relayoutData['shapes'][0]['x0'], relayoutData['shapes'][0]['x1']]
                coords_y = [relayoutData['shapes'][0]['y0'], relayoutData['shapes'][0]['y1']]
            else:
                raw_coords_list = relayoutData['shapes'][0]['path'].replace(
                    'M', 'L').split('L')
                coords_x = [float(x.split(',')[0])
                            for x in raw_coords_list if not len(x) == 0]
                coords_y = [float(x.split(',')[1])
                            for x in raw_coords_list if not len(x) == 0]
                
            spaghetti_fig_dict['layout']['shapes'] = None
            # spaghetti_fig_dict['layout']['images'] = [image_layout_store]
            spaghetti_fig = go.Figure(spaghetti_fig_dict)
            if not 'images' in spaghetti_fig_dict['layout'].keys():
                spaghetti_fig.add_layout_image(
                    dict(
                        source=lth_livarna_layout,
                        xref="x",
                        yref="y",
                        # x=0.6,
                        # y=3.7,
                        # sizex=4.8,
                        # sizey=4.8,
                        x=x_img_loc,
                        y=y_img_loc,
                        sizex=scale_img_loc,
                        sizey=scale_img_loc,
                        # sizing="stretch",
                        opacity=1,
                        layer="below")
                )
            else:
                type(spaghetti_fig_dict['layout']['images']) == list
                if len(spaghetti_fig_dict['layout']['images']) >= 2:
                    spaghetti_fig_dict['layout']['images'] = [spaghetti_fig_dict['layout']['images'][0]]
            spaghetti_fig.update_layout(
                # dragmode='drawopenpath',
            width=width, height=height,
                # style of new shapes
                newshape=dict(line_color=marker_color,
                              opacity=1),
                
                legend_traceorder="reversed"
            )
            spaghetti_fig.layout.template = None
            # spaghetti_fig.update_layout(legend_traceorder="reversed")

            # breakpoint()
            # if not type(traces_mapping_dict['traces_list']) == list():
            #     traces_mapping_dict['traces_list'] = list()
            # breakpoint()
            if input_groupname in traces_mapping_dict.keys():
                if input_name_entitiy in traces_mapping_dict[input_groupname]: #extendej (ni novega trace)
                    # append_trace = True
                    # breakpoint()
                    trace_id_to_append = str(
                        input_groupname)+':'+str(input_name_entitiy)
                    ind_to_append = trace_id_list.index(trace_id_to_append)
                    spaghetti_fig.data[ind_to_append].x = [
                        x for x in spaghetti_fig.data[ind_to_append].x] + coords_x
                    spaghetti_fig.data[ind_to_append].y = [
                        y for y in spaghetti_fig.data[ind_to_append].y] + coords_y
                    next_step_number = max(
                        [int(x) for x in traces_mapping_dict[input_groupname][input_name_entitiy]['steps'].keys()]) + 1
                    # breakpoint()
                    # traces_mapping_dict[input_groupname][input_name_entitiy]['steps'].update({next_step_number:{'x':coords_x,'y':coords_y}})
                    # breakpoint()
                    traces_mapping_dict[input_groupname][input_name_entitiy]['steps'].update({str(next_step_number): {
                        'x': coords_x, 'y': coords_y}}) # damn, če ni str(key) poj kr ni več dict tole in vrze callback error
                    # breakpoint()
                    
                    x = np.array(spaghetti_fig.data[ind_to_append].x)
                    y = np.array(spaghetti_fig.data[ind_to_append].y)
                    dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2
                    dolzina=np.round(np.sum(np.sqrt(dist_array))*scaler,decimals=1)
                    text_object = [dolzina]*len(x)
                    customdata_object = [input_groupname+':'+input_name_entitiy]*len(x)
                    
                    spaghetti_fig.data[ind_to_append].text = text_object
                    spaghetti_fig.data[ind_to_append].customdata = customdata_object
                    spaghetti_fig.layout.font.size = 16
                    spaghetti_fig.update_layout(legend_traceorder="reversed")
                    spaghetti_fig.layout.template = None
                    spaghetti_fig.update_layout(hovermode='closest')
                    spaghetti_fig.update_traces(hovertemplate=
                                        '%{customdata}<br>Dolžina: %{text} [m]<extra></extra>',
                                        )
                    
                    return [spaghetti_fig, traces_mapping_dict, no_update]

                else: #novi trace
                
                    traces_mapping_dict[input_groupname].update(
                        {input_name_entitiy: {'x': coords_x, 'y': coords_y, 'trace_id': trace_id}})
                    if not type(traces_mapping_dict['traces_list']) == list():
                        traces_mapping_dict['traces_list'] = list()
                    traces_mapping_dict.update(
                        {'traces_list': trace_id_list + [(str(input_groupname)+':'+str(input_name_entitiy))]})
                    traces_mapping_dict[input_groupname][input_name_entitiy].update(
                        {'steps': {0: {'x': coords_x, 'y': coords_y}}})
                    # breakpoint()
                    trace_ID = str(input_groupname)+':'+str(input_name_entitiy)
                    if trace_ID not in traces_mapping_dict['legend_instances'].keys():
                        traces_mapping_dict['legend_instances'].update({trace_ID:{'visible':[True]}})
                    
                    i = 0
                    
                    # breakpoint()
                    taken_colors = [vals for vals in traces_mapping_dict['colors'].values()]
                    color_picked = False
                    if input_groupname in [ID.split(":")[0] for ID in traces_mapping_dict['colors'].keys()]:
                        instance=list(traces_mapping_dict[input_groupname].keys())[0]
                        next_color = traces_mapping_dict['colors'][(str(input_groupname)+':'+str(instance))]
                        color_picked = True
                    
                    if not color_picked:
                        while colors_list[traces_mapping_dict[input_groupname][input_name_entitiy]['trace_id']+i] in taken_colors:
                            i = i + 1
                        next_color = colors_list[traces_mapping_dict[input_groupname][input_name_entitiy]['trace_id']+i]
                    
                    x = np.array(coords_x)
                    y = np.array(coords_y)
                    dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2
                    dolzina=np.round(np.sum(np.sqrt(dist_array))*scaler,decimals=1)
                    text_object = [dolzina]*len(coords_x)
                    customdata_object = [input_groupname+':'+input_name_entitiy]*len(coords_x)

                    spaghetti_fig.add_trace(go.Scatter(
                        x=coords_x,
                        y=coords_y,
                        mode='lines',
                        text= text_object,
                        name=input_groupname+':'+input_name_entitiy,
                        customdata = customdata_object,
                        # name=input_name_entitiy,
                        # legendgroup=input_groupname,
                        # legendgrouptitle_text=input_groupname,
                        opacity=1,
                        line=dict(width=4),
                        connectgaps=True,
                        # line_shape='spline',
                        marker = dict(color = next_color)
                        
                    ))
                    spaghetti_fig.layout.font.size = 16
                    spaghetti_fig.update_layout(legend_traceorder="reversed")
                    spaghetti_fig.layout.template = None
                    spaghetti_fig.update_layout(hovermode='closest')
                    spaghetti_fig.update_traces(hovertemplate=
                                        '%{customdata}<br>Dolžina: %{text} [m]<extra></extra>',
                                        )
                    traces_mapping_dict['colors'].update({(str(input_groupname)+':'+str(input_name_entitiy)):next_color})
                    # breakpoint()
                    # spaghetti_fig_returned = spaghetti_fig.to_dict()
                    # for ind, trace in enumerate(spaghetti_fig_dict['data']):
                    #     if 'name' in trace.keys():
                    #         if trace['name']=='markers':
                    #             idcs_2_remove = idcs_2_remove + [ind]
                    #         else:
                    #             if trace['name'] in list_of_IDs_to_show:
                    #                 spaghetti_fig_dict['data'][ind].update({'visible':True})
                    #             else:
                    #                 spaghetti_fig_dict['data'][ind].update({'visible':False})
                    return spaghetti_fig, traces_mapping_dict, no_update
                    # spaghetti_fig.update_yaxes(range=[0,4])
                    # spaghetti_fig.update_xaxes(range=[1,6])
            else: #novi trace
                traces_mapping_dict[input_groupname] = {input_name_entitiy: {
                    'x': coords_x, 'y': coords_y, 'trace_id': trace_id}}
                if not type(traces_mapping_dict['traces_list']) == list():
                    traces_mapping_dict['traces_list'] = list()
                traces_mapping_dict.update(
                    {'traces_list': trace_id_list + [(str(input_groupname)+':'+str(input_name_entitiy))]})
                traces_mapping_dict[input_groupname][input_name_entitiy].update(
                    {'steps': {'0': {'x': coords_x, 'y': coords_y}}})
                # breakpoint()
                trace_ID = str(input_groupname)+':'+str(input_name_entitiy)
                if trace_ID not in traces_mapping_dict['legend_instances'].keys():
                    traces_mapping_dict['legend_instances'].update({trace_ID:{'visible':[True]}})
                i = 0
                # breakpoint()
                taken_colors = [vals for vals in traces_mapping_dict['colors'].values()]
                
                color_picked = False
                if input_groupname in [ID.split(":")[0] for ID in traces_mapping_dict['colors'].keys()]:
                    instance=list(traces_mapping_dict[input_groupname].keys())[0]
                    next_color = traces_mapping_dict['colors'][(str(input_groupname)+':'+str(instance))]
                    color_picked = True
                

                if not color_picked:
                    while colors_list[traces_mapping_dict[input_groupname][input_name_entitiy]['trace_id']+i] in taken_colors:
                        i = i + 1
                        
                next_color = colors_list[traces_mapping_dict[input_groupname][input_name_entitiy]['trace_id']+i]
                x = np.array(coords_x)
                y = np.array(coords_y)
                dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2
                dolzina=np.round(np.sum(np.sqrt(dist_array))*scaler,decimals=1)
                text_object = [dolzina]*len(coords_x)
                customdata_object = [input_groupname+':'+input_name_entitiy]*len(coords_x)
            
                spaghetti_fig.add_trace(go.Scatter(
                    x=coords_x,
                    y=coords_y,
                    mode='lines',
                    text= text_object,
                    name=input_groupname+':'+input_name_entitiy,
                    customdata = customdata_object,
                    opacity=1,
                    line=dict(width=4),
                    connectgaps=True,
                    # line_shape='spline',
                    marker = dict(color = next_color)
                    
                ))
                spaghetti_fig.layout.font.size = 16
                spaghetti_fig.update_layout(legend_traceorder="reversed")
                spaghetti_fig.layout.template = None
                spaghetti_fig.update_layout(hovermode='closest')
                spaghetti_fig.update_traces(hovertemplate=
                                    '%{customdata}<br>Dolžina: %{text} [m]<extra></extra>',
                                    )
                traces_mapping_dict['colors'].update({(str(input_groupname)+':'+str(input_name_entitiy)):next_color})
                # breakpoint()
                # spaghetti_fig_returned = spaghetti_fig.to_dict()
                return spaghetti_fig, traces_mapping_dict, no_update
    # breakpoint()
    
    # Input('checklist_kategorije', 'value'),
    # Input('checklist_otoki', 'value'),
    # Input('checklist_atributi', 'value'),
    
    
    if (ctx_triggered_info == 'toggle_heatmap' or ctx_triggered_info == 'toggle_poti' or ctx_triggered_info == 'checklist_kategorije' or ctx_triggered_info == 'checklist_atributi'  or ctx_triggered_info == 'checklist_otoki' or ctx_triggered_info == 'checklist_atributi_secondary' or ctx_triggered_info == 'checklist_atributi_tertiary'):
        
        datatable_sunburst_selected_df= pd.DataFrame(datatable_sunburst_store)
                
        if not checklist_kategorije == None:
            if not len(checklist_kategorije) == 0:
                if type(checklist_kategorije) == str:
                    checklist_kategorije = [checklist_kategorije]
                datatable_sunburst_selected_df = datatable_sunburst_selected_df[datatable_sunburst_selected_df['Kategorija'].isin(checklist_kategorije)]    
        
        if not checklist_otoki == None:
            if not len(checklist_otoki) == 0:
                if type(checklist_otoki) == str:
                    checklist_otoki = [checklist_otoki]
                datatable_sunburst_selected_df = datatable_sunburst_selected_df[datatable_sunburst_selected_df['Otok'].isin(checklist_otoki)]
        
        if type(checklist_atributi) == list:
            checklist_atributi = checklist_atributi[0]
        if not checklist_atributi == None:
            datatable_sunburst_selected_df = datatable_sunburst_selected_df[datatable_sunburst_selected_df['Atribut poti'].str.contains(checklist_atributi)]
            
        if type(checklist_atributi_secondary) == list:
            checklist_atributi_secondary = checklist_atributi_secondary[0]
        if not checklist_atributi_secondary == None:
            datatable_sunburst_selected_df = datatable_sunburst_selected_df[datatable_sunburst_selected_df['Atribut poti'].str.contains(checklist_atributi_secondary)]
            
        if type(checklist_atributi_tertiary) == list:
            checklist_atributi_tertiary = checklist_atributi_tertiary[0]
        if not checklist_atributi_tertiary == None:
            datatable_sunburst_selected_df = datatable_sunburst_selected_df[datatable_sunburst_selected_df['Atribut poti'].str.contains(checklist_atributi_tertiary)]
        

        list_of_IDs_to_show = list(datatable_sunburst_selected_df['Otok'] + ':' + datatable_sunburst_selected_df['Atribut poti'])
        # ab = [spaghetti_fig_dict['data'][x].update({'visible':'legendonly'}) if x['name'] in list_of_IDs_to_show else spaghetti_fig_dict['data'][x].update({'visible':True}) for x in spaghetti_fig_dict['data']]
        idcs_2_remove = []

        for ind, trace in enumerate(spaghetti_fig_dict['data']):
            if 'name' in trace.keys():
                if trace['name']=='markers':
                    idcs_2_remove = idcs_2_remove + [ind]
                else:
                    if trace['name'] in list_of_IDs_to_show:
                        spaghetti_fig_dict['data'][ind].update({'visible':True})
                    else:
                        spaghetti_fig_dict['data'][ind].update({'visible':False})
            else:
                idcs_2_remove = idcs_2_remove + [ind]
                
        for index in sorted(idcs_2_remove, reverse=True):
            del spaghetti_fig_dict['data'][index]

        spaghetti_fig = go.Figure(spaghetti_fig_dict)
        if not 'images' in spaghetti_fig_dict['layout'].keys():
            spaghetti_fig.add_layout_image(
                dict(
                    source=lth_livarna_layout,
                    xref="x",
                    yref="y",
                    # x=0.6,
                    # y=3.7,
                    # sizex=4.8,
                    # sizey=4.8,
                    x=x_img_loc,
                    y=y_img_loc,
                    sizex=scale_img_loc,
                    sizey=scale_img_loc,
                    # sizing="stretch",
                    opacity=1,
                    layer="below")
            )
        else:
            type(spaghetti_fig_dict['layout']['images']) == list
            if len(spaghetti_fig_dict['layout']['images']) >= 2:
                spaghetti_fig_dict['layout']['images'] = [spaghetti_fig_dict['layout']['images'][0]]
        spaghetti_fig.update_layout(
            # dragmode='drawopenpath',
            width=width, height=height,
            # style of new shapes
            newshape=dict(line_color=marker_color,
                          opacity=1),
            
            legend_traceorder="reversed"
        )
        spaghetti_fig.layout.template = None
        spaghetti_fig.update_traces(hovertemplate=
                                    '%{customdata}<br>Dolžina: %{text} [m]<extra></extra>',
                                    )
        # breakpoint()
        for ID in traces_mapping_dict['legend_instances'].keys():
            if ID in list_of_IDs_to_show:
                traces_mapping_dict['legend_instances'][ID].update({'visible':True})
            else:
                traces_mapping_dict['legend_instances'][ID].update({'visible':False})
                
        if ctx_triggered_info == 'toggle_heatmap':
            # breakpoint()
            datatable_data_selected_heatmap_df = datatable_sunburst_selected_df.copy()
            datatable_data_selected_heatmap_df['Število enot'] = datatable_data_selected_heatmap_df['Število enot'].astype(int)
            datatable_data_selected_heatmap_df['ID_name'] = datatable_data_selected_heatmap_df['Otok'] + ':' + datatable_data_selected_heatmap_df['Atribut poti'] 
            # max_gostota = 0.0005
            # max_enot = max(datatable_data_selected_heatmap_df['Število enot'])
            # min_enot = min(datatable_data_selected_heatmap_df['Število enot'])
            # min_gostota = max_gostota * max_enot/min_enot
            # k_utezi = (max_gostota-min_gostota)/(max_enot-min_enot)
            # n_utezi = max_gostota - k_utezi*max_enot
            # def get_utez_gostota(stevilo_enot):
            #     return k_utezi*stevilo_enot + n_utezi
           
            x_all = []
            y_all = []
            poti_stevilo_enot_dict = pd.Series(datatable_data_selected_heatmap_df['Število enot'].values,index=datatable_data_selected_heatmap_df['ID_name']).to_dict()
            dolzine_dict = dict(zip(datatable_data_selected_heatmap_df['ID_name'], datatable_data_selected_heatmap_df['Dolžina [m]']))
            
            for trace in spaghetti_fig_dict['data']:
                if trace['name'] in poti_stevilo_enot_dict.keys():
                    trace_linestring = redistribute_vertices(LineString(tuple([x,y] for x,y in zip(trace['x'],trace['y']))),1/poti_stevilo_enot_dict[trace['name']],trace['name'])
                    x_all=x_all + list(trace_linestring.xy[0])
                    y_all=y_all + list(trace_linestring.xy[1])
                # else:
                #     pass
                    # breakpoint()
                    
            # heatmap = go.Histogram2d(
            #                 x=x_all,
            #                 y=y_all,
            #                 # colorscale='YlGnBu',
            #                 # zmax=400,
            #                 # nbinsx=60,
            #                 # nbinsy=60,
            #                 xbins=dict(size=0.1,start=0.3),
            #                 ybins=dict(size=0.1*0.6),
            #                 histnorm='probability density',
            #                 zauto=False,
            #                 opacity=0.65,
            #                 colorbar=dict(len=0.25,y=0.8,x=0.9),
            #             )
            import plotly.figure_factory as ff
            colorscale = ['#7A4579', '#D56073', 'rgb(236,158,105)',(1, 1, 0.2), (0.98,0.98,0.98)]
            density_plot = ff.create_2d_density(
                            x=x_all, y=y_all,
                            # hist_color='rgb(255, 237, 222)',
                            colorscale=colorscale,
                            ncontours  = 20,
                            # height = height*0.2,
                            # width = width*0.4,
                            # opacity = 0.5
                        )
            density_fig_dict = density_plot.to_dict()
            del density_fig_dict['data'][-1]
            del density_fig_dict['data'][-1]
            del density_fig_dict['data'][0]
            # for idx,trace in enumerate(density_fig_dict['data']):
            #     if trace['type']=='histogram':
            #         # breakpoint()
            #         del density_fig_dict['data'][idx]
            # breakpoint()
            density_fig_cleared = go.Figure(density_fig_dict)
            
                
            # for idx,trace in enumerate(density_fig_dict['data']):
            #     if trace['type']=='histogram2dcontour':
            #         breakpoint()
            #         spaghetti_fig.add_trace(density_fig_cleared.data)
                    
            spaghetti_fig = go.Figure(data=spaghetti_fig.data + density_fig_cleared.data,layout=spaghetti_fig.layout)
            # spaghetti_fig = fig3.to_dict()
            spaghetti_fig.add_layout_image(
                dict(
                    source=lth_livarna_layout,
                    xref="x",
                    yref="y",
                    # x=0.6,
                    # y=3.7,
                    # sizex=4.8,
                    # sizey=4.8,
                    x=x_img_loc,
                    y=y_img_loc,
                    sizex=scale_img_loc,
                    sizey=scale_img_loc,
                    # sizing="stretch",
                    opacity=0.3,
                    layer="above")
            )
            spaghetti_fig.update_traces(
                hovertemplate='<extra></extra>%{z}'
                # hovertemplate='<extra></extra>Dolžina [m]: %{x:.1f} m'
                )
            # spaghetti_fig = px.density_heatmap(
            #                 x=x_all, y=y_all,
            #                 color_continuous_scale='inferno',
            #                 # hist_color='rgb(255, 237, 222)',
            #                 height = height,
            #                 width = width,
            #             )
            # # spaghetti_fig.add_trace(heatmap)
            # spaghetti_fig.update_traces(hovertemplate=
            #                     '%{z}<extra></extra>', selector=dict(type='histogram2d'))
            # spaghetti_fig.update_traces(visible = False, selector=dict(type='scatter'))

    
            # spaghetti_fig.add_trace(go.Scatter(
            #     x=x_all,
            #     y=y_all,
            #     mode='markers',
            #     name='markers',
            #     opacity=1,
            #     visible='legendonly'
            # ))
            
            # breakpoint()
            # image_heatmap = (go.Figure(heatmap)).to_image()
            # image_array = np.array(Image.open(io.BytesIO(image_heatmap))) 
            #mogla bi bit grayscale single channel, ne RGBA
            # fig.show()
            # 2d_array = np.array([x_all,y_all])
            # def convolution2d(image, kernel, bias):
            #     m, n = kernel.shape
            #     if (m == n):
            #         y, x = image.shape
            #         y = y - m + 1
            #         x = x - m + 1
            #         new_image = np.zeros((y,x))
            #         for i in range(y):
            #             for j in range(x):
            #                 new_image[i][j] = np.sum(image[i:i+m, j:j+m]*kernel) + bias
            #     return new_image

        if ctx_triggered_info == 'toggle_poti':
            # spaghetti_fig_dict = spaghetti_fig.to_dict()
            if len(spaghetti_fig_dict['layout']['images']) > 1:
                for ind,image in enumerate(spaghetti_fig_dict['layout']['images']):
                    if image['layer'] == 'above':
                        del spaghetti_fig_dict['layout']['images'][ind]
            spaghetti_fig = spaghetti_fig_dict
                    
        return spaghetti_fig, traces_mapping_dict, no_update
    raise dash.exceptions.PreventUpdate

#%% iz izberi dropdown v vnesi input
@app.callback(
    Output('input_name', 'value'),
    Input('dropdown_name', 'value'),
    Input('sunburst_poti', 'clickData'),
    Input('spaghetti_graph', 'clickData'),
    prevent_initial_call=False
)
def input_name(dropdown_name,clickData,pot_graph_clicked):
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx_triggered_info == 'sunburst_poti':
        # breakpoint()
        level_hiearchy_string = clickData['points'][0]['id']
        level_hiearchy_list = level_hiearchy_string.split('/')
        if len(level_hiearchy_list) >= 4:
            clicked_atribut = level_hiearchy_list[3]
            return clicked_atribut
    elif ctx_triggered_info == 'spaghetti_graph':
        return pot_graph_clicked['points'][0]['customdata'].split(":")[-1]
    else:
        return dropdown_name
    # return dropdown_name
# spaghetti_graph
@app.callback(
    Output('input_groupname', 'value'),
    Input('dropdown_groupname','value'),
    Input('sunburst_poti', 'clickData'),
    Input('spaghetti_graph', 'clickData'),

    prevent_initial_call=False
)
def input_groupname(dropdown_groupname,clickData,pot_graph_clicked):
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx_triggered_info == 'sunburst_poti':
        # breakpoint()
        level_hiearchy_string = clickData['points'][0]['id']
        level_hiearchy_list = level_hiearchy_string.split('/')
        if len(level_hiearchy_list) >= 3:
            clicked_sklop = level_hiearchy_list[2]
            return clicked_sklop
        else:
            return no_update
    elif ctx_triggered_info == 'spaghetti_graph':
        return pot_graph_clicked['points'][0]['customdata'].split(":")[0]
    elif ctx_triggered_info == 'dropdown_groupname':
        return dropdown_groupname
    # return dropdown_groupname
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output('input_kategorija', 'value'),
    Input('dropdown_kategorija','value'),
    Input('sunburst_poti', 'clickData'),
    prevent_initial_call=False
)
def input_kategorija(dropdown_kategorija,clickData):
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    if ctx_triggered_info == 'sunburst_poti':
        # breakpoint()
        level_hiearchy_string = clickData['points'][0]['id']
        level_hiearchy_list = level_hiearchy_string.split('/')
        if len(level_hiearchy_list) >= 2:
            clicked_kategorija = level_hiearchy_list[1]
            return clicked_kategorija
        else:
            return no_update
    elif ctx_triggered_info == 'dropdown_kategorija':
        return dropdown_kategorija
    raise dash.exceptions.PreventUpdate
# %% poti lengths plot
@app.callback(
    Output('spaghetti_plot_lengths', 'figure'),
    Output('lengths_store', 'data'),
    Output('download_graf_dolžine_izpis_xlsx', 'data'),
    Output('download_graf_dolžine_izpis_xlsx_vsi_stolpci', 'data'),
    # Input('spaghetti_graph', 'restyleData'),
    # State('spaghetti_graph', 'figure'),
    State('traces_mapping', 'data'),
    Input('traces_mapping', 'modified_timestamp'),
    Input('radioitems_poti_rubrike', 'value'),
    Input('graf_dolžine_izpis_xlsx', 'n_clicks'),
    State('save_file_name_download_graf_dolžine_izpis', 'value'),
    State('datatable_sunburst_store', 'data'),
    
    # Input('undo_button', 'n_clicks'),
    # Input('viewport_container',
    #       'children'),
    prevent_initial_call=False
)
# @timer
def update_spaghetti_plot_lengths(
                                  # restyleData,spaghetti_graph,
                                  traces_mapping_dict, traces_mapping_timestamp, radioitems_poti_rubrike,
                                  graf_dolžine_izpis_xlsx_click,
                                  save_file_name_input,
                                  datatable_sunburst_store
                                   # undo_click,
                                  # viewport_container
                                  ):
    
    
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    download_graf_dolžine = no_update
    time.sleep(0.3)
    # breakpoint()
    if ctx_triggered_info == 'traces_mapping':
        time.sleep(0.3)
    if ctx_triggered_info == '':
        raise dash.exceptions.PreventUpdate
    rubrike_linij_list = []
    poti_list = []
    dolzine_list = []
    unique_identifier = []
    # lengths_store_dict = {}
    scaler = 58.077784760408484  # v metre
    # breakpoint()
    # spaghetti_fig.data[0].line.color
    for rubrike_linij in traces_mapping_dict.keys():
        if rubrike_linij == 'number_of_traces' or rubrike_linij == 'traces_list' or rubrike_linij =='legend_instances' or rubrike_linij == 'colors':
            continue
        index_hidden_state_list = 0
        for Pot in traces_mapping_dict[rubrike_linij].keys():
            # breakpoint()
            # indeks_poti_legend_instances_instances = traces_mapping_dict['legend_instances'][rubrike_linij]['instances'].index(Pot)
            if Pot == 'x' or Pot == 'trace_id' or Pot == 'y' or traces_mapping_dict['legend_instances'][rubrike_linij+':'+Pot]['visible'] == False:
                continue
            list_of_lists_x = [traces_mapping_dict[rubrike_linij][Pot]['steps'][step]['x']
                               for step in traces_mapping_dict[rubrike_linij][Pot]['steps'].keys()]
            list_of_lists_y = [traces_mapping_dict[rubrike_linij][Pot]['steps'][step]['y']
                               for step in traces_mapping_dict[rubrike_linij][Pot]['steps'].keys()]
            x = np.array([x for l in list_of_lists_x for x in l])
            y = np.array([y for l in list_of_lists_y for y in l])
            dist_array = (x[:-1]-x[1:])**2 + (y[:-1]-y[1:])**2
            dolzine_list.append(np.sum(np.sqrt(dist_array))*scaler)
            rubrike_linij_list.append(rubrike_linij)
            poti_list.append(Pot)
            unique_identifier.append(rubrike_linij+':'+Pot)
            index_hidden_state_list += 1 

    df_dolzine = pd.DataFrame(list(zip(rubrike_linij_list, poti_list, dolzine_list, unique_identifier)), columns=[
                              'Otok', 'Pot', 'Dolžina [m]', 'ID'])
    lengths_store_dict=df_dolzine.set_index('ID')
    lengths_store_dict=lengths_store_dict[['Dolžina [m]']].to_dict('index')
    # breakpoint()
    if radioitems_poti_rubrike == 'Po poteh':
        x_column = 'ID'
        color_column = 'ID'
        barmode='relative'
    elif radioitems_poti_rubrike == 'Po otokih':
        x_column = 'Otok'
        color_column = 'ID'
        barmode='stack'
    spaghetti_plot_lengths = px.bar(data_frame=df_dolzine, x=x_column, y='Dolžina [m]', color=color_column,             # differentiate color of marks
                                    color_discrete_map = traces_mapping_dict['colors'],
                                    custom_data=['Pot'],
                                    # set opacity of markers (from 0 to 1)
                                    opacity=0.9,
                                    orientation='v',              # 'v','h': orientation of the marks
                                    barmode=barmode,
                                    width=1500,
                                    height=500,
                                
                                    # labels={column_sklop:column_sklop}
                                    # hover_data={
                                    # 'Vrsta stroška ': dff_groupby[column_vrsta_stroska],
                                    # data not in dataframe, customized formatting
                                    # 'suppl_2': (':.3f', np.random.random(len(df)))
                                    # }
                                    )
    spaghetti_plot_lengths.update_traces(
        hovertemplate='<extra></extra>Otok: %{x}<br>Pot: %{customdata[0]}<br>Dolžina: %{y:.1f} m'
        # hovertemplate='<extra></extra>Dolžina [m]: %{x:.1f} m'
        )
    spaghetti_plot_lengths.update_layout(
        showlegend=False,
        # title="Plot Title",
        xaxis_title="Transportna pot",
        yaxis_title="Dolžina [m]",
        # legend_x = 0.745,
        # legend_y = 1.0,
        # legend_title="Pot",
        
        paper_bgcolor=piechart_paper_bgcolor,
        plot_bgcolor='rgb(251, 251, 251)',
        # font=dict(
        #     family="helvetica",
        #     size=17,
        #     color="rgb(61, 61, 92)"
        # ),
        font={'family': 'Bahnschrift', 'size': 13},
        legend=dict(bgcolor='rgb(245, 245, 245)',
                    orientation="v",
                    # bordercolor="Gray",
                    # borderwidth=1
                    # yanchor="top",
                    # y=1,
                    # x=1.3,
                    # xanchor="right"
                    ),
        # bargap=0.1,  # gap between bars of adjacent location coordinates.
        # bargroupgap=0.1,
        xaxis={
            'categoryorder': 'total ascending'}
    )
    
    # fig2_stroski = px.line(dff_groupby, y=dff_groupby['Meja'],
    #                x=column_sklop, color=px.Constant('Meja'), color_discrete_sequence=['yellow'])
    # if not len(fig2_stroski.data)==0:
    #     fig_stroski.add_trace(fig2_stroski.data[0])
    # fig_stroski.update_layout(plot_bgcolor='rgb(251, 251, 251)')
    # spaghetti_plot_lengths.update_layout(margin=dict(t=0.3, b=0, l=0, r=0))
    # spaghetti_plot_lengths.layout.xaxis.fixedrange = True
    # spaghetti_plot_lengths.layout.yaxis.fixedrange = True
    # spaghetti_plot_lengths.update_traces(width=0.12)
    download_graf_dolžine_vsi_stolpci = no_update
    
    if ctx_triggered_info == 'graf_dolžine_izpis_xlsx':
        datatable_sunburst_store_df = pd.DataFrame(datatable_sunburst_store)
        datatable_sunburst_store_df['ID'] = datatable_sunburst_store_df['Otok'] +':'+ datatable_sunburst_store_df['Atribut poti']
        dff_groupby=df_dolzine.groupby([x_column],as_index=False).agg(lambda x : x.sum() if x.dtype=='float64' else ', '.join(x))
        dff_groupby['Dolžina [m]']= dff_groupby['Dolžina [m]'].apply(lambda x: "{:.1f}".format(x))
        datatable_sunburst_store_df_no_duplicate=datatable_sunburst_store_df.drop_duplicates(subset='Otok', keep='first')
        datatable_sunburst_store_df_no_duplicate=datatable_sunburst_store_df_no_duplicate.reset_index(drop=True)
        dff_groupby['Kategorija'] = get_dictionary_from_df_pripadnost_columns('Otok', 'Kategorija', dff_groupby,datatable_sunburst_store_df_no_duplicate)
        # dff_groupby = df_dolzine.groupby([x_column])['Dolžina [m]'].sum().reset_index()
        filename = save_file_name_input + ".xlsx"
        # breakpoint()
        
        download_graf_dolžine = no_update
        # download_graf_dolžine = dcc.send_data_frame(dff_groupby.to_excel, filename, sheet_name=filename)
        
        filename = save_file_name_input+'_vsi_stolpci' + ".xlsx"
        # datatable_sunburst_store_df_export_selected = datatable_sunburst_store[]unique_identifier
        datatable_sunburst_store_df_export_selected = datatable_sunburst_store_df[datatable_sunburst_store_df['ID'].isin(unique_identifier)]
        download_graf_dolžine_vsi_stolpci = dcc.send_data_frame(datatable_sunburst_store_df_export_selected.to_excel, filename, sheet_name=filename)
        

    return spaghetti_plot_lengths,lengths_store_dict, download_graf_dolžine, download_graf_dolžine_vsi_stolpci


# %% edit 1 entry datatable
# @timer
@app.callback(
    Output('datatable_initial_data', 'data'),
    # State('datatable_initial_data', 'data'),
    # Input('datatable_initial_data', 'modified_timestamp'),
    Input('datatable_sunburst', 'data'),
    State('datatable_sunburst', 'data_previous'),
    State('datatable_sunburst', 'active_cell'),
    State('datatable_initial_data', 'data'),
    Input('izvedi_preimenovanje', 'n_clicks'),
    Input('posodobi_atribute', 'n_clicks'),
    # Input('upload_datatable_sunburst_data', 'last_modified'),
    prevent_initial_call=False
)
def edit_one_entry_datatable(
        # n_clicks, 
                     # datatable_sunburst_active_cell_store,datatable_sunburst_active_cell_store_timestamp,
                     datatable_data,
                     datatable_data_previous,
                     datatable_data_active_cell,
                     datatable_initial_data,
                     izvedi_preimenovanje_click,
                     posodobi_atribute_click
                     ):

    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    # ctx_triggered_property = ctx.triggered[0]['prop_id'].split('.')[1]
    # breakpoint()
    if ctx_triggered_info == 'izvedi_preimenovanje':
        # initial_datatable_data = datatable_data
        # breakpoint()
        return datatable_data
    
    if ctx_triggered_info == 'posodobi_atribute':
       if datatable_initial_data == None:
           initial_datatable_data = datatable_data_previous
       else:
           initial_datatable_data = datatable_initial_data 
       time.sleep(0.3)
       return initial_datatable_data
    
    if datatable_data == None or datatable_data_previous == None:
        raise dash.exceptions.PreventUpdate
    
    if datatable_initial_data == None:
        initial_datatable_data = datatable_data_previous
    else:
        initial_datatable_data = datatable_initial_data
    
    time.sleep(0.3)
    # breakpoint()
    # raise dash.exceptions.PreventUpdate
    return initial_datatable_data
# %% Sunburst, dcc store (posodobitev)
# @timer
@app.callback(
    Output('datatable_sunburst', 'data'),
    Output('datatable_sunburst_store', 'data'),
    Output('sunburst_poti', 'figure'),
    # Output('datatable_sunburst_active_cell_store', 'data'),
    # Input('dodaj_vrstico_button', 'n_clicks'),
    Input('datatable_sunburst', 'data'),
    State('datatable_sunburst', 'columns'),
    Input('upload_data', 'contents'),
    State('upload_data', 'filename'),
    State('upload_data', 'last_modified'),
    State('datatable_sunburst_store', 'data'),
    State('datatable_sunburst_store', 'modified_timestamp'),
    State('input_name', 'value'),
    State('input_groupname', 'value'),
    State('input_kategorija', 'value'),
    State('traces_mapping','modified_timestamp'),
    State('traces_mapping','data'),
    Input('lengths_store','modified_timestamp'),
    State('lengths_store','data'),
    Input('izbrisi_vnos','n_clicks'),
    Input('izbrisi_vnos_iz_undo','modified_timestamp'),
    State('izbrisi_vnos_iz_undo','data'),
    State('preimenuj_atribute_input', 'value'),
    State('datatable_sunburst', 'active_cell'),
    # Input('breakpoint', 'n_clicks'),
    State('datatable_sunburst', 'data_previous'),
    Input('posodobi_atribute','n_clicks'),
    Input('izvedi_preimenovanje','n_clicks'),
    State('datatable_initial_data', 'data'),
    Input('upload_datatable', 'contents'),
    State('upload_datatable', 'filename'),
    State('upload_datatable', 'last_modified'),
    prevent_initial_call=False
)
def update_dcc_store(
        # n_clicks, 
                     datatable_sunburst_data, columns,
                     contents_graph, filename_graph, last_modified_graph,
                     datatable_sunburst_store_data, datatable_sunburst_store_timestamp,
                     input_name,input_groupname,input_kategorija,
                     traces_mapping_dict_timestamp,traces_mapping_dict,
                     lengths_store_timestamp,lengths_store,
                     nclicks_izbrisi_vnos,izbrisi_vnos_undo_timestamp,izbrisi_vnos_undo,
                     preimenuj_atribute_input,
                     datatable_sunburst_active_cell, datatable_data_previous,
                     posodobi_atribute_click,izvedi_preimenovanje,
                     datatable_initial_data,
                     upload_datatable_contents,upload_datatable_filename,upload_datatable_last_modified,
                     ):
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    # ctx_triggered_property = ctx.triggered[0]['prop_id'].split('.')[1]
    # breakpoint()
    invalid_entry = False
    datatable_vals = [input_kategorija,input_groupname,input_name]
    if input_name == None or input_groupname == None or input_kategorija == None:
        invalid_entry = True
    elif len(input_name) == 0 or len(input_groupname) == 0 or len(input_kategorija) == 0:
        invalid_entry = True
    if ctx_triggered_info == 'posodobi_atribute' and preimenuj_atribute_input == 'random':   
        # breakpoint()
        derived_data_df = pd.DataFrame(datatable_sunburst_data)
        letters = string.ascii_uppercase*20
        letters_list = [''.join(random.choice(letters) for i in range(5)) for x in letters]
        numbers = string.digits*20
        numbers_list = [''.join(random.choice(numbers) for i in range(4)) for x in numbers]
        # derived_data_df['Delovno mesto'] = ''.join(random.choice(letters_list) for i in range(5))
        derived_data_df['Delovno mesto'] = np.random.choice(letters_list, derived_data_df.shape[0])
        derived_data_df['I/O'] = np.random.choice(letters_list, derived_data_df.shape[0])
        derived_data_df['Prazne/Polne'] = np.random.choice(letters_list, derived_data_df.shape[0])
        derived_data_df['Tip'] = np.random.choice(letters_list, derived_data_df.shape[0])
        derived_data_df['Število enot'] = np.random.choice(numbers_list, derived_data_df.shape[0])
        
        derived_data_df['Atribut poti'] = derived_data_df['Delovno mesto']+', '+derived_data_df['I/O']+', '+derived_data_df['Prazne/Polne']+', '+derived_data_df['Tip']
        datatable_rows = derived_data_df.to_dict('records')
        return datatable_rows, datatable_rows, no_update
    
    if ctx_triggered_info == 'upload_datatable':   
        # breakpoint()
        content_type, content_string = upload_datatable_contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_excel(io.BytesIO(decoded))
        datatable_rows = (pd.DataFrame(df)).to_dict('records')
        # breakpoint()
        # er
        # če obstaja MATCH, dodaj, nove (brez obstoječe definicije v poteh) ignoriraj, že narisane, stare potke, brez novih definicij pusti
        datatable_initial_data_df = pd.DataFrame(datatable_initial_data)
        return datatable_rows, datatable_rows, no_update
    
    # if ctx_triggered_info == 'posodobi_atribute' and preimenuj_atribute_input == 'break':   
    #     breakpoint()
    #     datatable_sunburst_data_df = pd.DataFrame(datatable_sunburst_data)
    #     spaghetti_fig_df = spaghetti_fig.to_dict()
    if ctx_triggered_info == 'posodobi_atribute':   
        # breakpoint()
        derived_data_df = pd.DataFrame(datatable_sunburst_data)
        derived_data_df['Atribut poti'] = derived_data_df['Delovno mesto']+', '+derived_data_df['I/O']+', '+derived_data_df['Prazne/Polne']+', '+derived_data_df['Tip']
        datatable_rows = derived_data_df.to_dict('records')
        return datatable_rows, datatable_rows, no_update
    
    if ctx_triggered_info == 'izvedi_preimenovanje':   
        # breakpoint()
        sunburst_data = pd.DataFrame(datatable_sunburst_data)
        datatable_rows = sunburst_data.to_dict('records')
        sunburst_data['Vse'] = 'Vse'
        sunburst_data['Skupina'] = sunburst_data['Otok'].astype(str).str[0:3]
        # breakpoint()
        fig_sunburst_updated = px.sunburst(
            data_frame=sunburst_data,
            path=['Vse','Kategorija', 'Otok'],  # Root, branches, leaves
            color='Skupina',
            width=244,
            height=244,
            maxdepth=-1,                        # set the sectors rendered. -1 will render all levels in the hierarchy
            branchvalues='total',  # total or 'remainder'
            template='seaborn'
        )
        fig_sunburst_updated.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            font_color='white',
            title_font_color='white',
            font={'family': 'Bahnschrift', 'size': 13},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_sunburst_updated.update_traces(
            hovertemplate=None,
        )

        fig_sunburst_updated.layout.template = None
        return datatable_rows, datatable_rows, fig_sunburst_updated

    if ctx_triggered_info == 'izbrisi_vnos' or ctx_triggered_info == 'izbrisi_vnos_iz_undo':
        # breakpoint()
        i_to_rem = 0
        for row in datatable_sunburst_data:
            if row['Otok'] == input_groupname and row['Atribut poti'] == input_name:
                # breakpoint()
                break
            i_to_rem += 1
        del datatable_sunburst_data[i_to_rem]
        
        datatable_sunburst_store_data_df_new = pd.DataFrame(datatable_sunburst_store_data)
        datatable_sunburst_store_data_df_new['Vse'] = 'Vse'
        index_to_remove_from_df = (datatable_sunburst_store_data_df_new[(datatable_sunburst_store_data_df_new['Atribut poti']  == input_name) & (datatable_sunburst_store_data_df_new['Otok'] == input_groupname)].index.tolist())[0]
        datatable_sunburst_store_data_df_new = datatable_sunburst_store_data_df_new.drop(labels=[index_to_remove_from_df], axis=0)
        # breakpoint()
        sunburst_data = datatable_sunburst_store_data_df_new.copy()
        sunburst_data['Skupina'] = sunburst_data['Otok'].astype(str).str[0:3]
        
        fig_sunburst = px.sunburst(
            data_frame=sunburst_data,
            path=['Vse','Kategorija', 'Otok'],  # Root, branches, leaves
            color='Skupina',
            width=244,
            height=244,
            maxdepth=-1,                        # set the sectors rendered. -1 will render all levels in the hierarchy
            branchvalues='total',  # total or 'remainder'
            template='seaborn',
        )
        fig_sunburst.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            font_color='white',
            title_font_color='white',
            font={'family': 'Bahnschrift', 'size': 13},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        fig_sunburst.update_traces(
            hovertemplate=None,
        )
        fig_sunburst.layout.template = None
        print('izbrisi_vnos')
        return datatable_sunburst_data, datatable_sunburst_data, fig_sunburst
        
    # content_type, content_string = upload_datatable_contents.split(',')
    # decoded = base64.b64decode(content_string)
    # df = pd.read_excel(io.BytesIO(decoded))
    elif ctx_triggered_info == 'upload_data':
        # breakpoint()
        content_type, content_string = contents_graph.split(',')
        decoded = base64.b64decode(content_string)
        decoded_data_list_dicts=json.loads(decoded)
        uploaded = decoded_data_list_dicts[2]
    #     # breakpoint()
        data_df = pd.DataFrame(uploaded)
        data_df['Vse'] = 'Vse'
        sunburst_data = data_df.copy()
        sunburst_data['Skupina'] = sunburst_data['Otok'].astype(str).str[0:3]
        # breakpoint()
        fig_sunburst = px.sunburst(
            data_frame=sunburst_data,
            path=['Vse','Kategorija', 'Otok'],  # Root, branches, leaves
            color='Skupina',
            width=244,
            height=244,
            maxdepth=-1,                        # set the sectors rendered. -1 will render all levels in the hierarchy
            branchvalues='total',  # total or 'remainder'
            template='seaborn',
        )
        fig_sunburst.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            font_color='white',
            title_font_color='white',
            font={'family': 'Bahnschrift', 'size': 13},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        fig_sunburst.update_traces(
            hovertemplate=None,
        )
        # breakpoint()
        fig_sunburst.layout.template = None
        return uploaded, uploaded, fig_sunburst

    elif ctx_triggered_info == 'lengths_store':
        # breakpoint()
        if not invalid_entry: #ko rišeš updatanje sunbursta po izrisu dolžin na graf
            if not datatable_sunburst_data == None:
                rows_dict = {k:[v['Kategorija'],v['Otok'],v['Atribut poti']] for k,v in zip(range(0,len(datatable_sunburst_data)),datatable_sunburst_data)}
                if not [datatable_vals[0],datatable_vals[1],datatable_vals[2]] in rows_dict.values() and datatable_vals[1]+':'+datatable_vals[2] in lengths_store.keys():
                    datatable_vals.append(np.round(lengths_store[datatable_vals[1]+':'+datatable_vals[2]]['Dolžina [m]'],decimals=1))
                    datatable_sunburst_data.append({c['id']: datatable_vals for c,datatable_vals in zip(columns,datatable_vals)})
                    data_df = pd.DataFrame(datatable_sunburst_data)
                    data_df['Vse'] = 'Vse'
                    sunburst_data = data_df.copy()
                    sunburst_data['Skupina'] = sunburst_data['Otok'].astype(str).str[0:3]
                    # data_df = pd.concat()
                    fig_sunburst = px.sunburst(
                        data_frame=sunburst_data,
                        path=['Vse','Kategorija', 'Otok'],  # Root, branches, leaves
                        color='Skupina',
                        width=244,
                        height=244,
                        maxdepth=-1,                        # set the sectors rendered. -1 will render all levels in the hierarchy
                        branchvalues='total',  # total or 'remainder'
                        template='seaborn',
                    )
                    fig_sunburst.update_layout(
                        margin=dict(t=0, l=0, r=0, b=0),
                        font_color='white',
                        title_font_color='white',
                        font={'family': 'Bahnschrift', 'size': 13},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )
                    fig_sunburst.update_traces(
                        hovertemplate=None,
                    )
                    fig_sunburst.layout.template = None
                    print('lengths_store')
                    return datatable_sunburst_data, datatable_sunburst_data, fig_sunburst
                else:
                    raise dash.exceptions.PreventUpdate
                # breakpoint()
                      
            if datatable_sunburst_data == None:
                datatable_vals.append(np.round(lengths_store[datatable_vals[1]+':'+datatable_vals[2]]['Dolžina [m]'],decimals=1))
                datatable_sunburst_data = [{c['id']: datatable_vals for c,datatable_vals in zip(columns,datatable_vals)}]
                return datatable_sunburst_data, datatable_sunburst_data, no_update
        else: # upload data
            # breakpoint()
            # raise dash.exceptions.PreventUpdate
            # breakpoint()
            data_df_temp = pd.DataFrame(datatable_sunburst_data)
            data_df_temp['name'] = data_df_temp['Otok'] +":"+ data_df_temp['Atribut poti']
            data_df_temp['Vse'] = 'Vse'
            data_df_temp_dict = data_df_temp.to_dict('records')
            
            if len(lengths_store) == len(data_df_temp_dict):
                for row in data_df_temp_dict:
                    # if row['name'] not in lengths_store.keys():
                    row['Dolžina [m]'] = lengths_store[row['name']]['Dolžina [m]']
            else:
                raise dash.exceptions.PreventUpdate
            data_df = pd.DataFrame(data_df_temp_dict)
            data_df['Dolžina [m]'] = data_df['Dolžina [m]'].apply(lambda x: round(x, 1))
            sunburst_data = data_df.copy()
            sunburst_data['Skupina'] = sunburst_data['Otok'].astype(str).str[0:3]
            fig_sunburst = px.sunburst(
                data_frame=sunburst_data,
                path=['Vse','Kategorija', 'Otok'],  # Root, branches, leaves
                color='Skupina',
                width=244,
                height=244,
                maxdepth=-1,                        # set the sectors rendered. -1 will render all levels in the hierarchy
                branchvalues='total',  # total or 'remainder'
                template='seaborn',
            )
            fig_sunburst.update_layout(
                margin=dict(t=0, l=0, r=0, b=0),
                font_color='white',
                title_font_color='white',
                font={'family': 'Bahnschrift', 'size': 13},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            fig_sunburst.update_traces(
                hovertemplate=None,
            )
            fig_sunburst.layout.template = None
            data_df.drop('name', inplace=True, axis=1)
            data_df.drop('Vse', inplace=True, axis=1)
            data_dict_out = data_df.to_dict('records')
            return data_dict_out, data_dict_out, fig_sunburst
    else:
        # breakpoint()
        raise dash.exceptions.PreventUpdate
#%% Checklist Kategorije Sunburst Interactivity
@app.callback(
    Output(component_id='checklist_kategorije', component_property='options'),
    Output(component_id='checklist_kategorije', component_property='value'),
    Output(component_id='checklist_otoki', component_property='options'),
    Output(component_id='checklist_otoki', component_property='value'),
    # Output(component_id='all_or_none_checklist_otoki', component_property='value'),
    Input(component_id='sunburst_poti', component_property='clickData'),
    # Input(component_id='all_or_none_checklist_kategorije', component_property='value'),
    State(component_id='checklist_kategorije', component_property='options'),
    Input(component_id='checklist_kategorije', component_property='value'),
    # State(component_id='all_or_none_checklist_otoki', component_property='value'),
    State(component_id='checklist_otoki', component_property='options'),
    Input(component_id='checklist_otoki', component_property='value'),
    # Input(component_id='all_or_none_checklist_atributi', component_property='value'),
    # State(component_id='checklist_atributi', component_property='options'),
    Input(component_id='checklist_atributi', component_property='value'),
    Input('datatable_sunburst', 'data'),
    prevent_initial_call=False
)
# @timer
def update_checklists_kategorije_otoki_atributi(clickData, 
                                # all_selected_kategorije,
                                options_kategorije,values_kategorije,
                                # all_selected_otoki,
                                options_otoki,values_otoki,
                                # all_selected_atributi, options_atributi,
                                values_atributi,
                                datatable_sunburst_data,
                            # datatable_sunburst_store_data, datatable_sunburst_store_timestamp
                            ):
    # print('*********************************************')
    # print('clickData: {}'.format(clickData))
    ctx = dash.callback_context
    ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
    # breakpoint()
    sunburst_df = pd.DataFrame(datatable_sunburst_data)

    
    if ctx_triggered_info == 'checklist_kategorije' or ctx_triggered_info == 'checklist_otoki':
        # breakpoint()
        current_selection_df = sunburst_df
        if type(values_kategorije) == str:
            values_kategorije = [values_kategorije]
        if type(values_otoki) == str:
            values_otoki = [values_otoki]
        # if type(values_atributi) == str:
        #     values_atributi = [values_atributi]    
        if not len(values_kategorije) == 0:
            current_selection_df = current_selection_df[current_selection_df['Kategorija'].isin(values_kategorije)]
        else:
            raise dash.exceptions.PreventUpdate 
        if not len(values_otoki) == 0:    
            current_selection_df = current_selection_df[current_selection_df['Otok'].isin(values_otoki)]
        else:
            # kategorije = np.unique(current_selection_df['Kategorija'].values)
            otoki = np.unique(current_selection_df['Otok'].values)
            # atributi = np.unique(current_selection_df['Atribut poti'].values)
            checklist_kategorije_options = no_update
            checklist_kategorije_values = no_update
            checklist_otoki_options = [{'label': i, 'value': i} for i in otoki]
            checklist_otoki_values = no_update
            checklist_atributi_options = no_update
            checklist_atributi_values = no_update
            return checklist_kategorije_options, checklist_kategorije_values,checklist_otoki_options,checklist_otoki_values
        
        if not ctx_triggered_info == 'checklist_otoki':
            if not len(values_atributi) == 0: 
                current_selection_df = current_selection_df[current_selection_df['Atribut poti'].str.isin(values_atributi)]
            else:
                # kategorije = np.unique(current_selection_df['Kategorija'].values)
                # otoki = np.unique(current_selection_df['Otok'].values)
                atributi = np.unique(current_selection_df['Atribut poti'].values)
                checklist_kategorije_options = no_update
                checklist_kategorije_values = no_update
                checklist_otoki_options = no_update
                checklist_otoki_values = no_update
                checklist_atributi_options = [{'label': i, 'value': i} for i in atributi]
                checklist_atributi_values = no_update
                return checklist_kategorije_options, checklist_kategorije_values,checklist_otoki_options, checklist_otoki_values
        # breakpoint()
    
    if ctx_triggered_info == 'datatable_sunburst':
        if len(sunburst_df) == 0:
            raise dash.exceptions.PreventUpdate 
        # breakpoint()
        kategorije = np.unique(sunburst_df['Kategorija'].values)
        otoki = np.unique(sunburst_df['Otok'].values)
        atributi = np.unique(sunburst_df['Atribut poti'].values)
        checklist_kategorije_options = [{'label': i, 'value': i} for i in kategorije]
        # checklist_kategorije_values = list(kategorije)
        checklist_kategorije_values = no_update
        checklist_otoki_options = [{'label': i, 'value': i} for i in otoki]
        # checklist_otoki_values = list(otoki)
        checklist_otoki_values = no_update
        checklist_atributi_options = [{'label': i, 'value': i} for i in atributi]
        # checklist_atributi_values = list(atributi)
        checklist_atributi_values = no_update
        return checklist_kategorije_options, checklist_kategorije_values,checklist_otoki_options, checklist_otoki_values
    
    if ctx_triggered_info == 'sunburst_poti':
        # breakpoint()
        level_hiearchy_string = clickData['points'][0]['id']
        level_hiearchy_list = level_hiearchy_string.split('/')
        if len(level_hiearchy_list) == 4:
            atribut_clicked = level_hiearchy_list[3]
            return no_update, no_update, no_update, no_update
        elif len(level_hiearchy_list) == 3:
            otok_clicked = level_hiearchy_list[2]
            preostali_atributi_df = sunburst_df[sunburst_df['Otok'] == otok_clicked]
            preostali_atributi = list(np.unique(preostali_atributi_df['Atribut poti'].values))
            checklist_atributi_options = [{'label': i, 'value': i} for i in preostali_atributi]
            return no_update,no_update,no_update,otok_clicked
        elif len(level_hiearchy_list) == 2:
            kategorija_clicked = level_hiearchy_list[1]
            preostali_otoki_df = sunburst_df[sunburst_df['Kategorija'] == kategorija_clicked]
            preostali_otoki = list(np.unique(preostali_otoki_df['Otok'].values))
            checklist_otoki_options = [{'label': i, 'value': i} for i in preostali_otoki]
            preostali_atributi_df = sunburst_df[sunburst_df['Kategorija'] == kategorija_clicked]
            preostali_atributi = list(np.unique(preostali_atributi_df['Atribut poti'].values))
            checklist_atributi_options = [{'label': i, 'value': i} for i in preostali_atributi]
            return no_update, kategorija_clicked, checklist_otoki_options, preostali_otoki
        elif len(level_hiearchy_list) == 1:
            # breakpoint()
            kategorije = np.unique(sunburst_df['Kategorija'].values)
            otoki = np.unique(sunburst_df['Otok'].values)
            atributi = np.unique(sunburst_df['Atribut poti'].values)
            checklist_kategorije_options = [{'label': i, 'value': i} for i in kategorije]
            checklist_kategorije_values = list(kategorije)
            checklist_otoki_options = [{'label': i, 'value': i} for i in otoki]
            checklist_otoki_values = list(otoki)
            checklist_atributi_options = [{'label': i, 'value': i} for i in atributi]
            checklist_atributi_values = list(atributi)
            return checklist_kategorije_options, checklist_kategorije_values,checklist_otoki_options, checklist_otoki_values
        else:
            raise dash.exceptions.PreventUpdate 

    # elif ctx_triggered_info == 'all_or_none_checklist_kategorije':
    #     all_or_none_kategorije = []
    #     all_or_none_kategorije = [option['value'] for option in options_kategorije if all_selected_kategorije]
    #     # options_kategorije=[{'label': 'Izberi vse', 'value': 'All'}]
    #     return no_update, all_or_none_kategorije, no_update, no_update, no_update, no_update
            
    # elif ctx_triggered_info == 'all_or_none_checklist_otoki':
    #     # breakpoint()
    #     current_selection_df = sunburst_df
    #     if type(values_kategorije) == str:
    #         values_kategorije = [values_kategorije] 
    #     if not len(values_kategorije) == 0:
    #         current_selection_df = current_selection_df[current_selection_df['Kategorija'].isin(values_kategorije)]
    #     if len(all_selected_otoki):
    #         otoki = np.unique(current_selection_df['Otok'].values)
    #         otoki_options = [{'label': i, 'value': i} for i in otoki]
    #         otoki_values = list(otoki)  
    #         return no_update, no_update, otoki_options, otoki_values, no_update
    #     else:
    #         return no_update, no_update, no_update, [], no_update
                
    raise dash.exceptions.PreventUpdate  
 

#%% image layout store callback

# @app.callback(
#     Output('image_layout_store', 'data'),
#     State('image_layout_store','modified_timestamp'),
#     Input('image_layout_store','data'),
#     State('spaghetti_graph','figure'),
#     # Input('upload_data', 'contents'),
#     # Input('upload_datatable_sunburst_data', 'last_modified'),
#     # prevent_initial_call=False
# )
# def image_layout_callback(
#                       image_layout_store_timestamp,
#                       image_layout_store,
#                       spaghetti_fig_dict,
#                       # upload_data
#                       ):
#     # ctx = dash.callback_context
#     # ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
#     # breakpoint()
#     if image_layout_store == None:
#         return spaghetti_fig_dict['layout']['images'][0]
#     else:
#         raise dash.exceptions.PreventUpdate
#%% Radio View-mode
# @app.callback(
#     Output('radio_viewmode', 'value'),
#     Input('sunburst_poti','clickData'),
#     Input('spaghetti_graph', 'restyleData'),
#     Input('spaghetti_graph','relayoutData'),
#     # Input('upload_datatable_sunburst_data', 'last_modified'),
#     # prevent_initial_call=False
# )
# def radio_viewmode(
#                       sunburst_poti_clickData,
#                       spaghetti_graph_restyleData,
#                       spaghetti_graph_relayoutData
#                       ):
#     ctx = dash.callback_context
#     ctx_triggered_info = ctx.triggered[0]['prop_id'].split('.')[0]
#     # breakpoint()
#     if ctx_triggered_info == 'sunburst_poti':
#         return 'View Mode'
#     elif ctx_triggered_info == 'spaghetti_graph':
#         return 'Draw Mode'
#     else:
#         return no_update
    
# %% suggested_input_fields

@app.callback(
    Output('dropdown_name', 'options'),
    Output('dropdown_groupname', 'options'),
    Output('dropdown_kategorija', 'options'), 
    Input('datatable_sunburst', 'data'),
    # Input('datatable_sunburst', 'modified_timestamp'),
    # prevent_initial_call=False
)
def suggested_input_fields(
                      datatable_sunburst_data,
                      # datatable_sunburst_timestamp,
                      # spaghetti_graph_relayoutData
                      ):
    # breakpoint()
    if datatable_sunburst_data == None:
        raise dash.exceptions.PreventUpdate 
    sunburst_df = pd.DataFrame(datatable_sunburst_data)
    kategorije = np.unique(sunburst_df['Kategorija'].values)
    otoki = np.unique(sunburst_df['Otok'].values)
    atributi = np.unique(sunburst_df['Atribut poti'].values)
    checklist_kategorije_options = [{'label': i, 'value': i} for i in kategorije]
    checklist_otoki_options = [{'label': i, 'value': i} for i in otoki]
    checklist_atributi_options = [{'label': i, 'value': i} for i in atributi]
    return checklist_atributi_options, checklist_otoki_options, checklist_kategorije_options
      
# %% App start

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False)
    # app.run_server(debug=False, host='0.0.0.0', port = 8081)
