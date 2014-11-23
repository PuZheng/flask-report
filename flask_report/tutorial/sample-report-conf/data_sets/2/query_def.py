# -*- coding: UTF-8 -*-
from sqlalchemy import func


def get_query(db, model_map):
    '''
    :param db: data base instance
    :param model_map: a dict of which keys are model classes' name, values are
        model classes
    '''
    Department = model_map['Department']
    Worker = model_map['Worker']
    WorkCommand = model_map['WorkCommand']
    s_q = db.session.query(Worker.id, Worker.name,
                           func.sum(WorkCommand.quantity).label('performance'))\
        .group_by(WorkCommand.worker_id).join(WorkCommand).subquery('s_q')
    return db.session.query(Department.id, Department.name,
                            func.count(Worker.id).label('work no.'),
                            func.sum(s_q.c.performance).label('performance'))\
        .group_by(Worker.department_id).join(Worker)\
        .join(s_q, s_q.c.id == Worker.id)
