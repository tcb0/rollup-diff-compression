# Reddit bricks (FortniteBR contracts):
# https://rinkeby.etherscan.io/address/0xb28e596e801c8631662c1f355213a72981c267aa#code
# https://rinkeby.etherscan.io/address/0x8fdc779f1e8ae2256c663cd80e8d090c4523f159#code
# https://rinkeby.etherscan.io/token/0xe0d8d7b8273de14e628d2f2a4a10f719f898450a?a=0x1F0569682c4146c8540a7b987142899E788caeFd#readProxyContract
from typing import List, Dict
from new.utils import get_user_data, get_transactions, get_repeated_users_data, get_parsed_users_data


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


def get_cumulative_gas_costs_per_month_with_savings(gas_costs_per_month: Dict[int, int], gas_costs_per_month_compressed_same_amounts: Dict[int, int]) -> Dict[int, Dict[str, int]]:

    gas_costs_cumulative = {}

    for month_id, gas_cost_per_month in gas_costs_per_month.items():

        if month_id != 0:
            gas_costs_cumulative[month_id] = {
                'native': gas_costs_cumulative[month_id - 1]['native'] + gas_cost_per_month,
                'compressed': gas_costs_cumulative[month_id - 1]['compressed'] + gas_costs_per_month_compressed_same_amounts[month_id]
            }
        else:
            gas_costs_cumulative[month_id] = {
                'native': gas_cost_per_month,
                'compressed': gas_costs_per_month_compressed_same_amounts[month_id]
            }

        gas_costs_cumulative[month_id]['savings'] = gas_costs_cumulative[month_id]['native'] - gas_costs_cumulative[month_id]['compressed']

    return gas_costs_cumulative


def get_stats_naive_vs_compressed(txs: List[List[dict]], airdrops_per_month: Dict[int, int], naive_gas_cost_per_airdrop: int):

    print("Airdrops per month", airdrops_per_month)

    gas_cost_per_month_naive = get_gas_costs_per_month(airdrops_per_month, naive_gas_cost_per_airdrop)
    gas_cost_per_month_compressed = get_gas_costs_per_month_compressed(txs)

    print("Gas cost per month naive", gas_cost_per_month_naive)
    print("Gas cost per month compressed", gas_cost_per_month_compressed)

    gas_costs_cumulative_with_savings = get_cumulative_gas_costs_per_month_with_savings(gas_cost_per_month_naive, gas_cost_per_month_compressed)

    print("Gas cost per month cumulative with savings: ", gas_costs_cumulative_with_savings)

    total_gas_cost_naive = get_total_gas_cost(gas_cost_per_month_naive)
    total_gas_cost_compressed_same_amounts = get_total_gas_cost(gas_cost_per_month_compressed)

    print("Total gas cost naive", total_gas_cost_naive)
    print("Total gas cost compressed same amounts", total_gas_cost_compressed_same_amounts)

    print("Gas saved: ", total_gas_cost_naive - total_gas_cost_compressed_same_amounts)
    print("Gas saved percent: ", (total_gas_cost_naive - total_gas_cost_compressed_same_amounts) / total_gas_cost_naive * 100)

    get_stats_for_month_may(gas_cost_per_month_naive[0], gas_cost_per_month_compressed[0])


def get_permutations_savings_all_data(txs: List[List[dict]], num_distributions: int):
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

    # check_if_permutations_are_unique(permutations)
    sorted_permutations = {k: v for k, v in sorted(permutations.items(), key=lambda item: item[1], reverse=True)}
    print("Sorted permutations", sorted_permutations)
    print("Total permutations", len(permutations.keys()))
    print("Total repeated users in permutations", sum(permutations.values()))

    permutations_savings = get_gas_cost_savings_by_reusing_groups_all_data(txs, permutations, repeated_users, 2)
    print("Permutations savings per month", permutations_savings)
    print("Permutations savings total", sum(permutations_savings))


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


def check_if_permutations_are_unique(permutations: Dict[str, int]):
    print("Permutations", permutations)

    unique_permutations = {}
    permutation_keys = permutations.keys()
    for key in permutation_keys:
        if key in unique_permutations:
            unique_permutations[key] += 1
        else:
            unique_permutations[key] = 1

    total_unique_permutations = sum(unique_permutations.values())
    print("Total unique permutations sum values:", total_unique_permutations)
    print("Total unique permutations keys:", len(unique_permutations.keys()))


def get_gas_cost_savings_by_reusing_groups_all_data(txs: List[List[dict]], permutations: Dict[str, int], repeated_users: List[str], gas_per_bit: int) -> List[int]:

    savings = [0] * (len(txs) + 1)

    for permutation_key, repeated_user_per_group in permutations.items():

        # back to list format
        perm_key_str = permutation_key[1:-1].split(",")
        perm_key_list = [int(x) for x in perm_key_str]

        source = 0

        for i, x in enumerate(perm_key_list):

            # find the group to permute
            if source != 0:
                if x == 0:
                    continue
                else:

                    # calculate how much the permute costs
                    cost_of_permutation = source * gas_per_bit * 1

                    savings[i] += (repeated_user_per_group * gas_per_bit * 17) - cost_of_permutation
                    source = len(txs[i])
            if x != 0:
                source = len(txs[i])

    return savings


def get_permutations_savings_previous_data(parsed_data: dict, bits_per_address=17, bits_per_balance=16, gas_cost_per_bit_total=7):

    gas_cost_per_airdrop = (bits_per_address + bits_per_balance) * gas_cost_per_bit_total

    for distribution_id, distribution_data in parsed_data.items():
        distribution_data['gas_cost'] = 0

        if distribution_id == 0:
            distribution_data['gas_cost'] = distribution_data['num_users'] * gas_cost_per_airdrop
            continue

        for user_key, user_data in distribution_data['users'].items():

            num_repeats = sum(user_data['repeats_in_prev_months'])
            user_gas_cost = 0

            if num_repeats == 0:
                # unique user
                user_gas_cost = gas_cost_per_airdrop
            else:
                user_gas_cost = bits_per_balance * gas_cost_per_bit_total + 1 # gas bits for

            distribution_data['gas_cost'] += user_gas_cost

    total_gas_cost = 0
    for distribution_id, distribution_data in parsed_data.items():
        total_gas_cost += distribution_data['gas_cost']
        print("Gas cost per distribution", distribution_id, distribution_data['gas_cost'])

    print("Total gas cost", total_gas_cost)


def main():

    txs = get_transactions()
    num_distributions = len(txs)
    naive_gas_cost_per_airdrop = 231
    airdrops_per_month = get_airdrops_per_month(txs)

    print("Stats naive vs compressed:")
    print("\n===========================================================================\n")
    get_stats_naive_vs_compressed(txs, airdrops_per_month, naive_gas_cost_per_airdrop)
    print("\n===========================================================================\n")

    print("Savings from permutations compared to naive (all data):")
    print("\n===========================================================================\n")
    get_permutations_savings_all_data(txs, num_distributions)
    print("\n===========================================================================\n")

    parsed_data = get_parsed_users_data(cached=False)
    for distribution_id, distribution_data in parsed_data.items():
        print(distribution_id, distribution_data['num_users'], distribution_data['num_unique_users'], distribution_data['permutations'])
    # print(txs_dict)

    print("Savings from permutations compared to naive (previous data):")
    print("\n===========================================================================\n")
    get_permutations_savings_previous_data(parsed_data)
    print("\n===========================================================================\n")


    # print(txs_dict)

if __name__ == '__main__':
    main()
