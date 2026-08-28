import json
import statistics
import os
import pandas as pd

# コントラクトごとに，入力プロンプトlength，出力len, 入出力合計のlenghと，exectimeを行にまとめる．








def sum_time_length(do_rag): 

    len_time_db = pd.DataFrame(columns=['category', 'contract', 'output_num', 'input_len', 'output_len', 'inout_len', 'exec_time'])
    mid_len_time_db = pd.DataFrame(columns=['category', 'contract', 'input_len', 'output_len', 'inout_len', 'exec_time'])

    for category in os.listdir(f'../../dataset/mitigate_patches'):
        if not os.path.isdir(f'../../dataset/mitigate_patches/{category}'):
            continue

        for contract in os.listdir(f'../../dataset/mitigate_patches/{category}'):
            if not os.path.isdir(f'../../dataset/mitigate_patches/{category}/{contract}'):
               continue

            print(f'\n=================================\n{category}/{contract}')

            # 入力のlenをget
            with open(f'../../results/gpt-5/{do_rag}/{category}/{contract}/prompt.txt', 'r') as f:
                prm = json.load(f)

            in_len = len(prm['system_prompt']) + len(prm['user_prompt'])

            times = []
            out_lens = []
            for i in range(0,5):
                # 出力のlenをget
                with open(f'../../results/gpt-5/{do_rag}/{category}/{contract}/{contract}_{i}.sol', 'r') as f:
                    out_len = len(f.read())

                # inf_timeをget
                with open(f'../../results/gpt-5/{do_rag}/{category}/{contract}/repair_info_{i}.json', 'r') as f:
                    exec_time = json.load(f)['exec_time']
                h, m, s = map(int, exec_time.split(":"))
                time = h*3600 + m*60 + s

                out_lens.append(out_len)
                times.append(time)

                len_time_db.loc[len(len_time_db)] = [category, contract, i, in_len, out_len, in_len+out_len, time]

            mid_out = statistics.median(out_lens)
            mid_time = statistics.median(times)
            mid_len_time_db.loc[len(mid_len_time_db)] = [category, contract, in_len, mid_out, in_len+mid_out, mid_time]

    len_time_db.to_csv(f'../../results/gpt-5/{do_rag}/promptlen_exectime.csv')
    mid_len_time_db.to_csv(f'../../results/gpt-5/{do_rag}/mid_promptlen_exectime.csv')




sum_time_length('rag')    
sum_time_length('no_rag')
