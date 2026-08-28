import json




def count_exec_time(file):
    with open(file, 'r') as f:
        result = json.load(f)

    total_patch = 0
    total_time = 0
    for repair_results in result['repair_results']:
        for result_list in repair_results['repair_result_list']:
            for result in result_list['results']['patch_results']:
                total_time += result['exec_time_sec']
                # print(result['exec_time_sec'])
                total_patch += 1

    return total_time, total_patch


time, patch = count_exec_time('../../results/gpt-5/rag/repair_results_numcodelines.json')
print('rag_results')
print(time)
print(time/patch)

time, patch = count_exec_time('../../results/gpt-5/no_rag/repair_results_numcodelines.json')
print('no_rag_results')
print(time)
print(time/patch)
