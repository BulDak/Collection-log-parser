import os
import sys
import datetime
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
        
        section='basic_information'
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
                            line=line.strip()
                            if line=='':    break
                            data[section].append(line)
                            line=fd.readline()
                        if data[section][0].endswith('E01'):
                            data['collection_result_type']='E01'
                        section=None
                        continue
                        
                    elif section=='Image Verification Results':
                        while True:
                            if line.strip()=='':    break
                            res=line.split(': ')
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

    def parse_ftklog_standardization(self, log_path):
        data=self.parse_ftklog(log_path)

        ret=dict()
        ret['case']=''
        ret['data_name']=data['basic_information']['Evidence Number']
        ret['collection_result_type']=data['collection_result_type']
        ret['hash']='{}:{}'.format('MD5', data['Image Verification Results']['MD5 checksum'].upper())
        ret['Source_Serialnumber']=data['Drive Serial Number']
        ret['timezone_time']=None

        ret['collection_start_datetime']=datetime.datetime.strptime('{date}'.format(date=data['Image Information']['Acquisition started']), '%a %b %d %H:%M:%S %Y')

        if data['Verification finished']:  ret['collection_complete_datetime']=datetime.datetime.strptime(data['Verification finished'], '%a %b %d %H:%M:%S %Y')
        else:   ret['collection_complete_datetime']=datetime.datetime.strptime(data['Image Information']['Acquisition finished'], '%a %b %d %H:%M:%S %Y')

        ret['collection_tool']=data['basic_information']['collection_tool']
        ret['collection_tool_version']=data['basic_information']['collection_tool_version']
        return ret


if __name__=='__main__':
    # Argument parsing
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path', help='Path to parsing')
    parser.add_argument('-s', '--standardization', action='store_true', help='Get the parsing data with standardization format')
    args=parser.parse_args()

    log_path=args.input_path
    parser=logparser_ftkimager()

    if args.standardization:    print (parser.parse_ftklog_standardization(log_path))
    else:    print (parser.parse_ftklog(log_path))