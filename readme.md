# QGIS Map Library #

This plug-in is meant for organizations or organizational units (that can be you !) as a means to provide one or more libraries of (often used) maps (layers) to the end user.

Both libraries and maps can be available local on the file system or remotely on a server accessible via http(s).

Layers can be just about any type QGIS supports, including group layers. Layers can be defined from a "connection string" defining the connection to the data, or from a QGIS layer file (.qlr) containing the connection to the data as well as styling and other properties.

Of course, entries in the library can have a meta data url associated, so the end user can find meta data for layers and sections in the library.

You will find the plug-in in the Web menu. That's also the place where you can define the library the plug-in uses.

More info in the [help](https://marcoduiker.github.io/QGIS_Map_library/help/build/html/index.html). 

## Version history

###  1.4

Contains the implementation of an error catcher for PostgreSQL errors. 
When a PostgreSQL error occurs (currently, it only works with error code 42501 – insufficient_privilege), a message is displayed via the QGIS message bar.

In addition, a click-able link has been added that allows the user to send an email directly to the administrator or the person responsible for the database regarding table access permissions.
The configuration for the email link can be provided via the following JSON structure in the libs.json:

```json
{
    "Example":        "libs/example/example.json",
    "email_address":  "administrator@my_organization.org",
    "text_mail_link": "PostgreSQL administrator"
}
```

`email_address`: The email address of the database admin.
`text_mail_link`: The text displayed as a click-able link in the message bar, e.g., "Contact Admin" or "Report Error".

To ensure that the error catcher works correctly, QGIS must either be set to English or a translation file must be used (see the i18n folder) with translations for the error keywords `permission denied` and `no SELECT privilege`.

Also, bug fix where closing and reopening the dialog with search strings in the search box could lead to errors.

###  1.3

Contains the opportunity to auto reload the libraries. To do so, the following tag (`LibrariesRefreshInterval`) needs to be added in libs.json:

```json
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

