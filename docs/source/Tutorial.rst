Tutorial
========

Flask-Report may help you to create beautiful reports in web pages quickly,
Here we will guide to complete some reports using it.

We assume there is a toy factory with 3 departmets, A, B and C, and in each 
department, some workers worked there. Each day, the workers receive work
commands which contains number of toys to be made. For simplicity, we assume
only work commands in last 180 days are keeped.

The boss want to see reports of deparments and the department leader want
to see reports of each worker in her department.

First, we need to create a Flask app skeleton. All the codes are located in 
*flask_report.tutorial*.

.. literalinclude:: ../../flask_report/tutorial/basemain.py
   :lines: 3, 19-22
   :linenos:


Next, We create some models and add some records.

.. literalinclude:: ../../flask_report/tutorial/models.py
  :lines: 3, 7-
  :linenos:

.. literalinclude:: ../../flask_report/tutorial/utils.py
  :lines: 3, 8-
  :linenos:

Now we are ready to create our first data set. execute *tools/create_data_set.py* by:

.. code-block:: bash
  
  python -m flask_report.tools.create_data_set.py  # don't use flask.ext.report 

this tool will guide you to create a data set. After we create the data set, 
we could find a new data set configuration directory. 

and let us open meta.yaml to check the content:

.. code-block:: yaml

   {
      name: a list of work commands
      description: as the name
      create_time: 2014-11-16 12:03:27.423386
      creator: xiechao06@gmail.com
   }

Then we create the query definition file.

Then we create a synthetic filter.

Then we create a report for leader of department A. all the workers' performance in
this month.

You could open http://127.0.0.1/report/1 to see the result.

Futhermore, the department leader want to see the average performance of her
workers in this month

Then the boss what to see the performance of each department,

The boss may be very busy, so she requires a pie chart of each department in
this month, and a bar chart for each month in last 180 days.


