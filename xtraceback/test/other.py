

class Other(object):

    def one(self, long):
        number = 1
        result = number * 10
        self.b(number, long)

    def b(self, number, long):
        self.c("arg1", "arg2", a_kw_arg=1)

    def c(self, *args, **kwargs):
        self.d()

    def d(self):
        self.e()

    def e(self):
        raise Exception("exc")
