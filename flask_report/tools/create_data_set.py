#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from datetime import datetime

import yaml
from clint.textui import puts, prompt, validators


class NotNull(object):

    message = '%s can\'t be empty!'

    def __init__(self, name):
        self._name = name

    def __call__(self, value):

        if not value:
            raise validators.ValidationError(self.message % self._name)
        return value

if __name__ == '__main__':

    config_dir = prompt.query('please input the configuration directory: ',
                              validators=[NotNull('configuration directory')])
    name = prompt.query('please input the name of data set: ',
                        validators=[NotNull('data set\'s name')])
    description = prompt.query(
        '[optional]please input description of data set:')
    creator = prompt.query('[optional]please input your name: ')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    data_sets_dir = os.path.join(config_dir, 'data_sets')
    if not os.path.exists(data_sets_dir):
        os.makedirs(data_sets_dir)
    new_data_set_id = max([int(dir_) for dir_ in os.listdir(data_sets_dir) if
                           dir_.isdigit()] or [1])
    new_data_set_dir = os.path.join(data_sets_dir, str(new_data_set_id))
    os.mkdir(new_data_set_dir)
    meta_file = os.path.join(new_data_set_dir, 'meta.yaml')
    with file(meta_file, 'w') as f:
        yaml.safe_dump({
            'name': name,
            'description': description,
            'creator': creator,
            'created': str(datetime.now())
        }, allow_unicode=True, stream=f)

    puts('Congratulations! the data set meta file is created, '
         'please go on to edit ' + meta_file)
