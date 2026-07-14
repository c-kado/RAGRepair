import os
import subprocess
from subprocess import PIPE, STDOUT
import json

class Slither:

    def run_slither(sol_file, output_file, option=''):
        if os.path.exists(output_file):
            os.remove(output_file)
        proc = subprocess.run(f'slither --exclude-informational --exclude-optimization {" ".join(option)} {sol_file} --json {output_file}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
        # if 'slither: not found' in proc.stderr:
        if not os.path.exists(output_file):
            print(proc.stderr)
            return False
        return True
 


    def check_non_vulnerable(result_json_file, target_vul):
        with open(result_json_file, 'r') as f:
            result_json = json.load(f)

        if not result_json['success']:
            return False, f'Execution of slither is failed.'

        if not result_json['results']:
            # result_json['results'] == {}
            # result_json['results'] is empty -> non-vulnerable
            # There is any vulnerabilities
            return True, ''

        for detector in result_json['results']['detectors']:
            if detector['check'] in target_vul:
                return False, 'Detected vulnerability.'

        # There is any target vulnerabilities
        return True, ''


    '''
    def check_nontargetvul_count(result_json_file, original_result_json_file, nontarget_vul):
        with open(result_json_file, 'r') as f:
            result = json.load(f)

        if not result_json['results']:
            return True, ''
        else:
            # fixed code have some vulnerabilities
            with open(original_result_json_file, 'r') as f:
                original_result = json.load(f)
            if not 'detectors' in reuslt.keys():
                # code before being fixed doesn't have a vulnerability
                return False, 'Vul exists in the patch, but no vul is in the original.'


            # code before being fixed has some vulnerabilities
            if result['results']['detectors'] > original_result['results']['detectors']:
                return False, 'More vul in the patch than the original.'
    '''



    def check_nontargetvul_count(result_json_file, target_vul):
        with open(result_json_file, 'r') as f:
            result_json = json.load(f)

        if not result_json['results']:
            return 0
        
        count = 0
        for detector in result_json['results']['detectors']:
            if not detector['check'] in target_vul:
                count += 1

        return count
