#connecting colab with drive
from google.colab import drive
drive.mount('/content/drive')

# Data importing
import pandas as pd
listing = pd.read_csv('/content/drive/MyDrive/PORTFOLIO/Airbnb Analysis/DQLab_listings(22Sep2022) (1).csv', sep = ',')
nbhood = pd.read_csv('/content/drive/MyDrive/PORTFOLIO/Airbnb Analysis/DQLab_nieghbourhood(22Sep2022).csv', sep = ',')
rvw = pd.read_csv('/content/drive/MyDrive/PORTFOLIO/Airbnb Analysis/DQLab_reviews(22Sep2022).csv', sep = ',')

#Data Overview & Cleansing

#Airbnb Listing Dataset

#listing info
print(listing.info())
print('\n Banyak missing data pada dataset :', listing.isna().sum().sum())
print('\n Banyak duplicated data pada dataset :', listing.duplicated().sum().sum())

listing.describe()

display(listing.head())

import plotly.express as px
fig_dist1 = px.box(data_frame=listing, x = 'availability_365', width = 500, height=200)
display(fig_dist1)
fig_dist2 = px.box(data_frame=listing, x = 'minimum_nights', width = 500, height=200)
display(fig_dist2)
fig_dist3 = px.box(data_frame=listing, x = 'price', width = 500, height=200)
display(fig_dist3)

listing = listing[listing['minimum_nights']<=365].reset_index()
fig_dist2 = px.box(data_frame=listing, x = 'minimum_nights', width = 500, height=200)
display(fig_dist2)

listing = listing[listing['price']>0].reset_index()
fig_dist3 = px.box(data_frame=listing, x = 'price', width = 500, height=200)
display(fig_dist3)

fig_map = px.scatter_mapbox(listing, lat="latitude", lon="longitude", hover_name='id',zoom=9, height=300, width=400)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig_map.show()

listing = listing[listing['latitude']<1.45328] #hapus tempat yang memiliki latitude lebih dari 1.45328(di sebelah utara Singapura)
#hapus tempat yang berada lebih dari barat laut Singapura
outer_place_index = listing[ (listing['latitude'] > 1.405) & (listing['longitude'] < 103.664) ].index 
listing.drop(outer_place_index , inplace=True)
#hapus tempat yang masih berada di luar Singapura 
outer_id_index = listing[listing['id'].isin([708999801528964619,39732595,39757287,28268681,29171020,27248990,27532454,540170321699689740])].index
listing.drop(outer_id_index , inplace=True)

#Map plot after cleaning
fig_map2 = px.scatter_mapbox(listing, lat="latitude", lon="longitude", hover_name='name',zoom=9, height=300, width=500)
fig_map2.update_layout(mapbox_style="open-street-map")
fig_map2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig_map2.show()


#Neighborhood Dataset info
rvw.info()
print('\n Banyak missing data pada dataset :', rvw.isna().sum().sum())
print('\n Banyak duplicated data pada dataset :', rvw.duplicated().sum().sum())

display(rvw.head())

rvw = rvw[rvw['listing_id'].isin(listing['id']) == True]
print(f'Kini dataset Listing memiliki {rvw.shape[1]} kolom data, dan {rvw.shape[0]} baris data ')

display(rvw.head())

rvw = rvw.sort_values('date')
display(rvw.head())
display(rvw.tail())

#Neighborhood Dataset info
nbhood.info()
print('\n Banyak missing data pada dataset :', nbhood.isna().sum().sum())
print('\n Banyak duplicated data pada dataset :', nbhood.duplicated().sum().sum())

display(nbhood.head())

!pip install pandasql

import pandasql as ps
listing_nbgroup = ps.sqldf("""
                   select b.id, b.name, a.neighbourhood_group,b.room_type, b.neighbourhood,b.longitude, b.latitude, b.minimum_nights, b.price, (365-b.availability_365) rented_365
                   from nbhood a join listing b on a.neighbourhood=b.neighbourhood 
                """)
display(listing_nbgroup)

import pandasql as ps

listing_reviews = ps.sqldf("""
                   select a.date, strftime('%Y-%m', a.date) month, strftime('%Y', a.date) year, b.id,b.name, b.room_type, b.neighbourhood, 
                   c.neighbourhood_group, b.price, b.minimum_nights, (365-b.availability_365) rented_365
                   from rvw a left join listing b on a.listing_id=b.id join nbhood c on b.neighbourhood = c.neighbourhood
                """)
listing_reviews

room_type_pie = px.pie(listing, values=listing['room_type'].value_counts().values, color=listing['room_type'].value_counts().index, names=listing['room_type'].value_counts().index, color_discrete_sequence=["#97DECE","#7F167F","#FF597B","#ADE792"], hole=0.5)
room_type_pie.update_traces(textposition="outside", textfont=dict(color="black",size=13), textinfo="label+percent",pull=[0.1,0,0,0,0],rotation = -115)
room_type_pie.update_layout(title="<b>Listing distribution by Room_type</b>", title_font=dict(size=16))
room_type_pie.show()

top_nbhood = listing_nbgroup.groupby(['neighbourhood_group', 'neighbourhood']).agg(count=('neighbourhood','count')).sort_values(by=['count'],ascending=False).reset_index().head(10)
display(top_nbhood)

top_nbhood_plot = px.bar(top_nbhood.sort_values('count'), x = 'count', y = 'neighbourhood', color = 'neighbourhood_group', orientation = 'h', width = 750, color_discrete_sequence=['#ffcaaf','#cc97c1'] )
top_nbhood_plot.update_layout(title="<b>Top 10 Neighbourhood with the most rooms</b>", title_font=dict(size=16))
top_nbhood_plot

listing.groupby(['host_id', 'host_name']).agg(count=('neighbourhood','count')).sort_values(by=['count'],ascending=False).reset_index().head(5)

nbg_pie = px.pie(listing_nbgroup, values=listing_nbgroup['neighbourhood_group'].value_counts().values, color=listing_nbgroup['neighbourhood_group'].value_counts().index, names=listing_nbgroup['neighbourhood_group'].value_counts().index, color_discrete_sequence=["#97DECE","#7F167F","#FF597B","#C58940","#ADE792"], hole=0.5, width = 750)
nbg_pie.update_traces(textposition="outside", textfont=dict(color="black",size=13), textinfo="label+percent",pull=[0.1,0,0,0,0],rotation = -115)
nbg_pie.update_layout(title="<b>Listing distribution by Neighbourhood Group</b>", title_font=dict(size=16))
nbg_pie.show()

import plotly.express as px

listing_map = px.scatter_mapbox(listing_nbgroup, lat="latitude", lon="longitude", color="neighbourhood_group", hover_name="neighbourhood_group", zoom=9, width=750, color_discrete_sequence=["#2B3A55","#CE7777","#810CA8","#9C254D","#C060A1"])
listing_map.update_layout(mapbox_style="open-street-map")
listing_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
listing_map.show()

price_mean = listing['price'].mean()
price_max = listing['price'].max()
price_min = listing['price'].min()
print(f'Rata rata harga penginapan di Singapura adalah {price_mean:.2f}')
print(f'dengan harga terendah sebesar {price_min:.2f}')
print(f'dan harga tertinggi sebesar {price_max:.2f}')


import plotly.express as px
price_dist = px.box(listing, x='price')
price_dist.show()

import plotly.express as px

price_map = px.scatter_mapbox(listing_nbgroup, lat="latitude", lon="longitude", color="price", hover_name="neighbourhood_group", zoom=9, width=750)
price_map.update_layout(mapbox_style="open-street-map")
price_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
price_map.show()

listing_nbgroup.groupby('neighbourhood_group').agg(price_mean=('price','mean')).sort_values(by=['price_mean'],ascending=False).reset_index()

price_by_nbg_dist = px.box(listing_nbgroup, x='price', y='neighbourhood_group', color='neighbourhood_group' )
price_by_nbg_dist.show()

listing_nbgroup[listing_nbgroup['price']==listing_nbgroup['price'].max()]

price_by_roomtype = listing_nbgroup.groupby('room_type').agg(price_mean=('price','mean')).sort_values(by=['price_mean'],ascending=False).reset_index()
price_by_roomtype

price_by_roomtype_plot = px.histogram(price_by_roomtype, x = 'room_type', y = 'price_mean', color = 'room_type', width = 750)
price_by_roomtype_plot.update_layout(title="<b>Price mean of each Room Type</b>", title_font=dict(size=16), yaxis_title = 'price_mean')
price_by_roomtype_plot

rented_mean = listing_nbgroup['rented_365'].mean()
print(f'Rata rata penginapan di Singapura tersewa selama {rented_mean:.2f} hari tiap tahunnya')

import plotly.express as px
rented_365_dist = px.box(listing_nbgroup, x='rented_365')
rented_365_dist.show()

import plotly.express as px

rented_365_map = px.scatter_mapbox(listing_nbgroup, lat="latitude", lon="longitude", color="rented_365", hover_name='neighbourhood_group',zoom=9, width=750)
rented_365_map.update_layout(mapbox_style="open-street-map")
rented_365_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
rented_365_map.show()

listing_nbgroup.groupby('neighbourhood_group').agg(mean_days_rented=('rented_365','mean')).sort_values(by=['mean_days_rented'],ascending=False).reset_index()

listing_nbgroup_top_rented_365 = listing_nbgroup.groupby(['neighbourhood','neighbourhood_group'])['rented_365'].mean().reset_index().sort_values('rented_365', ascending = False).head(10)
display(listing_nbgroup_top_rented_365)

display(listing_nbgroup[['rented_365','minimum_nights','price']].corr())
import seaborn as sns
listing_corr1 = sns.heatmap(listing_nbgroup[['rented_365','minimum_nights','price']].corr(), vmax=1, vmin=-1).set_title('Correlation between room_type and price', fontdict={'fontsize': 15, 'horizontalalignment': 'right'})
listing_corr1

rented_365_vs_minimum_nights = px.scatter(data_frame=listing_nbgroup,x='rented_365', y='minimum_nights', color="room_type", trendline="ols", trendline_scope="overall", trendline_color_override="black", template="simple_white", width=750)
rented_365_vs_minimum_nights.update_layout(title="<b>Rented_365 vs Minimum Night</b>",title_font=dict(size=18, color="black"))
rented_365_vs_minimum_nights

rented_365_vs_price = px.scatter(data_frame=listing_nbgroup,x='rented_365', y='price', color="room_type", trendline="ols", trendline_scope="overall", trendline_color_override="black", template="simple_white", width=750)
rented_365_vs_price.update_layout(title="<b>Rented_365 vs Price</b>",title_font=dict(size=18, color="black"))
rented_365_vs_price

listing_reviews_per_date = listing_reviews.groupby('date').agg(count=('date','count')).sort_values(by=['date']).reset_index()
listing_reviews_per_month = listing_reviews.groupby('month').agg(count=('month','count')).sort_values(by=['month']).reset_index()
listing_reviews_per_years = listing_reviews.groupby('year').agg(count=('year','count')).sort_values(by=['year']).reset_index()

rvw_by_date = px.line(listing_reviews_per_date, x='date', y='count',title='Review Trend per Day')
rvw_by_date

rvw_by_month = px.line(listing_reviews_per_month, x='month', y='count',title='Review Trend by Year', markers = True)
rvw_by_month

rvw_by_year = px.line(listing_reviews_per_years, x='year', y='count',title='Review Trend by Year', markers=True, width = 750)
rvw_by_year

listing_reviews_by_neighbourhood_group2 = listing_reviews.groupby('neighbourhood_group').agg(count=('neighbourhood_group','count')).sort_values(by=['count'], ascending=False).reset_index()
display(listing_reviews_by_neighbourhood_group2)

fig_rvw_nbg = px.bar(listing_reviews_by_neighbourhood_group2, x='neighbourhood_group',y='count', color = 'neighbourhood_group', title='Reviews Trend by Neighbourhood Group')
fig_rvw_nbg.add_hline(y=listing_reviews_by_neighbourhood_group2['count'].mean())

listing_reviews_by_room_type2 = listing_reviews.groupby('room_type').agg(count=('room_type','count')).sort_values(by=['count'], ascending=False).reset_index()
display(listing_reviews_by_room_type2)

rvw_roomtype = px.bar(listing_reviews_by_room_type2, x='room_type',y='count', color = 'room_type', title='Reviews Trend by Room Type')
rvw_roomtype.add_hline(y=listing_reviews_by_room_type2['count'].mean())

rvw_by_room_type_tab = listing_reviews.groupby(['year','room_type']).agg(count=('year','count')).sort_values(by=['year']).reset_index()
rvw_by_room_type = px.line(rvw_by_room_type_tab, x='year', y='count', color = 'room_type' ,title='<b>Review Trend by Year', markers=True, width = 750)
rvw_by_room_type

rvw_by_neighbourhood = listing_reviews.groupby(['neighbourhood_group','neighbourhood']).agg(count=('neighbourhood','count')).sort_values(by=['count'], ascending=False).reset_index().head(10)
display(rvw_by_neighbourhood)

rvw_by_neighbourhood_plot = px.bar(rvw_by_neighbourhood.sort_values('count', ascending = True), x = 'count', y = 'neighbourhood', color = 'neighbourhood_group', orientation = 'h', width = 750, color_discrete_sequence=['#ffcaaf','#cc97c1'] )
rvw_by_neighbourhood_plot.update_layout(title="<b>Top 10 Neighbourhood with the most reviews</b>", title_font=dict(size=16))
rvw_by_neighbourhood_plot

Berikut merupakan tabel dari 10 daftar kamar di Airbnb Singapura yang memiliki review paling banyak.

listing_by_room = listing_reviews.groupby(['id','minimum_nights','name','neighbourhood','neighbourhood_group','price','rented_365','room_type']).agg(review_num=('date','count')).sort_values(by=['review_num'], ascending=False).reset_index()

import plotly.graph_objects as go
import numpy as np

listing_corr2 = go.Figure()
listing_corr2.add_trace(
    go.Heatmap(
        x = listing_by_room[['price','minimum_nights','rented_365','review_num']].corr().columns,
        y = listing_by_room[['price','minimum_nights','rented_365','review_num']].corr().index,
        z = np.array(listing_by_room[['price','minimum_nights','rented_365','review_num']].corr()),
        text=listing_by_room[['price','minimum_nights','rented_365','review_num']].corr().values,
        texttemplate='%{text:.4f}',
        colorscale=px.colors.sequential.Sunset
    )
)
listing_corr2.update_layout(width = 750)
listing_corr2.show()

review_num_vs_price = px.scatter(data_frame=listing_by_room,x='review_num', y='price', color = 'room_type', trendline="ols", trendline_scope="overall", trendline_color_override="black", template="simple_white", width=750)
review_num_vs_price.update_layout(title="<b>Review_num vs Price</b>",title_font=dict(size=18, color="black"))
review_num_vs_price

!pip install jupyter-dash

from jupyter_dash import JupyterDash 
from dash import html 
from dash import dcc

from dash import Input
from dash import Output


app = JupyterDash(__name__)

# Design Layout
app.layout = html.Div([
    html.Div(html.H1("Singapore Airbnb Analysis",style={'textAlign':'center', 'font-family':'Calibri','font-size':40,'color':'#1A0000'}))
    ,html.Img(src = 'https://www.johnlkong.com/wp-content/uploads/2018/01/hilton_hotel_header-720x245.jpg',style={'height': '40%','width': '100%','textAlign' : 'center'})
    ,html.P("author: Lutfia Husna Khoirunnisa (https://www.linkedin.com/in/lutfiahusnakhoirunnisa)",style={'textAlign':'center', 'font-family':'Calibri','font-style': 'italic','font-size':20,'color':'#1A0000','font-weight':'lighter'})
    ,html.Br()
    ,html.Div(
        children = [html.H3('Bisnis Penginapan di Airbnb', style = {'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,html.Div(dcc.Markdown('''
            Pada satu tahun terakhir ini, kasus covid-19 di dunia sudah cukup menurun. 
            Banyak aktivitas yang sebelumnya tidak dapat dilakukan karena adanya pandemi covid-19 kini telah mulai berjalan kembali, salah satu aktivitas 
            yang kini sudah mulai banyak dilakukan adalah traveling. Dengan mulai bergeraknya kembali industri pariwisata, para pebisnis mulai kembali melirik 
            sektor tersebut untuk mengambil peluang sebesar-besarnya. Salah satu bisnis yang sedang naik saat ini adalah bisnis penginapan.

            Dengan kemajuan teknologi, kini pebisnis dipermudah dalam memasarkan penginapan dengan adanya suatu online market platform yaitu Airbnb. 
            Dengan adanya Airbnb ini tentu sangat membantu pemilik penginapan untuk berhubungan dengan customernya, dan membantu dalam memasarkan penginapannya.
            Dengan mulai naiknya bisnis penginapan, tentu persaingan akan semakin ketat dan pebisnis perlu untuk melakukan riset terlebih dahulu sebelum melakukan investasi 
            agar dapat menetapkan strategi yang tepat untuk memperoleh keuntungan yang maksimal dan dapat bersaing dengan kompetitornya. Riset ini dapat dilakukan 
            dengan melihat bagaimana aktivitas bisnis pada beberapa tahun terakhir, untuk melihat bagaimana gambaran, dan mengetahui trendnya.

            Pada artikel ini akan diberikan gambaran bagaimana aktivitas bisnis penginapan di Airbnb Singapura selama 5 tahun terakhir. 
        '''),style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'})
        ]
    )
    ,html.Div(children = [
        html.H3('Bagaimana Aktivitas Penyewaan penginapan di Airbnb Singapura?', style = {'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':23,'color':'#1A0000','font-weight':'light'})
        ,html.P('Aktivitas penyewaan penginapan di Airbnb Singapura jika dilihat dari aktivitas review di Airbnb', style = {'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':20,'color':'#1A0000','font-weight':'light'})
        ,html.P('''
            Tentu kita memiliki keterbatasan untuk mendapatkan data aktivitas penyewaan pada tiap penginapan di Airbnb, karena tentu data tersebut bersifat rahasia
            milik tiap-tiap penyedia penginapan. Tetapi kita dapat melihat bagaimana gambaran umum dari aktivitas penyewaan dengan melihat aktivitas review yang
            dilakukan oleh customer melalui platform Airbnb. Dengan melihat bagaimana gambaran dari aktivitas review penginapan di Airbnb, kita dapat melihat 
            bagaimana trend penyewaan dari tiap penginapan pada tiap waktunya.
        ''', style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'})
        ,dcc.Tabs([
            dcc.Tab(
                label = 'Per Hari', children = [
                    dcc.Graph(id = 'rvw_by_date', figure = rvw_by_date,config={"displayModeBar": False})
                ]
            ),
            dcc.Tab(
                label = 'Per Bulan', children = [
                    dcc.Graph(id = 'rvw_by_month',figure = rvw_by_month, config = {"displayModeBar": False})
                ]
            ),
            dcc.Tab(
                label = 'Per Tahun', children = [
                    html.Div(dcc.Graph(id = 'rvw_by_year',figure = rvw_by_year,config = {"displayModeBar": False})
                    , style = {'width' : '60%', 'margin-left':300})
                ]
            )
        ])
        ,html.Div(dcc.Markdown('''
            Dapat dilihat bahwa banyak review penginapan tiap tahunnya, banyak review melonjak dari 2018 menuju 2019, kemudian turun drastis pada tahun 2020. 
            Hal ini sejalan dengan grafik 'Development of the tourism sector in Singapore from 1995 to 2020' yang dipublikasikan oleh www.worlddata.info, dimana 
            banyak turis yang masuk pada tahun 2019 mengalami kenaikan jika dibandingkan dengan tahun 2018, dan terjadi penurunan drastis pada tahun 2020. 
            Dengan banyak turis yang masuk ini tentu sangat berpengaruh dengan aktivitas review penginapan pada Airbnb di Singapura.
        ''', style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'}))
        ,html.Img(src = 'https://cdn.worlddata.info/graphs/tourism/arrivals-singapur-930.png', style = {'width':'80%','display':'inline-block', 'margin-left':100})
        ,html.Div(dcc.Markdown('img source: https://cdn.worlddata.info/graphs/tourism/arrivals-singapur-930.png'), style = {'textAlign':'center', 'font-family':'Calibri','font-style': 'italic','font-size':20,'color':'#1A0000','font-weight':'light'})
        ,html.Div(dcc.Markdown('''
            Penurunan aktivitas review kamar berlanjut pada tahun 2021, dimana pada tahun 2021 aktivitas review kamar Airbnb di 
            Singapura merupakan yang paling rendah selama 5 tahun terakhir. Tetapi terjadi kenaikan aktivitas review kamar Airbnb di Singapura pada tahun 2022.
            Penurunan dan kenaikan ini mungkin disebabkan oleh adanya pandemi covid-19 yang dimulai pada tahun 2020 dan berlangsung hingga awal tahun 2022
             yang menyebabkan terbatasnya aktivitas pariwisata di Singapura. Tentu hai ini berakibat pada aktivitas review penginapan Airbnb yang ada di Singapura. Dan pandemi covid-19 ini 
            kasus covid-19 berangsur menurun, sehingga aktivitas review kamar Airbnb kembali naik. 

            Jika dilihat dari banyak review penginapan per bulannya, pada bulan Desember hingga Januari tiap tahunnya pada 5 tahun terakhir cenderung lebih tinggi aktivitas reviewnya dibandingkan
            dengan bulan-bulan lain. Hal ini tentu menarik, karena trend ini cenderung berulang pada 5 tahun terakhir. 
        '''),style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'})
        ])
    ,html.Div([
        html.H3('Bagaimana Penyebaran Penginapan di Singapura?', style = {'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,html.Div(
            children = dcc.Graph(
                id = 'fig_map2', figure = listing_map, config={"displayModeBar": False}),
             style={'width': '60%', 'margin-left':'3%', 'display': 'inline-block'}
        )
        ,html.Div(children = dcc.Markdown('''
            Penginapan yang disediakan di Airbnb Singapura menyebar di seluruh wilayah Singapura, tetapi penginapan paling banyak berada pada Central Region. 
            Central Region sendiri merupakan pusat bisnis dan hiburan di Singapura, sehingga pembangunan penginapan di sini sangat menjanjikan
            untuk dijadikan tempat untuk berbisnis penyewaan penginapan di Singapura. Tetapi  tentu dengan banyaknya penginapan di Central Region, 
            tentu persaingan dengan kompetitor akan semakin ketat, maka perlu untuk merancang strategi yang baik untuk lebih unggul dari kompetitor. 
            
            Strategi yang baik sangat diperlukan untuk unggul dalam persaingan, contohnya seperti mengembangkan konsep penginapan yang unik 
            untuk menarik pengunjung, memperkuat marketing, dan fokus pada kualitas layanan serta kualitas kamar yang disewakan. Letak penginapan 
            yang strategis juga perlu dipertimbangkan, karena letak penginapan merupakan salah satu faktor
            yang paling berpengaruh pada aktivitas penyewaan.                  
            '''),
                style={'vertical-align':'top', 'margin-left':10, 'width': '35%', 'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000','font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'}
            )
    ])
    ,html.Div([
        html.H3('Gambaran Umum pada Neighbourhood di Singapura', style = {'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,html.Div( dcc.Graph( 
                id = 'top5_nbhood_plot', figure = top_nbhood_plot, config={"displayModeBar": False}),
                style={'width': '47%', 'display': 'inline-block', 'margin-left':30})
                ,html.Div(dcc.Graph( 
                id = 'rvw_by_neighbourhood_plot', figure = rvw_by_neighbourhood_plot, config={"displayModeBar": False}),
                style={'width': '50%', 'display': 'inline-block'})
    ])
    ,html.Div(children = dcc.Markdown('''
            Diketahui neighbourhood yang menyediakan penginapan terbanyak di Airbnb Singapura adalah 
            Kallang yang berada di Central Region. Karena memiliki banyak penginapan, Kallang juga mendapatkan akumulasi review penginapan paling banyak di Airbnb Singapura.
            Kallang memiliki banyak daya tarik bagi wisatawan, seperti Sungai Kallang, dan tempat iconic lain seperti new National Stadium, 
            Kallang Wave Mall, dan Kallang menyediakan banyak fasilitas untuk melakukan aktivitas olahraga sehingga Kallang menjadi tempat yang memiliki daya tarik turis
            dan menjanjikan untuk dijadikan tempat berbisnis penyewaan penginapan melalui Airbnb.
            '''),
            style={'vertical-align':'top', 'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word','padding':7, 'margin-left':30, 'margin-right':30}
            ) 
    ,html.Div([
        html.H3("Bagaimana Gambaran Umum Mengenai Room Type di Airbnb Singapura?",style={'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,dcc.Tabs([
            dcc.Tab(
                label = 'Room type distribution', children = [
                    dcc.Graph(id = 'room_type_pie', figure = room_type_pie,config={"displayModeBar": False})
                ]
            ),
            dcc.Tab(
                label = 'Number of Reviews for Each Room Type', children = [
                    dcc.Graph(id = 'rvw_by_room_type',figure = rvw_by_room_type, config = {"displayModeBar": False})
                ]
            ),
            dcc.Tab(
                label = 'Price mean for Each Room Type', children = [
                    html.Div(dcc.Graph(id = 'price_by_roomtype_plot',figure = price_by_roomtype_plot,config = {"displayModeBar": False})
                    , style = {'width' : '60%', 'margin-left':300})
                ]
            )
        ])
        ,html.Div(children = dcc.Markdown('''
              Jenis kamar yang paling banyak di Airbnb Singapura adalah Private room dengan banyak kamar sebesar 47.4% dari total kamar.
              Hal ini sesuai dengan aktivitas review Airbnb Singapura yang pada 5 tahun terakhir, dimana diketahui bahwa kamar dengan tipe Private room 
              selalu mendapatkan banyak review tertinggi di antara tipe kamar lainnya. 
              Dengan rata-rata harga 168 SGD, per malam yaitu nomor 2 terendah dibandingkan dengan tipe kamar lainnya, tipe kamar private room ini disewa 
              banyak customer di Singapura, dilihat dari banyak review yang ada pada Airbnb.
              '''),
                style={'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'}
            )
    ])
    ,html.H3("Singaporean Airbnb Price Distribution and Rental Trend",style={'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
    ,dcc.Tabs([
        dcc.Tab(
            label = 'Price Mapping', children = [
                html.Div(dcc.Graph(
                    id = 'price_map', figure = price_map, config={"displayModeBar": False}
                ), style = {'width' : '60%', 'margin-left':300})
            ]
        ),
        dcc.Tab(
            label = 'Length of a Room is Rented in a Year Mapping', children = [
                html.Div(dcc.Graph(
                    id = 'rented_365_map', figure = rented_365_map, config={"displayModeBar": False}
                ), style = {'width' : '60%', 'margin-left':300})
            ]
        )
    ])
    ,html.Div(children = dcc.Markdown('''
        Dari mapping plot harga tersebut, diketahui bahwa mayoritas dari penyewa penginapan di Airbnb memberikan harga dibawah 2000. 
        Distribusi harga ini menyebar, dan tidak bergantung pada dimana letak dari penginapan tersebut. Sehingga dapat dikatakan bahwa 
        posisi penginapan tidak berkorelasi dengan harga yang diberikan oleh penyewa. Pemberian harga ini kemungkinan lebih bergantung pada
        fasilitas apa saja yang disediakan oleh penginapan dan juga bergantung pada kelas dari penginapan.
            
        Begitu juga pada lama suatu kamar penginapan tersewa dalam satu tahun, pada mapping plot tersebut diketahui bahwa distribusinya menyebar dan tidak bergantung pada 
        letak penginapan. Dapat dilihat bahwa di daerah North-east Region memiliki sedikit penginapan yang disewakan, tetapi mayoritas memiliki lama penginapan tersewa 
        yang cenderung tinggi. Pada Central Region, terlihat sangat banyak penginapan yang disewakan tetapi memiliki lama penginapan tersewa dalam satu tahun yang 
        mayoritas relatif rendah. Hal ini mungkin terjadi karena banyaknya pilihan penginapan yang tersedia di kawasan Central Region, menjadikan turis lebih sering 
        berpindah pindah penginapan sehingga menyebabkan lama penginapan tersewa dalam satu tahun cenderung rendah.
        '''), 
        style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'})
    ,html.Div([
        html.H3('Apa yang Memiliki Pengaruh Pada Banyak Review?',style={'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,html.Div(dcc.Graph(id = 'listing_corr2', figure = listing_corr2), style = {'width':'60%', 'margin-left':300})
        ,html.Div(dcc.Markdown('''
            Terlihat dari nilai koefisien korelasi yang mendekati 0, antara minimal lama menyewa, harga, lama suatu kamar tersewa dalam satu tahun, 
            dan banyak review tidak ada yang memiliki korelasi kuat. Keempat variable tersebut berkorelasi sangat lemah terhadap satu sama lain. 
            Tetapi diantara korelasi variable-variable tersebut, korelasi antara minimal lama menyewa suatu kamar, dan harga memiliki korelasi yang 
            paling tinggi dengan nilai koefisien korelasi sebesar 0.263.

            Jika dilihat dari koefisien korelasi, variable yang paling memiliki pengaruh pada banyak review adalah price. 
            Berikut merupakan visualisasi dari data banyak review dari suatu kamar dengan harganya:
        '''), style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'})
        ,html.Div(
            dcc.Graph(id = 'review_num_vs_price', figure = review_num_vs_price), style = {'width':'60%', 'margin-left':300}
        )
        ,html.Div(
            dcc.Markdown('''
            Terihat bahwa antara banyak review dan harga memiliki korelasi negatif, artinya semakin banyak review yang diperoleh 
            semakin rendah harga penyewaan per malamnya. Tetapi karena koefisien korelasi sangat kecil dan mendekati 0,
            kita tetap tidak dapat memutuskan jika harga memiliki pengaruh terhadap banyak review.
            '''), style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'}
        )
    ])
    ,html.Div([
        html.H3('Business Recomendation',style={'margin':0,'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,html.Div(
            dcc.Markdown('''
            Diketahui bahwa  harga, minimal lama sewa, lama suatu kamar tersewa dalam satu tahun, dan banyaknya review yang diperoleh dalam 5 tahun terakhir 
            memiliki hubungan korelasi yang sangat rendah sehingga tidak dapat menyimpulkan bahwa variabel variable tersebut berhubungan. Sehingga, pebisnis 
            lebih baik melakukan riset lanjutan dengan melihat fasilitas atau keunikan apa yang belum disediakan oleh kompetitor sehingga dapat lebih unggul 
            dan menambah daya tarik pelanggan.
            
            Untuk menentukan harga yang tepat untuk ditawarkan, pebisnis dapat melakukan pemodelan prediksi harga secara statistik, contohnya dengan model 
            logistic regression, atau model regresi lain. Untuk mendapatkan prediksi yang lebih baik dan akurat, pebisnis dapat mengumpulkan kembali lebih 
            banyak data, atau menambah variabel - variabel yang mungkin memiliki hubungan dengan harga, seperti fasilitas yang disediakan, berapa kamar yang 
            ditawarkan, dan variable lain yang kiranya memiliki pengaruh terhadap harga.

            '''), style = {'textAlign':'Left', 'margin-left':30, 'margin-right':30,'display': 'inline-block', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'}
        )
    ,html.Div([
        html.H3('References',style={'margin':0,'textAlign':'Left', 'margin-left':30, 'font-family':'Calibri','font-style': 'italic','font-size':25,'color':'#1A0000','font-weight':'light'})
        ,html.Div(
            dcc.Markdown('''
            * https://www.airbnb.com/
            * https://www.visitsingapore.com/see-do-singapore/
            * https://www.worlddata.info/asia/singapore/tourism.php
            '''), style = {'margin-top':0, 'margin-left':30, 'display': 'inline', 'font-family':'Calibri','font-style': 'italic','font-size':17,'color':'#1A0000',
                       'font-weight':'light','textAlign': 'justify','text-justify': 'inter-word'}
        )
      ])
    ])
])

# Run Application
if __name__ == '__main__':
  app.run_server(debug=False, host = "0.0.0.0", port = 8080)
