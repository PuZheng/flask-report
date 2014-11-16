# -*- coding: UTF-8 -*-
from sqlalchemy import func


def get_query(db, model_map):

    WorkCommand = model_map['WorkeCommand']
    Worker = model_map['Worker']
    return db.session.query(Worker.id, Worker.name.label('name'),
                            Worker.department.label('department'),
                            func.sum(WorkCommand.quantity).label(
                                'performance')).group_by(
                                    WorkCommand.worker_id).join(WorkCommand)
