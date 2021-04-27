import os
from re import I
import sys
import datetime
from argparse import ArgumentParser
from collections import defaultdict
import configparser

class logparser_udf(object):
    def is_ufdlog(self, log_path :str):
        # check the extension
        if os.path.splitext(log_path)[1].lower()!='.ufd':  return False
        return True

    def parse_ufdlog(self, log_path :str):
        """
        :param log_path str: Path the log file
        :return dict: parsed data
        """
        if not self.is_ufdlog(log_path): return False

        data=defaultdict(dict)
        
        section=None
        config=configparser.ConfigParser()
        config.read(log_path, encoding='utf-8-sig')
        for section in config.sections():
            data[section]=dict()
            for key, value in config[section].items():
                data[section][key]=value
        return data

    def parse_ufdlog_standardization(self, log_path):
        data=self.parse_ufdlog(log_path)

        ret=dict()
        ret['case']=''
        ret['data_name']=''
        ret['collection_result_type']='{}:{}'.format(data['General']['extractiontype'], data['General']['device'])
        ret['hash']="{}:{}".format('HMAC', data['Hash']['hmac'])
        ret['Source_Serialnumber']=''
        ret['timezone_time']=''

        ret['collection_start_datetime']=datetime.datetime.strptime(data['General']['date'], '%d-%m-%Y %H:%M:%S')
        ret['collection_complate_datetime']=datetime.datetime.strptime(data['General']['endtime'], '%d-%m-%Y %H:%M:%S')

        ret['collection_tool']=''
        ret['collection_tool_version']=data['General']['extractionsoftwareversion']

        return ret


if __name__=='__main__':
    # Argument parsing
    parser=ArgumentParser()
    parser.add_argument('input_path', help='Path to parsing')
    parser.add_argument('-s', '--standardization', action='store_true', help='Get the parsing data with standardization format')
    args=parser.parse_args()

    log_path=args.input_path
    parser=logparser_udf()
    
    if args.standardization:    print (parser.parse_ufdlog_standardization(log_path))
    else:    print (parser.parse_ufdlog(log_path))