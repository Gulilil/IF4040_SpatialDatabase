import pandas as pd 
import numpy as np
import psycopg2
from dotenv import load_dotenv
from queries import *
import os
import json

load_dotenv()
PREPROCESSED_DATA = os.path.join(os.getcwd(), 'preprocessed_data')


def execute_query(conn, cur, query: str):
  try:
    cur.execute(query)
    conn.commit()
  except Exception as e:
    print(f"[FAILED] Failed to execute query {query} : {e}")

def make_string(text: str, quote : str = "\'"):
  return f"{quote}{text}{quote}"

def adjust_point_insert_query(data):
  data_split = data.split(",")
  lon = data_split[0].strip()
  lat = data_split[1].strip()
  return f"ST_MakePoint({lon}, {lat})::geography"

def adjust_polygon_insert_query(data):
  return f"ST_SetSRID(ST_GeomFromGeoJSON({make_string(data)}), 4326)::geography"


def insert_region(conn, cur, df):
  i = 0
  max_batch = 1
  while (i <= len(df)):
    bound = min(len(df), (i+1) * max_batch)
    partial_df = df[i*max_batch:bound]
    query = "INSERT INTO region VALUES \n"
    for _, row in partial_df.iterrows():
      row_query = "("
      row_query += make_string(row['region_code']) + ", "
      row_query += make_string(row['region_name']) + ", "
      row_query += adjust_point_insert_query(row['point']) + ", "
      row_query += adjust_polygon_insert_query(row['region']) + ", "
      row_query += make_string(row['country_code']) + ", "
      row_query += make_string(row['country_name'])
      row_query += ")\n"
      query += row_query

    execute_query(conn, cur, query)
    i += max_batch
    break


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
    print(f"[CONNECTED] Connected to database: {os.getenv('POSTGRE_DB_NAME')}")

  except Exception as e: 
    print(f"[CONNECTION FAILED] Failed to connect to database: {os.getenv('POSTGRE_DB_NAME')} : {e}")

  
  if (conn is not None and cur is not None):
    # # Create tables if not exists
    # execute_query(conn, cur, CREATE_TABLE_REGION)
    # execute_query(conn, cur, CREATE_TABLE_DISTRICT)
    # execute_query(conn, cur, CREATE_TABLE_ROAD)
    # execute_query(conn, cur, CREATE_TABLE_EARTHQUAKE)
    # print(f"[SUCCESS] Successfully create tables")

    # Import data from csv
    region_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'region.csv'))
    district_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'district.csv'))
    road_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'road.csv'))
    earthquake_df = pd.read_csv(os.path.join(PREPROCESSED_DATA, 'earthquake.csv'))

    # Insert data
    insert_region(conn, cur, region_df)

    cur.close()
    conn.close()