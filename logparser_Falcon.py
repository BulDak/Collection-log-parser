import os
from re import I
import sys
import datetime
from argparse import ArgumentParser
from collections import defaultdict
import pdfplumber

class logparser_falcon(object):
    def __init__(self):
        self.section_names=['Operation Parameters', 'Hash Information','Verify Information', 'Case Information', 'Segment Information', 'Drive Information', 'Drive Capacities', 'Drive ATA Security Information', 'Drive Encryption Information', 'Source Partition Information']

    def is_falconlog(self, log_path :str):
        # check the extension
        if os.path.splitext(log_path)[1].lower()!='.pdf':  return False
        return True

    def parse_falconlog(self, log_path :str):
        """
        :param log_path str: Path the log file
        :return dict: parsed data
        """
        def get_keyvalue(line):
            try:
                key=line.split(':')[0].strip()
                value=line[len(key)+1:].strip()
                return key, value
            except:
                pass

        if not self.is_falconlog(log_path): return False

        data=defaultdict(dict)
        
        section=None
        with pdfplumber.open(log_path) as fd:
            pdf_lines=list()
            for page in fd.pages:
                pdf_lines=pdf_lines+[line.replace('\t', ' ') for line in page.extract_text().split('\n')]

            def get_line(lines):
                for line in lines:
                    yield line

            section='basic_information'

            line=get_line(pdf_lines)
            while True:
                try:    pdf_line=next(line)
                except: break
                if pdf_line is False:    break
                if pdf_line in (self.section_names):
                    section=pdf_line
                    continue

                if section in ['basic_information', 'Operation Parameters', 'Hash Information', 'Case Information']:
                    try:
                        key, value=get_keyvalue(pdf_line)
                        data[section][key]=value
                    except:
                        pass

                elif section=='Verify Information':
                    if pdf_line.startswith('Drive'):
                        drive=pdf_line
                        data[section][drive]=dict()
                        while True:
                            key, value=get_keyvalue(next(line))
                            data[section][drive][key]=value
                            if key=='Result':
                                break

                elif section=='Segment Information':
                    if section not in data.keys():
                        data[section]=list()
                    try:
                        key, value=get_keyvalue(pdf_line)
                        if key=='UID':
                            data[section].append({'info':{key:value}})
                        elif key in ['Path', 'Filesystem', 'Serial']:
                            data[section][-1]['info'][key]=value
                        elif key=='File Name':
                            filename=value
                            data[section][-1][filename]=dict()
                            for i in range(3):
                                key, value=get_keyvalue(next(line))
                                data[section][-1][filename][key]=value
                    except:
                        pass

                elif section=='Drive Information':  pass
                elif section=='Drive Capacities':   pass

                elif section in ['Drive ATA Security Information', 'Drive Encryption Information']:
                    if pdf_line.replace(' ', '')=='BayRoleEnabledLocked': continue
                    bay, role, enabled, locked = pdf_line.split(' ')
                    data[section][bay]={'Role':role, 'Enabled':enabled, 'Locked':locked}

                elif section=='Source Partition Information':
                    pass
        return data

    def parse_falconlog_standardization(self, log_path):
        data=self.parse_falconlog(log_path)

        ret=dict()
        ret['case']=data['Case Information']['Case ID']
        ret['data_name']=data['Case Information']['Evidence ID']
        if data['Method']=='E01Capture':
            ret['collection_result_type']='E01'
        ret['hash']="{}:{}".format(data['Hash Information']['Hash Type'], data['Hash Information']['Source Hash'].upper())
        ret['Source_Serialnumber']=''
        ret['timezone_time']=data['basic_information']['Time (Local)'].split(' ')[2][:-1]

        start_date=datetime.datetime.strptime('{date}'.format(date=data['basic_information']['Date']), '%b %d, %Y')
        start_time=datetime.datetime.strptime('{time}'.format(time=data['basic_information']['Time (Local)'].split(' ')[0]), '%H:%M:%S')
        ret['collection_start_datetime']=start_date+datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second, microseconds=start_time.microsecond)

        start_date=ret['collection_start_datetime']
        duration_time=start_time=datetime.datetime.strptime('{time}'.format(time=data['Operation Parameters']['Duration']), '%H:%M:%S')
        ret['collection_complete_datetime']=start_date+datetime.timedelta(hours=duration_time.hour, minutes=duration_time.minute, seconds=duration_time.second, microseconds=duration_time.microsecond)

        ret['collection_tool']=data['basic_information']['Product']
        ret['collection_tool_version']=data['basic_information']['Software Version']

        return ret


if __name__=='__main__':
    # Argument parsing
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path', help='Path to parsing')
    parser.add_argument('-s', '--standardization', action='store_true', help='Get the parsing data with standardization format')
    args=parser.parse_args()

    log_path=args.input_path
    parser=logparser_falcon()
    
    if args.standardization:    print (parser.parse_falconlog_standardization(log_path))
    else:    print (parser.parse_falconlog(log_path))