import sys
import os
import logging

from audiobatch.service import ServiceEvent

_LOGGER = logging.getLogger()
_event_to_log_lvl = { ServiceEvent.INFO : logging.INFO,
                      ServiceEvent.ERROR : logging.DEBUG }




def log_event( event ):
    _LOGGER.log( _event_to_log_lvl[ event.severity ], event.get_message() )


def prompt( prompt = None, options = None, pre_prompt = None ):

    """
    Prompt to stdout and readln from stdin

    Format of prompt:
      <pre_prompt>
      <prompt> [ opt1, opt2, ..., optn ] > 

    If options are specified, the prompt is repeated until the input
    matches one of the options (not case sensitive).
    """

    while True:
        response = _do_prompt( prompt, options, pre_prompt )
        if options == None or response.lower() in options:
            break
        sys.stdout.write( "Try again:" + os.linesep )
    return response


def _do_prompt( prompt, options, pre_prompt ):
    # In py 2.6, under at least some system configs, raw_input() uses stderr
    # which is not the behavior we want.  It is simple enough to just use
    # stdout directly.

    if pre_prompt != None:
        sys.stdout.write( pre_prompt + os.linesep )
    if prompt != None:
        sys.stdout.write( prompt + " " )
    if options != None:
        sys.stdout.write( "[%s] " % ", ".join(options) )
    sys.stdout.write( "> " )

    input = sys.stdin.readline().rstrip( os.linesep )
    return input


def _setup_logging():
    logging.getLogger().setLevel( logging.DEBUG )


def _setup_console_logging():
    # DEBUG messages will go to stderr and INFO will go to stdout.  This
    # allows debug or diagnostic information to be redirected to a secondary
    # location, e.g. another terminal or file, while keeping primary
    # info in the main terminal.

    formatter = logging.Formatter("[%(levelname)-8s]: %(message)s")

    # For not we will not differentiate between debug and diagnostic
    # information.  An example of diagnostic information is the exact
    # shell command used to convert an audio stream or the progress
    # output by that shell command 
    diagnostic = logging.StreamHandler( sys.stderr )
    diagnostic.setFormatter(formatter)
    diagnostic.setLevel( logging.DEBUG )
    diag_filter = logging.Filter()
    # we _want _only_ debug to go to stderr, not higher level messages, which
    # will go to stdout
    diag_filter.filter = lambda record: record.levelno == logging.DEBUG
    diagnostic.addFilter( diag_filter )
    logging.getLogger().addHandler( diagnostic )

    # Now we setup up the logger for primary info, e.g. status updates
    # for a batch conversion process.
    primary = logging.StreamHandler( sys.stdout )
    primary.setFormatter(formatter)
    primary.setLevel( logging.INFO )
    logging.getLogger().addHandler( primary )


_setup_logging()
_setup_console_logging()

