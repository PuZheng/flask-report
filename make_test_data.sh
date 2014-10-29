#!/bin/bash

rm flask_report/example/temp.db
cd flask_report/example
python make_test_data.py
cd ../../
