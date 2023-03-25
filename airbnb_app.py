#Data Importing and Cleansing
import pandas as pd
listing = pd.read_csv('DQLab_listings.csv', sep = ',')
nbhood = pd.read_csv('DQLab_nieghbourhood.csv', sep = ',')
rvw = pd.read_csv('DQLab_reviews.csv', sep = ',')

#Listing dataset cleansing
listing = listing[listing['minimum_nights']<=365].reset_index() #hapus penginapan yang minimum_nights>1 tahun
listing = listing[listing['price']>0].reset_index() #hapus penginapan yang harga = 0
listing = listing[listing['latitude']<1.45328] #hapus tempat yang memiliki latitude lebih dari 1.45328(di sebelah utara Singapura)
#hapus tempat yang berada lebih dari barat laut Singapura
outer_place_index = listing[ (listing['latitude'] > 1.405) & (listing['longitude'] < 103.664) ].index 
listing.drop(outer_place_index , inplace=True)
#hapus tempat yang masih berada di luar Singapura 
outer_id_index = listing[listing['id'].isin([708999801528964619,39732595,39757287,28268681,29171020,27248990,27532454,540170321699689740])].index
listing.drop(outer_id_index , inplace=True)

#Review Dataset Cleansing
rvw = rvw[rvw['listing_id'].isin(listing['id']) == True]
rvw = rvw.sort_values('date')

#Data Merging
import pandasql as ps
listing_nbgroup = ps.sqldf(""" select b.id, b.name, a.neighbourhood_group,b.room_type, b.neighbourhood,b.longitude, b.latitude, b.minimum_nights, b.price, (365-b.availability_365) rented_365 from nbhood a join listing b on a.neighbourhood=b.neighbourhood""")
listing_reviews = ps.sqldf(""" select a.date, strftime('%Y-%m', a.date) month, strftime('%Y', a.date) year, b.id,b.name, b.room_type, b.neighbourhood, c.neighbourhood_group, b.price, b.minimum_nights, (365-b.availability_365) rented_365 from rvw a left join listing b on a.listing_id=b.id join nbhood c on b.neighbourhood = c.neighbourhood""")

#Data Visualization
import plotly.express as px

#Review Trend
listing_reviews_per_date = listing_reviews.groupby('date').agg(count=('date','count')).sort_values(by=['date']).reset_index()
rvw_by_date = px.line(listing_reviews_per_date, x='date', y='count',title='Review Trend per Day', color_discrete_sequence=px.colors.qualitative.G10,)

listing_reviews_per_month = listing_reviews.groupby('month').agg(count=('month','count')).sort_values(by=['month']).reset_index()
rvw_by_month = px.line(listing_reviews_per_month, x='month', y='count',title='Review Trend by Month', markers = True, color_discrete_sequence=px.colors.qualitative.G10)

listing_reviews_per_years = listing_reviews.groupby('year').agg(count=('year','count')).sort_values(by=['year']).reset_index()
rvw_by_year = px.line(listing_reviews_per_years, x='year', y='count',title='Review Trend by Year', markers=True, width = 750, color_discrete_sequence=px.colors.qualitative.G10)

#Room mapping distribution

listing_map = px.scatter_mapbox(listing_nbgroup, lat="latitude", lon="longitude", color="neighbourhood_group", hover_name="neighbourhood_group", zoom=9, width=700, color_discrete_sequence=px.colors.qualitative.G10)
listing_map.update_layout(mapbox_style="open-street-map")
listing_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#Review by Neoighbourhood
rvw_by_neighbourhood = listing_reviews.groupby(['neighbourhood_group','neighbourhood']).agg(count=('neighbourhood','count')).sort_values(by=['count'], ascending=False).reset_index().head(10)
rvw_by_neighbourhood_plot = px.bar(rvw_by_neighbourhood, x = 'count', y = 'neighbourhood', color = 'neighbourhood_group', orientation = 'h',color_discrete_sequence=px.colors.qualitative.G10, width = 600)
rvw_by_neighbourhood_plot.update_layout(title="<b>Top 10 Neighbourhood with the most review</b>", title_font=dict(size=16))
rvw_by_neighbourhood_plot.update_layout(yaxis={'categoryorder':'total ascending'})

#Top 10 Neighbourhood with the most room
top_nbhood = listing_nbgroup.groupby(['neighbourhood_group', 'neighbourhood']).agg(count=('neighbourhood','count')).sort_values(by=['count'],ascending=False).reset_index().head(10)
top_nbhood_plot = px.bar(top_nbhood, x = 'count', y = 'neighbourhood', color = 'neighbourhood_group', orientation = 'h', color_discrete_sequence=px.colors.qualitative.G10, width = 600 )
top_nbhood_plot.update_layout(title="<b>Top 10 Neighbourhood with the most room</b>", title_font=dict(size=16))
top_nbhood_plot.update_layout(yaxis={'categoryorder':'total ascending'})

#Listing Dist by Room Type
room_type_pie = px.pie(listing, values=listing['room_type'].value_counts().values, color=listing['room_type'].value_counts().index, names=listing['room_type'].value_counts().index, color_discrete_sequence=px.colors.qualitative.G10, hole=0.5)
room_type_pie.update_traces(textposition="outside", textfont=dict(color="white",size=13), textinfo="label+percent",pull=[0.1,0,0,0,0],rotation = -115)
room_type_pie.update_layout(title="<b>Listing distribution by Room_type</b>", title_font=dict(size=16))

#Review by Room Type
rvw_by_room_type_tab = listing_reviews.groupby(['year','room_type']).agg(count=('year','count')).sort_values(by=['year']).reset_index()
rvw_by_room_type = px.line(rvw_by_room_type_tab, x='year', y='count', color = 'room_type' ,title='<b>Review Trend by Year', markers=True, color_discrete_sequence=px.colors.qualitative.G10, width = 750)

#Price mean of each Room Type
price_by_roomtype = listing_nbgroup.groupby('room_type').agg(price_mean=('price','mean')).sort_values(by=['price_mean'],ascending=False).reset_index()
price_by_roomtype_plot = px.histogram(price_by_roomtype, x = 'room_type', y = 'price_mean', color = 'room_type', color_discrete_sequence=px.colors.qualitative.G10, width = 750)
price_by_roomtype_plot.update_layout(title="<b>Price mean of each Room Type</b>", title_font=dict(size=16), yaxis_title = 'price_mean')

#Price Mapping
price_map = px.scatter_mapbox(listing_nbgroup, lat="latitude", lon="longitude", color="price", hover_name="neighbourhood_group", zoom=9, width=750, color_continuous_scale='Inferno')
price_map.update_layout(mapbox_style="open-street-map")
price_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#Length of a Room is Rented in a Year Mapping
rented_365_map = px.scatter_mapbox(listing_nbgroup, lat="latitude", lon="longitude", color="rented_365", hover_name='neighbourhood_group',zoom=9, width=750, color_continuous_scale='Inferno')
rented_365_map.update_layout(mapbox_style="open-street-map")
rented_365_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#Correlation Plot
import plotly.graph_objects as go
import numpy as np

listing_by_room = listing_reviews.groupby(['id','minimum_nights','name','neighbourhood','neighbourhood_group','price','rented_365','room_type']).agg(review_num=('date','count')).sort_values(by=['review_num'], ascending=False).reset_index()
listing_corr = go.Figure()
listing_corr.add_trace(
    go.Heatmap(
        x = listing_by_room[['price','minimum_nights','rented_365','review_num']].corr().columns,
        y = listing_by_room[['price','minimum_nights','rented_365','review_num']].corr().index,
        z = np.array(listing_by_room[['price','minimum_nights','rented_365','review_num']].corr()),
        text=listing_by_room[['price','minimum_nights','rented_365','review_num']].corr().values,
        texttemplate='%{text:.4f}',
        colorscale=px.colors.sequential.Inferno
    )
)
listing_corr.update_layout(width = 750)

#Review Num vs Price
review_num_vs_price = px.scatter(data_frame=listing_by_room,x='review_num', y='price', color = 'room_type', color_discrete_sequence=px.colors.qualitative.G10, width=750)
review_num_vs_price.update_layout(title="<b>Review_num vs Price</b>",title_font=dict(size=18, color="black"))

# Web building
import streamlit as st 
st.set_page_config(layout="wide")
st.title('Singapore Airbnb Analysis')

st.image('https://www.johnlkong.com/wp-content/uploads/2018/01/hilton_hotel_header-720x245.jpg', use_column_width=True)
st.caption('author: Lutfia Husna Khoirunnisa (https://www.linkedin.com/in/lutfiahusnakhoirunnisa)')
st.subheader('Bisnis Penginapan di Airbnb')
st.markdown('''<p style='text-align: justify; color: white;'>
         Pada satu tahun terakhir ini, kasus covid-19 di dunia sudah cukup menurun. Banyak aktivitas yang sebelumnya 
         tidak dapat dilakukan karena adanya pandemi covid-19 kini telah mulai berjalan kembali, salah satu aktivitas
         yang kini sudah mulai banyak dilakukan adalah traveling. Dengan mulai bergeraknya kembali industri 
         pariwisata, para pebisnis mulai kembali melirik sektor tersebut untuk mengambil peluang sebesar-besarnya. 
         Salah satu bisnis yang sedang naik saat ini adalah bisnis penginapan.</p>''', unsafe_allow_html=True)
st.markdown('''<p style='text-align: justify; color: white;'>
         Dengan kemajuan teknologi, kini pebisnis dipermudah dalam memasarkan penginapan dengan adanya suatu online 
         market platform yaitu Airbnb. Dengan adanya Airbnb ini tentu sangat membantu pemilik penginapan untuk 
         berhubungan dengan customernya, dan membantu dalam memasarkan penginapannya. Dengan mulai naiknya bisnis penginapan, tentu persaingan akan semakin ketat dan pebisnis perlu untuk melakukan riset terlebih dahulu sebelum melakukan investasi agar dapat menetapkan strategi yang tepat untuk memperoleh keuntungan yang maksimal dan dapat bersaing dengan kompetitornya. Riset ini dapat dilakukan dengan melihat bagaimana aktivitas bisnis pada beberapa tahun terakhir, untuk melihat bagaimana gambaran, dan mengetahui trendnya.
         Pada artikel ini akan diberikan gambaran bagaimana aktivitas bisnis penginapan di Airbnb Singapura selama 5
         tahun terakhir. </p>''', unsafe_allow_html=True)
st.subheader('Bagaimana Aktivitas Penyewaan penginapan di Airbnb Singapura?')
st.write('Aktivitas penyewaan penginapan di Airbnb Singapura jika dilihat dari aktivitas review di Airbnb')
st.markdown('''<p style='text-align: justify; color: white;'>
         Tentu kita memiliki keterbatasan untuk mendapatkan data aktivitas penyewaan pada tiap penginapan di Airbnb, karena tentu data tersebut bersifat rahasia
         milik tiap-tiap penyedia penginapan. Tetapi kita dapat melihat bagaimana gambaran umum dari aktivitas penyewaan dengan melihat aktivitas review yang
         dilakukan oleh customer melalui platform Airbnb. Dengan melihat bagaimana gambaran dari aktivitas review penginapan di Airbnb, kita dapat melihat 
         bagaimana trend penyewaan dari tiap penginapan pada tiap waktunya.</p>''', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(['Per Hari','Per Bulan','Per Tahun'])

with tab1:
   st.plotly_chart(rvw_by_date, use_container_width = True)

with tab2:
   st.plotly_chart(rvw_by_month, use_container_width = True)
   
with tab3:
   st.plotly_chart(rvw_by_year, use_container_width = True)
st.markdown('''<p style='text-align: justify; color: white;'>
         Dapat dilihat bahwa banyak review penginapan tiap tahunnya, banyak review melonjak dari 2018 menuju 2019, kemudian turun drastis pada tahun 2020. 
         Hal ini sejalan dengan grafik 'Development of the tourism sector in Singapore from 1995 to 2020' yang dipublikasikan oleh www.worlddata.info, dimana 
         banyak turis yang masuk pada tahun 2019 mengalami kenaikan jika dibandingkan dengan tahun 2018, dan terjadi penurunan drastis pada tahun 2020. 
         Dengan banyak turis yang masuk ini tentu sangat berpengaruh dengan aktivitas review penginapan pada Airbnb di Singapura.</p>''', unsafe_allow_html=True)   

st.image('https://cdn.worlddata.info/graphs/tourism/arrivals-singapur-930.png', use_column_width=True)

st.write('img source: https://cdn.worlddata.info/graphs/tourism/arrivals-singapur-930.png')

st.markdown('''<p style='text-align: justify; color: white;'>
         Penurunan aktivitas review kamar berlanjut pada tahun 2021, dimana pada tahun 2021 aktivitas review kamar Airbnb di 
         Singapura merupakan yang paling rendah selama 5 tahun terakhir. Tetapi terjadi kenaikan aktivitas review kamar Airbnb di Singapura pada tahun 2022.
         Penurunan dan kenaikan ini mungkin disebabkan oleh adanya pandemi covid-19 yang dimulai pada tahun 2020 dan berlangsung hingga awal tahun 2022
         yang menyebabkan terbatasnya aktivitas pariwisata di Singapura. Tentu hai ini berakibat pada aktivitas review penginapan Airbnb yang ada di Singapura. Dan pandemi covid-19 ini 
         kasus covid-19 berangsur menurun, sehingga aktivitas review kamar Airbnb kembali naik. 
         </p>''', unsafe_allow_html=True)
st.markdown('''<p style='text-align: justify; color: white;'>
         Jika dilihat dari banyak review penginapan per bulannya, pada bulan Desember hingga Januari tiap tahunnya pada 5 tahun terakhir cenderung lebih tinggi aktivitas reviewnya dibandingkan
         dengan bulan-bulan lain. Hal ini tentu menarik, karena trend ini cenderung berulang pada 5 tahun terakhir. 
         </p>''', unsafe_allow_html=True)

st.subheader('Bagaimana Penyebaran Penginapan di Singapura?')
col_1, col_2 = st.columns([2,1])
col_1.plotly_chart(listing_map)
col_2.markdown('''<p style='text-align: justify; color: white;'>
         Penginapan yang disediakan di Airbnb Singapura menyebar di seluruh wilayah Singapura, tetapi penginapan paling banyak berada pada Central Region. 
         Central Region sendiri merupakan pusat bisnis dan hiburan di Singapura, sehingga pembangunan penginapan di sini sangat menjanjikan
         untuk dijadikan tempat untuk berbisnis penyewaan penginapan di Singapura. Tetapi  tentu dengan banyaknya penginapan di Central Region, 
         tentu persaingan dengan kompetitor akan semakin ketat, maka perlu untuk merancang strategi yang baik untuk lebih unggul dari kompetitor. 
         </p>''', unsafe_allow_html=True) 
st.markdown('''<p style='text-align: justify; color: white;'> 
         Strategi yang baik sangat diperlukan untuk unggul dalam persaingan, contohnya seperti mengembangkan konsep penginapan yang unik 
         untuk menarik pengunjung, memperkuat marketing, dan fokus pada kualitas layanan serta kualitas kamar yang disewakan. Letak penginapan 
         yang strategis juga perlu dipertimbangkan, karena letak penginapan merupakan salah satu faktor
         yang paling berpengaruh pada aktivitas penyewaan.  
         </p>''', unsafe_allow_html=True) 
st.subheader('Gambaran Umum pada Neighbourhood di Singapura')
col1, col2 = st.columns([2,2])

col1.plotly_chart(top_nbhood_plot)

col2.plotly_chart(rvw_by_neighbourhood_plot)
   
st.markdown('''<p style='text-align: justify; color: white;'>
         Diketahui neighbourhood yang menyediakan penginapan terbanyak di Airbnb Singapura adalah 
         Kallang yang berada di Central Region. Karena memiliki banyak penginapan, Kallang juga mendapatkan akumulasi review penginapan paling banyak di Airbnb Singapura.
         Kallang memiliki banyak daya tarik bagi wisatawan, seperti Sungai Kallang, dan tempat iconic lain seperti new National Stadium, 
         Kallang Wave Mall, dan Kallang menyediakan banyak fasilitas untuk melakukan aktivitas olahraga sehingga Kallang menjadi tempat yang memiliki daya tarik turis
         dan menjanjikan untuk dijadikan tempat berbisnis penyewaan penginapan melalui Airbnb.
         </p>''', unsafe_allow_html=True)
st.subheader('Bagaimana Gambaran Umum Mengenai Room Type di Airbnb Singapura?')
tabb1, tabb2, tabb3= st.tabs(['Room type distribution','Number of Reviews for Each Room Type', 'Price mean for Each Room Type'])

with tabb1:
   st.plotly_chart(room_type_pie, use_container_width = True)

with tabb2:
   st.plotly_chart(rvw_by_room_type, use_container_width = True)
   
with tabb3:
   st.plotly_chart(price_by_roomtype_plot, use_container_width = True)
      
st.markdown('''<p style='text-align: justify; color: white;'>
         Jenis kamar yang paling banyak di Airbnb Singapura adalah Private room dengan banyak kamar sebesar 47.4% dari total kamar.
         Hal ini sesuai dengan aktivitas review Airbnb Singapura yang pada 5 tahun terakhir, dimana diketahui bahwa kamar dengan tipe Private room 
         selalu mendapatkan banyak review tertinggi di antara tipe kamar lainnya. 
         Dengan rata-rata harga 168 SGD, per malam yaitu nomor 2 terendah dibandingkan dengan tipe kamar lainnya, tipe kamar private room ini disewa 
         banyak customer di Singapura, dilihat dari banyak review yang ada pada Airbnb.
         </p>''', unsafe_allow_html=True)
st.subheader('Singaporean Airbnb Price Distribution and Rental Trend')
tabbb1, tabbb2= st.tabs(['Price Mapping','Length of a Room is Rented in a Year Mapping'])

with tabbb1:
   st.plotly_chart(price_map, use_container_width = True)

with tabbb2:
   st.plotly_chart(rented_365_map, use_container_width = True)
st.markdown('''<p style='text-align: justify; color: white;'>
         Dari mapping plot harga tersebut, diketahui bahwa mayoritas dari penyewa penginapan di Airbnb memberikan harga dibawah 2000. 
         Distribusi harga ini menyebar, dan tidak bergantung pada dimana letak dari penginapan tersebut. Sehingga dapat dikatakan bahwa 
         posisi penginapan tidak berkorelasi dengan harga yang diberikan oleh penyewa. Pemberian harga ini kemungkinan lebih bergantung pada
         fasilitas apa saja yang disediakan oleh penginapan dan juga bergantung pada kelas dari penginapan.
         </p>''', unsafe_allow_html=True)
st.markdown('''<p style='text-align: justify; color: white;'>            
         Begitu juga pada lama suatu kamar penginapan tersewa dalam satu tahun, pada mapping plot tersebut diketahui bahwa distribusinya menyebar dan tidak bergantung pada 
         letak penginapan. Dapat dilihat bahwa di daerah North-east Region memiliki sedikit penginapan yang disewakan, tetapi mayoritas memiliki lama penginapan tersewa 
         yang cenderung tinggi. Pada Central Region, terlihat sangat banyak penginapan yang disewakan tetapi memiliki lama penginapan tersewa dalam satu tahun yang 
         mayoritas relatif rendah. Hal ini mungkin terjadi karena banyaknya pilihan penginapan yang tersedia di kawasan Central Region, menjadikan turis lebih sering 
         berpindah pindah penginapan sehingga menyebabkan lama penginapan tersewa dalam satu tahun cenderung rendah.
         </p>''', unsafe_allow_html=True)
st.subheader('Apa yang Memiliki Pengaruh Pada Banyak Review?')
st.write(listing_corr, use_container_width = True)
st.markdown('''<p style='text-align: justify; color: white;'>
         Terlihat dari nilai koefisien korelasi yang mendekati 0, antara minimal lama menyewa, harga, lama suatu kamar tersewa dalam satu tahun, 
         dan banyak review tidak ada yang memiliki korelasi kuat. Keempat variable tersebut berkorelasi sangat lemah terhadap satu sama lain. 
         Tetapi diantara korelasi variable-variable tersebut, korelasi antara minimal lama menyewa suatu kamar, dan harga memiliki korelasi yang 
         paling tinggi dengan nilai koefisien korelasi sebesar 0.263.
         </p>''', unsafe_allow_html=True)
st.markdown('''<p style='text-align: justify; color: white;'>   
         Jika dilihat dari koefisien korelasi, variable yang paling memiliki pengaruh pada banyak review adalah price. 
         Berikut merupakan visualisasi dari data banyak review dari suatu kamar dengan harganya:
         </p>''', unsafe_allow_html=True)
st.plotly_chart(review_num_vs_price, use_container_width = True)
st.markdown('''<p style='text-align: justify; color: white;'>
         Terihat bahwa antara banyak review dan harga memiliki korelasi negatif, artinya semakin banyak review yang diperoleh 
         semakin rendah harga penyewaan per malamnya. Tetapi karena koefisien korelasi sangat kecil dan mendekati 0,
         kita tetap tidak dapat memutuskan jika harga memiliki pengaruh terhadap banyak review.
         </p>''', unsafe_allow_html=True)
st.subheader('Business Recomendation')
st.markdown('''<p style='text-align: justify; color: white;'>
         Diketahui bahwa  harga, minimal lama sewa, lama suatu kamar tersewa dalam satu tahun, dan banyaknya review yang diperoleh dalam 5 tahun terakhir 
         memiliki hubungan korelasi yang sangat rendah sehingga tidak dapat menyimpulkan bahwa variabel variable tersebut berhubungan. Sehingga, pebisnis 
         lebih baik melakukan riset lanjutan dengan melihat fasilitas atau keunikan apa yang belum disediakan oleh kompetitor sehingga dapat lebih unggul 
         dan menambah daya tarik pelanggan.
         </p>''', unsafe_allow_html=True)
st.markdown('''<p style='text-align: justify; color: white;'>   
         Untuk menentukan harga yang tepat untuk ditawarkan, pebisnis dapat melakukan pemodelan prediksi harga secara statistik, contohnya dengan model 
         logistic regression, atau model regresi lain. Untuk mendapatkan prediksi yang lebih baik dan akurat, pebisnis dapat mengumpulkan kembali lebih 
         banyak data, atau menambah variabel - variabel yang mungkin memiliki hubungan dengan harga, seperti fasilitas yang disediakan, berapa kamar yang 
         ditawarkan, dan variable lain yang kiranya memiliki pengaruh terhadap harga.
         </p>''', unsafe_allow_html=True)
st.subheader('References')
st.write('''
         * https://www.airbnb.com/
         * https://www.visitsingapore.com/see-do-singapore/
         * https://www.worlddata.info/asia/singapore/tourism.php
         ''')
