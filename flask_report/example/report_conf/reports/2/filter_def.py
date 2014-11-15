# -*- coding: UTF-8 -*-


def get_filter(db, table_map):
    Group = table_map['TB_GROUP']
    return Group.name == u'蜀'
