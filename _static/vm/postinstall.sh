#!/bin/sh

# apt update
# apt install libgtk-3-dev
# pip3 install --upgrade wxpython==4.0.7
if [ ! -d /usr/local/lib/python3.6/dist-packages/wx ] ; then
    cd /tmp
    wget http://geo102.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2020/dist-packages.zip
    unzip dist-packages.zip
    cp -r dist-packages/* /usr/local/lib/python3.6/dist-packages/
fi

if [ ! -d /home/user/geodata/models ] ; then
    cp -r /opt/grass-gis-workshop-jena/_static/models/ /home/user/geodata/
fi

ogrinfo /home/user/geodata/osm/jena_rivers.gpkg -sql 'alter table lines rename to jena_rivers'
ogrinfo /home/user/geodata/osm/jena_boundary.gpkg -sql 'alter table multipolygons rename to jena_boundary'
ogrinfo /home/user/geodata/osm/germany_boundary.gpkg -sql 'alter table lines rename to germany_boundary'

if [ ! -f /home/user/geodata/osm/basemap.pack ] ; then
    cd /home/user/geodata/osm/
    wget http://geo102.fsv.cvut.cz/geoforall/grass-gis-workshop-jena/2020/basemap.pack
fi

###

cd /opt

# update GRASS
(
    cd grass;
    git pull;
    make
)

# update materials
(
    cd grass-gis-workshop-jena;
    git pull;
    make html
)

exit 0
