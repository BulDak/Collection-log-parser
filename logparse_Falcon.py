import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
import pdfplumber

class logparser_falcon(object):
    def __init__(self):
        self.path=None
        self.section_names=['Operation Parameters', 'Hash Information','Verify Information', 'Case Information', 'Segment Information', 'Drive Information', 'Drive Capacities', 'Drive ATA Security Information', 'Drive Encryption Information', 'Source Partition Information']

    def is_falconlog(self, log_path :str):
        # check the extension
        if os.path.splitext(log_path)[1].lower()!='.pdf':  return False
        return True

    def parse_falconlog(self, log_path :str):
        """
        :param path str: Path the log file
        :return dict: parsed data
        """
        def get_keyvalue(line):
            try:
                key, value=line.split(':')
                return key.strip(), value.strip()
            except:
                pass

        if not self.is_falconlog(log_path): return False

        data=defaultdict(dict)
        
        section='input_information'
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

                elif section=='Drive Information':
                    pass

                elif section=='Drive Capacities':
                    pass

                elif section in ['Drive ATA Security Information', 'Drive Encryption Information']:
                    if pdf_line.replace(' ', '')=='BayRoleEnabledLocked': continue
                    bay, role, enabled, locked = pdf_line.split(' ')
                    data[section][bay]={'Role':role, 'Enabled':enabled, 'Locked':locked}

                elif section=='Source Partition Information':
                    pass


        return data

if __name__=='__main__':
    # Argument parsing
    parser=ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_path')
    args=parser.parse_args()

    log_path=args.input_path
    parser=logparser_falcon()
    print (parser.get_falconlog(log_path))
