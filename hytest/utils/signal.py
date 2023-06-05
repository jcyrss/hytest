class Signal:
    _clients = []
    _curMethodName = None
    
    def register(self, client):
        if isinstance(client,list):
            self._clients += client
        else:
            self._clients.append(client)

    def _broadcast(self,*arg,**kargs):

        for logger in self._clients:
            method = getattr(logger,self._curMethodName,None)
            if method:
                method(*arg,**kargs)

    def __getattr__(self, attr):
        self._curMethodName = attr        
        return self._broadcast

signal = Signal()
