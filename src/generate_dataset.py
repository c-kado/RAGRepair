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
    # 論文参考に，精度の良いツールの結果を優先度高く採用
    # SolGPT    (74%)
    # SmartFix  (53%)
    # TIPS      (49%)
    # sGuard+   (48%)
    # sGuard    (33%)
    high_acc_tool = ['SolGPT', 'SmartFix', 'TIPS', 'sGuard+', 'sGuard']

    df = pd.read_csv(repcomp_file)

    # 修正できていないものをテストとして使ってみる？
    sol_fix_pair_df = get_solfix_pair(df)
    mitigate_patches_df = get_mitigate_patches(sol_fix_pair_df)
    mitigate_patches_df = mitigate_patches_df.sort_values('Tool', key=lambda s: s.map({v: i for i, v in enumerate(high_acc_tool)}))
    mitigate_patches_df = mitigate_patches_df.sort_values('Original', kind='stable').sort_values('Category', kind='stable')

    mitigate_patches_df.to_csv(f'{dataset_dir}/mitigate_patches/mitigate_patches.csv', index=False)
    mitigate_patches_nodup_df = mitigate_patches_df.drop_duplicates(subset='Original', keep='first')


    # まず，1個目をvul/fix pairとしてソース取得
    original_path = '../tools/sb-heists/smartbugs-curated/0.4.x/contracts/dataset'
    patch_path = '../tools/RepairComp/results/smartbugs'
    for idx, row in mitigate_patches_nodup_df.iterrows():
        contract_path = f'{dataset_dir}/mitigate_patches/{row['Category']}/{row['Original'][:-4]}'
        os.makedirs(contract_path, exist_ok=True)

        # Originalのsolファイルを記録
        with open(f'{original_path}/{row['Category']}/{row['Original']}', 'r') as f:
            # re.sub('/\*.*?\*/','', code, re.DOTALL)
            # /*(改行含む任意の文字列)*/
            # or
            # //(改行含まない任意の文字列)'\n'
            # を削除
            code = re.sub(r'/\*.*?\*/','\n', f.read(), flags=re.DOTALL)
            code = re.sub(r'//.*', '', code) 
            code = re.sub(r'\n\s*\n+', '\n\n', code)
        with open(f'{contract_path}/{row['Original']}', 'w') as f:
            f.write(code)

        # Patchのsolファイルを記録
        with open(f'{patch_path}/{row['Tool']}/{row['Category']}/{row['Original'][:-4]}/{row['Patch']}', 'r') as f:
            code = re.sub(r'/\*.*?\*/','\n', f.read(), flags=re.DOTALL)
            code = re.sub(r'//.*', '', code) 
            code = re.sub(r'\n\s*\n+', '\n\n', code)
        with open(f'{contract_path}/patched_{row['Original']}', 'w') as f:
            f.write(code)

    return mitigate_patches_nodup_df



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
        return True
    else:
        return False



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
mitigate_patches.loc[mitigate_patches['Category'] == 'arithmetic', 'retriever_dataset'] = False


for idx, contract_info in mitigate_patches[mitigate_patches['retriever_dataset']==True].iterrows():
    # 各vul/fixのペアに対して，vulのファイルをslitherで解析, solcによるast出力
    # 解析情報を記録
    
    os.makedirs(f'{dataset_dir}/mitigate_patches/{contract_info['Category']}/{contract_info['Original'][:-4]}/output', exist_ok=True)
    if not record_contract_info(contract_info):
        # not match for retrieved dataset
        # shutil.rmtree(f'mitigate_patches/{contract_info['Category']}/{contract_info['Original'][:-4]}/')
        mitigate_patches.at[idx, 'retriever_dataset'] = False
        print(f'{contract_info['Category']}/{contract_info['Original']}: not match dataset')

mitigate_patches.to_csv(f'{dataset_dir}/mitigate_patches/mitigate_patches.csv', index=False)
