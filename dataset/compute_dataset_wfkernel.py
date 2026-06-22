# ASTをグラフ化
    # ASTの該当箇所を抽出
        # パターン1. 脆弱な行を含む関数
        # パターン2. 脆弱な行の1個上の親のノードから
    # 脆弱性を適切に検出できない場合
        # AST全体をグラフ化しとく？
    # 脆弱性が複数検知されている場合
        # パターン1. 今回は検出対象の脆弱性を制限しておく？
        # パターン2. 脆弱なコントラクトのAST全体をグラフ化する方に含めちゃう？


# カーネルを計算する


# カーネルの比較対象を減らすために，脆弱性の検知結果（1つの脆弱性に絞って）をbm25で検索(bm25というより，語彙的に似ているものを探す簡易的なもので足切りする感じ)
# これで，同じ脆弱性とかぐらいには絞れる？
# subgraphの方のnetworkxのカーネル計算方法で，bm25?でマッチしたやつで，astから近い部分を探す，とかできる．．？


# networkx library reference
# https://networkx.org/documentation/stable/tutorial.html#directed-graphs

import os
from pathlib import Path
import json
import networkx as nx
from networkx.readwrite import json_graph


def get_ast(file):
    with open(file, 'r') as f:
        ast_json = json.load(f)

    return ast_json


# Input: マッピングするAST（該当箇所抽出済みとする）
def mapping_ast2graph(ast):
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

    ast_graph = nx.DiGraph()

    # solc option '--ast-json' is legacy ast option
    # id does not always exist
    no_id_node = 0
    if 'id' in ast:
        node_id = ast['id']
    else:
        no_id_node -= 1
        node_id = no_id_node
        print(node_id)
        print(ast['name'])

    ast_graph.add_node(node_id, node_type=ast['name'])

    # add nodes to the graph recursively
    if 'children' in ast:
        add_children_node(ast_graph, ast['children'], node_id, no_id_node) 

    return ast_graph


def add_children_node(g, children, parent_id, no_id_node):
    for node in children:
        if 'id' in node:
            node_id = node['id']
        else:
            no_id_node -= 1
            node_id = no_id_node
            print(node_id)
            print(node['name'])

        g.add_node(node_id, node_type=node['name'])
        g.add_edge(parent_id, node_id)

        if 'children' in node:
            add_children_node(g, node['children'], node_id, no_id_node)



for category in os.listdir('mitigate_patches'):
    if not os.path.isdir(f'mitigate_patches/{category}'):
        continue

    for contract in os.listdir(f'mitigate_patches/{category}'):
        if not os.path.isdir(f'mitigate_patches/{category}/{contract}'):
            continue
        
        print(f'{category}/{contract}')

        # Build ast graph
        ast = get_ast(f'mitigate_patches/{category}/{contract}/output/{contract}.sol_json.ast')
        ast_graph = mapping_ast2graph(ast)

        # Get wl subgraph hashes
        # TODO: iterationの値は要検討．kernelで計算するグラフのサイズ(行単位/関数単位/etc.)によって変える？適切な値を検討(empiricalに？？？)
        ast_hashes = nx.weisfeiler_lehman_subgraph_hashes(ast_graph, node_attr='node_type', iterations=2)

        # compute wlhash of vulnerable position
        # TODO: TODO: TODO: tx_verification/src/dataset_creation/generate_prompt.pyを参考に，各脆弱性ごとに，該当する行を取得する．(elementでnodeを探すやつ)
        # その後，test_compute.pyのように，rootを設定（行の一番上にあるのーどid?）して，ハッシュ計算，counter
        # 以上をファイルに保存しておく

        # save the graph info
        ast_graph_info = {'graph': json_graph.node_link_data(ast_graph), 'wl_hashes': ast_hashes}

        with open(f'mitigate_patches/{category}/{contract}/output/{contract}.sol_ast_graph.json', 'w') as f:
            json.dump(ast_graph_info, f, indent=2)




