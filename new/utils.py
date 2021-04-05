import csv
import json
import os
from typing import List, Dict, Union


filenames = [
    "round_1_finalized",
    "round_2_finalized",
    "round_3_finalized",
    "round_4_finalized",
    "round_5_finalized",
    "round_6_finalized",
    "round_7_finalized",
    "round_8_finalized",
    "round_9_finalized",
    "round_10_finalized"
]


def get_transactions() -> List[List[dict]]:
    # break data into daily updates
    txs = []
    month_count = 0
    current_month = 0
    for i, filename in enumerate(filenames):
        reader = csv.DictReader(open("data/" + filename + ".csv"))
        for row in reader:
            # get only mints
            month = i

            if current_month != month:
                month_count += 1
                current_month = month

            try:
                txs[month_count].append(row)
            except:
                txs.append([])
                txs[month_count].append(row)

    return txs


def get_user_data(txs) -> Dict[str, Union[Dict[str, float], List[str], Dict[str, list]]]:
    parsed_data_file_path = "./user_data/parsed_user_data.json"

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
            user = tx["username"]
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


def get_repeated_users_data(txs) -> Dict[str, Union[Dict[int, List[str]], Dict[int, int]]]:
    parsed_repeated_user_data = "./user_data/parsed_repeated_user_data.json"

    if os.path.exists(parsed_repeated_user_data):
        with open(parsed_repeated_user_data, "r") as f:
            data = json.loads(f.read())
    else:
        data = make_repeated_users_data(txs)
        with open(parsed_repeated_user_data, "w") as f:
            f.write(json.dumps(data))

    return data


def make_repeated_users_data(txs) -> Dict[str, Union[Dict[int, List[str]], Dict[int, int]]]:
    # TODO: Change this for unique users
    users_per_month = {}
    # get users per month
    for i, month in enumerate(txs):
        users_per_month[i] = []
        for tx in month:
            user = tx["username"]
            users_per_month[i].append(user)

    # get repeated users per month
    repeated_users_per_month = {}
    for i, month in enumerate(txs):
        repeated_users_per_month[i] = {}
        # previous months loop
        for j in range(0, i):
            repeated_users_per_month[i][j] = 0
            for tx in month:
                user = tx['username']
                if user in users_per_month[j]:
                    repeated_users_per_month[i][j] += 1

    return {'users': users_per_month, 'repeated_users': repeated_users_per_month}
