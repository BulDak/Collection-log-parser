import os
import sys
import datetime
from argparse import ArgumentParser
from collections import defaultdict
import pdfplumber

class logparser_HancomRED(object):
    def is_hancomredlog(self, log_path :str):
        # Check the extension
        if os.path.splitext(log_path)[1].lower()!='.pdf':  return False

        # Check the first line
        with pdfplumber.open(log_path, encoding='utf-8') as fd:
            line=fd.readline().strip()
            if 'HancomWITH' not in line:
                return False
        return True

    def parse_hancomredlog(self, log_path :str):
        """
        :param log_path str: Path the log file
        :return dict: parsed data
        """
        section_names=['획득 정보', '획득 목록']
        item_name=['모델', '획득 방법', '획득 시간', '기기 시간대', '프로그램 버전', '사건 번호', '소속', '담당자', '경로', '파일 크기', '획득 데이터 크기', 'MD5']
        ignore_name=['항목 내용', 'LOGICAL', '경로']

        if not self.is_hancomredlog(log_path): return False

        data=defaultdict(dict)
        
        section='input_information'
        with pdfplumber.open(log_path, encoding='utf-8') as fd:
            for page in fd.pages:
                text=page.extract_text()

                for line in text.plite('\n'):
                    line=line.strip()

                    if line in section_names:
                        section=line
                        data[section]=dict()
                        continue
                    elif line in ignore_name:   continue
                    elif len(data.keys())==0:   continue

                    key=str
                    for key in item_name:
                        if key==line[:len(key)]:
                            value=line[len(key)+1:]
                            data[section][key]=value
                            break
                    if section=='획득 목록' and key not in data[section].keys():
                        if '경로' not in data['획득 목록'].keys():
                            data[section]['경로']=''
                        data[section]['경로']=data[section]['경로']+line
        data['collection_tool']='HancomRED'
        return data

    def parse_hancomredlog_standardization(self, log_path):
        data=self.parse_ftklog(log_path)

        ret=dict()
        ret['case']=''
        ret['data_name']=data['Evidence Number']
        ret['collection_result_type']=''
        ret['hash']="{}:{}".format("MD5", data['MD5 checksum'].upper())
        ret['Source_Serialnumber']=data['Drive Serial Number']
        ret['timezone_time']=None

        ret['collection_start_datetime']=datetime.datetime.strptime('{date}'.format(date=data['Acquisition started']), '%a %b %d %H:%M:%S %Y')

        if data['Verification finished']:  ret['collection_complete_datetime']=datetime.datetime.strptime(data['Verification finished'], '%a %b %d %H:%M:%S %Y')
        else:   ret['collection_complete_datetime']=datetime.datetime.strptime(data['Acquisition finished'], '%a %b %d %H:%M:%S %Y')

        ret['collection_tool']=data['collection_tool']
        ret['collection_tool_version']=data['Software Version']
        return ret


if __name__=='__main__':
    # Argument parsing
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path', help='Path to parsing')
    parser.add_argument('-s', '--standardization', action='store_true', help='Get the parsing data with standardization format')
    args=parser.parse_args()

    log_path=args.input_path
    parser=logparser_HancomRED()
    
    if args.standardization:    print (parser.parse_hancomredlog_standardization(log_path))
    else:    print (parser.parse_hancomredlog(log_path))

