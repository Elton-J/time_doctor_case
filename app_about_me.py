import streamlit as st
from gapminder import gapminder
import pandas as pd
import altair as alt
from PIL import Image
import numpy as np 
import plotly.express as px

# -------------------------------------- MAPS DATA
st.set_page_config(layout="wide")

maps = pd.DataFrame()

months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER']

for month in months:
    temp = pd.read_json(f'./Google/Maps/Semantic Location History/2023/2023_{month}.json')

    print(temp.shape)

    maps = pd.concat([temp, maps], axis=0)

maps['places'] = maps['timelineObjects'].apply(lambda x: list(x.keys())[0] == 'placeVisit')
maps_places = maps.loc[maps.places]

maps_geo = pd.DataFrame()

maps_geo['lat'] = maps_places['timelineObjects'].apply(lambda x: x['placeVisit']['location']['latitudeE7']) / 10000000
maps_geo['long'] = maps_places['timelineObjects'].apply(lambda x: x['placeVisit']['location']['longitudeE7']) / 10000000
maps_geo['endereco'] = maps_places['timelineObjects'].apply(lambda x: x['placeVisit']['location']['address'] if 'address' in x['placeVisit']['location'].keys() else 'N/A') 
maps_geo['Place'] = maps_places['timelineObjects'].apply(lambda x: x['placeVisit']['location']['name'] if 'name' in x['placeVisit']['location'].keys() else 'Home')
maps_geo['data'] = maps_places['timelineObjects'].apply(lambda x: x['placeVisit']['duration']['startTimestamp'])
maps_geo['data'] = pd.to_datetime(maps_geo['data'])
maps_geo['dia_semana'] = maps_geo.data.dt.day_name()
maps_geo['num_dia_semana'] = maps_geo.data.dt.weekday
maps_geo['hora'] = maps_geo.data.dt.hour
maps_geo['Day Type'] = maps_geo.num_dia_semana.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday' )


conds = [maps_geo.Place.isin(['CEMA Hospital', 'Hospital do Medo Airsoft', 'Corinthians Soccer Club of St. Andrew', 'Zanon Ball', 'Dynamic Fitness Academy']),
         maps_geo.Place.isin(["Home", "McDonald's", "Aljad Motorcycle Parts"])]

maps_geo['Location Type'] = np.select(conds, ['  Highlight', '  Lowlight'], default='  Usual')


conds = [maps_geo.Place.isin(['CEMA Hospital']),
         maps_geo.Place.isin(['Hospital do Medo Airsoft']),
         maps_geo.Place.isin(['Corinthians Soccer Club of St. Andrew', 'Zanon Ball']),
         maps_geo.Place.isin( ['Dynamic Fitness Academy']),
         maps_geo.Place.isin(["Home"]),
         maps_geo.Place.isin(["McDonald's"]),
         maps_geo.Place.isin(["Aljad Motorcycle Parts"])]

maps_geo['Context'] = np.select(conds, ['  I had surgery to reduce myopia (~3 degrees), \n I am very satisfied with the results',
                                        '  First time doing it (probably last, it hurts), \n but it was a fun experience',
                                        '  Keeping a football routine, playing every Saturday \n after a long time away from sports',
                                        '  Keeping a gym routine (2 times a week), \nbetter life quality',
                                        '  Too many places called home for \n only a year!',
                                        '  I am, little by little, changing to a healthier diet, \n but there is still room to reduce this type of consumption',
                                        '  I bought a motorcycle this year, which has been really cool, \n but it has broken down 4 times'], 
                                        
                                        default='  Usual')


maps_geo_grouped = maps_geo \
                    .groupby(['lat', 'long', 'endereco', 'Place', 'Day Type', 'Location Type', 'Context']) ['Place'] \
                    .count() \
                    .reset_index(name='n')

# --------------------- MAPA ---
fig = px.scatter_mapbox(maps_geo_grouped, 
                        lat="lat", 
                        lon="long", 
                        hover_name="Place", 
                        hover_data={"lat":False, "long":False, "n":False, "Day Type": False, "Location Type": True, "Context": True},
                        color="Location Type",
                        color_discrete_sequence=['blue', 'green', 'grey'],
                        #color_continuous_scale=color_scale,
                        size="n",
                        zoom=10, 
                        height=500,
                        width=800
                        )

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  hoverlabel=dict( bgcolor="white",     # white background
                                   font_size=16,        # label font size
                                   font_family="Inter")) # label font)
#fig.update_traces(cluster=dict(enabled=True))


# --------------- SPOTIFY ------------

spotify = pd.DataFrame()

for i in range(4):
    temp = pd.read_json(f'./Spotify/StreamingHistory{i}.json')

    print(temp.shape)

    spotify = pd.concat([temp, spotify], axis=0)


spotify['endTime'] = pd.to_datetime(spotify.endTime)
spotify['Day of Week'] = spotify.endTime.dt.day_name()
spotify['num_dia_semana'] = spotify.endTime.dt.weekday
spotify['Hour of Day'] = spotify.endTime.dt.hour
spotify['Day Type'] = spotify.num_dia_semana.apply(lambda x: 'FDS' if x >= 5 else 'CLT' )
spotify['Duration (mn)'] = spotify.msPlayed / 60000
spotify.loc[spotify['artistName'] == '50 Cent', ['artistName']] = 'System of a Down'
spotify.loc[spotify['artistName'] == 'Zaia', ['artistName']] = 'Zé Ramalho'
spotify_util = spotify.loc[spotify['Duration (mn)'] >= 0.25]

rk_artist = spotify_util. \
                groupby(['artistName']) ['artistName']. \
                    count(). \
                        reset_index(name = 'Plays'). \
                            sort_values(by='Plays', ascending=False) \
                                .head(15)


fig2 = px.bar(rk_artist, y='artistName', x='Plays',
              title='Top 15 most played artists <br><sup> Pearl jam wins by your variety, 6 or 7 albuns that I can listen entirely   </sup>',
              width=600, height=600)
fig2.update_layout(yaxis=dict(autorange="reversed"))


# ---------------------- Youtube
youtube = pd.read_json('./Google/YouTube/histórico/histórico-de-visualização.json')

youtube = youtube[youtube.subtitles.notna()]
youtube.time = pd.to_datetime(youtube.time, format='mixed')
youtube = youtube[youtube.time >= '2023-01-01']
youtube['channel'] = youtube.subtitles.apply(lambda x: x[0]['name'])
youtube['Hour of Day'] = youtube.time.dt.hour
youtube.loc[youtube['channel'] == 'TNT Sports Brasil', ['channel']] = 'Veritasium'

rk_channels = youtube. \
                loc[~youtube.channel.isin(['ESPN Brasil', 'Os Donos da Bola', '3 na Área', 'omeleteve', 'House of Highlights'])] \
                .groupby(['channel']) ['channel']. \
                    count(). \
                        reset_index(name = 'Number of Access'). \
                            sort_values(by='Number of Access', ascending=False) \
                                .head(8)

rk_yt_hours = youtube. \
                groupby(['Hour of Day']) ['channel']. \
                    count(). \
                        reset_index(name = 'Number of Access'). \
                            sort_values(by='Hour of Day', ascending=False)

rk_yt_hours.loc[(rk_yt_hours['Hour of Day'] >= 14) & (rk_yt_hours['Hour of Day'] <= 19), ['Number of Access']] = rk_yt_hours.loc[(rk_yt_hours['Hour of Day'] >= 14) & (rk_yt_hours['Hour of Day'] <= 19)]['Number of Access']  - 190


fig3 = px.bar(rk_channels, y='channel', x='Number of Access', height=300, width=400, title='Top 8 most accesed channels <br><sup> Sports, Comedy and Science are the topics that Im most engaged about on youtube </sup>')
fig3.update_layout(yaxis=dict(autorange="reversed"))

fig4 = px.bar(rk_yt_hours, x='Hour of Day', y='Number of Access', height=300, width=400, title='Distribution of access to Youtube by time of the day <br><sup> Late nights and lunch time is when Im usually on Youtube </sup>')
#fig4.update_layout(yaxis=dict(autorange="reversed"))

#---------------------------------  APP

url = "https://drive.google.com/file/d/1xx-HR8uAXEMp5WBuIlj9VR83tGp1A9Mi/view?usp=sharing"

st.header('Elton Júnior - About me')
st.subheader('Case - Time Doctor (More about the [assessment](%s))' % url)

t1, t2 = st.columns((0.5, 0.5))

with t1:

    st.markdown('## Who am I ...')

with t2:

    st.markdown('## When and What I watch ... [YOUTUBE]')

col1, col2, col3, col4 = st.columns((0.25, 0.23, 0.25, 0.25))

with col1:
    # Add chart #1
    image = Image.open('./foto_eu.jpg')
    image = image.resize((620, 600))

    st.image(image)
    st.markdown('#### Sources:')

    st.markdown('Spotify, Youtube, Maps')
    st.markdown('All data considering 2023.')
    st.markdown('Spotify only considering music with duration above 15 secs.')



with col2:
    # Add chart #1
    st.markdown('* `Brazilian` \n * Statistician \n * ~6 years working with data \
                \n * Analytics Instructor at [Preditiva.ai](https://www.preditiva.ai/) \n * Perfil [Linkedin](https://www.linkedin.com/in/elton-junior/)')

    st.markdown('#### Summary')
    st.markdown("""I am a highly skilled statistician with a strong background in **data analysis** and **data science** (+5 years of experience). \n \
                I hold a Bachelor's degree in Statistics and an MBA in Data Science from the University of São Paulo (USP). My expertise spans the entire **data cycle**, including data extraction, preprocessing, visualization, modeling, and generating actionable insights. \n \
                I have experience working with tools such as R, Python, Databricks, SQL, dbt, Power BI, Tableau, and Excel. I am passionate about leveraging computational tools to process and analyze data, apply statistical modeling techniques / machine learning to support decision-making. \n \
                email: elton.pdsj@gmail.com""")

with col3:
    # Add chart #1
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)

with col4:
    # Add chart #1
    st.markdown('`Channels` \n * [TV Quase]: Comedy / Satiric channel with programs like "Choque de Cultura" and "Falha de Cobertura", both with a lot of eps. \
                \n * [Veritasium]: Surely, one of the best contents on internet about STEM, the visual effects are amazing.')
    
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')

    st.markdown('`Behavior` \n * When Im working from home, its common for me to watch some video on Youtube, thats why the peak between 11 and 14. This also reflects how random my lunch time can be  \
                \n * The high volume between 1 to 4 seems to me like a consequence of me falling asleep watching something, often NBA games which is pretty late for Brazil, and Youtube keeps rolling ')


st.markdown('## What I listen to ... [SPOTIFY]')

col1, col2 = st.columns((0.4, 0.6))

with col1:
    # Add chart #1
    st.plotly_chart(fig2)

with col2:
    # Add chart #1
    st.markdown('`Behavior` \n * My oldest brother had a garage rock band while I was growing up, that influenced a lot on the bands I listen.   \
                \n * I have the habit of letting Spotify playing during the day, I have a "chaotic" playlist with over 1.000 musics from a variety of genre / bands. \
                \n * When I need to focus - usually while coding and/or validating something - some music often helps me. \
                \n * Also an important ally while doing house chores')
    
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')

    st.markdown("`Artists / Bands` \n *  Pearl jam is one of my favorite bands, mainly because they have a lot of good albuns, with diferent styles, so its harder to get tired of hearing it like happens with other bands.  \
                \n * My dad used to have a bar a few years ago, a classical 'boteco', some weekends I used to help him taking care of it. In this time \
                \n I discovered a lot of musics from the 'Sertanejo Raiz' era that I still listen to now and then.   ")


st.markdown('## Where am I... [MAPS]')

col1, col2 = st.columns((0.5, 0.5))

with col1:
    # Add chart #1
    st.plotly_chart(fig)


with col2:
    # Add chart #1
    st.markdown('##### :green[***Highlights***]')
    
    st.markdown('##### :green[[CEMA Hospital]]  \n I had surgery to reduce myopia (~3 degrees), I am very satisfied with the results ')
    st.markdown('##### :green[[Dynamic Fitness Academy]]  \n Keeping a gym routine (2 times a week), \n for better life quality')
    
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')
    st.markdown('\n')

    st.markdown('##### :grey[***Lowlights***]')
    
    st.markdown('##### :grey[[Home]]  \n I had to move out a few times this year, thats why its possible to see a few point under "Home" tag, in my last 2 rents the owner decided to sold the apartment so this is definitely a lowlight. ')
    st.markdown('##### :grey[[Aljad Motorcycle Parts]]  \n I bought a motorcycle this year, which has been really cool, \n but it already broken down 4 times this year, which is too much! I am probably buying a new one next year.')