# QGIS Map Library #

This plug-in is meant for organizations or organizational units (that can be you !) as a means to provide one or more libraries of (often used) maps (layers) to the end user.

Both libraries and maps can be available local on the file system or remotely on a server accessible via http(s).

Layers can be just about any type QGIS supports, including group layers. Layers can be defined from a "connection string" defining the connection to the data, or from a QGIS layer file (.qlr) containing the connection to the data as well as styling and other properties.

Of course, entries in the library can have a meta data url associated, so the end user can find meta data for layers and sections in the library.

You will find the plug-in in the Web menu. That's also the place where you can define the library the plug-in uses.

More info in the [help](https://marcoduiker.github.io/QGIS_Map_library/help/build/html/index.html). 

## Version history

###  1.3

Contains the opportunity to auto reload the libraries. Therefore, the following tag ("LibrariesRefreshInterval") needs to be added in libs.json:

```
{
    "Example": "libs/example/example.json",
    "LibrariesRefreshInterval": 60
}
```
The value has to be defined in minutes.
This feature is sponsored by [GIS of Canton of Schaffhausen, Switzerland](https://sh.ch/CMS/Webseite/Kanton-Schaffhausen/Beh-rde/Verwaltung/Volkswirtschaftsdepartement/Amt-f-r-Geoinformation-3854-DE.html). 

###  1.2

This version adds the possibility to message the user via message bars. Such a message is shown upon selection of a library item, and/ or when adding a library item to the map.

This feature is sponsored by [Natuurmonumenten](https://www.natuurmonumenten.nl/).

### 1.1

Fixed bug, where some results were skipped when navigating filtered results.

This fix was contributed by [MiraGeowerkstatt](https://github.com/MiraGeowerkstatt).

### 1.0

Bug fixes on opening meta data links and restoring settings.

Added an option to filter search result and navigate with up/ down keys. 

Bug fixes and option were contributed by [MiraGeowerkstatt](https://github.com/MiraGeowerkstatt).

### 0.9

Added the option to sort the library alphabetically.

### 0.8

Moved settings to QgsSettings as advised by [Thomas Schüttenberg](https://github.com/tschuettenberg).

### 0.7

Bug fixes and improvements.

### 0.6

The first Map Library plug-in develop for our new company [LandGoed](https://landgoed.it). This plug-in was developed in honor of the [BORIS](https://edepot.wur.nl/109167) application. The BORIS application was born more than 20 years ago and featured a library, with spatial data to go, and an integrated meta data system. 

