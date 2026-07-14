import json
import sys
import argparse
import traceback
import shutil
import re
import os
import pathlib
import subprocess
from subprocess import PIPE, STDOUT

from analyze import Slither
from aggregation import Aggregation

vul_mapping = {'access_control': ['tx-origin', 'controlled-delegatecall', 'suicidal'], # incorrect_constructor, mappin_write, wallet_0x検知できず, 
                'arithmetic': [], # Slither do not detect overflow/underflow.
                'bad_randomness': ['timestamp'], # blackjack検知できず
                'denial_of_service': [],
                'front_running': [], # No target contract
                'reentrancy': ['reentrancy-eth'],   #modifier_reentrancyのreentrancy-no-ethは修正後にも検知, reentrancy_bonus検知できず
                'time_manipulation': ['timestamp'],
                'unchecked_low_level_calls': ['unchecked-lowlevel', 'unchecked-send'],    # 0x52..のやつは他のところも変わってるけど，，-xa1f...は検知できず
                'other': ['uninitialized-storage']}
               # In this exp., 'other' is only 'uninitialized-storage'


def main(model_id, do_rag):
    repair_verif_data = {'repair_results':[]}
    extract_keys = ['filename', 'version', 'contract_name', 'original_vul_func']
    os.makedirs('output', exist_ok=True)
    
    # with open('../../results/target_solfile_list.json', 'r') as f:
    #    solfile_list_data = json.load(f)


    for category in os.listdir('../dataset/mitigate_patches'):
        if not os.path.isdir(f'../dataset/mitigate_patches/{category}'):
            continue


        vul_repair_list = []
        for contract in os.listdir(f'../dataset/mitigate_patches/{category}'):
            if not os.path.isdir(f'../dataset/mitigate_patches/{category}/{contract}'):
               continue

            print(f'\n=================================\n{category}/{contract}')


            # repair_results = {k: file_info[k] for k in extract_keys}
            with open(f'../dataset/mitigate_patches/{category}/{contract}/contract_info.json', 'r') as f:
                file_info = json.load(f)


            repair_results = file_info
            repair_results.update({'results':{'patch_results':[]}})

            # get_solc_version
            change_solc_version(file_info['version'])
            for i in range(0, 5):
                print('\noutput: ' + str(i))

                repair_results['results']['patch_results'].append(verify_results(category, contract, file_info, i, model_id, do_rag))

            print('... done\n\n----------')
            verif_key = ['format', 'compilable', 'non-vulnerable', 'no-add-vul', 'functionality']
            repair_results['results']['contract_results'] = {
                key: any(result[key] for result in repair_results['results']['patch_results'])
                for key in verif_key
            }

            vul_repair_list.append(repair_results)
        
        if len(vul_repair_list) > 0:
            repair_verif_data['repair_results'].append({'vul_type': category, 'repair_result_list': vul_repair_list})
        if os.path.exists(f'../results/{model_id}/{do_rag}/{category}/output'):
            shutil.rmtree(f'../results/{model_id}/{do_rag}/{category}/output')



    with open(f'../results/{model_id}/{do_rag}/repair_results.json', 'w') as f:
        json.dump(repair_verif_data, f, indent=2)

    os.makedirs(f'../results/{model_id}/{do_rag}/sum_data', exist_ok=True)
    Aggregation().sum_results(f'../results/{model_id}/{do_rag}/repair_results.json', model_id, do_rag)


def verify_results(vul, contract, fileinfo, output_count, model_id, do_rag):
    output_file_dir = f'../results/{model_id}/{do_rag}/{vul}/{contract}'
    output_file = f'{output_file_dir}/{contract}_{output_count}.sol'

    verify_funcs = [('format', verify_format, []),
                    ('compilable', verify_compilable, [output_file]),
                    # ('differential', verify_differential, []),
                    ('non-vulnerable', verify_vulnerability, [output_file, f'{output_file}_slither.json', vul_mapping[vul]]),
                    ('no-add-vul', verify_noaddvul, [f'{output_file}_slither.json', f'../dataset/mitigate_patches/{vul}/{contract}/output/{contract}.sol_slither.json', vul_mapping[vul]]),
                    ('functionality', verify_functionality, [vul, output_file_dir, f'{contract}_{output_count}.sol', fileinfo])]

    results = {'output_count': output_count}
    results.update({verify_type: False for verify_type, _, _ in verify_funcs})

    for verify_type, func, args in verify_funcs:
        verif_success, error_message = func(*args)
        if verif_success:
            results[verify_type] = True
        else:
            results[f'fail_{verify_type}_results'] = error_message
            return results

    return results


def verify_format():
#def verify_format(vul, fileinfo, output_file):
    # get output with json format

    '''
    try:
        with open(output_file, 'r') as f:
            patch = json.load(f)
            # corrected_codeの最後に改行があった場合はそれ以前で取得
            patch_func = patch['corrected_code'][:-1 if patch['corrected_code'][-1] == '\n' else len(patch['corrected_code'])]
    except json.decoder.JSONDecodeError as e:
        return False, f'Fail to load output as json.\tFile: {output_file}\n\t{str(e)}\n'
    except Exception as e:
        return False, f'Error with json decoder\tFile: {output_file}\n\t{str(e)}\n'

    with open(f'{output_file}_func.sol', 'w') as f:
        f.write(patch_func)

    with open(f'../../results/dataset/{vul}/{fileinfo["filename"]}', 'r') as f:
        source_code = f.read()
    with open(f'{output_file}_patched.sol', 'w') as f:
        f.write(source_code[:fileinfo[f'vul_func']['vulfunc_start']])
        f.write(patch_func)
        f.write(source_code[fileinfo[f'vul_func']['vulfunc_start']+fileinfo[f'vul_func']['vulfunc_length']:])
    '''

    return True, ''


def verify_compilable(patched_file):
    print('Verify: Compilability')
    proc = subprocess.run(f'solc {patched_file}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if len(re.findall(rf'{patched_file.split("/")[-1]}:[\d]+:[\d]+: Error: ', proc.stderr)) > 0:
        # Error message by solc: "'filename':line:column?: Error:" 
        return False, proc.stderr
    elif len(re.findall('Internal compiler error during compilation:', proc.stderr)) > 0:
        # Compiler internal error?
        return False, proc.stderr

    return True, ''


def verify_vulnerability(patched_file, output_file, target_vul):
    print('Verify: Vulnerability')
    Slither.run_slither(patched_file, output_file)
    return Slither.check_non_vulnerable(output_file, target_vul)


def verify_noaddvul(patch_detection_file, original_detection_file, exclude_vul):
    print('Verify: No Added Vulnerability')
    original_vul_count = Slither.check_nontargetvul_count(original_detection_file, exclude_vul)
    patch_vul_count = Slither.check_nontargetvul_count(patch_detection_file, exclude_vul)
    if patch_vul_count > original_vul_count:
        return False, 'More vul in the patch than the original.'
    else:
        return True, ''




def verify_functionality(vul, repair_results_dir, repair_solfile, fileinfo):
    print('Verify: Functionality')
    filename = fileinfo['filename']
    abs_file_path = pathlib.Path(repair_results_dir).resolve()
    tx_success, output_dir, error_message = runTx(f'{abs_file_path}/{repair_solfile}', f'{vul}/{filename}', fileinfo['main_contract'], f'{abs_file_path}/output')
    print('Finish evaluator')

    if not tx_success:
        print('Check evaluator environment.(ref: sb-heists/evaluator/README.md, sb-heists/smart-bugs-curated/0.4.x/README.md)')
        with open('output/verify_functionality_error.txt', 'a') as f:
            f.write(f'{vul}/{filename}: {error_message}\nCheck evaluator environment.(ref: sb-heists/evaluator/README.md, sb-heists/smart-bugs-curated/0.4.x/README.md)\n')

        return False, error_message
    else:
        with open(f'{output_dir}/test-results.json', 'r') as f:
            tx_results = json.load(f)

        if tx_results['failedFunctionalCheck']:
            # failed transactions
            # with open('output/verify_functionality_fail.txt', 'a') as f:
            #     f.write(f'{vul}/{filename}: \n')
            #     f.write(f'Function results:\n{tx_results["failedFunctionalCheckResults"]}\n')
            #     f.write(f'Exploit results:\n{tx_results["failedResults"]}\n')
            #     f.write('========================================\n')
            return False, f'Function results:\n{tx_results["failedFunctionalCheckResults"]}\n'
        else:
            return True, ''


def runTx(contract_file, base_contract, main_contractname, output_dir):
    # run evaluator of sb-heist @tx_verification/evaluator/
    current_dir = os.getcwd()
    os.chdir('../tools/sb-heists/evaluator')

    print('Exec sb-heists evaluator')
    # run sb-heists evaluator
    proc = subprocess.run(f'python3 src/main.py --format solidity --patch {contract_file} --contract-file {base_contract} --main-contract {main_contractname} --output {output_dir}', shell=True, stdout=PIPE, stderr=PIPE, text=True, timeout=600)
    if proc.stderr != '': 
        os.chdir(current_dir)
        return False, '', f'Proc Error: {proc.stderr}'

    # Results saved in output_dir/20251127_154645
    output_dir += f'/{proc.stdout.split("/")[-1][:-1]}'

    # check error
    with open(f'{output_dir}/hardhat_error.txt', 'r') as f:
        error_txt = f.read()
    if error_txt != 'WARNING: You are currently using Node.js v25.1.0, which is not supported by Hardhat. This can lead to unexpected behavior. See https://hardhat.org/nodejs-versions\n' and error_txt != '':
        os.chdir(current_dir)
        return False, output_dir, f'Hardhat Error: {error_txt}'

    os.chdir(current_dir)

    return True, output_dir, ''


def change_solc_version(version):
    proc = subprocess.run('solc-select use %s' % version, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if proc.stderr != '':
        print(version)
        print('ERROR: ' + proc.stderr)
        return False
    print('solc-select use >> ' + proc.stdout)
    return True


def argument_processing(args):
    model_list = {
        'gpt': ['gpt-5'],
        'codellama': ['codellama-7b', 'codellama-13b']
    }

    codellama_id = {
        'codellama-7b': 'CodeLlama-7b-Instruct-hf',
        'codellama-13b': 'CodeLlama-13b-Instruct-hf'
    }

    if args.model in model_list['gpt']:
        model_id = args.model
    elif args.model in model_list['codellama']: 
        model_id = codellama_id[args.model]
    else:
        raise 

    return model_id


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', choices=['gpt-5', 'codellama-7b', 'codellama-13b'], required=True, )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    try:
        args = get_args()
        model = argument_processing(args)
        main(model, 'rag')
        main(model, 'no_rag')
        Aggregation().combine_rag_norag_result(model)
    except Exception as e:
        print('An error has occured. Exit the program.\n')
        print('Traceback:')
        etype, value, tb = sys.exc_info()
        traceback.print_tb(tb)

        print(str(e))



