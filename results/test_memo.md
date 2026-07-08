# Test by chatGPT

## Test prompt

```
Fix {category} vulnerability in a Solidity code. Output only fixed entire code. [CODE]
```



## Test results


### Unchecked low-level call

- 0x66xxxxx
  - 2026/06/24 chatgpt (GPT-5.5)
    - solfile全体は長い．
    - 脆弱性と関係ない場所の修正．
    - 全体の出力を求めているが，コメントアウトで省略している．(コンパイルエラーになる形？)
  - 2026/06/25 claude (Sonnet 4.6)
    - コード以外の出力
    - low-levelでないtransferでのrequire
    - send -> call.valueへの変更

### Access control
- phishable
  - 2026/06/24 chatgpt (GPT-5.5)
    - 機能は変わらないが，脆弱性と無関係の編集あり
      - constructorにpublicを追記
      - thisをaddress(this)に変更
  - 2026/06/25 claude (Sonnet 4.6)
    - 修正できてる
    - ただし，いらないコードを追加して，修正させたら，そのコードが出力されなかった(mutated_phishable.sol)

### Other(Uninitialized storage)
- crypto_roulette.sol
  - 2026/06/24 chatgpt (GPT-5.5)
    - memoryのみをつけて修正できている
    - 直近のGPTになっていると，修正済みのデータセット自体を学習している可能性も否定できない
      - <span style="color: red; ">試しに元のコードに1行関係ないコードを足した場合，その行が反映されず，脆弱性のみ修正された結果が出力された．(test_prompt_crypto_roulette.txtの結果も同じもの)</span>
  - 2026/06/25 claude (Sonnet 4.6)
    - memoryのみをつけて修正できている
    - ただし，コードから1行抜いたとき，元の1行抜かれていないバージョンで修正されていた

### Reentrancy
- 0x23...
  - 2026/06/24 chatgpt (GPT-5.5)
    - 修正できてそう
    - 関数のvisibilityなど，脆弱性と関係ない部分も修正されている
  - 2026/06/25 claude (Sonnet 4.6)
    - 修正はできてる？？
    - ただ，過剰に対策盛り込んでいる
      - Flagでの対策
      - 変数更新の順序変更


## Consideration

- ネット上に修正したリポジトリがアップされていることを考えると，最近のでできるのは不思議じゃない．
  - 修正しているのか，同じパターンを覚えているのかわからない．
  - 1行追加したり，削除したりして，それが出力に反映されていないことから，元のコードをそのまま覚えている，的なことが否定できなさそう
- RAGによる情報の補強がどの程度有効かを把握する方向になる？？？
  - どこまでの情報を入れるのか． 
- 脆弱性と無関係の箇所を変更している．
  - 機能は変わらないものの，fix {category} vulnerabilityで指定しているタスク以上のことをしてしまっているのは．．？