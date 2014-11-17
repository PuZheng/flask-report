#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# utils.py
import random
from datetime import datetime, timedelta


def make_data(db):
    from models import Department, Worker, WorkCommand
    db.create_all()

    d_a = db.session.add(Department(name='A'))
    d_b = db.session.add(Department(name='B'))
    d_c = db.session.add(Department(name='C'))

    workers = [
        Worker(name='Noah', department=d_a),
        Worker(name='Liam', department=d_a),
        Worker(name='Jacob', department=d_a),
        Worker(name='Mason', department=d_a),
        Worker(name='William', department=d_a),
        Worker(name='Ethan', department=d_a),
        Worker(name='Michael', department=d_b),
        Worker(name='Alexander', department=d_b),
        Worker(name='Jayden', department=d_b),
        Worker(name='Daniel', department=d_c),
        Worker(name='Sophia', department=d_c),
        Worker(name='Emma', department=d_c),
        Worker(name='Olivia', department=d_c),
        Worker(name='Isabella', department=d_c),
        Worker(name='Ava', department=d_c),
        Worker(name='Mia', department=d_c),
        Worker(name='Emily', department=d_c),
        Worker(name='Abigail', department=d_c),
        Worker(name='Madison', department=d_c),
        Worker(name='Elizabeth', department=d_c),
    ]

    for worker in workers:
        db.session.add(worker)
        for i in xrange(random.randrange(1, 559)):
            quantity = random.randrange(1, 21)
            today = datetime.now().replace(hour=0, minute=0, second=0,
                                           microsecond=0)
            # last six month
            created = today - timedelta(random.randrange(1, 186))
            db.session.add(WorkCommand(worker=worker, quantity=quantity,
                                       created=created))
