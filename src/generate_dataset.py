# Extract vulnerable / fix pairs written in Solidity
# Solidityで修正している，修正できているVul/Fixのペアを収集
# 同じコントラクトに対する複数の修正結果は一旦おいておいて，後でどれか選択．（sGuardのように，別コントラクトを作成して呼び出しているようなものは，検知に偽陽性/偽陰性が出やすいから優先度低(ソースしっかり調べる)）


# 脆弱性が検知されているもの同士比較したい
# 検知されている部分のみを抜き出して比較？ソース/AST



# dataset/RepairComp/results/smartbugs/data_analysis/all_patches_stats.csv
# に各ツールで生成したパッチの正否やファイルのパスが記録
# functional_check = passed & mitigates = yesのものが攻撃を防いだパッチ(論文のTable 4の数と一致)



# グラフの類似度を測る手法は
# GNNの学習にはデータ数が足りない
# カーネルとは
# ASTの比較

# 2. グラフカーネル
# 少量データでは非常に有力です。
# 代表例：
# Weisfeiler-Lehman Kernel
# Shortest Path Kernel
# Graphlet Kernel
# これらはGNNのような大量学習データを必要とせず、
# 「グラフ同士の類似度行列」
# を作ってSVMなどで学習できます。
# 数百サンプル以下ではGNNより強いことも珍しくありません。



# dataset
# |
# - mitigate_patches
#   |
#   - mitigate_patches.csv
#   |
#   - VUL
#     |
#     - CONTRACT
#       | 
#       - CONTRACT.sol
#       |
#       - patched_CONTRACT.sol

from difflib import SequenceMatcher
import json
import os
import pandas as pd
import re
import shutil
import subprocess
from subprocess import PIPE


vul_mapping = {'access_control': ['tx-origin', 'controlled-delegatecall', 'suicidal'], # incorrect_constructor, mappin_write, wallet_0x検知できず, 
                'arithmetic': [], # Slither do not detect overflow/underflow.
                'bad_randomness': ['timestamp'], # blackjack検知できず
                'denial_of_service': [],
                'front_running': [], # No target contract
                'reentrancy': ['reentrancy-eth'],   #modifier_reentrancyのreentrancy-no-ethは修正後にも検知, reentrancy_bonus検知できず
                'time_manipulation': ['timestamp'],
                'unchecked_low_level_calls': ['unchecked-lowlevel', 'unchecked-send'],    # 0x52..のやつは他のところも変わってるけど，，-xa1f...は検知できず
                'other': ['uninitialized-storage']}

dataset_dir = '../dataset'







def extract_dataset(repcomp_file):
    # 元のコードとの差分が一番小さい結果を優先的に採用
    df = pd.read_csv(repcomp_file)
    df = df[df['Category']!='arithmetic']

    sol_fix_pair_df = get_solfix_pair(df)
    mitigate_patches_df = get_mitigate_patches(sol_fix_pair_df)

    mitigate_patches_df.to_csv(f'{dataset_dir}/mitigate_patches/mitigate_patches.csv', index=False)
    min_diff_mitigate_patches_df = pd.DataFrame(columns=mitigate_patches_df.columns)

    original_path = '../tools/sb-heists/smartbugs-curated/0.4.x/contracts/dataset'
    patch_path = '../tools/RepairComp/results/smartbugs'

    for original, group in mitigate_patches_df.groupby('Original'):
        category = group['Category'].iat[0]
        with open(f'{original_path}/{category}/{original}', 'r') as f:
            code = remove_comment(f.read())

        min_diff = len(code.splitlines())
        min_diff_patch = group.iloc[0]
        # 空白(インデントやスペース）をなくす
        code = [re.sub(r"\s+", "", line) for line in code.splitlines()]

        # originalごと
        for idx, row in group.iterrows():
            # no_com_oricode = 元ファイルのコメント削除

            with open(f'{patch_path}/{row['Tool']}/{category}/{original[:-4]}/{row['Patch']}', 'r') as f:
                patched_code = remove_comment(f.read()) 
                # 空白(インデントやスペース）をなくす
                patched_code = [re.sub(r"\s+", "", line) for line in patched_code.splitlines()]

            # no_com_oricodeとno_com_patchの行の差分の数を取得
            matcher = SequenceMatcher(None, code, patched_code) 
            count = sum(
                tag != "equal"
                for tag, *_ in matcher.get_opcodes()
            )

            if count < min_diff:
               min_diff = count 
               min_diff_patch = group.loc[idx]
 
        contract_path = f'{dataset_dir}/mitigate_patches/{category}/{original[:-4]}'
        os.makedirs(contract_path, exist_ok=True)

        copy_code_wot_comment(f'{original_path}/{category}/{original}', f'{contract_path}/{original}')
        copy_code_wot_comment(f'{patch_path}/{min_diff_patch['Tool']}/{category}/{original[:-4]}/{min_diff_patch['Patch']}', f'{contract_path}/patched_{original}')
        min_diff_mitigate_patches_df.loc[len(min_diff_mitigate_patches_df)] = min_diff_patch

    return min_diff_mitigate_patches_df


def remove_comment(code):
    code = re.sub(r'/\*.*?\*/','\n', code, flags=re.DOTALL)
    code = re.sub(r'//.*', '', code) 
    code = re.sub(r'\n\s*\n+', '\n\n', code)

    return code


def copy_code_wot_comment(ori_file, cp_file):
    with open(ori_file, 'r') as f: 
        # remove comment
        code = remove_comment(f.read())

    with open(cp_file, 'w') as cp_f:     
        cp_f.write(code)





def get_solfix_pair(df):
    # get the vul/fixed pair written in Solidity
    return df[df['COMP'].notna()]


def get_mitigate_patches(df):
    # get the fixed contract mitigating vulnerability

    return df[(df['functional_check'] == 'passed') & (df['mitigates'] == 'yes')]


def record_contract_info(contract_info):

    # 1. get solidity version
    # 2. get solc ast
    # 3. get analysis result by Slither

    contract_dir = f'{dataset_dir}/mitigate_patches/{contract_info['Category']}/{contract_info['Original'][:-4]}'
 
    vul_source = f'{contract_dir}/{contract_info['Original']}'
    patched_source = f'{contract_dir}/patched_{contract_info['Original']}'

    with open(vul_source, 'r') as f:
        code = f.read()
    
    # TODO: Revise the version parser to account for more complex version specification patterns.
    solc_ver = re.search(r'pragma solidity \^?(0\.\d+\.\d+);', code).group(1)
    change_solc_version(solc_ver)
   
    # In solc under v0.4.??, the option `-o ./' occurs an error.
    # To except this, the ast output is recorded in `output/'.

    print(f'{vul_source[:-4]}\nRun Solc...')
    if not solc_compile(vul_source, f'{contract_dir}/output'):
       print('solc-error!!')
       exit()

    print('Run Slither....')
    # TODO: 実験設定メモ: 今回は対象の脆弱性を1つ含んでいる場合のみをデータセットとして持つ
    # データセット生成時，slitherの解析結果としては対象の脆弱性の結果のみを記録
    # ただし，脆弱性修正対象としては，他の脆弱性が増えてはいけないので，全ての解析結果と比べる． 

    # TODO: 実験設定メモ: 次のslither実行は，テスト対象として修正をする時，修正後に脆弱性が増加しないか確認するため，全脆弱性を解析

    all_results_file = f'{contract_dir}/output/{contract_info['Original']}_slither.json'
    targetvul_results_file = f'{contract_dir}/output/{contract_info['Original']}_slither_{contract_info['Category']}.json'

    # slither can not overwrite -> remove file
    if os.path.exists(all_results_file):
        os.remove(all_results_file)
    if not run_slither(vul_source, all_results_file):
        return False
    
    # extract results of only target vulnerability from all results
    targetvul_detection = extract_vul_results(all_results_file, contract_info['Category'])
    with open(targetvul_results_file, 'w') as f:
        json.dump(targetvul_detection, f, indent=2)
    # run_slither(vul_source, f'{contract_dir}/output/{contract_info['Original']}_slither_{contract_info['Category']}.json', option=[f'--detect {','.join(vul_mapping[contract_info['Category']])}'])


    # まず，originalの脆弱性を検知できていなければアウト
    if not targetvul_detection['results']:
        return False 

    # 今回はretriever側のデータセットとしては1つの解析結果の場合のみに限定．複数検知されているのもアウト
    if len(targetvul_detection['results']['detectors']) != 1:
        return False

    # originalとpatchで結果を比較
    # originalの解析から脆弱性が減っていない場合（slitherでは検知できない場合?）はデータセットから除外
    patched_targetvul_results_file = f'{contract_dir}/output/patched_{contract_info['Original']}_slither_{contract_info['Category']}.json'
    if not run_slither(patched_source, patched_targetvul_results_file, option=[f'--detect {','.join(vul_mapping[contract_info['Category']])}']):
        return False

    with open(patched_targetvul_results_file, 'r') as f:
        patch_detection = json.load(f)

    if not patch_detection['results']:
        # 脆弱性なし！
        with open(f'{contract_dir}/contract_info.json', 'w') as f:
            d = {'filename': contract_info['Original'], 'version': solc_ver, 'main_contract': get_maincontract(code.splitlines())}
            json.dump(d, f, indent=2)
        return True
    else:
        return False


def get_maincontract(contents):
    contract = []
    for line in contents:
        # count contracts in solfile
        # remove space of left side of 'line'
        line = line.lstrip()
        if line.startswith('contract '): 
            contract.append(re.findall(r'contract\s+([A-Za-z_][A-Za-z0-9_]*)\s*', line)[0])
            name =  re.findall(r'contract\s+([A-Za-z_][A-Za-z0-9_]*)\s*', line)[0]

    if len(contract) == 1:
        # solfile has only 1 contract -> target!!
        return contract[0]
    elif len(contract) > 1:
        # multiple contract
        # get main contract
        return select_main_contract(filename, contract)


def select_main_contract(filename, contract_name_list):
    # TODO: remove 17-21!
    # adjusting the case of this study
    main_cands = ['DepositProxy', 'ModifierEntrancy', 'TokenBank', 'PoCGame', 'EtherGet', 'VaultProxy', 'PandaCore', 'MultiOwnable', 'FibonacciBalance']

    main_list = []
    for contract in contract_name_list:
        if not contract.startswith('Log'):
            main_list.append(contract)
    
    for cand in main_cands:
        if cand in main_list:
            return cand
    
    if len(main_list) == 1:
        return main_list[0]

    print(f'Select main contract of {filename}')
    for i, contract in enumerate(contract_name_list):
        print(f'{i}: {contract}')

    index = int(input())

    if 0 <= index and index < len(contract_name_list):
        return contract_name_list[index] 
    else:
        return ''






def change_solc_version(version):
    proc = subprocess.run('solc-select use %s --always-install' % version, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if proc.stderr != '':
        print(version)
        print('ERROR: ' + proc.stderr)
    print('solc-select use >> ' + proc.stdout)


def solc_compile(sol_file, output_dir):
    proc = subprocess.run(f'solc {sol_file} --ast-json -o {output_dir} --overwrite', shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if len(re.findall(rf'{sol_file.split("/")[-1]}:[\d]+:[\d]+: Error: ', proc.stderr)) > 0:
        # Error message by solc: "'filename':line:column?: Error:" 
        return False
    elif len(re.findall('Internal compiler error during compilation:', proc.stderr)) > 0:
        # Compiler internal error?
        return False
    elif len(re.findall('Traceback (most recent call last):', proc.stderr)) > 0:
        # run solc fail
        print(proc.stderr)
        return False

    return True


def run_slither(sol_file, output_file, option=''):
    proc = subprocess.run(f'slither --exclude-informational --exclude-optimization {" ".join(option)} {sol_file} --json {output_file}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
    if not os.path.exists(output_file):
        print(proc.stderr)
        return False
    return True
    

def extract_vul_results(all_results_file, category):
    with open(all_results_file, 'r') as f:
        results = json.load(f)

    if not results['results']:
        # 脆弱性なし
        return results    
    
    results['results']['detectors'] = [d for d in results['results']['detectors'] if d['check'] in vul_mapping[category]]
    
    if len(results['results']['detectors']) == 0:
        results['results'] = {}

    return results




# MAIN
if not os.path.exists(f'{dataset_dir}/mitigate_patches/'):
    os.makedirs(f'{dataset_dir}/mitigate_patches/')

mitigate_patches = extract_dataset('../tools/RepairComp/results/smartbugs/data_analysis/all_patches_stats.csv')
mitigate_patches['retriever_dataset'] = True
# mitigate_patches.loc[mitigate_patches['Category'] == 'arithmetic', 'retriever_dataset'] = False


for idx, contract_info in mitigate_patches[mitigate_patches['retriever_dataset']==True].iterrows():
    # 各vul/fixのペアに対して，vulのファイルをslitherで解析, solcによるast出力
    # 解析情報を記録
    
    print(contract_info)
    os.makedirs(f'{dataset_dir}/mitigate_patches/{contract_info['Category']}/{contract_info['Original'][:-4]}/output', exist_ok=True)
    if not record_contract_info(contract_info):
        # not match for retrieved dataset
        shutil.rmtree(f'{dataset_dir}/mitigate_patches/{contract_info['Category']}/{contract_info['Original'][:-4]}/')
        mitigate_patches.at[idx, 'retriever_dataset'] = False
        print(f'{contract_info['Category']}/{contract_info['Original']}: not match dataset')

mitigate_patches.to_csv(f'{dataset_dir}/mitigate_patches/mitigate_patches.csv', index=False)
