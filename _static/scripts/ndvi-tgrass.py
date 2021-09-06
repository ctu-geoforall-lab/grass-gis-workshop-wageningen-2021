#!/usr/bin/env python3
#
##############################################################################
#
# MODULE:       ndvi-tgrass-v1
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI TGRASS version 1
#
# DATE:         Sat Feb  3 15:45:35 2018
#
##############################################################################

#%module
#% description: NDVI TGRASS script version 1
#%end                
#%option G_OPT_STRDS_INPUT
#% key: b4
#% description: Name of input 4th band space time raster dataset
#%end
#%option G_OPT_STRDS_INPUT
#% key: b8
#% description: Name of input 8th band space time raster dataset
#%end
#%option G_OPT_STRDS_INPUT
#% key: mask
#% description: Name of input mask space time raster dataset
#%end
#%option G_OPT_F_OUTPUT
#%end
#%option
#% key: basename
#% description: Basename for output raster maps
#% required: yes
#%end
#%option
#% key: threshold
#% description: Threshold for removing small areas
#% answer: 1200
#%end

import sys
import os
import atexit

from grass.pygrass.modules import Module
from grass.script import parser, parse_key_val
from grass.script.vector import vector_db_select
    
def cleanup():
    Module('g.remove', flags='f', name='ndvi', type='raster')
    Module('g.remove', flags='f', name='ndvi_class', type='raster')
    Module('g.remove', flags='f', name='ndvi_class', type='vector')

def compute(b4, b8, msk, output):

    Module("g.region",
           overwrite = True,
           raster = msk,
           align = b4)

    Module("r.mask",
           overwrite = True,
           raster = msk)

    Module("i.vi",
           overwrite = True,
           red = b4,
           output = "ndvi",
           nir = b8)
                
    recode_str="""-1:0.1:1
0.1:0.5:2
0.5:1:3"""

    Module("r.recode",
           overwrite = True,
           input = "ndvi",
           output = "ndvi_class",
           rules = "-",
           stdin_ = recode_str)

    Module("r.reclass.area",
           overwrite = True,
           input = "ndvi_class",
           output = "ndvi_class2",
           mode = "greater",
           value = int(options["threshold"]) / 10000)

    Module("r.grow.distance",
           overwrite = True,
           input = "ndvi_class2",
           value = output)

    colors_str="""1 grey
2 255 255 0
3 green"""
    Module("r.colors",
           map = output,
           rules = "-",
           stdin_ = colors_str)
    
    
def stats(output, date, fd):
    fd.write('-' * 80)
    fd.write(os.linesep)
    fd.write('NDVI class statistics ({0}: {1})'.format(output, date))
    fd.write(os.linesep)
    fd.write('-' * 80)
    fd.write(os.linesep)
    fd.flush()
    Module(
        "r.report", map=output, units="hectares", flags="ihn", stdout_=fd
    )
        
def main():
    import grass.temporal as tgis

    tgis.init()

    sp4 = tgis.open_old_stds(options['b4'], 'raster')
    sp8 = tgis.open_old_stds(options['b8'], 'raster')
    msk = tgis.open_old_stds(options['mask'], 'raster')

    idx = 1
    fd = open(options['output'], 'w')
    for item in sp4.get_registered_maps(columns='name,start_time'):
        b4 = item[0]
        date=item[1]
        b8 = sp8.get_registered_maps(columns='name',
                                     where="start_time = '{}'".format(date))[0][0]
        ms = msk.get_registered_maps(columns='name',
                                     where="start_time = '{}'".format(date))[0][0]
        output = '{}_{}'.format(options['basename'], idx)
        # compute(b4, b8, ms, output)
        stats(output, date, fd)
        cleanup()
        idx += 1

    fd.close()
    
    return 0

if __name__ == "__main__":
    options, flags = parser()
    sys.exit(main())
