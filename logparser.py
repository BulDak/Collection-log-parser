import os
from argparse import ArgumentParser

import logparser_Falcon
import logparser_FTKimager
import logparser_HancomRED

class logparser(object):
    def __init__(self):
        self.parser_falcon=logparser_Falcon.logparser_falcon()
        self.parser_ftkimager=logparser_FTKimager.logparser_ftkimager()
        self.parser_hancomred=logparser_HancomRED.logparser_HancomRED()

    def parsing(self, path):
        if self.parser_falcon.is_falconlog(path):
            return self.parser_falcon.parse_falconlog(path)
        elif self.parser_ftkimager.is_ftklog(path):
            return self.parser_ftkimager.parse_ftklog(path)
        elif self.parser_hancomred.is_hancomredlog(path):
            return self.parser_hancomred.parse_hancomredlog(path)
        return False

    def parsing_standardization(self, path):
        if self.parser_falcon.is_falconlog(path):
            return self.parser_falcon.parse_falconlog_standardization(path)
        elif self.parser_ftkimager.is_ftklog(path):
            return self.parser_ftkimager.parse_ftklog_standardization(path)
        elif self.parser_hancomred.is_hancomredlog(path):
            return self.parser_hancomred.parse_hancomredlog_standardization(path)
        return False


if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path', help='Path to parsing')
    parser.add_argument('-s', '--standardization', action='store_true', help='Get the parsing data with standardization format')
    args=parser.parse_args()

    log_path=args.input_path
    lp=logparser()

    parsing_func=lp.parsing
    if args.standardization:    parsing_func=lp.parsing_standardization
    if os.path.isfile(log_path):    print (parsing_func(log_path))
    elif os.path.isdir(log_path):   pass