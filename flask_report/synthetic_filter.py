# -*- coding: UTF-8 -*-


class SyntheticFilter(object):

    """
    SyntheticFilter is man-made filter, when some complex logic need to be
    implemented
    """

    @property
    def name(self):
        raise NotImplementedError('unimplemented')

    @property
    def operators(self):
        raise NotImplementedError('unimplemented')

    @property
    def type(self):
        raise NotImplementedError('unimplemented')

    @property
    def options(self):
        '''
        :return list: a list of pair, each pair contains the option's value and
            name, for example

            .. code-block:: python

                [
                    ('1', 'Tom'),
                    ('2', 'Jerry')
                ]
        '''
        raise NotImplementedError('unimplemented')

    def __call__(self, model_map, value, q):
        '''
        :param model_map: a map of model, ref to
            :py:attribute:`flask_report.FlaskReport.model_map`
        :param value: value of the filter
        :param q: query object
        :return: query object
        '''
        raise NotImplementedError('unimplemented')
