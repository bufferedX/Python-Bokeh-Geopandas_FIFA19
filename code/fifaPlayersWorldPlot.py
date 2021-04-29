# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 23:29:56 2019

@author: Sandipani
"""
import json
import os
import pandas as pd
import geopandas as gpd
from bokeh.io import  show,curdoc
from bokeh.layouts import widgetbox, column, row
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool , Select
from bokeh.palettes import brewer

def json_data(position):
    dataset1 = dataset[dataset.POS == str(position)].groupby('Nationality').count()[['Name']]
    #dataset1['Nationality'] = dataset1.index
    dataset1.rename(columns =  {'Name':'Count'},inplace = True)
    
    #Merge dataframes gdf and df_2016.
    merged = gdf.merge(dataset1, left_on = 'country', right_on = 'Nationality' , how = 'left')
    merged.fillna('No data', inplace = True)
    #Read data to json.
    merged_json = json.loads(merged.to_json())
    #Convert to String like object.
    json_data = json.dumps(merged_json)
    return json_data

def update_plot(attrname, old, new):
    position = position_select.value
    new_data = json_data(position)
    geosource.geojson = new_data
    p.title.text = "Worldwide spread of " + position_select.value + " in FIFA19"

print(os.getcwd())
shapefile = 'data//countryMap//ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']
#gdf.head()

#Importing the dataset
dataset = pd.read_csv('data//FootballData.csv')
POS = []
for x in dataset['Position']:
    if x == 'GK':
        POS.append('Goalkeeper')
    elif x in ('RCB','CB','LCB','LB','RB'):
        POS.append('Defender')
    elif x in ('RCM','LAM','LCM','LDM','CAM','CDM','RM','LM','RDM','CM'):
        POS.append('Midfielder')
    elif x in ('LW','LF','ST','LS','RF','RW','RS'):
        POS.append('Attacker')
    else:
        POS.append('Unknown')
dataset['POS'] = POS

#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data('Goalkeeper'))
#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]
#Reverse color order so that dark blue is highest count.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 70,nan_color = '#d9d9d9')
#Define custom tick labels for color bar.
#tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '40%' , '45':'45%' , '50':'>50%'}
tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '40%', '45': '45%','50': '50%','55': '55%','60': '60%','65': '65%','70': '>70%'}
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('No. of players', '@Count')])
#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=10,width = 600, height = 20,
border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Worldwide spread of Goalkeepers in FIFA19', plot_height = 600 , plot_width = 950, toolbar_location = None , tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'Count', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify figure layout.
p.add_layout(color_bar, 'below')

    
position_select = Select(value='Goalkeeper', title='Position', 
                      options=['Goalkeeper','Defender','Midfielder','Attacker'])

position_select.on_change('value',update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = row(p,widgetbox(position_select))
curdoc().add_root(layout)
#Display plot inline in Jupyter notebook
#Display plot
show(layout)
