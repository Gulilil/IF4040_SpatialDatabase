CREATE_DATABASE = "CREATE DATABASE earthquake"

CREATE_POSTGIS_EXTENSION = "CREATE EXTENSION IF NOT EXISTS postgis"

CREATE_TABLE_REGION = """CREATE TABLE IF NOT EXISTS region (
  region_code VARCHAR(255) PRIMARY KEY,
  region_name VARCHAR(255) NOT NULL,
  point GEOGRAPHY(Point) NOT NULL,
  shape GEOGRAPHY(MultiPolygon) NOT NULL,
  country_code VARCHAR(255) NOT NULL,
  country_name VARCHAR(255) NOT NULL
)
"""

CREATE_TABLE_DISTRICT = """CREATE TABLE IF NOT EXISTS district (
  district_code VARCHAR(255) PRIMARY KEY,
  district_name VARCHAR(255) NOT NULL,
  district_type VARCHAR(100) NOT NULL,
  point GEOGRAPHY(Point) NOT NULL,
  shape GEOGRAPHY NOT NULL,
  region_code VARCHAR(255) NOT NULL,
  FOREIGN KEY (region_code) REFERENCES region(region_code) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT check_polygon_multipolygon CHECK (
      GeometryType(shape) IN ('POLYGON', 'MULTIPOLYGON')
  )
)
"""

CREATE_TABLE_ROAD = """CREATE TABLE IF NOT EXISTS road (
  id INT PRIMARY KEY,
  point GEOGRAPHY(Point) NOT NULL,
  line GEOGRAPHY(LineString) NOT NULL,
  length FLOAT NOT NULL
)
"""

CREATE_TABLE_EARTHQUAKE = """CREATE TABLE IF NOT EXISTS earthquake (
  id INT PRIMARY KEY,
  date DATE NOT NULL,
  time TIME NOT NULL,
  depth FLOAT NOT NULL,
  magnitude_range FLOAT NOT NULL,
  n_station INT NOT NULL,
  rms FLOAT NOT NULL,
  locality VARCHAR(100) NOT NULL,
  point GEOGRAPHY(Point) NOT NULL
)
"""