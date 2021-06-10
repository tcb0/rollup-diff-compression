import json
from new import charting

stats_basepath = "../stats"

file_name_mappings = {
    'naive': 'naiveGasCosts.json',
    'compressed': 'compressedGasCosts.json'
}


def make_cmp_charts(dataset: str = 'bricks', enc_type: str = 'rlp', cmp_param: str = 'gasCosts'):
    stats = {
        'naive': {},
        'compressed': {},
        'compressed_bitmaps': {}
    }

    for fn_key, fn in file_name_mappings.items():
        with open(f"{stats_basepath}/{enc_type}/{dataset}/{fn}", "r") as f:
            data = json.loads(f.read())
            for dist_name in data['dists']:
                dist_id = int(dist_name.split('_')[1]) - 1
                stats[fn_key][dist_id] = data['dists'][dist_name][cmp_param]['total']


    title = f"Naive_v_compressed_{enc_type}_{cmp_param}"
    charting.create_gas_cost_diff_chart((stats['naive'], stats['compressed']), (f"Naive {cmp_param}", f"Compressed {cmp_param}"), title, cmp_param, "Distributions", dataset)

    print(f"comparison charts created for: {dataset} {enc_type} {cmp_param}")


def make_savings_charts(dataset: str = 'bricks', enc_type: str = 'rlp', cmp_param: str = 'gasCosts'):
    stats = {
        'compressed_naive': {
            'global': {

            },
            'dists': {

            }
        }
    }

    with open(f"{stats_basepath}/{enc_type}/{dataset}/savings.json", "r") as f:
        data = json.loads(f.read())
        for stats_name in data:
            stats[stats_name]['global'] = data[stats_name]['global']
            for dist_name in data[stats_name]['dists']:
                dist_id = int(dist_name.split('_')[1])
                stats[stats_name]['dists'][dist_id] = data[stats_name]['dists'][dist_name][cmp_param]

    title = f'Compressed_v_naive_savings_{enc_type}_{cmp_param}'
    charting.create_bar_chart(stats['compressed_naive']['dists'], dataset=dataset, title=title, x_label='Dists', y_label=cmp_param, val_key='saving')

    # title = f'Savings_by_strategy_{enc_type}_{cmp_param}'
    # data = {cmp_type: stats[cmp_type]['global'][cmp_param] for cmp_type in stats}
    # charting.create_bar_chart(data, dataset=dataset, title=title, x_label='Strategy type', y_label=cmp_param,
    #                           val_key='saving')


def make_charts():
    datasets = ['bricks', 'moons']
    enc_types = ['rlp', 'native']
    cmp_params = ['gasCosts', 'byteSizes']

    for enc_type in enc_types:
        for dataset in datasets:
            for cmp_param in cmp_params:
                make_cmp_charts(dataset=dataset, enc_type=enc_type, cmp_param=cmp_param)
                make_savings_charts(dataset=dataset, enc_type=enc_type, cmp_param=cmp_param)


if __name__ == '__main__':
    # make_savings_charts()
    make_charts()

