Final Project - Interactive Data Visualization  
===

## Parts of our code:
We did not place any pre-written libraries in our repository. All of the files present in the repository were created by members of the team.

## Libraries utilized:
With that being said there are multiple libraries we utilized to do invaluable processing on our data for creating our final CSV passed into our visualizations.
- GoShippo: https://goshippo.com/, this allowed for us to determine the origin location of packages using their tracking numbers.
- GeoPy: https://geopy.readthedocs.io/en/stable/, this library allowed us to convert those origin locations into counties for easier grouping.
- AddFIPS: https://github.com/fitnr/addfips/, this library allowed us to fill in FIPS code data for the found counties. This code number was needed for filling our county heat map.
- US Atlas TopoJSON: https://github.com/topojson/us-atlas/, this library contained pre-generated geoJSON files for mapping out the counties and states of the US. This enabled our process of filling a county map in the first place.

## Links to our other stuff:
- Website: https://woosterum.github.io/final/
- Screencast Video: https://www.youtube.com/watch?v=I8-Nu6m1iRM/

## Non-obvious Interface Features
- Most chart visualizations have zoom and cropping by selecting an area with your mouse.
- All visualizations have additional info from hovering over certain areas.
- The county heat map can be zoomed in on using your scroll wheel.
- The "Process Book" and "Data Source" links in "Discussion" will start a download for the PDF and CSV of the respective files.
