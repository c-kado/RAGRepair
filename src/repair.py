import argparse
import json
import os
import textwrap

from LLMInterface import GPT
import retriever


def get_prompt(category, contract):
    with open(f'../dataset/mitigate_patches/{category}/{contract}/{contract}.sol', 'r') as f:
        vul_code = f.read()

    augumented_prompt = f'Fix the {category} vulnerability in TARGET code. [TARGET]{vul_code}{retriever.retrieve(args.category, args.contract)}'
    system_prompt = textwrap.dedent("""
    You are an expert secure software engineer.
    Task: Fix vulnerability in TARGET.
    Reference: Use the repair pattern of VUL_EX and FIX_EX as guide.
    Output: Return only the fixed source code.
    """)[1:]

    with open('tmp/prompt.txt', 'w') as f:
        json.dump({'system_prompt': system_prompt, 'user_prompt': augumented_prompt}, f, indent=2)

    return system_prompt, augumented_prompt
   


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('category', choices=['access_control', 'arithmetic', 'bad_randomness', 'other', 'reentrancy', 'unchecked_low_level_calls'], help='specify the vulnerabilty category of a fix target contract', required=True)
    parser.add_argument('contract', help='specify the fix target contract', required=True)
    parser.add_argument('--model', choices=['gpt', 'gpt-5', 'codellama', 'codellama-7b', 'codellama-13b', 'codet5p-770m', 'codet5p-2b', 'codet5p-6b'], required=True)

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

    return model


def main(model, category, contract):
    
    sys_prmpt, usr_prmpt = get_prompt(category, contract)


    model.run_inference(sys_prmpt, usr_prmpt) 
    model.save_output('tmp/repair_output.txt')
    with open('tmp/repair_info.txt', 'w') as f:
        f.write(f'Model: {model.model_id}')
        f.write(f'Category: {category}')
        f.write(f'Contract: {contract}')
        f.write()


if __name__ == '__main__':
    args = parse_args()

    model = argument_processing(args)
    main(model, args.category, args.contract)

