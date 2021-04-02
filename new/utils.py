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


def make_user_data(txs) -> Dict[str, Union[Dict[str, float], List[str], Dict[str, list]]]:
    users = {}
    repeated_users = []
    user_txs = {}
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

