from difflib import SequenceMatcher
import json
import os
import pandas as pd
import re




def extract_dataset(repcomp_file):
    df = pd.read_csv(repcomp_file)
    df = df[df['Category']!='arithmetic']

    sol_fix_pair_df = get_solfix_pair(df)
    mitigate_patches_df = get_mitigate_patches(sol_fix_pair_df)

    clm = ['Tool', 'patch_num', 'diffline_total', 'avg_diffline', 'per_totallin', 'avg_pertotalline', 'max', 'min']
    result = pd.DataFrame(columns=clm)

    original_path = '../../tools/sb-heists/smartbugs-curated/0.4.x/contracts/dataset'
    patch_path = '../../tools/RepairComp/results/smartbugs'

    for tool, group in mitigate_patches_df.groupby('Tool'):
        tool = group['Tool'].iat[0]

        patch_count = 0
        diffline_total = 0
        diffline_per_totalline_total = 0
        max_diff = 0
        max_diff_per = 0
        min_diff = 10000
        min_diff_per = 10000
        
        for idx, row in group.iterrows():
            original = row['Original']
            category = row['Category']

            with open(f'{original_path}/{category}/{original}', 'r') as f:
                code = remove_comment(f.read())

            # min_diff = len(code.splitlines())
            # min_diff_patch = group.iloc[0]
            # 空白(インデントやスペース）をなくす
            code = [re.sub(r"\s+", "", line) for line in code.splitlines()]
            # 空行を削除
            code = [line for line in code if line]

            with open(f'{patch_path}/{tool}/{category}/{original[:-4]}/{row['Patch']}', 'r') as f:
                patched_code = remove_comment(f.read()) 
                # 空白(インデントやスペース）をなくす
                patched_code = [re.sub(r"\s+", "", line) for line in patched_code.splitlines()]
                code = [line for line in patched_code if line]

            # no_com_oricodeとno_com_patchの行の差分の数を取得
            matcher = SequenceMatcher(None, code, patched_code) 
            count = sum(
                tag != "equal"
                for tag, *_ in matcher.get_opcodes()
            )
            per_totalline = count / len(code)

            if max_diff < count:
                max_diff = count
            if min_diff > count:
                min_diff = count
 
            patch_count += 1
            diffline_total += count
            diffline_per_totalline_total += per_totalline

            print(f'{tool}/{category}/{original}/{row['Patch']}')
            print(f'diff_line: {count}, per_totalline: {diffline_per_totalline_total}')

        result.loc[len(result)] = [tool, patch_count, diffline_total, diffline_total/patch_count, diffline_per_totalline_total, diffline_per_totalline_total/patch_count, max_diff, min_diff]
        print(result)
     

    print(result)




def remove_comment(code):
    code = re.sub(r'/\*.*?\*/','\n', code, flags=re.DOTALL)
    code = re.sub(r'//.*', '', code) 
    code = re.sub(r'\n\s*\n+', '\n\n', code)

    return code

def get_solfix_pair(df):
    # get the vul/fixed pair written in Solidity
    return df[df['COMP'].notna()]


def get_mitigate_patches(df):
    # get the fixed contract mitigating vulnerability

    return df[(df['functional_check'] == 'passed') & (df['mitigates'] == 'yes')]




mitigate_patches = extract_dataset('../../tools/RepairComp/results/smartbugs/data_analysis/all_patches_stats.csv')

