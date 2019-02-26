Updating translation
============


Update the language file with changes in gui and code

	pylupdate5 MapLibrary.pro
	
Add translations by editing `MapLibrary_nl.ts` (it is an xml file).

Release the translations with:

	lrelease MapLibrary_nl.ts
	
or something like this (if the wrong lrelease version is selected):

	/usr/lib/x86_64-linux-gnu/qt5/bin/lrelease MapLibrary_nl.ts