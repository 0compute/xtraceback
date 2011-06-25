_missing = object()

class cachedproperty(property):

    def __init__(self, fget, *args, **kwargs):
        super(cachedproperty, self).__init__(fget, *args, **kwargs)
        self.__doc__ = fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, instance, cls):
        if instance is None:
            return self
        value = instance.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = instance.__dict__[self.__name__] = self.fget(instance)
        return value
