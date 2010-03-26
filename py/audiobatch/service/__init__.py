class ServiceEvent( object ):
    INFO = "info"
    ERROR = "error"

    def __init__( self, severity ):
        self.severity = severity

    def is_info( self ):
        return self._serverity == INFO

    def is_error( self ):
        return self._serverity == ERROR

    def message( self ):
        raise NotImplementedError

def default_event_listener():
    from audiobatch import console
    return console.print_event


