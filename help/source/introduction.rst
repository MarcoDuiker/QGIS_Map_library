Introduction
************

About
=====

This plug-in is developed by Marco Duiker from `MD-kwadraat <http://www.md-kwadraat.nl/>`_ . 

The plugin is inserted in the Web Menu of QGIS. Furthermore, an icon is added to the toolbars.

This plug-in is meant for organizations or organizational units (that can be you !) as a means to provide one or more libraries of (often used) maps (layers) to the end user.

Both libraries and maps can be available local on the file system or remotely on a server accessible via http(s).

Layers can be just about any type QGIS supports, including group layers. Layers can be defined from a "connection string" defining the connection to the data, or from a QGIS layer file (.qlr) containing the connection to the data as well as styling and other properties.

Of course, entries in the library can have a metadata url associated, so the end user can find metadata for layers and sections in the library.


Using the plugin
================

Using the plugin is as simple as clicking the icon to open the Map Library dialog.

Then the Map Library can be browsed or searched via the search bar.

Once an interesting layer is found, metadata can be accessed via the `Metadata` button. A layer can be added to the project by double clicking the item, or by pressing the `Add` button.

Via the settings of the plugin (accesible via the Map Library menu in the Web menu of QGIS), the library can be selected. Optionaly the default alphabetical sorting of the map library can be turned off.

Via the settings of the plugin (accesible via the Map Library menu in the Web menu of QGIS), the default position (top or bottom) where the layer will be added can be selected. 

Managing Libraries
==================

Up till now there is no application for managing libraries. So a text editor is all you need (preferably one which shows errors in json files).

Map Library index file
----------------------

In the Map Library settings the user chooses a Map Library index file in json format. 

By default this is the ``libs\libs.json`` file in the plugin folder.

This file should be a json file with contents like:

::

    {
        "Example": "libs/example/example.json"
    }

In this example only one top level entry ``Example`` is shown to the user. The contents from this entry is taken from the Map Library contents file ``libs/example/example.json``.

You can have as many top level entries as you like, by adding more entries separated by colons like:

::

    {
        "Example":          "libs/example/example.json",
        "Another Example":  "libs/example/example2.json"
    }

The Map Library contents file may be specified by:

  - an absolute path on the file system
  - a relative path on the file system (relative to the Map Library plugin folder) 
  - an URL starting with ``http://`` or ``https://``

Automatic Reloading
'''''''''''''''''''

It is possible to have the map libraries reloaded automatically by adding a ``LibrariesRefreshInterval`` entry like:

::

    {
        "Example":          "libs/example/example.json",
        "Another Example":  "libs/example/example2.json",
        "LibrariesRefreshInterval": 60
    } 

The interval must be specified in minutes.


Map Library contents file
-------------------------

The Map Library contents file specifies the content of a top level entry in json format. It is a hierarchical structure with as many levels as you like. Don't go overboard on this as people tend to find things better in wide than in deep structures.

An example of a small piece of a Map Library Contents file is:

::

    {
    "Aerial Photographs": {
        "description": "A nice description ...",
        "Bing": {
            "connection": "libs/example/bing_aerial.qlr",
            "provider": "qlr", 
            "description": "Bing satellite",
            "keywords": ["Microsoft"],
            "metadata_url": "https://wikipedia.org/wiki/Bing_Maps"
        },
        "Blue Marble": {
            "connection": "contextualWMSLegend=0&crs=EPSG:3857&dpiMode=7&featureCount=10&format=image/png&layers=nasa:bluemarble&styles&url=https://demo.boundlessgeo.com/geoserver/ows",
            "provider": "wms", 
            "description": "Nasa Blue Marble provided by Boundless",
            "keywords": ["boundless"],
            "on_load_message": "Please enjoy this beautiful image",
            "metadata_url": "https://visibleearth.nasa.gov/view_cat.php?categoryID=1484"
        }
    },
    "Topography and Roads": {
        "description": "Descriptions on sections may be empty or omited altogether",
        "OpenStreetMap": {
            "connection": "libs/example/osm_standard.qlr",
            "provider": "qlr", 
            "description": "OpenStreetMap standard",
            "keywords": [],
            "metadata_url": "https://www.openstreetmap.org/"
        }
    }
    
    
Defining Sections
'''''''''''''''''

All items which have children and not the properties:
    - ``connection``
    - ``provider``

are sections. A section can have other properties just like the layers (see below). The following properties are allowed:
    - ``description``
       - this is the description shown to the user
    - ``keywords``
       - these keywords get indexed so they aid searching. Don't duplicate words from the ``description`` as those words get indexed anyhow.
    - ``metadata_url``
       - an URL to a page containing metadata for the layer  



Defining Layers
'''''''''''''''

A layer is an item without children which has at least the following properties:
    - ``connection``
       - this defines the path to the data
    - ``provider``
       - this tells QGIS how to interpret the path to add the layer to the project.

Optionally a layer can have the following properties:
    - ``description``
       - this is the description shown to the user
    - ``keywords``
       - these keywords get indexed so they aid searching. Don't duplicate words from the ``description`` as those words get indexed anyhow.
    - ``metadata_url``
       - an URL to a page containing metadata for the layer  
    - ``on_load_message``
       - a message to show the user when the layer gets loaded. This message is shown in the message bar
    - ``on_select_message``
       - a message to show the user when the user selects the layer in the library. This message is shown in a message bar in the library dialog.
    - ``insert_point``
       - a value of ``top`` will insert a layer in the top of the layer tree. For layers based on .qlr files this will only work for QGIS versions above 3.30. 
       
Both the ``on_load_message`` and the ``on_select_message`` can be a simple string. In that case the message is shown as an "Info" message on a blue background and should be clicked away by the user.

Both the ``on_load_message`` and the ``on_select_message`` can be a dictionary like this:

.. code-block:: none

    "on_select_message": {
          "msg": "Just an example critical select message",
          "level": "Critical",
          "duration": 5
    }


These properties mean:
    - ``msg``
       - (required) The message shown to the user. 
    - ``level``
       - (optional, defaults to ``Info``) The message level as in this table:
           - ``Info``:      background color will be blue
           - ``Warning``:   background color will be orange
           - ``Critical``:  background color will be red
           - ``Succes``:    background color will be green
    - ``duration``
       - (optional, defaults to 0) The duration in seconds the message will be shown. When zero, this will be indefinitely.



Defining VALID layers
'''''''''''''''''''''

A valid layer has to have a ``provider`` property which is supported. The following providers are supported (case sensitive):

   - Vector Layers
      - ``delimitedtext``
      - ``gpx``
      - ``ogr``
      - ``postgres``
      - ``spatialite``
      - ``WFS``
   - Raster Layers
      - ``gdal``
      - ``wcs``
      - ``wms``
   - Any layer type via qlr file
      - ``qlr``

All these require a ``connection`` which QGIS uses to add the layer. Creating a valid ``connection`` is a bit of a black art for these layer types. Adding the layer to be defined to QGIS first and then looking at the source properties helps, as well as `this page <https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_ in the pyQGIS cookbook.

A much easier way to create a valid layer is the following process:

   1. In QGIS create a layer (or a group layer) having all the properties you want the layer in the library to have)
   2. Export this layer (or layer group) to a QGIS layer definition file (.qlr)
   3. Make the path to this .qlr file the ``connection``. This may be  
       - an absolute path on the file system
       - a relative path on the file system (relative to the Map Library plugin folder) 
       - an URL starting with ``http://`` or ``https://``
   4. Set the ``provider`` to  
       - ``qlr``

The nice thing about this approach is that the QGIS layer definition file saves all properties of the layer(group) like styling, scale dependent visibility, metadata, etc.


**Beware:** 

If you create layers from local files the user must have access to the file paths which ends up in the ``.qlr`` file. Depending on system configuration it might be easier to work with relative paths (relative to the Map Library plugin folder) or rather with absolute paths.  

For things to work out it might be necessary to edit the ``.qlr`` files with a text editor to get the file paths right.

Distributing Map Libraries in an organization
---------------------------------------------

Many organizations distribute plugins and settings via the QGIS user profile to the end users. Often different profiles are distributed to different user groups.

In the user profile the file ``QGIS3.ini`` plays a central role. A lot of settings, including plugins, plugin settings but also eg. the users tool bar settings are stored in this file.

Because all of these different settings in this file it is not nice to push a new ``QGIS3.ini`` file to a group of users to distribute a new Map Library Index file.

This can be avoided by offloading the plugin settings to a global settings file  ``your_QGIS_PKG_path/resources/qgis_global_settings.ini``. 
To do this use a text editor to create ``your_QGIS_PKG_path/resources/qgis_global_settings.ini`` and copy to that file the appropriate section from the ``QGIS3.ini`` file (don't forget to remove that section from the ``QGIS3.ini`` as well) . This section will look something like this:

::

    [MapLibrary]
    lib_path=https://your_url.org/your_library.json


For more information on the QGIS configuration see: https://docs.qgis.org/3.10/en/docs/user_manual/introduction/qgis_configuration.html#running-qgis-with-advanced-settings

For more information on distributing settings to users or user groups see the outdated but still informative: http://www.qgis.nl/2014/04/22/qgis-in-de-klas-onder-windows/?lang=en 











