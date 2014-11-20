# -*- coding: UTF-8 -*-
from sqlalchemy import func


def get_query(db, model_map):

    WorkCommand = model_map['WorkCommand']
    Worker = model_map['Worker']
    Department = model_map['Department']
    return db.session.query(Worker.id, Worker.name.label('name'),
                            Department,
                            Worker.age.label('age'),
                            func.sum(WorkCommand.quantity).label(
                                'performance')).group_by(
                                    WorkCommand.worker_id).join(WorkCommand)
