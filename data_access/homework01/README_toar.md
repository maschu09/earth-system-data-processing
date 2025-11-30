Nils Hornstein, 7369566

Identification of a Dataset

To identify a specific dataset to work with, I went with the tip and picked air quality as a broad topic to focus on. In this context, I selected a specific variable later on. I started by organizing the list of given suggestions. Therefore, I created a table containing all datasets as entries and evaluated them regarding the type of data, the resolution and scope, ease of use and accessibility, and if applicable special features as well as the areas of application. To support this step and speed up the process, I designed a suitable LLM prompt: 

“Erstelle eine Vergleichstabelle für Wissenschaftler zum Thema Wetter-, Klima- und Erdbeobachtungsdaten. Die Tabelle soll den späteren Auswahlprozess eines Datensatzes unterstützen. Tabellenspalten: Art der Daten, Auflösung/Umfang (zeitlich und räumlich mit Einheiten), Benutzerfreundlichkeit/Zugänglichkeit (Begründung und vergebe eine Note schlecht, mittel, gut oder sehr gut), Besonderheiten/Einsatzbereiche. Bleib bei der Evaluation der einzelnen Datensätze kurz und präzise. Nutze die folgenden Datenquellen: [Namen + Links].”

Based on the table that ChatGPT-5 created using the prompt, I have selected two datasets that I find interesting regarding the overarching topic of air quality - the TOAR as well as the IAGOS dataset. In the end, I opted for the TOAR data on global air quality for several reasons.
First, TOAR appeared substantially more manageable for the scope of this assignment. While exploring both options, I felt somewhat overwhelmed by the complexity and breadth of the IAGOS dataset, which spans multiple data types, instruments, measurement platforms, and access pathways. In contrast, the TOAR data is supported by very clear, well-structured documentation that not only explains how to access the data but also provides sample code snippets in Python and even a dedicated GitLab repository from a user workshop containing additional Jupyter notebooks.
Moreover, gaining access to TOAR data was considerably easier. Access was possible directly via Shibboleth using my University of Cologne account, which made the process straightforward and quick. The IAGOS dataset, on the other hand, required a much more involved registration workflow. This includes the creation of an additional AERIS account, completing a questionnaire, and submitting a request that needed approval. In summary, this made the IAGOS dataset less convenient and appealing. The clearer documentation, simpler access workflow, and overall lower complexity led me to choose TOAR as the more suitable dataset for this first assignment.

Description of the TOAR Dataset

The TOAR dataset is part of the TOAR database which is a central data repository for global data from surface ozone and ozone precursor measurements and one of the largest collections of ozone-related surface observations worldwide. It is fully committed to Open Data and FAIR principles, and all data are provided without restrictions under a CC-BY 4.0 license. The term TOAR is an acronym standing for Tropospheric Ozone Assessment Report. Started as a project to support scientists worldwide to perform standardized analyses of ozone-related data, already the second phase referred as TOAR-II has started to further develop, extend and improve the TOAR database. Thereby, the TOAR database is operated by the Jülich Supercomputing Centre at Forschungszentrum Jülich in Germany. 

Overall, the database contains measurements from almost 24,000 stations, covering a period from the 1970s up to 2022/2023. Its total data volume amounts to nearly 10 Terabytes. The dataset primarily consists of hourly surface-level ozone measurements, although finer temporal resolutions (e.g., half-hourly) are included when available, depending on the data provider. In addition, TOAR also offers aggregated statistics and trend estimates derived from these time series, all of which are based on the harmonised hourly format used for TOAR analyses to support long-term environmental assessments. Moreover, the database includes time series from ERA5 reanalysis that support the investigation of ozone changes and their drivers by providing relevant meteorological context. 

The data of the TOAR database originate from 18 major air-quality monitoring networks, public data services and many individual data providers. To ensure good quality of the data, only measurements from research-grade instruments are accepted. Besides this restriction, quality assurance is performed through a combination of provider-level checks, automated quality-control tools, and, in some cases, manual inspection. 
As the TOAR data is used for scientific papers during TOAR-II, insights from preliminary analyses of the data are also fed back into the database as a recursive feedback-loop. The TOAR database's data flagging scheme also makes it possible to distinguish the respective quality flags and identify the origin of this evaluation.

Beyond its main purpose of provisioning ground-level ozone concentration time series, the TOAR database also includes harmonised metadata such as several ozone precursor variables and meteorological information. 
TOAR augments station metadata using globally uniform geospatial aggregates (GEO-PEAS), including population, landcover or nightlight statistics within user-defined radii. This geospatial metadata forms the basis to enable harmonized filtering and several station characterisation approaches. TOAR offers different options of characterisation for the measurement stations which differ in levels of complexity and harmonisation. Besides the location, this includes four distinct approaches for characterisation. Starting off with the TOAR Station Characterisation, the European Station Characterisation Scheme, the Station Characterisation Through Geospatial Data, as well as Individual Station Description. 
For example, the TOAR Station Characterisation distinguishes into four categories: Urban, RuralLowElevation, RuralHighElevation, and Unclassified. However, the documentation points out that the specific values and thresholds associated with the criteria for classification into the four categories are only approximate and subjectively selected reference points.

In terms of data access, users don’t directly access the TOAR database itself. Instead, two access routes are provided. It can either be accessed through a graphical user interface, which they call dashboard, on the TOAR homepage, or through a search endpoint via a REST API which can be used in the browser or your own programs. When retrieving data, a distinction is made between anonymous users and registered users, whereby the full scope of data requests is only possible upon registration. For REST API queries, an access token is required, but more on this later and in the sample code. By default, queries to the TOAR REST API return a JSON structure, but CSV files are also possible. Processing time and data volume is significantly influenced by a targeted selection of query fields, as already explicitly highlighted by the documentation.


https://toar-data.fz-juelich.de/sphinx/TOAR_UG_Vol04_FAQ/build/html/TOAR_database.html 
https://toar-data.org/about-toar-data/#about_data
https://toar-data.org/about-toar/
https://online.ucpress.edu/elementa/article/doi/10.1525/elementa.244/112447/Tropospheric-Ozone-Assessment-Report-Database-and

Schröder, S., Selke, N., and Schultz, M. G.: The TOAR data infrastructure: A generalised database infrastructure for environmental time series, EGU General Assembly 2023, Vienna, Austria, 24–28 Apr 2023, EGU23-1848, https://doi.org/10.5194/egusphere-egu23-1848, 2023 

Data Access and Development of Download Script

Scalability (15-45 lines)

