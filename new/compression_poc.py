# Reddit bricks (FortniteBR contracts):
# https://rinkeby.etherscan.io/address/0xb28e596e801c8631662c1f355213a72981c267aa#code
# https://rinkeby.etherscan.io/address/0x8fdc779f1e8ae2256c663cd80e8d090c4523f159#code
# https://rinkeby.etherscan.io/token/0xe0d8d7b8273de14e628d2f2a4a10f719f898450a?a=0x1F0569682c4146c8540a7b987142899E788caeFd#readProxyContract
from typing import List, Dict
from new.utils import get_user_data, get_transactions


def get_airdrops_per_month(txs: List[List[dict]]) -> Dict[int, int]:
    airdrops_per_month = {i: len(txs_per_month) for i, txs_per_month in enumerate(txs)}
    return airdrops_per_month


def get_total_gas_cost(gas_costs_per_month: Dict[int, int]):
    return sum(gas_costs_per_month.values())


def get_gas_costs_per_month(airdrops_per_month: Dict[int, int], naive_gas_cost_per_airdrop: int):
    gas_costs_per_month = {month_id: airdrops * naive_gas_cost_per_airdrop for month_id, airdrops in airdrops_per_month.items()}
    return gas_costs_per_month


def get_gas_costs_per_month_compressed(txs: List[List[dict]]) -> dict:
    gas_costs_per_month_compressed = {}
    amounts_for_all_months = get_amounts_for_each_month(txs)
    for month_id, amounts_per_month in enumerate(amounts_for_all_months):
        gas_costs_per_month_compressed[month_id] = same_amount_monthly(amounts_per_month)

    return gas_costs_per_month_compressed


def get_amounts_for_each_month(txs: List[List[dict]]) -> List[List[float]]:
    months = [[] for i in txs]

    for i, monthly_txs in enumerate(txs):
        for tx in monthly_txs:
            months[i].append(float(tx["karma"]))

    return months


def same_amount_monthly(month_amounts: List[float]) -> int:
    amount_occurrences = {}
    for amount in month_amounts:
        if amount in amount_occurrences:
            amount_occurrences[amount] += 1
        else:
            amount_occurrences[amount] = 1

    total_compressed_gas_cost = 0
    for karma, num_repeats in amount_occurrences.items():
        total_bits_for_addresses = num_repeats * 17
        total_bits_for_amount = 16
        total_bits_for_airdrop = total_bits_for_addresses + total_bits_for_amount
        gas_cost_for_grouped_item = total_bits_for_airdrop * 7
        total_compressed_gas_cost += gas_cost_for_grouped_item

    return total_compressed_gas_cost


def get_stats_for_month_may(total_gas_cost_naive: int, total_gas_cost_compressed_same_amounts: int):

    print("May Amount gas cost naive", total_gas_cost_naive)
    print("May Amount gas cost compressed same amounts", total_gas_cost_compressed_same_amounts)

    print("May Gas saved: ", total_gas_cost_naive - total_gas_cost_compressed_same_amounts)
    print("May Gas saved percent: ",
          (total_gas_cost_naive - total_gas_cost_compressed_same_amounts) / total_gas_cost_naive * 100)


def get_stats_naive_vs_compressed(txs: List[List[dict]], airdrops_per_month: Dict[int, int], naive_gas_cost_per_airdrop: int):

    print("Airdrops per month", airdrops_per_month)

    gas_cost_per_month_naive = get_gas_costs_per_month(airdrops_per_month, naive_gas_cost_per_airdrop)
    gas_cost_per_month_compressed = get_gas_costs_per_month_compressed(txs)

    print("Gas cost per month naive", gas_cost_per_month_naive)
    print("Gas cost per month compressed", gas_cost_per_month_compressed)

    total_gas_cost_naive = get_total_gas_cost(gas_cost_per_month_naive)
    total_gas_cost_compressed_same_amounts = get_total_gas_cost(gas_cost_per_month_compressed)

    print("Total gas cost naive", total_gas_cost_naive)
    print("Total gas cost compressed same amounts", total_gas_cost_compressed_same_amounts)

    print("Gas saved: ", total_gas_cost_naive - total_gas_cost_compressed_same_amounts)
    print("Gas saved percent: ", (total_gas_cost_naive - total_gas_cost_compressed_same_amounts) / total_gas_cost_naive * 100)

    get_stats_for_month_may(gas_cost_per_month_naive[0], gas_cost_per_month_compressed[0])


def get_permutations_per_distribution(repeated_users: List[str], user_txs: Dict[str, list], num_distributions: int) -> Dict[str, int]:
    repeats = {}
    # Gets repeats, permutations for user appearance in each month
    for user in repeated_users:
        user_repeat = [0] * num_distributions
        for tx in user_txs[user]:
            user_repeat[tx["month"]] = 1

        user_repeat_key = str(user_repeat)
        if user_repeat_key in repeats:
            repeats[user_repeat_key] += 1
        else:
            repeats[user_repeat_key] = 1

    return repeats


def main():

    txs = get_transactions()
    num_distributions = len(txs)
    naive_gas_cost_per_airdrop = 231
    airdrops_per_month = get_airdrops_per_month(txs)

    # print("Stats naive vs compressed:")
    # print("\n===========================================================================\n")
    # get_stats_naive_vs_compressed(txs, airdrops_per_month, naive_gas_cost_per_airdrop)
    # print("\n===========================================================================\n")

    user_data = get_user_data(txs)

    users = user_data['users']
    repeated_users = user_data['repeated_users']
    user_txs = user_data['user_txs']

    total_users = len(users.keys())
    total_repeated_users = len(repeated_users)

    print("Number of airdrop distributions: ", num_distributions)

    print("Total users: ", total_users)
    print("Repeat users: ", total_repeated_users)

    print("Repeat users percent: ", (total_repeated_users / total_users) * 100)

    permutations = get_permutations_per_distribution(repeated_users, user_txs,  num_distributions)

    print("Permutations", permutations)
    print("Total permutations", len(permutations.keys()))


if __name__ == '__main__':
    main()
