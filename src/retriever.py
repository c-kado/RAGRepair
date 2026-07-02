import argparse
from collections import Counter
import json
import networkx as nx
import numpy as np
import os
import pandas as pd
import re
import shutil
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
from subprocess import PIPE

import compute_dataset_wlkernel as comwl


class Retriever:

    def get_target_contract(self, category, contract):
        vul_source = 'tmp/tmp.sol'
        vul_mapping = {'access_control': ['tx-origin', 'controlled-delegatecall', 'suicidal'], # incorrect_constructor, mappin_write, wallet_0x検知できず, 
                    'arithmetic': [], # Slither do not detect overflow/underflow.
                    'bad_randomness': ['timestamp'], # blackjack検知できず
                    'denial_of_service': [],
                    'front_running': [], # No target contract
                    'reentrancy': ['reentrancy-eth'],   #modifier_reentrancyのreentrancy-no-ethは修正後にも検知, reentrancy_bonus検知できず
                    'time_manipulation': ['timestamp'],
                    'unchecked_low_level_calls': ['unchecked-lowlevel', 'unchecked-send'],    # 0x52..のやつは他のところも変わってるけど，，-xa1f...は検知できず
                    'other': ['uninitialized-storage']}

        shutil.copy(f'../dataset/mitigate_patches/{category}/{contract}/{contract}.sol', vul_source)
        with open(vul_source, 'r') as f:
            code = f.read()
        
        solc_ver = re.search(r'pragma solidity \^?(0\.\d+\.\d+);', code).group(1)
        self.change_solc_version(solc_ver)

        if not self.solc_compile(vul_source, 'tmp/output'):
           print('solc-error!!')
           exit()

        result_file = 'tmp/output/tmp.sol_slither.json'
        if os.path.exists(result_file):
            os.remove(result_file)
        # if not run_slither(vul_source, result_file):
        #    return False
     
        if not self.run_slither(vul_source, result_file, option=[f'--detect {','.join(vul_mapping[category])}']):
            return False


    def change_solc_version(self, version):
        proc = subprocess.run('solc-select use %s --always-install' % version, shell=True, stdout=PIPE, stderr=PIPE, text=True)
        if proc.stderr != '':
            print(version)
            print('ERROR: ' + proc.stderr)
        print('solc-select use >> ' + proc.stdout)


    def solc_compile(self, sol_file, output_dir):
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


    def run_slither(self, sol_file, output_file, option=''):
        proc = subprocess.run(f'slither --exclude-informational --exclude-optimization {" ".join(option)} {sol_file} --json {output_file}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
        if not os.path.exists(output_file):
            print(proc.stderr)
            return False
        return True
     

    def compute_wlcounter(self, ast_file, detection_file):
        ast_graph = comwl.mapping_ast2graph(ast_file)
        # TODO: TODO: slitherで複数の脆弱性が検知されてても，前から順番に修正みたいな形を考慮すると，get_vul_rootでしてる1個目の検知結果のrootを取るでOK
        vul_root = comwl.get_vul_root(detection_file, ast_file)
        vul_sub_tree = {vul_root} | nx.descendants(nx.DiGraph(ast_graph), vul_root)
        vul_hashes = nx.weisfeiler_lehman_subgraph_hashes(ast_graph.subgraph(vul_sub_tree), node_attr='node_type', iterations=2)
        return comwl.hash_to_vect(vul_hashes)


    def retrieve_similar_vectors(self, hash_counter, target_category, target_contract):
        # データベースopen
        counter_db = pd.read_csv('../dataset/wl_counter.csv')
        counter_db = counter_db[(counter_db['Category'] != target_category) | (counter_db['contract'] != target_contract)]

        nearest = 0
        max_sim = 0
        for idx, row in counter_db.iterrows(): 
            # 順にhashの類似度を計算
            db_counter = Counter(json.loads(row['wl_counter']))
            sim = self.compute_similarity(hash_counter, db_counter)

            if sim > max_sim:
                # 一番近いものを取得
                nearest = idx
                max_sim = sim

        self.nearest_contract = counter_db.iloc[nearest]
        self.nearest_sim = max_sim


    def compute_similarity(self, counter1, counter2):
    # MIN: 0, MAX: 1
        labels = sorted(set(counter1) | set(counter2))

        vec1 = [counter1.get(x,0) for x in labels]
        vec2 = [counter2.get(x,0) for x in labels]

        sim = cosine_similarity(
            np.array(vec1).reshape(1,-1),
            np.array(vec2).reshape(1,-1)
        )[0,0]

        return sim


    def retrieve(self, category, contract):
        # tmpファイルにターゲットのコントラクトコピー
        # tmp/
        # |
        # - tmp.sol
        # - output
        #   |
        #   - empty -> ast, slither, etc

        os.makedirs('tmp/output', exist_ok=True)
        self.get_target_contract(category, contract)


        target_hash_counter = self.compute_wlcounter('tmp/output/tmp.sol_json.ast', 'tmp/output/tmp.sol_slither.json')

        self.retrieve_similar_vectors(target_hash_counter, category, contract)
        print(f'Nearest contract: {self.nearest_contract['Category']}/{self.nearest_contract['contract']}')
        print(f'Similarity: {self.nearest_sim}')

        self.gen_augument_prompt(self.nearest_contract['Category'], self.nearest_contract['contract'])



    def gen_augument_prompt(self, category, contract):
        contract_path = f'../dataset/mitigate_patches/{category}/{contract}'

        with open(f'{contract_path}/{contract}.sol', 'r') as f:
            code = f.read()

        with open(f'{contract_path}/patched_{contract}.sol', 'r') as f:
            fix_code = f.read()

        self.aug_prompt = f'[VUL_EX]{code}[FIX_EX]{fix_code}'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'category',
        choices=['access_control', 'arithmetic', 'bad_randomness', 'other', 'reentrancy', 'unchecked_low_level_calls'],
        help='specify the vulnerabilty category of a fix target contract'
    )

    parser.add_argument(
        'contract',
        help='specify the fix target contract'
    )

    return parser.parse_args()


# categoryとコントラクト名の入力
if __name__ == '__main__':
    args = parse_args()
    if not os.path.exists(f'../dataset/mitigate_patches/{args.category}/{args.contract}'):
        print(f'"../dataset/mitigate_patches/{args.category}/{args.contract}" does not exist.')
        exit()

    rtrv = Retriever()
    rtrv.retrieve(args.category, args.contract)

    print(rtrv.nearest_contract)
    print(rtrv.nearest_sim)
    print(rtrv.aug_prompt)




