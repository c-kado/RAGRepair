import subprocess
from subprocess import PIPE, STDOUT
import json

class Slither:

    def run_slither(contract, output_json, option):
        opt_str = ' '.join(option)
        proc = subprocess.run(f'slither {opt_str} {contract} --json {output_json}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
        if 'slither: not found' in proc.stderr:
             raise Exception(f'{proc.stderr}')
        return


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



