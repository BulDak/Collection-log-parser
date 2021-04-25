import os
import sys
from argparse import ArgumentParser
from collections import defaultdict

class logparser_ftkimager(object):
    def __init__(self):
        self.path=None

    def is_ftklog(self, log_path :str):
        # Check the extension
        if os.path.splitext(log_path)[1].lower()!='.txt':  return False

        # Check the first line
        with open(log_path, encoding='utf-8') as fd:
            line=fd.readline().replace('®', '').strip()
            if 'Created By AccessData FTK Imager' not in line:
                return False
        return True

    def parse_ftklog(self, log_path :str):
        """
        :param path str: Path the log file
        :return dict: parsed data
        """

        if not self.is_ftklog(log_path): return False

        data=defaultdict(dict)
        
        section='input_information'
        with open(log_path, encoding='utf-8') as fd:
            while True:
                line=fd.readline()
                if line=='':    break
                if line.strip()=='':    continue

                if 'Created By AccessData' in line and 'FTK' in line and 'Imager' in line:
                    data[section]['collection_tool']='FTK Imager'
                    data[section]['collection_tool_version']=line.strip().split(' ')[-1]
                    continue

                if section in ('ATTENTION', 'Segment list', 'Image Verification Results'):
                    if section=='ATTENTION':
                        section_lines=line
                        while True:
                            line=fd.readline()
                            if line.strip()=='':    break
                            section_lines='{}{}'.format(section_lines, line)
                        data[section]=section_lines
                        section=None
                        continue

                    elif section=='Segment list':
                        data[section]=list()
                        while True:
                            line=fd.readline()
                            if line.strip()=='':    break
                            data[section].append(line.strip())
                        section=None
                        continue
                        
                    elif section=='Image Verification Results':
                        while True:
                            if line.strip()=='':    break
                            res = line.split(': ')
                            if len(res)==2:
                                key=res[0].strip()
                                value=res[1].strip()
                                data[section][key]=value
                            elif len(res)==3:
                                hash_type, hash_value, is_verified = line.split(': ')
                                hash_type=hash_type.strip()
                                hash_value=hash_value.strip()
                                is_verified=is_verified.strip()
                                data[section][hash_type]='{}:{}'.format(hash_value, is_verified)
                            line=fd.readline()
                        section=None
                        continue
                else:
                    try:
                        key, value=line.split(': ')
                        key=key.strip()
                        value=value.strip()
                        data[section][key]=value
                        continue
                    except: pass

                if line.strip()[0]=='[' and line.strip()[-1]==']':
                    section=line.strip()[1:-1]
                    continue
                if line.strip()[-1]==':':
                    section=line.strip()[:-1]
                    continue

        return data

if __name__=='__main__':
    # Argument parsing
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path')
    args=parser.parse_args()

    log_path=args.input_path
    parser=logparser_ftkimager()
    print (parser.get_ftklog(log_path))
