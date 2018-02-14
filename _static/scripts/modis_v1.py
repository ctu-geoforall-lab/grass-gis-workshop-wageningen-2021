import os

from pywps import Process, LiteralInput, LiteralOutput

__author__ = 'Martin Landa'

class ModisV1(Process):
    def __init__(self):
        inputs = [LiteralInput('start', 'Start date (eg. 2017-03-01)',
                               data_type='string'),
                  LiteralInput('end', 'End date (eg. 2017-04-01)',
                               data_type='string')]
        outputs = [LiteralOutput('stats', 'Computed LST statistics',
                                 data_type='string')]

        super(ModisV1, self).__init__(
            self._handler,
            identifier='modis-v1',
            version='0.1',
            title="Modis process (v1)",
            abstract='The process uses the GRASS GIS to compute LST ' \
            'statistics for given period in 2017 for Germany',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            grass_location="/opt/grassdata/germany-modis"
        )

    def check_date(self, date_str):
        from datetime import datetime

        d = datetime.strptime(date_str, '%Y-%m-%d')
        if d.year != 2017:
            raise Exception("Only year 2017 allowed")

    def _handler(self, request, response):
        from grass.pygrass.modules import Module
        from grass.exceptions import CalledModuleError
        
        start = request.inputs['start'][0].data
        end = request.inputs['end'][0].data
        self.check_date(start)
        self.check_date(end)

        output = 'modis_response'
        
        # be silent
        os.environ['GRASS_VERBOSE'] = '0'

        # need to set computation region (would be nice g.region strds or t.region)
        Module('g.region', raster='c_001')
        try:
            Module('t.rast.series',
                   input='modis_c@PERMANENT',
                   output=output,
                   method='average',
                   where="start_time > '{start}' and start_time < '{end}'".format(
                       start=start, end=end
            ))
        except CalledModuleError:
            raise Exception('Unable to compute statistics')

        stats = Module('r.univar',
                       flags='g',
                       map=output
        )

        outstr = ''
        outstr += 'Min: {0:.1f};'.format(float(stats['min']))
        outstr += 'Max: {0:.1f};'.format(float(stats['max']))
        outstr += 'Mean: {0:.1f}'.format(float(stats['mean']))

        response.outputs['stats'].data = outstr

        return response
