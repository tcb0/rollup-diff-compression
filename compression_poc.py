# Reddit bricks (FortniteBR contracts):
# https://rinkeby.etherscan.io/address/0xb28e596e801c8631662c1f355213a72981c267aa#code
# https://rinkeby.etherscan.io/address/0x8fdc779f1e8ae2256c663cd80e8d090c4523f159#code
# https://rinkeby.etherscan.io/token/0xe0d8d7b8273de14e628d2f2a4a10f719f898450a?a=0x1F0569682c4146c8540a7b987142899E788caeFd#readProxyContract
import csv
from typing import List
import matplotlib.pyplot as plt

import pdb

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


def same_amount_monthly(month: List[float]) -> int:

    amount_occurences = {}
    for num in month:
        if num in amount_occurences:
            amount_occurences[num] += 1
        else:
            amount_occurences[num] = 1

    total_compressed_gas_cost = 0
    for karma, num_repeats in amount_occurences.items():
        total_bits_for_addresses = num_repeats * 17
        total_bits_for_amount = 16
        total_bits_for_airdrop = total_bits_for_addresses + total_bits_for_amount
        gas_cost_for_grouped_item = total_bits_for_airdrop * 7
        total_compressed_gas_cost += gas_cost_for_grouped_item

    return total_compressed_gas_cost

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


def make_user_data(txs):
    users = {}
    repeat_users = []
    user_txs = {}
    for i, month in enumerate(txs):
        for tx in month:
            user = tx["username"]

            # shows what month the tx was from
            tx["month"] = i
            if user in users.keys():
                users[user] += float(tx["karma"])
                user_txs[user].append(tx)
                if user not in repeat_users:
                    repeat_users.append(user)
            else:
                users[user] = float(tx["karma"])
                user_txs[user] = [tx]

    return users, repeat_users, user_txs


def get_karma_for_each_month(txs: List[List[dict]]) -> List[List[float]]:
    months = [[] for i in txs]

    for i, monthly_txs in enumerate(txs):
        for tx in monthly_txs:
            months[i].append(float(tx["karma"]))

    return months


def get_total_gas_cost_naive(txs: List[List[dict]], naive_gas_cost_per_airdrop: int):
    brick_distributions = len(txs)

    total_airdrops = 0

    for i in range(0, brick_distributions):
        airdrops_per_distribution = len(txs[i])
        total_airdrops += airdrops_per_distribution

    total_gas_cost = naive_gas_cost_per_airdrop * total_airdrops

    return total_gas_cost


def get_total_gas_cost_compressed_same_amounts(txs: List[List[dict]]):
    months_karma = get_karma_for_each_month(txs)
    compressed_gas_cost = sum([same_amount_monthly(month_karma) for month_karma in months_karma])
    return compressed_gas_cost


def get_gas_cost_stats_may(txs: List[List[dict]], naive_gas_cost_per_airdrop: int):

    total_gas_cost_naive = get_total_gas_cost_naive(txs, naive_gas_cost_per_airdrop)
    total_gas_cost_compressed_same_amounts = get_total_gas_cost_compressed_same_amounts(txs)

    print("May Amount gas cost naive", total_gas_cost_naive)
    print("May Amount gas cost compressed same amounts", total_gas_cost_compressed_same_amounts)

    print("May Gas saved: ", total_gas_cost_naive - total_gas_cost_compressed_same_amounts)
    print("May Gas saved percent: ",
          (total_gas_cost_naive - total_gas_cost_compressed_same_amounts) / total_gas_cost_naive * 100)


def main():

    txs = get_transactions()

    naive_gas_cost_per_airdrop = 231

    total_gas_cost_naive = get_total_gas_cost_naive(txs, naive_gas_cost_per_airdrop)
    total_gas_cost_compressed_same_amounts = get_total_gas_cost_compressed_same_amounts(txs)

    print("Amount gas cost naive", total_gas_cost_naive)
    print("Amount gas cost compressed same amounts", total_gas_cost_compressed_same_amounts)

    print("Gas saved: ", total_gas_cost_naive - total_gas_cost_compressed_same_amounts)
    print("Gas saved percent: ", (total_gas_cost_naive - total_gas_cost_compressed_same_amounts) / total_gas_cost_naive * 100)

    get_gas_cost_stats_may([txs[0]], naive_gas_cost_per_airdrop)

    users, repeat_users, user_txs = make_user_data(txs)
    total_users = len(users.keys())
    total_repeat_users = len(repeat_users)
    print("Total users: ", total_users)
    print("Repeat users: ", total_repeat_users)

    print("Repeat users percent: ", (total_repeat_users / total_users) * 100)

    #
    # months = get_karma_for_each_month(txs)
    #
    # amount_gas_cost_may = len(txs[0]) * naive_gas_cost_per_airdrop
    #
    # compressed_amount_may = same_amount_monthly(months[0])




if __name__ == '__main__':
    main()