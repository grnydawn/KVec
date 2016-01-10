# kvec_order.py
# Pyro (https://pythonhosted.org/Pyro4/index.html)

import Pyro4

class KVOrder(object):
    CREATED, STARTED, COMPLETED = range(3)

    def __init__(self):
        self.status = self.CREATED

    def start(self):
        raise Exception('Subclass should implement start function')

class KVGetRefPerf(KVOrder):
    def __init__(self, filename, srclines, build_cmd):
        super(KVGetRefPerf, self).__init__()

        self.filename = filename
        self.srclines = srclines
        self.build_cmd = build_cmd

    def start(self):
        self.status = self.STARTED

    def tostr(self):
        if self.status==self.CREATED:
            return 'PLANNED: Reference perforamcne measurement order is taken.'
        elif self.status==self.STARTED:
            return 'PROGRESS: Reference perforamcne is being measured.'
        elif self.status==self.COMPLETED:
            return 'COMPLETED: Reference perforamcne is measured.'
        else:
            return 'Unknown status in KVGetRefPerf'

class KVBackEnd(object):
    orders = {}

    def create_order(self, order, filename, srclines, build_cmd):
        if order=='build':
            self.orders[order] = KVGetRefPerf(filename, srclines, build_cmd)
            self.orders[order].start()

    def get_order_status(self, order):
        return self.orders[order].tostr()

backend = KVBackEnd()

def main():
    daemon = Pyro4.Daemon()
    backend_uri = daemon.register(backend)
    ns = Pyro4.locateNS()
    ns.register("kvec.backend", backend_uri)
    daemon.requestLoop()

if __name__ == "__main__":
    main()
