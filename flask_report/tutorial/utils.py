#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# utils.py
import random
from datetime import datetime, timedelta


def commit(db, *objs):
    for obj in objs:
        db.session.add(obj)
    db.session.commit()
    return obj


def make_data(db):
    from models import Department, Worker, WorkCommand
    db.create_all()

    _commit = (lambda *objs: commit(db, *objs))

    d_a = Department(name='A')
    d_b = Department(name='B')
    d_c = Department(name='C')
    _commit(d_a, d_b, d_c)

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

    _commit(*workers)

    work_commands = []
    for worker in workers:
        for i in xrange(random.randrange(1, 559)):
            quantity = random.randrange(1, 21)
            today = datetime.now().replace(hour=0, minute=0, second=0,
                                           microsecond=0)
            # last six month
            created = today - timedelta(random.randrange(1, 186))
            work_commands.append(WorkCommand(worker=worker, quantity=quantity,
                                             created=created))

    _commit(*work_commands)
