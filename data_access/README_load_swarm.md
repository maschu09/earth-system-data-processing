Author: Maximilian Gregorius

A jupyter notebook explaining briefly how to acceess and download data from ESA's Swarm mission as part of the module Earth system data processing.

This readme file serves more as a lab book of my findings during the work with the Swarm data than a more conventional, purely descriptive readme file
and follows mostly the layout given in the homework assignment sheet. But first a brief summary of the Swarm mission and on the data retrival system VirES.

# The Swarm Mission 
Swarm is ESA's first constellation mission to survey Earth's magnetic and electric field and their temporal variations. It launched in 2013 and consits of three sattelites, called Alpha(A), Bravo(B) and Charlie(C) and is planned to continue the survey until 2025. A basic overview of the mission can be found at https://earth.esa.int/eogateway/missions/swarm.

In this notebook we will use the data retrival system VirES to get access to a vast amount of data inluding many of ESA’s Earth Explorer missions, Aeolus and most importantly Swarm. This data is available for many different collections of measurements and auxiliary measurements and associated models including the magnetic field, electric field, ion temperature, sattelite positions and many more. A more experienced use might use this data to calculate and visualize Earth's magnetic field or do simple space weather forecasting, but in this notebook we will focus mainly on getting access to the data and how to download some magnetic field data. The goal is to get the user familiarized with the VirEs environment and working with Swarm data so they can modify it in the future for their own needs. Some basic understanding of geomagnetism is advised but not necessary and anyone willing to learn can check out the ressources below to deepen their understanding.


Understanding Earth's geomagnetic sources: https://link.springer.com/journal/11214/volumes-and-issues/206-1.

# Evaluation of VirES as a Data Portal
As desribed above VirES(Virtual environments for Earth observation Scientists) is a data retrival system, that also includes a server system and a graphical web interface which allows easy visualisation and manipulation of Swarm products. 
It is designed to lower the barrier of entry for Scientists who want to acceess Swarm data. The website(https://notebooks.vires.services/docs/vre-overview#)offer a lot of basic explanations and example code to make it possible to get started in 
a matter of minutes. 
To identify the magnetic data used in the notebook the Swarm Product Data Handbook https://swarmhandbook.earth.esa.int/catalogue/index, which is directly provided by the ESA, was used. Using the appropriate filters for Swarm and magnetic data it is possible to identify a handful of products that would give potentially useful data. Searching the VirES support website Available parameters for Swarm(https://viresclient.readthedocs.io/en/latest/available_parameters.html) gives a long list of available collections and measurements making it possible to identify "MAG" as the best collection for use in the homework notebook. While the ressources are plentiful and everything is logically inter-linked, it still can be quite difficult to find the data
one wants to use, as the load of options can be overwhelmimg . It is very helpful to know exactly what you are looking for and to have a backround in geomagnetism to quickly understand all the abbreviations used for the measurements.
