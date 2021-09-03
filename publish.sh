#!/bin/sh

rsync -av --delete _build/html/* geo106:/var/www/geoharmonizer/odse_workshop_2021/grass-gis/

exit 0
