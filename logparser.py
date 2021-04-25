import os
from argparse import ArgumentParser

import logparser_Falcon
import logparser_FTKimager

class logparser(object):
    def __init__(self):
        self.parser_falcon=logparser_Falcon.logparser_falcon()
        self.parser_ftkimager=logparser_FTKimager.logparser_ftkimager()
    def parsing(self, path):
        if self.parser_falcon.is_falconlog(path):
            return self.parser_falcon.parse_falconlog(path)
        elif self.parser_ftkimager.is_ftklog(path):
            return self.parser_ftkimager.parse_ftklog(path)
        return False

if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path')
    args=parser.parse_args()

    log_path=args.input_path
    lp=logparser()
    if os.path.isfile(log_path):
        print (lp.parsing(log_path))
    elif os.path.isdir(log_path):
        pass