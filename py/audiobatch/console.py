import sys
import os

def print_event( event ):
    print( event.severity.upper() + ": " + event.message() )


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

