import os
from argparse import ArgumentParser
from re import A

import logparser_Falcon
import logparser_FTKimager
import logparser_HancomRED
import logparser_UFD

class logparser(object):
    def __init__(self):
        self.parser_falcon=logparser_Falcon.logparser_falcon()
        self.parser_ftkimager=logparser_FTKimager.logparser_ftkimager()
        self.parser_hancomred=logparser_HancomRED.logparser_HancomRED()
        self.parser_ufd=logparser_UFD.logparser_udf()

    def parsing(self, path):
        if self.parser_falcon.is_falconlog(path):
            return self.parser_falcon.parse_falconlog(path)
        elif self.parser_ftkimager.is_ftklog(path):
            return self.parser_ftkimager.parse_ftklog(path)
        elif self.parser_hancomred.is_hancomredlog(path):
            return self.parser_hancomred.parse_hancomredlog(path)
        elif self.parser_ufd.is_ufdlog(path):
            return self.parser_ufd.parse_ufdlog(path)
        return False

    def parsing_standardization(self, path):
        if self.parser_falcon.is_falconlog(path):
            return self.parser_falcon.parse_falconlog_standardization(path)
        elif self.parser_ftkimager.is_ftklog(path):
            return self.parser_ftkimager.parse_ftklog_standardization(path)
        elif self.parser_hancomred.is_hancomredlog(path):
            return self.parser_hancomred.parse_hancomredlog_standardization(path)
        elif self.parser_ufd.is_ufdlog(path):
            return self.parser_ufd.parse_ufdlog_standardization(path)
        return False


if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('input_path', help='Path to parsing')
    parser.add_argument('-s', '--standardization', action='store_true', help='Get the parsing data with standardization format')
    args=parser.parse_args()

    log_path=args.input_path
    lp=logparser()

    parsing_func=lp.parsing
    if args.standardization:    parsing_func=lp.parsing_standardization

    if os.path.isfile(log_path):    print (parsing_func(log_path))
    elif os.path.isdir(log_path):
        for parent_path, dirs, filenames in os.walk(log_path):
            for filename in filenames:
                try:
                    filepath=os.path.join(parent_path, filename)
                    res=parsing_func(filepath)
                    if res: print (res)
                except: pass