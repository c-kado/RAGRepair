
# 修正パターンというか，脆弱性パターンがほぼ同じものがあったりする．
# それを弾いて試すかどうか考える．


import argparse
import os

from LLMInterface import GPT
import repair

def main(model, do_rag, inf_time):
    for category in os.listdir(f'../dataset/mitigate_patches'):
        if not os.path.isdir(f'../dataset/mitigate_patches/{category}'):
            continue

        for contract in os.listdir(f'../dataset/mitigate_patches/{category}'):
            if not os.path.isdir(f'../dataset/mitigate_patches/{category}/{contract}'):
               continue

            print(f'\n=================================\n{category}/{contract}')

            save_dir = f'../results/{model.model_id}/{'rag' if do_rag else 'no_rag'}/{category}/{contract}'
            os.makedirs(save_dir, exist_ok=True)

            for i in range(0, inf_time):
                print('\n----------------------\n')
                print('Inference Count: '+str(i))
                repair.repair(model, category, contract, save_dir, do_rag, i)

            sum_repair_info(save_dir, inf_time)


def sum_repair_info(save_dir, inf_time):
    results = []
    
    for i in range(0, inf_time):
        with open(f'{save_dir}/repair_info_{i}.json', 'r') as f:
            info = json.load(f)

        results.append({'output_count': i, 'exec_time': info['exec_time']})

    repair_info = {'model': info['model'], 'category': info['category'], 'contrat': info['contract'], 'rag_info': info['rag_info'], 'results': results}
    with open(f'{save_dir}/repair_info.json', 'w') as f:
        json.dump(repair_info, f, indent=2)
        



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['gpt-5', 'codellama-7b', 'codellama-13b', 'codet5p-770m', 'codet5p-2b', 'codet5p-6b'], required=True)
    parser.add_argument('--no-rag', action='store_false', dest='do_rag', help='Inference by non rag.')
    parser.add_argument('--inference-time', default=1, type=int)

    return parser.parse_args()

   
def argument_processing(args):
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


if __name__ == '__main__':
    args = parse_args() 
    model = argument_processing(args)
    main(model, args.do_rag, args.inference_time)
