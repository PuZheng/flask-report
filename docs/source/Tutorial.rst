Tutorial
========

Flask-Report may help you to create beautiful reports in web pages quickly,
Here we will guide to complete some reports using it.

We assume there is a toy factory with 3 departmets, A, B and C, and in each 
department, some workers worked there. Each day, the workers receive work
commands which contains number of toys to be made.

The boss want to see reports of deparments and the department leader want
to see reports of each worker in her department.

First, we need to create a Flask app skeleton.

.. literalinclude:: ../../flask_report/tutorial/basemain.py

Next, We create some models and add some records.

.. literalinclude:: ../../flask_report/tutorial/models.py

.. literalinclude:: ../../flask_report/tutorial/utils.py

Now we are get ready to create our first data set. execute *tools/create_data_set.py* by:

.. code-block:: bash
  
  python -m flask_report.tools.create_data_set.py  # don't use flask.ext.report 

this tool will guide you to create a data set. After we create the data set, 
we could find a new data set configuration directory. 

.. image::

and let us open meta.yaml to check the content:

.. code-block:: yaml

   name: 三国人物
   description: 三国时期各个国家人物情况
   creator: 智冠 
   create_time: 2013-07-02 07:30:00
   default_report_name: xxxx报表

    
    
