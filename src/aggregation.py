import json
import csv
from decimal import Decimal, ROUND_DOWN
import os


class Aggregation:

    def sum_results(self, results_file, model, do_rag):
        with open(results_file, 'r') as f:
            results = json.load(f) 

        total_result = {
            'total_contract': 0,
            'total_patch':0,
            'contract':{'format':0, 'compilable':0, 'non-vulnerable':0, 'no-add-vul':0, 'functionality':0},
            'patch':{'format':0, 'compilable':0, 'non-vulnerable':0, 'no-add-vul':0, 'functionality':0},
        }
         
        criteria = ('format', 'compilable', 'non-vulnerable', 'no-add-vul', 'functionality')

        for i, vul_results in enumerate(results['repair_results']):
            vul_result = {
                'total_contract':0,
                'total_patch':0,
                'contract':{'format':0, 'compilable':0, 'non-vulnerable':0, 'no-add-vul':0, 'functionality':0},
                'patch': {'format':0, 'compilable':0, 'non-vulnerable':0, 'no-add-vul':0, 'functionality':0},
            }


            for file_results in vul_results['repair_result_list']:
                vul_result['total_contract'] += 1
                vul_result['total_patch'] += 5
                self.update_count_by_adding(vul_result['patch'], self.count_criteria(file_results['results'], criteria))
                self.update_count_by_adding(vul_result['contract'], file_results['results']['contract_results'])

            vul_type = vul_results['vul_type']
            self.output_count_data_csv(vul_result, f'../results/{model}/{do_rag}/sum_data/{vul_type}_result.csv', criteria, vul_type)

            #vulごとの結果をrepair_resultsに追記
            results['repair_results'][i]['satisfying_criteria_count'] = vul_result


            # total_resultsに追加
            total_result['total_contract'] += vul_result['total_contract']
            total_result['total_patch'] += vul_result['total_patch']
            for key in ['contract', 'patch']:
                self.update_count_by_adding(total_result[key], vul_result[key])

        results['satisfying_criteria_count'] = total_result
        self.output_count_data_csv(total_result, f'../results/{model}/{do_rag}/sum_data/total_result.csv', criteria, 'total')

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2) 

    def count_criteria(self, results, keys):
        counts = {k: 0 for k in keys}

        for item in results['patch_results']:
            for k in keys:
                if item.get(k) is True:
                    counts[k] += 1

        return counts

    def update_count_by_adding(self, total, added):
        """
        total: 加算先の dict（破壊的に更新）
        added: 加算元の dict
        """
        for k, v in added.items():
            total[k] = total.get(k, 0) + v

    def output_count_data_csv(self, result, output_file, criteria, vul_type):
        '''
        ---------- | total_C | total_P | format_C | format_P | compilable_C | compilable_P | ... | functionality_C | functionality_P |
        original   |   xx    |   xx    |
        ori_rate   |   --    |   --    |
        obfuscated |   xx    |   xx    |
        obf_rate   |   --    |   --    |
        '''

        mapping = {
            'C': ('contract', 'total_contract'),
            'P': ('patch', 'total_patch'),
        }


        count_data = {
            'success_count':{},
            'success_rate':{},
        }
         
        count_data['success_count']['total_C'] = result['total_contract']
        count_data['success_count']['total_P'] = result['total_patch']

        for c in criteria:
            for k, (data_key, total_key) in mapping.items():
                count_value = result[data_key][c]

                count_data['success_count'][f'{c}_{k}'] = count_value
                count_data['success_rate'][f'{c}_{k}'] = self.truncate3(count_value / result[total_key] * 100)


        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[vul_type] + list(count_data['success_count'].keys()))
            writer.writeheader()

            for row in count_data.keys():
                writer.writerow({vul_type: row, **count_data[row]})


    def truncate3(self, value):
        return float(
            Decimal(str(value)).quantize(
                Decimal('0.000'),
                rounding=ROUND_DOWN
            )
        )

    def combine_rag_norag_result(self, model):
        csv_list = os.listdir(f'../results/{model}/rag/sum_data')
        os.makedirs(f'../results/{model}/sum_data', exists_ok=True)

        for csv_file in csv_list:
            with open(f'../results/{model}/rag/sum_data/{csv_file}', 'r', newline="") as f1, \
                 open(f'../results/{model}/no_rag/sum_data/{csv_file}', 'r',  newline="") as f2, \
                 open(f'../results/{model}/sum_data/{csv_file}', 'w', newline="") as out:

                rag_reader = csv.reader(f1)
                no_rag_reader = csv.reader(f2)
                writer = csv.writer(out)

                # ヘッダー
                header = next(rag_reader)
                next(no_rag_reader)
                writer.writerow(header)

                # 1個目
                for row in rag_reader:
                    row[0] = "rag_" + row[0]   # A列
                    writer.writerow(row)

                # 2個目
                for row in no_rag_reader:
                    row[0] = "no_rag_" + row[0]
                    writer.writerow(row)


if __name__ == '__main__':
    Aggregation().combine_rag_norag_result('gpt-5')









