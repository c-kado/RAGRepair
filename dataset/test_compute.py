import json
import networkx as nx
from networkx.readwrite import json_graph
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


test1 = '0x07f7ecb66d788ab01dc93b9b71a88401de7d0f2e'
test2 = '0x52d2e0f9b01101a59b38a3d05c80b7618aeed984'
# test2 = '0x2972d548497286d18e92b5fa1f8f9139e5653fd2'


with open(f'mitigate_patches/unchecked_low_level_calls/{test1}/output/{test1}.sol_ast_graph.json', 'r') as f:
    data = json.load(f)

G1 = json_graph.node_link_graph(data['graph'])
G1_hashes = data['wl_hashes']

with open(f'mitigate_patches/unchecked_low_level_calls/{test2}/output/{test2}.sol_ast_graph.json', 'r') as f:
    data = json.load(f)

G2 = json_graph.node_link_graph(data['graph'])
G2_hashes = data['wl_hashes']


# id=402の関数にvulあり
# root1 = 402
root1 = 390
nodes = {root1} | nx.descendants(nx.DiGraph(G1), root1)
VulF1 = G1.subgraph(nodes).copy()
hashes1 = nx.weisfeiler_lehman_subgraph_hashes(VulF1, node_attr='node_type')

# id=60の関数にvulあり
# 0x29の行単位root2 = 54
root2 = 87
nodes = {root2} | nx.descendants(nx.DiGraph(G2), root2)
VulF2 = G2.subgraph(nodes).copy()
hashes2 = nx.weisfeiler_lehman_subgraph_hashes(VulF2, node_attr='node_type')

# print(hashes1)




# パターン1: counterで，ノードのattributeのみで出現回数をカウントして比較
#      → ASTの構造情報は消えそう(かなり抽出するASTを絞ってから使えそう)
# パターン2: 構造情報を保ったまま比較を行う

counter1 = Counter()
for hashes in hashes1.values():
    counter1.update(hashes)

counter2 = Counter()
for hashes in hashes2.values():
    counter2.update(hashes)



labels = sorted(
    set(counter1) |
    set(counter2)
)

vec1 = [counter1.get(x,0) for x in labels]
vec2 = [counter2.get(x,0) for x in labels]

print(vec1)
print(vec2)

sim = cosine_similarity(
    np.array(vec1).reshape(1,-1),
    np.array(vec2).reshape(1,-1)
)[0,0]

print(sim)
