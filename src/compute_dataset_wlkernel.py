# ASTをグラフ化
    # ASTの該当箇所を抽出
        # パターン1. 脆弱な行を含む関数
        # パターン2. 脆弱な行の1個上の親のノードから
    # 脆弱性を適切に検出できない場合
        # AST全体をグラフ化しとく？
    # 脆弱性が複数検知されている場合
        # パターン1. 今回は検出対象の脆弱性を制限しておく？
        # パターン2. 脆弱なコントラクトのAST全体をグラフ化する方に含めちゃう？


# ハッシュを計算する

# カーネルの比較対象を減らすために，脆弱性の検知結果（1つの脆弱性に絞って）をbm25で検索(bm25というより，語彙的に似ているものを探す簡易的なもので足切りする感じ)
# これで，同じ脆弱性とかぐらいには絞れる？
# subgraphの方のnetworkxのカーネル計算方法で，bm25?でマッチしたやつで，astから近い部分を探す，とかできる．．？


# networkx library reference
# https://networkx.org/documentation/stable/tutorial.html#directed-graphs

import warnings

warnings.filterwarnings(
    "ignore",
    message="The hashes produced for directed graphs changed in v3.5 due to a bugfix*"
)

from collections import Counter
import json
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
import os
import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

dataset_dir = '../dataset'

'''
def get_ast(file):
    with open(file, 'r') as f:
        ast_json = json.load(f)

    return ast_json
'''


# Input: マッピングするAST（該当箇所抽出済みとする）
def mapping_ast2graph(ast_file):
    # ast の形式
    # Tree_node = 
    # {
    #     "attributes" : key-value, // ノードの情報，ノードタイプによって中身変わる 
    #     "children" : [{children_tree_node}],  // ない時もある
    #     "id" : int, // unique number for each node    // --ast-jsonではない場合も
    #     "name" : str, // node_type: ContractDefinition, Assignment, etc.
    #     "src" : "start_char_num:char_count:0(?)"
    # }

    # mapping ast to graph(networkx)
    # nx.node_attr に，astのname(node_type)をマッピング
    # nx.nodeで，idをノードidとする
    # TODO: nx.node_attrとして，astのattributesを入れたパターンもやってみる
    #       (edge_attrにnode_typeをマッピングして，一番最初のSourceUnit?はなくなる形
    #        node_attrにastのattributesとか？)

    with open(ast_file, 'r') as f:
        ast = json.load(f)

    ast_graph = nx.DiGraph()

    # solc option '--ast-json' is legacy ast option
    # id does not always exist
    no_id_node = 0
    if 'id' in ast:
        node_id = ast['id']
    else:
        no_id_node -= 1
        node_id = no_id_node
        ast['id'] = node_id

    ast_graph.add_node(node_id, node_type=ast['name'])

    # add nodes to the graph recursively
    if 'children' in ast:
        ast['children'] = add_children_node(ast_graph, ast['children'], node_id, no_id_node) 

    return ast_graph


def add_children_node(g, children, parent_id, no_id_node):
    for i, node in enumerate(children):
        if 'id' in node:
            node_id = node['id']
        else:
            no_id_node -= 1
            node_id = no_id_node
            children[i]['id'] = node_id
            print(node_id)
            print(node['name'])

        g.add_node(node_id, node_type=node['name'])
        g.add_edge(parent_id, node_id)

        if 'children' in node:
            children[i]['children'] = add_children_node(g, node['children'], node_id, no_id_node)

    return children

def get_vul_root(detection_file, ast_file):

    # 脆弱性の該当行のトップのrootIDが欲しい
        # 脆弱性の該当行を特定
            # slitherの結果を確認
            # 脆弱性ごとに，脆弱性箇所のelementを抽出
            # 該当elementの行を抜き出し
        # 該当行の一番上のIDを特定
            # 脆弱行のノードをastから特定
            # 行の最大部分木(行の一部でなく全体になるよう)のrootをとる
   

    # TODO: ここでのelement抽出時に，elementが(funcitonやcontractを除いて)複数にまたがる場合，
    # 複数elementを子孫に持つノードをハッシュ計算のrootとする？
    # 各elementを統合して見る場合（element内で重複しているけど，重複させるのが重み的に重要なところのマッチを見れる？）
    # funcion, contract単位はdepth=3，nodeならdepth=2とかにして，統合？？
    # それぞれでコサイン類似度とって，nodeとかの方に重みつける？(nodeの数が異なった場合に困る？)reentrancyで，statevariableの更新が1つか2つか，みたいな差をどうするか
    # ハッシュをdepthだけ変えて求めてそのまま統合が良さげ？
 
    
    vul_trigger_element = {
        'tx-origin': {'type': 'node'},
        'controlled-delegatecall': {'type': 'node'},
        'suicidal': {'type': 'function'},
        'timestamp': {'type': 'node'},
        'reentrancy-eth': {'type': 'node', 'additional_fields':{'underlying_type': 'external_calls'}},
        'unchecked-lowlevel': {'type': 'node'},
        'unchecked-send': {'type': 'node'},
        'uninitialized-storage': {'type': 'variable'}}

    # 脆弱性の該当行を特定
    with open(detection_file, 'r') as f:
        detection_result = json.load(f)

    # node_ids start from 1(, 2, 3,..) or -1(, -2, -3, ..)
    if not detection_result['results']:
        return 0

    # datasetとして記録するvulfileは，1つのターゲット脆弱性のみ
    vul_info = detection_result['results']['detectors'][0]

    # 行単位で見る場合
    elements = vul_info['elements']
    for element in elements:
        if check_element(element, vul_trigger_element[vul_info['check']]):
            vul_element = element
            print('vul_element: '+element['name']+'\n')
            break

    # elementの行を抜き出す（該当行のスタートからエンドまでの文字位置）
    start_vul = vul_element['source_mapping']['start']
    vul_len = vul_element['source_mapping']['length']


    # 該当行の一番上のノードID
    # -> 該当文字位置全てを最小で含むノードを探す．
    # 親から再帰的に文字が含まれるか見ていって，含まれなくなる1個上のノードが該当ノード

    with open(ast_file, 'r') as f:
        ast = json.load(f)

    return is_include_vulsrc(ast['children'], ast['id'], start_vul, vul_len)


def check_element(element, trigger):
    for attr, value in trigger.items():
        if not check_element_attr(element, attr, value):
            return False            

    return True
   

def check_element_attr(element, attr, value):
    if type(value) == str:
        return element[attr] == value
    else:
        return check_element_attr(element[attr], *next(iter(value.items())))


def is_include_vulsrc(children_nodes, node_id, src_start, src_len):
    
    for node in children_nodes:
        node_start, node_len, _ = map(int, node['src'].split(':'))

        # node includes vulnerable line
        if node_start <= src_start and src_start+src_len <= node_start+node_len:
            if 'children' in node.keys():
                return is_include_vulsrc(node['children'], node['id'], src_start, src_len)
            else:
                return node['id']

    return node_id


def hash_to_vect(hashes):
    counter = Counter()
    for h in hashes.values():
        counter.update(h)

    return counter







def main():
    wl_counter_df = pd.DataFrame(columns=['Category', 'contract', 'subtree_root', 'node_num', 'wl_counter'])
    patch_list = pd.read_csv(f'{dataset_dir}/mitigate_patches/mitigate_patches.csv')

    for category in os.listdir(f'{dataset_dir}/mitigate_patches'):
        if not os.path.isdir(f'{dataset_dir}/mitigate_patches/{category}'):
            continue

        for contract in os.listdir(f'{dataset_dir}/mitigate_patches/{category}'):
            if not os.path.isdir(f'{dataset_dir}/mitigate_patches/{category}/{contract}'):
               continue

            if not patch_list.loc[(patch_list['Original'] == f'{contract}.sol'), 'retriever_dataset'].iloc[0]:
                continue
     
            print(f'{category}/{contract}')
            contract_dir = f'{dataset_dir}/mitigate_patches/{category}/{contract}'

            # Build ast graph
            # ast = get_ast(f'{contract_dir}/output/{contract}.sol_json.ast')
            ast_graph = mapping_ast2graph(f'{contract_dir}/output/{contract}.sol_json.ast')

            # Get wl subgraph hashes
            # compute wlhash of vulnerable position 
            vul_root = get_vul_root(
                f'{contract_dir}/output/{contract}.sol_slither_{category}.json',
                f'{contract_dir}/output/{contract}.sol_json.ast')
            vul_sub_tree = {vul_root} | nx.descendants(nx.DiGraph(ast_graph), vul_root)
            # TODO: iterationの値は要検討．kernelで計算するグラフのサイズ(行単位/関数単位/etc.)によって変える？適切な値を検討(empiricalに？？？)
            vul_hashes = nx.weisfeiler_lehman_subgraph_hashes(ast_graph.subgraph(vul_sub_tree), node_attr='node_type', iterations=2)
            vul_wl_counter = hash_to_vect(vul_hashes)

            # save the graph info
            ast_graph_info = {'graph': json_graph.node_link_data(ast_graph), 'vul_root': vul_root, 'vul_node_num': len(vul_sub_tree), 'vul_subgraph_hashes': vul_hashes, 'wl_counter': json.dumps(vul_wl_counter)}
            with open(f'{contract_dir}/output/{contract}.sol_ast_graph.json', 'w') as f:
                json.dump(ast_graph_info, f, indent=2)

            wl_counter_df.loc[len(wl_counter_df)] = {'Category': category, 'contract': contract, 'subtree_root': vul_root, 'node_num': len(vul_sub_tree), 'wl_counter': json.dumps(vul_wl_counter)}

    wl_counter_df.to_csv(f'{dataset_dir}/wl_counter.csv', index=False)



if __name__ == '__main__':
    main()
