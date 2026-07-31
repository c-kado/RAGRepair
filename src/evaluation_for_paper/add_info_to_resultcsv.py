import json
import re

def main(model_id, do_rag):
    with open(f'../../results/{model_id}/{do_rag}/repair_results.json', 'r') as f:
        repair_data = json.load(f)


    for i, category_result in enumerate(repair_data['repair_results']):
        category = category_result['vul_type']
        for j, contract_result in enumerate(category_result['repair_result_list']):
            contract = contract_result['filename']
            with open(f'../../dataset/mitigate_patches/{category}/{contract[:-4]}/{contract}') as f:
                code = remove_comment(f.read())

            # 空白削除
            code = [re.sub(r"\s+", "", line) for line in code.splitlines()]
            # 空行削除
            code = [line for line in code if line]

            repair_data['repair_results'][i]['repair_result_list'][j]['num_no_comment_lines'] = len(code)

    with open(f'../../results/{model_id}/{do_rag}/repair_results_numcodelines.json', 'w') as f:
        json.dump(repair_data, f, indent=2)



def remove_comment(code):
    code = re.sub(r'/\*.*?\*/','\n', code, flags=re.DOTALL)
    code = re.sub(r'//.*', '', code) 
    code = re.sub(r'\n\s*\n+', '\n\n', code)

    return code





 





if __name__ == '__main__':
    main('gpt-5', 'rag')
    main('gpt-5', 'no_rag')



