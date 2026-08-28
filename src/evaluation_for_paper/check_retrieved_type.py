import os
import json



total = 0

for category in os.listdir(f'../../dataset/mitigate_patches'):

    vul_total = 0
    if not os.path.isdir(f'../../dataset/mitigate_patches/{category}'):
        continue

    for contract in os.listdir(f'../../dataset/mitigate_patches/{category}'):
        if not os.path.isdir(f'../../dataset/mitigate_patches/{category}/{contract}'):
           continue


        with open(f'../../results/gpt-5/rag/{category}/{contract}/repair_info_0.json', 'r') as f:
            inf = json.load(f)

        if category != inf['rag_info']['nearest_category']:
            print(f'\tDifferent TYPE!!!:{category}/{contract}')
            print(f'\tRetrieved: {inf['rag_info']['nearest_category']}')
            total += 1
            vul_total += 1

    print(f'{category}, difftype: {vul_total}')

print(f'total, difftype: {total}')

