-- DROP DATABASE IF EXISTS museum_plant;
-- CREATE DATABASE museum_plant;
-- \c museum_plant;

DROP TABLE IF EXISTS plant_species;
DROP TABLE IF EXISTS country;
DROP TABLE IF EXISTS botanist;
DROP TABLE IF EXISTS plant;
DROP TABLE IF EXISTS sensor_data;


CREATE TABLE plant_species (
    scientific_name_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    plant_name VARCHAR(100),
    scientific_name VARCHAR(100)
);

CREATE TABLE country (
    country_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    country_name VARCHAR(100)
);

CREATE TABLE botanist (
    botanist_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    botanist_email VARCHAR(100),
    botanist_forename VARCHAR(100),
    botanist_surname VARCHAR(100),
    botanist_phone VARCHAR(20)
);

CREATE TABLE plant (
    plant_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    scientific_name_id INT, -- foreign key
    country_id INT, -- foreign key
    botanist_id INT, -- foreign key
    last_watered TIMESTAMP NOT NULL,
    FOREIGN KEY (scientific_name_id) REFERENCES plant_species(scientific_name_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id)
);

CREATE TABLE sensor_data (
    sensor_data_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    plant_id INT, -- foreign key
    recording_taken TIMESTAMP NOT NULL,
    soil_moisture FLOAT,
    temperature FLOAT,
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);