-- Drop database schema if it exists
IF OBJECT_ID('sensor_data', 'U') IS NOT NULL DROP TABLE sensor_data;
IF OBJECT_ID('plant', 'U') IS NOT NULL DROP TABLE plant;
IF OBJECT_ID('plant_species', 'U') IS NOT NULL DROP TABLE plant_species;
IF OBJECT_ID('country', 'U') IS NOT NULL DROP TABLE country;
IF OBJECT_ID('botanist', 'U') IS NOT NULL DROP TABLE botanist;


CREATE TABLE plant_species (
    scientific_name_id INT IDENTITY(1,1) PRIMARY KEY,
    plant_name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(100) NOT NULL
);

CREATE TABLE country (
    country_id INT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE botanist (
    botanist_id INT IDENTITY(1,1) PRIMARY KEY,
    botanist_email VARCHAR(100) NOT NULL,
    botanist_forename VARCHAR(100) NOT NULL,
    botanist_surname VARCHAR(100) NOT NULL,
    botanist_phone VARCHAR(20) NOT NULL
);

CREATE TABLE plant (
    plant_id INT IDENTITY(1,1) PRIMARY KEY,
    scientific_name_id INT, -- foreign key
    country_id INT, -- foreign key
    botanist_id INT, -- foreign key
    FOREIGN KEY (scientific_name_id) REFERENCES plant_species(scientific_name_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id)
);

CREATE TABLE sensor_data (
    sensor_data_id INT IDENTITY(1,1) PRIMARY KEY,
    plant_id INT, -- foreign key
    recording_taken DATETIME NOT NULL,
    last_watered DATETIME NOT NULL,
    soil_moisture FLOAT,
    temperature FLOAT,
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);