import os
import subprocess
from subprocess import PIPE, STDOUT
import json

class Slither:

    def run_slither(sol_file, output_file, option=''):
        proc = subprocess.run(f'slither --exclude-informational --exclude-optimization {" ".join(option)} {sol_file} --json {output_file}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
        # if 'slither: not found' in proc.stderr:
        if not os.path.exists(output_file):
            print(proc.stderr)
            return False
        return True
 


    def check_non_vulnerable(result_json_file):
        with open(result_json_file, 'r') as f:
            result_json = json.load(f)
        if not result_json['success']:
            return False, f'Execution of slither is failed. {contract}'

        if 'detectors' in result_json.keys():
            # result[detectors] exists -> vulnerable 
            return False, 'Detected vulnerability.'
        else:
            return True, ''


    def get_vul_list(result_json_file, original_result_json_file):
        with open(result_json_file, 'r') as f:
            result = json.load(f)

        if 'detectors' in result.keys():
            with open(original_result_json_file, 'r') as f:
                original_result = json.load(f)
            if not 'detectors' in reuslt.keys():
                return False, 'Vul exists in the path, but no vul is in the original.'

            if result['results']['detectors'] > original_result['results']['detectors']:
                return False, 'More vul in the patch than the original.'
        else:
            return True, ''

