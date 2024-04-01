# Project Title

Brief description of your project.

## Table of Contents
- [About the Dataset](#about-the-dataset)
- [About the Project](#about-the-project)
  - [Introduction](#introduction)
  - [Batch Processing Questions](#batch-processing-questions)
  - [Realtime Processing Questions](#realtime-processing-questions)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Architecture](#architecture)
- [Components](#components)
  - [Component 1](#component-1)
  - [Component 2](#component-2)
- [Communication](#communication)
  - [Subheading 1](#subheading-1)
  - [Subheading 2](#subheading-2)
- [Scripts](#scripts)

## About the Dataset

### Context

This dataset covers hourly weather data from 623 INMET weather stations in Brazil.

**Dataset Source:** INMET (National Meteorological Institute - Brazil).

**Equipment:** Vaisala Automatic Weather Station AWS310

**Category:** Weather

**Size:** 10.11GB

The dataset can be downloaded from [Kaggle](https://www.kaggle.com/datasets/PROPPG-PPG/hourly-weather-surface-brazil-southeast-region).

### Content

The dataset includes the following data:

| Data                                         | Description                                                 |
|----------------------------------------------|-------------------------------------------------------------|
| Date (YYYY-MM-DD)                            | The date of the observation                                 |
| Time (HH:00)                                 | The time of the observation                                 |
| Amount of precipitation (mm)                 | Amount of precipitation in millimeters (last hour)          |
| Atmospheric pressure at station level (mb)   | Atmospheric pressure at station level                       |
| Maximum air pressure (mb)                    | Maximum air pressure for the last hour                      |
| Minimum air pressure (mb)                    | Minimum air pressure for the last hour                      |
| Solar radiation (KJ/m2)                      | Solar radiation                                             |
| Air temperature (instant) (°C)               | Instantaneous air temperature                               |
| Dew point temperature (instant) (°C)         | Instantaneous dew point temperature                         |
| Maximum temperature (°C)                     | Maximum temperature for the last hour                       |
| Minimum temperature (°C)                     | Minimum temperature for the last hour                       |
| Maximum dew point temperature (°C)           | Maximum dew point temperature for the last hour             |
| Minimum dew point temperature (°C)           | Minimum dew point temperature for the last hour             |
| Maximum relative humidity (%)                | Maximum relative humidity for the last hour                 |
| Minimum relative humidity (%)                | Minimum relative humidity for the last hour                 |
| Relative humidity (instant) (%)              | Instantaneous relative humidity                             |
| Wind direction (degrees)                     | Wind direction in radius degrees (0-360)                    |
| Wind gust (m/s)                              | Wind gust in meters per second                              |
| Wind speed (m/s)                             | Wind speed in meters per second                             |
| Brazilian geopolitical regions               | Geopolitical region of Brazil                               |
| State (Province)                             | State or province                                           |
| Station Name                                 | Name of the weather station (usually city location or nickname) |
| Station code (INMET number)                  | Code number of the INMET station                            |
| Latitude                                     | Geographic latitude of the station                          |
| Longitude                                    | Geographic longitude of the station                         |
| Elevation                                    | Elevation of the station in meters                          |


## About the Project

### Introduction
```
This project focuses on designing and implementing an architecture for processing large datasets,  
demonstrated through data transformation, analysis, and presentation.  
It utilizes two datasets from distinct sources, with the primary dataset containing historical data with size of 10.11GB,  
and secondary dataset of getting realtime information from **OpenWeatherApi** once per second per city/region.  
A data lake with raw, transformation, and curated zones is created, and the loading of the dataset into the data lake is automated.  
The system's architecture is divided into 8 Docker containers for modular communication, and shell scripts are provided   
for easy system usage. Data processing includes batch processing with at least 10 complex queries/transformations and  
real-time processing with up to 5 complex data stream transformations. Results are visualized for the end-user,  
and mechanisms for automated data processing are in place. The entire system is designed to be fully automated,  
ensuring seamless operation and efficiency in handling large-scale data processing tasks.  
```

### Batch Processing Questions

```
1. What is the average temperature for each province in the specified region over the last few months?
2. How much total rainfall has each province in the specified region received in each month of the period?
3. What are the highest and lowest atmospheric pressures recorded in each province of the specified region over the selected period?
4. What is the average wind speed for each province in the specified region over the last few months?
5. How much total solar radiation has each province in the specified region received in each month of the period?
6. What is the distribution of wind directions (North, East, South, West) for each province in the specified region over the selected period?
7. How variable is the humidity in each province of the specified region over the last few months?
8. What is the average Temperature-Humidity Index (THI) for each province in the specified region over the selected period?
9. What is the range of dew point temperatures for each province in the specified region over the last few months?
10. How variable is the air temperature in each province of the specified region over the selected period?
```

### Realtime Processing Questions

Questions related to realtime processing in your project.

## Repository Structure

```

BrazilWeather/  
├── v10_Scripts/  
│ ├── buildDockerImages.sh  
│ ├── clear.sh  
│ ├── completeSetup.sh  
│ ├── configureSSH.sh  
│ ├── downloadDataSet.py  
│ ├── downloadDataSet.sh  
│ └── startSystem.sh  
├── v20_Test/  
│ ├── checkDataBase.py  
│ ├── checkDataBase.sh  
│ ├── processData.py  
│ └── processData.sh  
├── v30_Dataset/  
│ └── .gitkeep  
├── v40_Libraries/  
│ └── .gitkeep  
├── v50_Components/  
│ ├── Hadoop_comp/  
│ │ ├── comm.py  
│ │ ├── configureHadoop.sh  
│ │ ├── Dockerfile  
│ │ ├── hadoop.py  
│ │ ├── startHadoopServices.sh  
│ │ └── stopHadoopServices.sh  
│ ├── Loader_comp/  
│ │ ├── comm.py  
│ │ ├── Dockerfile  
│ │ └── loader.py  
│ ├── Marshaller_comp/  
│ │ ├── comm.py  
│ │ ├── configuration.json  
│ │ ├── Dockerfile  
│ │ ├── logger.py  
│ │ ├── marshaller.py  
│ │ └── runtime.py  
│ ├── Mosquitto_comp/  
│ │ ├── Dockerfile  
│ │ └── mosquitto.conf  
│ ├── Processor_comp/  
│ │ ├── calculator.py  
│ │ ├── comm.py  
│ │ ├── Dockerfile  
│ │ └── processor.py  
│ ├── Realtime_comp/  
│ │ ├── city_province.json  
│ │ ├── comm.py  
│ │ ├── configuration.json  
│ │ ├── Dockerfile  
│ │ └── realtime.py  
│ ├── Transformer_comp/  
│ │ ├── comm.py  
│ │ ├── Dockerfile  
│ │ └── transformer.py  
│ └── UI_comp/  
│ ├── comm.py  
│ ├── daoHandler.py  
│ ├── Dockerfile  
│ └── uiSystem.py  
├── .gitignore  
├── commands.txt  
├── README.md  
└── specification.pdf  
```

## Getting Started

To set up the project and build the Docker containers, follow these steps:

1. Run the `completeSetup.sh` script to prepare the environment for the Docker containers.
2. Download the dataset manually from the link provided in [About the Dataset](#about-the-dataset)    
since the `downloadDataSet.sh` script requires a `credentials.json` file,  
which is not available in the repository (these are credentials to download dataset hosted in private googledrive).   
After downloading, extract the dataset into the `v30_Dataset` directory.  
3. Run the `buildDockerImages.sh` script to build all 8 Docker images for the system.
4. To start the Docker containers, run the `startSystem.sh` script.

The responsibilities of each script will be discussed in detail in the Scripts section.

## Architecture

Description of the architecture of your project.

## Usage

Examples of how to use your project.

## Components

### Component 1

Description of a component in your project.

### Component 2

Description of another component in your project.

## Communication

### Subheading 1

Details about a specific aspect of communication in your project.

### Subheading 2

Details about another aspect of communication in your project.


## Scripts

Explanation of the scripts included in your project.