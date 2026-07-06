import argparse
import json
import os
import textwrap

from LLMInterface import GPT
from retriever import Retriever


def get_prompt(category, contract_code, do_rag=True):
    rag_inst = 'Reference: Use the repair pattern of VUL_EX and FIX_EX as guide.\n' if do_rag else ''

    system_prompt = textwrap.dedent(f"""
    You are an expert secure software engineer.
    Task: Fix vulnerability in TARGET.
    {rag_inst}Output: Return only the fixed source code.
    """)[1:]
    user_prompt = f'Fix the {category} vulnerability in TARGET code. [TARGET]{contract_code}'

    return system_prompt, user_prompt 
   



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('category', choices=['access_control', 'arithmetic', 'bad_randomness', 'other', 'reentrancy', 'unchecked_low_level_calls'], help='specify the vulnerabilty category of a fix target contract')
    parser.add_argument('contract', help='specify the fix target contract')
    parser.add_argument('--model', choices=['gpt-5', 'codellama-7b', 'codellama-13b', 'codet5p-770m', 'codet5p-2b', 'codet5p-6b'], required=True)

    return parser.parse_args()


def argument_processing(args):

    if not os.path.exists(f'../dataset/mitigate_patches/{args.category}/{args.contract}'):
        print(f'"../dataset/mitigate_patches/{args.category}/{args.contract}" does not exist.')
        exit()

    model_list = {'gpt': ['gpt-5'],
                  'codellama': ['codellama-7b', 'codellama-13b'],
                  'codet5p': ['codet5p-770m', 'codet5p-2b', 'codet5p-6b']}
    if args.model in model_list['gpt']:
        with open('api_key.txt', 'r') as f:
            key = f.read()
        model = GPT(args.model, key)
    elif args.model in model_list['codellama']:
        model = CodeLlama(args.model)
        model.install_model()
    elif args.model in model_list['codet5p']:
        model = CodeT5p(args.model)
        model.install_model()
    else:
        raise 

    return model, args.category, args.contract


def repair(model, category, contract, save_dir='tmp', do_rag=True):
    with open(f'../dataset/mitigate_patches/{category}/{contract}/{contract}.sol', 'r') as f:
        vul_code = f.read()

    sys_prmpt, usr_prmpt = get_prompt(category, vul_code, do_rag)

    if do_rag:
        # do_rag == True -> augument prompt
        rtrv = Retriever()
        rtrv.retrieve(category, contract)
        usr_prmpt += rtrv.aug_prompt

    with open(f'{save_dir}/prompt.txt', 'w') as f:
        json.dump({'system_prompt': sys_prmpt, 'user_prompt': usr_prmpt}, f, indent=2)



    model.run_inference(sys_prmpt, usr_prmpt) 
    if not os.path.exists(save_dir):
       os.makedirs(save_dir) 
    model.save_output(f'{save_dir}/{contract}.sol')
    with open(f'{save_dir}/repair_info.txt', 'w') as f:
        f.write(f'Model: {model.model_id}\n')
        f.write(f'Category: {category}\n')
        f.write(f'Contract: {contract}\n')
        if do_rag:
            f.write(f'Nearest: {rtrv.nearest_contract['contract']}\n')
            f.write(f'Nearest Similarity: {rtrv.nearest_sim}\n')


if __name__ == '__main__':
    repair(*argument_processing(parse_args()))

