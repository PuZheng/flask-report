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
        raise NotImplementedError('unimplemented')

    def __call__(self, value):
        raise NotImplementedError('unimplemented')
