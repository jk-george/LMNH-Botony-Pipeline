IF OBJECT_ID('alpha.sensor_data', 'U') IS NOT NULL DROP TABLE alpha.sensor_data;
IF OBJECT_ID('alpha.plant', 'U') IS NOT NULL DROP TABLE alpha.plant;
IF OBJECT_ID('alpha.plant_species', 'U') IS NOT NULL DROP TABLE alpha.plant_species;
IF OBJECT_ID('alpha.country', 'U') IS NOT NULL DROP TABLE alpha.country;
IF OBJECT_ID('alpha.botanist', 'U') IS NOT NULL DROP TABLE alpha.botanist;

CREATE TABLE alpha.plant_species (
    scientific_name_id INT IDENTITY(1,1) PRIMARY KEY,
    plant_name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(100) NOT NULL
);

CREATE TABLE alpha.country (
    country_id INT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE alpha.botanist (
    botanist_id INT IDENTITY(1,1) PRIMARY KEY,
    botanist_email VARCHAR(100) NOT NULL,
    botanist_forename VARCHAR(100) NOT NULL,
    botanist_surname VARCHAR(100) NOT NULL,
    botanist_phone VARCHAR(20) NOT NULL
);

CREATE TABLE alpha.plant (
    plant_id INT NOT NULL PRIMARY KEY,
    scientific_name_id INT,
    country_id INT,
    botanist_id INT,
    FOREIGN KEY (scientific_name_id) REFERENCES alpha.plant_species(scientific_name_id),
    FOREIGN KEY (country_id) REFERENCES alpha.country(country_id),
    FOREIGN KEY (botanist_id) REFERENCES alpha.botanist(botanist_id)
);

CREATE TABLE alpha.sensor_data (
    sensor_data_id INT IDENTITY(1,1) PRIMARY KEY,
    plant_id INT,
    recording_taken DATETIME NOT NULL,
    last_watered DATETIME NOT NULL,
    soil_moisture FLOAT,
    temperature FLOAT,
    FOREIGN KEY (plant_id) REFERENCES alpha.plant(plant_id)
);