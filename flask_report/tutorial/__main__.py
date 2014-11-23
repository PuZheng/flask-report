#! /usr/bin/env python
# -*- coding: UTF-8 -*-
"""
SYNOPSIS
    python runserver.py [options]
OPTIONS
    -h
        show this help
    -p  <port>
        the port of server runs on, default is 5000
    -s  <host>
        the ip of the server runs on, default is '0.0.0.0'
    -c  <configuration dir>
        the configuration directory, default is 'report-conf'
"""
import sys
from getopt import getopt

from flask.ext import report
from basemain import app, db


class MyFlaskReport(report.FlaskReport):

    pass
    #def report_template_param(self, report):

        #performance_list = [record[4] for record in report.data]
        #return {
            #'total_performance': sum(performance_list),
            #'avg_performance': float(sum(performance_list)) /
            #len(performance_list),
        #}


@app.before_first_request
def init():
    from utils import make_data
    db.engine.echo = False
    make_data(db)
    db.engine.echo = True

if __name__ == '__main__':

    opts, _ = getopt(sys.argv[1:], 'hp:s:c:')

    for o, v in opts:

        if o == '-h':
            print __doc__
            sys.exit(1)
        elif o == '-p':
            port = int(v)
        elif o == '-s':
            host = v
        elif o == '-c':
            conf_dir = v
        else:
            print 'unknown option: ' + o
            print __doc__
            sys.exit(1)

    try:
        port
        host
    except NameError:
        port = 5000
        host = '0.0.0.0'

    try:
        app.config['REPORT_CONFIG_DIR'] = conf_dir
    except NameError:
        pass

    import models

    MyFlaskReport(app, db, report.utils.collect_models(models))

    app.run(debug=True, port=port, host=host)
