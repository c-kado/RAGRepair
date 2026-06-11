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




# mitigate_patches
# |
# - mitigate_patches.csv
# |
# - VUL
#   |
#   - CONTRACT
#     | 
#     - CONTRACT.sol
#     |
#     - patched_CONTRACT.sol


import pandas as pd
import os
import shutil


def extract_dataset():
    # 論文参考に，精度の良いツールの結果を優先度高く採用
    # SolGPT    (74%)
    # SmartFix  (53%)
    # TIPS      (49%)
    # sGuard+   (48%)
    # sGuard    (33%)
    high_acc_tool = ['SolGPT', 'SmartFix', 'TIPS', 'sGuard+', 'sGuard']

    repcomp_file = '../tools/RepairComp/results/smartbugs/data_analysis/all_patches_stats.csv'
    df = pd.read_csv(repcomp_file)

    # 修正できていないものをテストとして使ってみる？
    sol_fix_pair_df = get_solfix_pair(df)
    mitigate_patches_df = get_mitigate_patches(sol_fix_pair_df)
    mitigate_patches_df = mitigate_patches_df.sort_values('Tool', key=lambda s: s.map({v: i for i, v in enumerate(high_acc_tool)}))
    mitigate_patches_df = mitigate_patches_df.sort_values('Original', kind='stable').sort_values('Category', kind='stable')

    mitigate_patches_df.to_csv('mitigate_patches/mitigate_pathces.csv', index=False)
    mitigate_patches_nodup = mitigate_patches_df.drop_duplicates(subset='Original', keep='first')


    # まず，1個目をvul/fix pairとしてソース取得
    original_path = '../tools/sb-heists/smartbugs-curated/0.4.x/contracts/dataset'
    patch_path = '../tools/RepairComp/results/smartbugs'
    for idx, row in mitigate_patches_df_nodup.iterrows():
        contract_path = f'mitigate_patches/{row['Category']}/{row['Original'][:-4]}'
        os.makedirs(contract_path, exist_ok=True)

        # Originalのsolファイルを記録
        shutil.copy(f'{original_path}/{row['Category']}/{row['Original']}', f'{contract_path}/{row['Original']}')

        # Pathのsolファイルを記録

        shutil.copy(f'{patch_path}/{row['Tool']}/{row['Category']}/{row['Original'][:-4]}/{row['Patch']}', f'{contract_path}/patched_{row['Original']}')

    return mitigate_patches_nodup



def get_solfix_pair(df):
    # get the vul/fixed pair written in Solidity
    return df[df['COMP'].notna()]


def get_mitigate_patches(df):
    # get the fixed contract mitigating vulnerability

    # regard the patches satisfying 'consistence' as mitigate patches
    df = df[df['Consistent'] == True]

    return df[(df['functional_check'] == 'passed') & (df['mitigates'] == 'yes')]


def analyze_source(contract_info):
    # analyze all vulnerable source codes in the dataset
    contract_dir = f'mitigate_patches/{contract_info['Category']}/{contract_info['Original'][:-4]}'
    
    vul_source = f'{contract_dir}/{contract_info['Original']}'
    



mitigate_patches = extract_dataset()
for idx, row in mitigate_patches_df.iterrows():
    # 各vul/fixのペアに対して，vulのファイルをslitherで解析
    analyze_soure(row)
    

solc-select use 0.8.1 --always-install





