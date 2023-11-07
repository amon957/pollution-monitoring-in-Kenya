# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 00:07:39 2023

@author: hp
"""

import streamlit as st
import calendar
import ee
import geemap.foliumap as geemap
import geopandas as gpd
from streamlit_folium import st_folium
from shapely.geometry import mapping
from authenticate import authenticate
import datetime as dt

global ee
global counties
counties=gpd.read_file('Shapefile/Counties.shp')
county_names=counties.sort_values(by=['COUNTY_NAM'], ascending=True)['COUNTY_NAM']

months = [calendar.month_name[i] for i in range(1, 13)]
pollutants = ['Aerosol Index','Carbon Monoxide','Ozone','Sulphur Dioxide','Nitrogen Dioxide']

def get_minimum(image,roi,band):
    min_value = image.reduceRegion(
    reducer=ee.Reducer.min(),
    geometry=roi,
    scale=1113.2
    )
    return min_value.getInfo()[band]
def get_maximum(image,roi,band):
    max_value = image.reduceRegion(
    reducer=ee.Reducer.max(),
    geometry=roi,
    scale=1113.2
    )
    return max_value.getInfo()[band]

def get_pollutant(area_of_study):
    p=st.session_state.pollutant
    start=str(st.session_state.start)
    end=str(st.session_state.end)
    collections={
    'Carbon Monoxide':{
        'collection':"COPERNICUS/S5P/OFFL/L3_CO",'band':'CO_column_number_density'},
    'Nitrogen Dioxide':{
        'collection':"COPERNICUS/S5P/OFFL/L3_NO2",'band':'NO2_column_number_density'},
    'Ozone':{
        'collection':"COPERNICUS/S5P/OFFL/L3_O3",'band':'O3_column_number_density'},
    'Aerosol Index':{
        'collection':"COPERNICUS/S5P/OFFL/L3_AER_AI",'band':'absorbing_aerosol_index'},
    'Sulphur Dioxide':{
        'collection':"COPERNICUS/S5P/OFFL/L3_SO2",'band':'SO2_column_number_density'}
    }
    image=(ee.ImageCollection(collections[p]['collection'])
                .filterDate(start,end)
                .select([collections[p]['band']])
                .filterBounds(area_of_study)
                .mean().clip(area_of_study)
                )
    min_=get_minimum(image,area_of_study,collections[p]['band'])
    max_=get_maximum(image,area_of_study,collections[p]['band'])
    
    return (image,min_,max_)

def create_map(aoi):
    image,min_,max_ = get_pollutant(aoi)
    Map = geemap.Map()
    Map.centerObject(aoi)
    Map.addLayer(aoi, {}, 'County Boundary')
    Map.addLayer(image,
                 {'min':min_,'max':max_,'palette': ['blue','green','yellow', 'red']},
                 'Pollutant')
    Map.add_colorbar_branca({'palette':['blue','green','yellow', 'red'], 'min':min_, 'max':max_})
    Map.addLayerControl()
    return (Map)

def display_county():
    county=st.session_state.county
    county_geom=counties[counties['COUNTY_NAM']==county]
    aoi_geometry = county_geom.geometry.iloc[0]
    aoi_ee_geometry = ee.Geometry(mapping(aoi_geometry))
    st.session_state.map_extent = create_map(aoi_ee_geometry)
def status():
    global ee
    ee=authenticate(ee)
    st.session_state.authentication_status=('Activated',"✅")
    
if 'map_extent' not in st.session_state:
    st.session_state.map_extent = ''
if isinstance(st.session_state.map_extent,geemap.Map):
    with st.container():
        st.markdown('<h5 align=center>'+st.session_state.county+' County '+st.session_state.pollutant+
                     " Between "+str(st.session_state.start)+' and '+str(st.session_state.end)+'</h5>',
                     unsafe_allow_html=True)
        st.markdown('<b align=center>Unit: moles/m2</b>',unsafe_allow_html=True)
        st_folium(st.session_state.map_extent,use_container_width=True,key='map_extent')


with st.sidebar:
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = st.error('Inactive', icon="🚨")
    with st.form('authenticate_earth_engine'):
        submitted = st.form_submit_button("Activate Google Earth Engine",on_click=status)
        if isinstance(st.session_state.authentication_status,tuple):
            values=st.session_state.authentication_status
            st.success(values[0],icon=values[1])
    
    with st.form('county_search'):
        pollutant = st.selectbox('Pollutant',pollutants,key='pollutant')
        county = st.selectbox('County',county_names,key='county')
        
        delta = dt.timedelta(days=6)
        start_date=st.date_input("Start Date",min_value=dt.date(2018,8,1),
                                 max_value=dt.date.today()-delta,
                                 value=dt.date(2018,8,1),
                                 key='start')
        end_date=st.date_input("End Date",min_value=dt.date(2018,8,1),
                               value=dt.date.today()-delta,
                               max_value=dt.date.today()-delta,
                               key='end')
        submitted = st.form_submit_button("Submit",on_click=display_county)
        
        
        