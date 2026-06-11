


retrieverの構成
1. vulのsolファイルでAST比較
    - 全体比較 or 脆弱性該当箇所比較 or 脆弱性関数比較
2. vulの解析結果でスパース比較

両方でスコア計算．
あるいは
スパース検索での上位からAST比較？


コンテキスト検索：タグやキーワードなどのメタデータをチャンクに付与して検索を容易に
→ 脆弱性のタイプを付与
<VUL_TYPE>reentrancy</VUL_TYPE><VUL_INFO>{analysis_results}</VUL_INFO><VUL_CODE>{vulnerable_sourcecode}</VUL_CODE><FIX_CODE>{fixed_sourcecode}</FIX_CODE>
みたいにしとく？VUL_TYPE検索後に各検索，あるいは，スパース検索のヒット率を上げるために入れる，ということにしとく？



AST比較の手法候補
(比較するとして，関数名などの固有情報は関係ない→構造のみを抽出して類似度計算？？同じ変数，といった情報も消えちゃう．．)

- Tree edit distance (Graph edit distance?)
- AST部分木のJaccard類似度
- Weisfeiler-Lehman Kernel




weisfeiler-lehman kernelで検討
- networkXでの実装を試す．
    - AST出力
    - ASTをnetworkXのWSkernelのグラフにマッチングさせる
    - 計算


- ASTの出力方法について，
今回のデータセットは0.8以降は含まれれない -> --ast-jsonで対応
ただし，以降を考慮し，--ast-compact-jsonを用いた変換も考慮する．

