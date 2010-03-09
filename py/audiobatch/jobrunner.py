#!/usr/bin/env python
import os
import sys
import logging
import optparse
import ConfigParser

from audiobatch.meta.convert import BasicMetaConverter
from audiobatch.stream.convert import ShellStreamConverter
from audiobatch import actions

_LOGGER = logging.getLogger()

_LIST_SEP = ';'

def _build_cmd_line_parser():
    parser = optparse.OptionParser()

    parser.add_option("-f",
                      "--no-confirmation",
                      action="store_true", 
                      dest="force_confirm",
                      default=False,
                      help=
"""Supplying this option avoids confirmation or any user input and is
useful for automated runs.  By default, console input is required to
confirm tasks before execution.  """ )

    return parser


def _determine_config_file_abs():
    # For now, the config file must be located in a specific directory
    # under the users home path
    home_path = os.path.expanduser('~')
    return os.path.join(home_path, '.audiobatch/audiobatch.ini')

def _parse_config( conf_file_abs ):

    def _parse_job( conf_parser, job_name ):

        #
        # required config params
        #

        source_dir = conf_parser.get( job_name, "source_dir" )
        target_dir = conf_parser.get( job_name, "target_dir" )
        audio_extensions = \
            conf_parser.get( job_name, "audio_extensions" ).split( _LIST_SEP )
        # strip whitespace and remove duplicates
        audio_extensions = set( [ x.strip() for x in audio_extensions ] )

        #
        # optional config params -- check for existence
        #

        if conf_parser.has_option( job_name, "convert_condition" ):
            convert_condition = conf_parser.get( job_name, "convert_condition" )
        else:
            convert_condition = None

        if conf_parser.has_option( job_name, "copy_condition" ):
            copy_condition = conf_parser.get( job_name, "copy_condition" )
        else:
            copy_condition = None

        if conf_parser.has_option( job_name, "exclude_patterns" ):
            exclude_patterns = \
                conf_parser.get( job_name,
                                 "exclude_patterns" ).split( _LIST_SEP )
            # strip whitespace and remove duplicates
            exclude_patterns = set( [ x.strip() for x in exclude_patterns ] )
        else:
            exclude_patterns = set()

        if conf_parser.has_option( job_name, "delete_matchless_target_files" ):
            is_delete_enabled = \
                conf_parser.getboolean( job_name,
                                        "delete_matchless_target_files" )
        else:
            is_delete_enabled = False

        job_config = _Config.JobConfig( source_dir,
                                        target_dir,
                                        audio_extensions,
                                        exclude_patterns,
                                        convert_condition,
                                        copy_condition,
                                        is_delete_enabled )
        return job_config

    conf_parser = ConfigParser.ConfigParser()
    conf_parser.read( conf_file_abs )

    log_file_abs = conf_parser.get( "system", "log_file" )
    default_decoder_seq = conf_parser.get( "default_decoder", "command_seq" )
    default_encoder_seq = conf_parser.get( "default_encoder", "command_seq" )
    decoders_by_extension = {}
    if conf_parser.has_section( "decoders_by_extension" ):
        for extension, cmd_seq in conf_parser.items("decoders_by_extension"):
            decoders_by_extension[ extension ] = cmd_seq

    config = _Config( log_file_abs,
                      default_decoder_seq,
                      default_encoder_seq,
                      decoders_by_extension )


    job_names = conf_parser.options( "jobs" )
    for job_name in job_names:
        config.job_configs[job_name] = _parse_job( conf_parser, job_name )

    return config

        
def _setup_logging( log_file_abs, is_verbose ):

    log_file_abs = os.path.expanduser( log_file_abs )
    logging.getLogger().setLevel( logging.DEBUG )

    file_handler = logging.FileHandler( filename = log_file_abs, mode = 'a')
    # We'll always send full debug logging (which really isn't _that_ much)
    # to the file, and only info level to the console unless verbse is
    # requested
    file_handler.setLevel( logging.DEBUG )
    log_file_format = "[%(asctime)s, %(levelname)-8s]: %(message)s"
    formatter = logging.Formatter( fmt=log_file_format,
                                   datefmt="%m-%d %H:%M" )
    file_handler.setFormatter( formatter )
    logging.getLogger().addHandler( file_handler )

    # We use a logger to handle console output
    console = logging.StreamHandler( sys.stdout )
    if is_verbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter("[%(levelname)-8s]: %(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger().addHandler(console)

    if not is_verbose:
        _LOGGER.info( "For verbose/debug output use '-b' or see log file: "
                      + log_file_abs )


class _Config:
    def __init__( self,
                  log_file_abs,
                  default_decoder,
                  default_encoder,
                  decoders_by_extension ):
        self.job_configs = {}
        self.log_file_abs = log_file_abs
        self.default_decoder_seq = default_decoder
        self.default_encoder_seq = default_encoder
        self.decoders_by_extension = decoders_by_extension

    def __str__( self ):
        str_rep = 'log file: %s\n' % self.log_file_abs
        str_rep += 'default decoder sequence: %s\n' % self.default_decoder_seq
        str_rep += 'default encoder sequence: %s\n' % self.default_encoder_seq
        for ext, seq in self.decoders_by_extension.items():            
            str_rep += '%s decoder sequence: %s\n' % (ext, seq)
        str_rep += 'jobs:\n'
        for job_name, job_config in self.job_configs.items():
            str_rep += "  %s:\n" % job_name
            str_rep += "    source: %s\n" \
                % job_config.source_dir_abs
            str_rep += "    target: %s\n" \
                % job_config.target_dir_abs
            str_rep += "    audio extensions: %s\n" \
                % job_config.audio_extensions
            str_rep += "    excluded patterns: %s\n" \
                % job_config.exclude_patterns
            str_rep += "    convert condition: %s\n" \
                % job_config.convert_condition
            str_rep += "    copy condition: %s\n" \
                % job_config.copy_condition
            str_rep += "    delete matchless target files: %s" \
                % str(job_config.is_delete_enabled)
        return str_rep
        
    class JobConfig:        
        def __init__( self,
                      source_dir_abs,
                      target_dir_abs,
                      audio_extensions,
                      exclude_patterns,
                      convert_condition,
                      copy_condition,
                      is_delete_enabled ):
            self.source_dir_abs = source_dir_abs
            self.target_dir_abs = target_dir_abs
            self.audio_extensions = audio_extensions
            self.exclude_patterns = exclude_patterns
            self.convert_condition = convert_condition
            self.copy_condition = copy_condition
            self.is_delete_enabled = is_delete_enabled


def _is_work_to_be_done( copy_list,
                         convert_list,
                         delete_list,
                         is_delete_enabled ):
    if not is_delete_enabled:
        delete_list = []

    if len(copy_list) + len(convert_list) + len(delete_list) > 0:
        return True
    else:
        return False

def _is_continue_confirmed( force_confirm ):
    if force_confirm:
        return True
    else:
        print( "Continue with identified tasks?" )
        is_confirmed = raw_input( "['y' to continue] > " ) == 'y'
        return is_confirmed

def _process_job( job_config,
                 default_decode_seq,
                 default_encode_seq,
                 decoders_by_extension,
                 force_confirm ):
    _LOGGER.info( "indexing source paths..." )
    source_paths = actions.find_paths( job_config.source_dir_abs,
                                       job_config.audio_extensions,
                                       job_config.exclude_patterns )
    source_paths = sorted( source_paths )

    _LOGGER.info( "indexing target paths..." )
    target_paths = actions.find_paths( job_config.target_dir_abs,
                                       job_config.audio_extensions,
                                       job_config.exclude_patterns )
    target_paths = sorted( target_paths )

    _LOGGER.info( "diffing source and target paths..." )
    new_sources, updated_sources, matchless_targets = \
        actions.extension_ignorant_diff( source_paths,
                                         target_paths,
                                         job_config.source_dir_abs,
                                         job_config.target_dir_abs )

    _LOGGER.info( "%4d sources not found in target directory" \
                      % len( new_sources ) )
    _LOGGER.info( "%4d sources changed since corresponding target created" \
                      % len( updated_sources ) )

    # We process adds and replaces the same way -- replaces just end
    # up leading to overwriting an existing file
    source_changes = []
    source_changes.extend( new_sources )
    source_changes.extend( updated_sources )

    if job_config.convert_condition != None:
        conversion_enabled = True
        paths_to_convert, paths_remaining = \
            actions.filter_audio_files( source_changes,
                                        job_config.source_dir_abs,
                                        job_config.convert_condition )
        _LOGGER.info( "%4d conversions to be done" % len( paths_to_convert ) )
    else:
        conversion_enabled = False
        _LOGGER.info( "Converting disabled; no condition set for selecting " +
                      "files to be converted" )

    if job_config.copy_condition != None:
        copy_enabled = True
        paths_to_copy, _ = \
            actions.filter_audio_files( paths_remaining,
                                        job_config.source_dir_abs,
                                        job_config.copy_condition )
        _LOGGER.info( "%4d copies to be done" % len( paths_to_copy ) )
    else: 
        copy_enabled = False
        _LOGGER.info( "Copying disabled; no condition set for selecting " +
                      "files to be copied" )
       
    if job_config.is_delete_enabled:
        _LOGGER.info( "%4d matchless target files to be deleted" \
                          % len( matchless_targets ) )

    if _is_work_to_be_done( paths_to_copy,
                            paths_to_convert,
                            matchless_targets ,
                            job_config.is_delete_enabled ):
        if _is_continue_confirmed( force_confirm ):

            # Copies are faster, so let's get them out of the way first
            if copy_enabled:
                actions.copy_paths( job_config.source_dir_abs,
                                   paths_to_copy,
                                   job_config.target_dir_abs )

            if conversion_enabled:
                stream_converter = ShellStreamConverter( default_decode_seq,
                                                         default_encode_seq,
                                                         decoders_by_extension )
                meta_converter = \
                    BasicMetaConverter( embed_folder_images = True)
                for source_rel, stream_error, meta_error in \
                        actions.convert_paths( job_config.source_dir_abs,
                                               paths_to_convert,
                                               job_config.target_dir_abs,
                                               stream_converter,
                                               meta_converter ):
                    if stream_error != None:
                        _LOGGER.error( "Problem converting stream for %s: %s" \
                                           % (source_rel, stream_error) )
                    if meta_error != None:
                        _LOGGER.error( "Problem converting metadata for %s: %s"\
                                           % (source_rel, meta_error) )

            if job_config.is_delete_enabled:
                actions.delete_paths( job_config.target_dir_abs,
                                      matchless_targets )
    else:
        _LOGGER.info( "There is nothing to do for this job." )


def main(args):    
    cmd_line_parser = _build_cmd_line_parser()
    cmd_line_options, _ = cmd_line_parser.parse_args(args[1:])

    conf_file_abs = _determine_config_file_abs()
    config = _parse_config( conf_file_abs )
    _setup_logging( config.log_file_abs, is_verbose = True )
    _LOGGER.info( "Config:\n%s" % config)

    for job_name, job_config in config.job_configs.items():
        _LOGGER.info( "Processing job: %s" % job_name )
        _process_job( job_config,
                     config.default_decoder_seq,
                     config.default_encoder_seq,
                     config.decoders_by_extension,
                     cmd_line_options.force_confirm)


if __name__ == "__main__":
    main(sys.argv)
