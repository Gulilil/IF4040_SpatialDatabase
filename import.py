import pandas as pd 
import numpy as np
import psycopg2
from dotenv import load_dotenv
from queries import *
import os
import json
import time
import re

load_dotenv()
PREPROCESSED_DATA = os.path.join(os.getcwd(), 'preprocessed_data')


def execute_query(query: str):
  conn = None
  cur = None
  try:
    conn = psycopg2.connect(user=os.getenv("POSTGRE_DB_USER"), 
                            database=os.getenv("POSTGRE_DB_NAME"),
                            password=os.getenv("POSTGRE_DB_PASSWORD"),
                            host=os.getenv("POSTGRE_DB_HOST"),
                            port=os.getenv("POSTGRE_DB_PORT"))
    cur = conn.cursor()
    cur.execute(CREATE_POSTGIS_EXTENSION)
    # print(f"[CONNECTED] Connected to database: {os.getenv('POSTGRE_DB_NAME')}")

  except Exception as e: 
    print(f"[CONNECTION FAILED] Failed to connect to database: {os.getenv('POSTGRE_DB_NAME')} : {e}")

  if (conn is not None and cur is not None):
    try:
      cur.execute(query)
      conn.commit()
    except Exception as e:
      print(f"[FAILED] Failed to execute query {query[:100]} ... {query[-100:]} : {e}")
    finally:
      cur.close()
      conn.close()

def make_string(text: str, quote : str = "\'"):
  return f"{quote}{text}{quote}"

def adjust_point_insert_query(data):
  data_split = data.split(",")
  lon = data_split[0].strip()
  lat = data_split[1].strip()
  return f"ST_MakePoint({lon}, {lat})::geography"

def adjust_geometry_insert_query(data):
  return f"ST_GeomFromGeoJSON({make_string(data)})::geography"


def insert_country(df):
  i = 0
  max_batch = 1
  while (i <= len(df)):
    bound = min(len(df), i + max_batch)
    partial_df = df[i:bound]
    query = "INSERT INTO countries VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += make_string(row['country_code']) + ", "
      row_query += make_string(row['country_name'].replace("\'", "")) + ", "
      row_query += adjust_point_insert_query(row['point']) + ", "
      row_query += adjust_geometry_insert_query(row['shape'])
      row_query += "),\n"
      query += row_query 
    query = query[:-2] +";"
    execute_query(query)
    print(f"[INSERTED] Insert {i} data")
    i += max_batch
    time.sleep(0.1)

def insert_region(df):
  i = 0
  max_batch = 1
  while (i <= len(df)):
    bound = min(len(df), i + max_batch)
    partial_df = df[i:bound]
    query = "INSERT INTO regions VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += make_string(row['region_code']) + ", "
      row_query += make_string(row['region_name'].replace("\'", "")) + ", "
      row_query += adjust_point_insert_query(row['point']) + ", "
      row_query += adjust_geometry_insert_query(row['shape']) + ", "
      row_query += make_string(row['country_code'])
      row_query += "),\n"
      query += row_query 
    query = query[:-2] +";"
    execute_query(query)
    print(f"[INSERTED] Insert {i} data")
    i += max_batch
    time.sleep(0.1)

def insert_district(df):
  i = 0
  max_batch = 10
  while (i <= len(df)):
    bound = min(len(df), i + max_batch)
    partial_df = df[i:bound]
    query = "INSERT INTO districts VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += make_string(row['district_code']) + ", "
      row_query += make_string(row['district_name'].replace("\'", "")) + ", "
      row_query += make_string(row['district_type'].replace("\'", "")) + ", "
      row_query += adjust_point_insert_query(row['point']) + ", "
      row_query += adjust_geometry_insert_query(row['shape']) + ", "
      row_query += make_string(row['region_code'])
      row_query += "),\n"
      query += row_query 
    query = query[:-2] +";"
    execute_query(query)
    print(f"[INSERTED] Insert {i} data")
    i += max_batch
    time.sleep(0.1)

def insert_road(df):
  i = 0
  max_batch = 1000
  while (i <= len(df)):
    bound = min(len(df), i + max_batch)
    partial_df = df[i:bound]
    query = "INSERT INTO roads VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += str(row['id']) + ", "
      row_query += adjust_point_insert_query(row['point']) + ", "
      row_query += adjust_geometry_insert_query(row['line']) + ", "
      row_query += str(row['length'])
      row_query += "),\n"
      query += row_query 
    query = query[:-2] +";"
    execute_query(query)
    print(f"[INSERTED] Insert {i} data")
    i += max_batch
    time.sleep(0.1)

def insert_rail(df):
  i = 0
  max_batch = 1000
  while (i <= len(df)):
    bound = min(len(df), i + max_batch)
    partial_df = df[i:bound]
    query = "INSERT INTO rails VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += str(row['id']) + ", "
      row_query += adjust_point_insert_query(row['point']) + ", "
      row_query += adjust_geometry_insert_query(row['line']) + ", "
      row_query += str(row['length'])
      row_query += "),\n"
      query += row_query 
    query = query[:-2] +";"
    execute_query(query)
    print(f"[INSERTED] Insert {i} data")
    i += max_batch
    time.sleep(0.1)

def insert_earthquake(df):
  i = 0
  max_batch = 500
  while (i <= len(df)):
    bound = min(len(df), i+ max_batch)
    partial_df = df[i:bound]
    query = "INSERT INTO earthquakes VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += str(row['id']) + ", "
      row_query += make_string(row['date']) + ", "
      row_query += make_string(row['time']) + ", "
      row_query += str(row['depth']) + ", "
      row_query += str(row['magnitude_range']) + ", "
      row_query += str(row['n_station']) + ", "
      row_query += str(row['RMS']) + ", "
      row_query += make_string(row['locality'].replace("\'", "")) + ", "
      row_query += adjust_point_insert_query(row['point'])
      row_query += "),\n"
      query += row_query 
    query = query[:-2] +";"
    execute_query(query)
    print(f"[INSERTED] Inserted {i} data")
    i += max_batch
    time.sleep(0.1)


if __name__ == "__main__":
  conn = None
  cur = None
  try:
    conn = psycopg2.connect(user=os.getenv("POSTGRE_DB_USER"), 
                            database=os.getenv("POSTGRE_DB_NAME"),
                            password=os.getenv("POSTGRE_DB_PASSWORD"),
                            host=os.getenv("POSTGRE_DB_HOST"),
                            port=os.getenv("POSTGRE_DB_PORT"))
    cur = conn.cursor()
    cur.execute(CREATE_POSTGIS_EXTENSION)

    conn.close()
    cur.close()

    # Create tables if not exists
    execute_query(CREATE_TABLE_COUNTRY)
    execute_query(CREATE_TABLE_REGION)
    execute_query(CREATE_TABLE_DISTRICT)
    execute_query(CREATE_TABLE_ROAD)
    execute_query(CREATE_TABLE_RAIL)
    execute_query(CREATE_TABLE_EARTHQUAKE)
    print(f"[SUCCESS] Successfully create tables")

    # Import data from csv
    country_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'country.csv'))
    region_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'region.csv'))
    district_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'district.csv'))
    road_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'road.csv'))
    rail_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'rail.csv'))
    earthquake_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'earthquake.csv'))

    # Insert data
    insert_country(country_df)
    insert_region(region_df)
    insert_district(district_df)
    insert_road(road_df)
    insert_rail(rail_df)
    insert_earthquake(earthquake_df)

  except Exception as e: 
    print(f"[CONNECTION FAILED] Failed to connect to database: {os.getenv('POSTGRE_DB_NAME')} : {e}")

