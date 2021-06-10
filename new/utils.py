import csv
import json
import os
import glob
from typing import List, Dict, Union


def get_file_paths(dataset: str):
    paths = glob.glob(f"../data/{dataset}/*.csv")
    paths = sorted(paths, key=lambda filename: int(filename.split('_')[1]))
    return paths


def get_transactions(dataset: str) -> List[List[dict]]:
    txs = []
    paths = get_file_paths(dataset)
    for i, path in enumerate(paths):
        reader = csv.DictReader(open(path))
        txs.append([])
        for row in reader:
            if not row['blockchain_address'] or not row['karma']:
                continue

            txs[i].append(row)

    return txs


# Returns dictionary in the form:
#   {
#    `month_id`: {
#       `num_users`: 5,
#       `sum_users_prev_months`: 0,
#       `num_unique_users`: 0, # the number of unique users per distribution
#       `permutations`: {}, # dict of permutation keys and repeats per key (used to determine how the users are distributed in regards of the previous months), contains permutations for the previous distributions only
#       `users`: {
#           `blockchain_address`: {
#             `karma`: 5,
#             `repeats_in_prev_months`: [] # list with length of the previous distributions
#            },
#            ...
#        }
#    }
#     ...
#   }
def get_parsed_users_data(dataset: str, cached=False) -> dict:
    parsed_data_file_path = f"../user_data/{dataset}/parsed_transactions_dict.json"

    if os.path.exists(parsed_data_file_path) and cached:
        with open(parsed_data_file_path, "r") as f:
            data = json.loads(f.read())
    else:
        data = make_parsed_users_data(dataset)
        with open(parsed_data_file_path, "w") as f:
            f.write(json.dumps(data))

    return data


def make_parsed_users_data(dataset: str) -> dict:
    txs = {}
    paths = get_file_paths(dataset)
    for i, path in enumerate(paths):
        reader = csv.DictReader(open(path))
        txs[i] = {
            'num_users': 0,
            'sum_users_prev_months': 0,
            'num_unique_users': 0,
            'permutations': {},
            'users': {},
        }
        for row in reader:

            if not row['blockchain_address'] or not row['karma']:
                continue

            txs[i]['users'][row['blockchain_address']] = {
                'karma': row['karma'],
                'repeats_in_prev_months': [],
            }

        txs[i]['num_users'] = len(txs[i]['users'].keys())

    txs = add_user_repeats_and_permutations(txs)
    verify_permutations(txs)

    return txs


def add_user_repeats_and_permutations(txs: dict) -> dict:

    for distribution_id, distribution_data in txs.items():
        # previous months loop
        # determine user repeats per month
        for j in range(0, distribution_id):

            for user in distribution_data['users'].keys():

                if len(distribution_data['users'][user]['repeats_in_prev_months']) == 0:
                    distribution_data['users'][user]['repeats_in_prev_months'] = [0]*distribution_id

                if user in txs[j]['users']:
                    distribution_data['users'][user]['repeats_in_prev_months'][j] = 1


    for distribution_id, distribution_data in txs.items():

        for user in distribution_data['users'].keys():
            user_repeats = distribution_data['users'][user]['repeats_in_prev_months']
            permutation_key_str = str(user_repeats)
            repeats_sum = sum(user_repeats)

            if repeats_sum == 0:
                distribution_data['num_unique_users'] += 1

            if permutation_key_str not in distribution_data['permutations']:
                distribution_data['permutations'][permutation_key_str] = 1
            else:
                distribution_data['permutations'][permutation_key_str] += 1

    return txs


def verify_permutations(txs):

    verify_list = []

    for month_id, month_data in txs.items():
        num_users = month_data['num_users']
        users_in_permutations = sum(month_data['permutations'].values())
        verify_list.append(num_users == users_in_permutations)

    print("Users in month match the sum of the permuted groups: ", verify_list)


def get_user_data(dataset: str, txs) -> Dict[str, Union[Dict[str, float], List[str], Dict[str, list]]]:
    parsed_data_file_path = f"../user_data/{dataset}/parsed_user_data.json"

    if os.path.exists(parsed_data_file_path):
        with open(parsed_data_file_path, "r") as f:
            data = json.loads(f.read())
    else:
        data = make_user_data(txs)
        with open(parsed_data_file_path, "w") as f:
            f.write(json.dumps(data))

    return data


def make_user_data(txs) -> Dict[str, Union[Dict[str, float], List[str], Dict[str, list]]]:
    users = {}
    repeated_users = []
    user_txs = {}
    # get general user data
    for i, month in enumerate(txs):
        for tx in month:
            user = tx["blockchain_address"]
            # shows what month the tx was from
            tx["month"] = i
            if user in users.keys():
                users[user] += float(tx["karma"])
                user_txs[user].append(tx)
                if user not in repeated_users:
                    repeated_users.append(user)
            else:
                users[user] = float(tx["karma"])
                user_txs[user] = [tx]

    return {'users': users, 'repeated_users': repeated_users, 'user_txs': user_txs}


def get_repeated_users_data(dataset: str, txs) -> Dict[str, Union[Dict[int, List[str]], Dict[int, int]]]:
    parsed_repeated_user_data = f"../user_data/{dataset}/parsed_repeated_user_data.json"

    if os.path.exists(parsed_repeated_user_data):
        with open(parsed_repeated_user_data, "r") as f:
            data = json.loads(f.read())
    else:
        data = make_repeated_users_data(txs)
        with open(parsed_repeated_user_data, "w") as f:
            f.write(json.dumps(data))

    return data


def make_repeated_users_data(txs) -> Dict[str, Union[Dict[int, List[str]], Dict[int, int]]]:
    users_per_month = {}
    # get users per month
    for i, month in enumerate(txs):
        users_per_month[i] = []
        for tx in month:
            user = tx["blockchain_address"]
            users_per_month[i].append(user)

    # get repeated users per month
    repeated_users_per_month = {}
    for i, month in enumerate(txs):
        repeated_users_per_month[i] = {}
        # previous months loop
        for j in range(0, i):
            repeated_users_per_month[i][j] = 0
            for tx in month:
                user = tx['blockchain_address']
                if user in users_per_month[j]:
                    repeated_users_per_month[i][j] += 1

    return {'users': users_per_month, 'repeated_users': repeated_users_per_month}

