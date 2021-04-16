# Reddit bricks (FortniteBR contracts):
# https://rinkeby.etherscan.io/address/0xb28e596e801c8631662c1f355213a72981c267aa#code
# https://rinkeby.etherscan.io/address/0x8fdc779f1e8ae2256c663cd80e8d090c4523f159#code
# https://rinkeby.etherscan.io/token/0xe0d8d7b8273de14e628d2f2a4a10f719f898450a?a=0x1F0569682c4146c8540a7b987142899E788caeFd#readProxyContract
from typing import List, Dict, Union, Tuple
from new.utils import get_user_data, get_transactions, get_repeated_users_data, get_parsed_users_data

# global params

BITS_USER_ID = 17
BITS_USER_BALANCE = 16
BITS_PERMUTATION = 1
BITS_PREV_REFERENCE = 1
GAS_COST_BIT = 7
TOTAL_GAS_COST_AIRDROP = (BITS_USER_ID + BITS_USER_BALANCE) * GAS_COST_BIT
GROUPING_BY_AMOUNT_RANGE_VALUES = [1, 2, 5, 10, 15, 20, 50]
GROUPING_BY_NUMBER_OF_AMOUNTS_VALUES = [2, 5, 10, 20, 50, 100]


def get_max_karma(parsed_data: dict):
    max_karma = 0

    for distribution_data in parsed_data.values():
        for user in distribution_data['users'].values():
            user_karma_int = int(user['karma'])
            if user_karma_int >= max_karma:
                max_karma = user_karma_int

    return max_karma


def get_max_karma_diff(parsed_data: dict):
    user_karmas = get_user_karmas(parsed_data)

    max_karma_diff = 0
    for user, karmas in user_karmas.items():
        for i, karma in enumerate(karmas):
            if i > 0:
                curr_karma_diff = abs(int(karma) - int(karmas[i-1]))
                if curr_karma_diff > max_karma_diff:
                    max_karma_diff = curr_karma_diff

    return max_karma_diff


def get_user_karmas(parsed_data: dict):

    user_karmas = {}
    for distribution_data in parsed_data.values():
        for user, user_data in distribution_data['users'].items():
            if user not in user_karmas:
                user_karmas[user] = []
            user_karmas[user].append(user_data['karma'])

    return user_karmas



def get_airdrops_per_month(txs: List[List[dict]]) -> Dict[int, int]:
    airdrops_per_month = {i: len(txs_per_month) for i, txs_per_month in enumerate(txs)}
    return airdrops_per_month


def get_total_gas_cost(gas_costs_per_month: Dict[int, int]):
    return sum(gas_costs_per_month.values())


def get_gas_costs_per_dist(airdrops_per_month: Dict[int, int]):
    gas_costs_per_dist = {dist_id: airdrops * TOTAL_GAS_COST_AIRDROP for dist_id, airdrops in
                          airdrops_per_month.items()}
    return gas_costs_per_dist


def get_gas_costs_per_dist_compressed(txs: List[List[dict]]) -> dict:
    gas_costs_per_dist_compressed = {}
    amounts_for_all_dists = get_amounts_for_each_dist(txs)
    for month_id, amount_per_dist in enumerate(amounts_for_all_dists):
        amount_occurrences = get_unique_amounts_per_distribution(amount_per_dist)
        gas_costs_per_dist_compressed[month_id] = same_amount_per_dist(amount_occurrences)[0]

    return gas_costs_per_dist_compressed


def get_gas_costs_per_dist_compressed_grouped_by_value_range(txs: List[List[dict]]) -> dict:

    gas_costs_per_dist_compressed = {grouping_range: {dist_id: 0 for dist_id in range(0, len(txs))} for grouping_range in GROUPING_BY_AMOUNT_RANGE_VALUES}

    dists_amounts = get_amounts_for_each_dist(txs)

    print("\nDists stats value range\n")

    for amount_range in GROUPING_BY_AMOUNT_RANGE_VALUES:
        unique_amounts_dists = group_amounts_by_value_range(dists_amounts, amount_range)
        gas_costs = {}
        amounts = {}
        for dist_id, unique_amount_dist in enumerate(unique_amounts_dists):
            gas_cost_dist, unique_groups_dist = same_amount_per_dist(unique_amount_dist)
            gas_costs_per_dist_compressed[amount_range][dist_id] = gas_cost_dist
            gas_costs[dist_id] = gas_cost_dist
            amounts[dist_id] = unique_groups_dist

        print(f"Dists stats for amount range: {amount_range}, total gas cost: {sum(gas_costs.values())}, total num amounts: {sum(amounts.values())}, gas costs: {gas_costs}, num amounts: {amounts}")

    return gas_costs_per_dist_compressed


def get_gas_costs_per_dist_compressed_grouped_by_number_of_values(txs: List[List[dict]]) -> dict:
    gas_costs_per_dist_compressed = {grouping_range: {dist_id: 0 for dist_id in range(0, len(txs))} for grouping_range in GROUPING_BY_NUMBER_OF_AMOUNTS_VALUES}

    dists_amounts = get_amounts_for_each_dist(txs)

    print("\nDists stats number of values in group\n")


    for amount_range in GROUPING_BY_NUMBER_OF_AMOUNTS_VALUES:
        dists_grouped_amounts = group_amounts_by_number_of_values(dists_amounts, amount_range)
        gas_costs = {}
        groups = {}
        for dist_id, dist_grouped_amount in enumerate(dists_grouped_amounts):
            gas_cost_dist, unique_groups_dist = same_amount_per_dist(dist_grouped_amount)
            gas_costs_per_dist_compressed[amount_range][dist_id] = gas_cost_dist
            gas_costs[dist_id] = gas_cost_dist
            groups[dist_id] = unique_groups_dist

        print(f"Dists stats for amount range: {amount_range}, total gas cost: {sum(gas_costs.values())}, total groups: {sum(groups.values())}, gas costs: {gas_costs}, groups: {groups}")

    return gas_costs_per_dist_compressed


def get_amounts_for_each_dist(txs: List[List[dict]]) -> List[List[float]]:
    months = [[] for i in txs]

    for i, monthly_txs in enumerate(txs):
        for tx in monthly_txs:
            months[i].append(float(tx["karma"]))

    return months


def group_amounts_by_value_range(dist_amounts: List[List[float]], amount_range: int) -> List[Dict[float, int]]:
    grouped_amounts = []
    for i, amounts in enumerate(dist_amounts):
        amounts.sort()
        curr_amount = 0
        amount_occurrences = {}
        for amount in amounts:

            if (amount - curr_amount > amount_range) or curr_amount == 0:
                curr_amount = amount
                amount_occurrences[curr_amount] = 1
            else:
                amount_occurrences[curr_amount] += 1

        grouped_amounts.append(amount_occurrences)

    return grouped_amounts


def group_amounts_by_number_of_values(dist_amounts: List[List[float]], amount_range: int) -> List[Dict[float, int]]:
    grouped_amounts = []
    for i, amounts in enumerate(dist_amounts):
        amounts.sort()
        groups = {}
        group_id = 0
        for amount in amounts:

            if group_id == 0 or groups[group_id] == amount_range:
                group_id += 1
                groups[group_id] = 1
            else:
                groups[group_id] += 1

        grouped_amounts.append(groups)

    return grouped_amounts


def same_amount_per_dist(amount_occurrences: Dict[float, int]) -> Tuple[int, int]:

    total_compressed_gas_cost = 0
    for karma, num_repeats in amount_occurrences.items():
        total_bits_for_addresses = num_repeats * BITS_USER_ID
        total_bits_for_airdrop = total_bits_for_addresses + BITS_USER_BALANCE
        gas_cost_for_grouped_item = total_bits_for_airdrop * GAS_COST_BIT
        total_compressed_gas_cost += gas_cost_for_grouped_item

    return total_compressed_gas_cost, len(amount_occurrences.keys())


def get_unique_amounts_for_all_distributions(txs: List[List[dict]]) -> dict:
    unique_amounts = {}
    amounts_for_all_months = get_amounts_for_each_dist(txs)
    for month_id, amounts_per_month in enumerate(amounts_for_all_months):
        unique_amounts[month_id] = get_unique_amounts_per_distribution(amounts_per_month)

    return unique_amounts


def get_unique_amounts_per_distribution(distribution_amounts: List[float]) -> Dict[float, int]:
    amount_occurrences = {}
    for amount in distribution_amounts:
        if amount in amount_occurrences:
            amount_occurrences[amount] += 1
        else:
            amount_occurrences[amount] = 1

    return amount_occurrences


def make_stats_compression(gas_costs_per_dist: Dict[int, int],
                           gas_cost_per_dist_same_amounts: Dict[int, int],
                           gas_cost_per_dist_permutations: Dict[int, int],
                           gas_cost_per_dist_referencing: Dict[int, int]
                           ) -> Dict[int, Dict[str, Union[int, float]]]:
    gas_cost_stats = {}

    for month_id, gas_cost_per_dist in gas_costs_per_dist.items():

        gas_cost_stats[month_id] = {
            'naive': gas_cost_per_dist,
            'same_amounts': gas_cost_per_dist_same_amounts[month_id],
            'permutations': gas_cost_per_dist_permutations[month_id],
            'referencing': gas_cost_per_dist_referencing[month_id]
        }

        gas_cost_stats[month_id]['savings_naive_v_same_amounts'] = gas_cost_stats[month_id]['naive'] - \
                                                                   gas_cost_stats[month_id]['same_amounts']
        gas_cost_stats[month_id]['savings_percent_naive_v_same_amounts'] = 100 * (
                    gas_cost_stats[month_id]['savings_naive_v_same_amounts'] / gas_cost_stats[month_id]['naive'])

        gas_cost_stats[month_id]['savings_naive_v_permutations'] = gas_cost_stats[month_id]['naive'] - \
                                                                   gas_cost_stats[month_id]['permutations']
        gas_cost_stats[month_id]['savings_percent_naive_v_permutations'] = 100 * (
                    gas_cost_stats[month_id]['savings_naive_v_permutations'] / gas_cost_stats[month_id]['naive'])

        gas_cost_stats[month_id]['savings_naive_v_referencing'] = gas_cost_stats[month_id]['naive'] - \
                                                                  gas_cost_stats[month_id]['referencing']
        gas_cost_stats[month_id]['savings_percent_naive_v_referencing'] = 100 * (
                    gas_cost_stats[month_id]['savings_naive_v_referencing'] / gas_cost_stats[month_id]['naive'])

        if month_id != 0:
            gas_cost_stats[month_id]['naive_cumulative'] = gas_cost_stats[month_id - 1][
                                                               'naive_cumulative'] + gas_cost_per_dist
            gas_cost_stats[month_id]['same_amounts_cumulative'] = gas_cost_stats[month_id - 1][
                                                                      'same_amounts_cumulative'] + \
                                                                  gas_cost_per_dist_same_amounts[month_id]
            gas_cost_stats[month_id]['permutations_cumulative'] = gas_cost_stats[month_id - 1][
                                                                      'permutations_cumulative'] + \
                                                                  gas_cost_per_dist_permutations[month_id]
            gas_cost_stats[month_id]['referencing_cumulative'] = gas_cost_stats[month_id - 1][
                                                                     'referencing_cumulative'] + \
                                                                 gas_cost_per_dist_referencing[month_id]
        else:
            gas_cost_stats[month_id]['naive_cumulative'] = gas_cost_per_dist
            gas_cost_stats[month_id]['same_amounts_cumulative'] = gas_cost_per_dist_same_amounts[month_id]
            gas_cost_stats[month_id]['permutations_cumulative'] = gas_cost_per_dist_permutations[month_id]
            gas_cost_stats[month_id]['referencing_cumulative'] = gas_cost_per_dist_referencing[month_id]

        gas_cost_stats[month_id]['savings_naive_v_same_amounts_cumulative'] = gas_cost_stats[month_id][
                                                                                  'naive_cumulative'] - \
                                                                              gas_cost_stats[month_id][
                                                                                  'same_amounts_cumulative']
        gas_cost_stats[month_id]['savings_percent_naive_v_same_amounts_cumulative'] = 100 * (
                    gas_cost_stats[month_id]['savings_naive_v_same_amounts_cumulative'] / gas_cost_stats[month_id][
                'naive_cumulative'])

        gas_cost_stats[month_id]['savings_naive_v_permutations_cumulative'] = gas_cost_stats[month_id][
                                                                                  'naive_cumulative'] - \
                                                                              gas_cost_stats[month_id][
                                                                                  'permutations_cumulative']
        gas_cost_stats[month_id]['savings_percent_naive_v_permutations_cumulative'] = 100 * (
                    gas_cost_stats[month_id]['savings_naive_v_permutations_cumulative'] / gas_cost_stats[month_id][
                'naive_cumulative'])

        gas_cost_stats[month_id]['savings_naive_v_referencing_cumulative'] = gas_cost_stats[month_id][
                                                                                 'naive_cumulative'] - \
                                                                             gas_cost_stats[month_id][
                                                                                 'referencing_cumulative']
        gas_cost_stats[month_id]['savings_percent_naive_v_referencing_cumulative'] = 100 * (
                    gas_cost_stats[month_id]['savings_naive_v_referencing_cumulative'] / gas_cost_stats[month_id][
                'naive_cumulative'])

    return gas_cost_stats


def print_compression_stats(stats: Dict[int, Dict[str, Union[int, float]]]):
    for dist_id, dist_stats in stats.items():
        print("===========================================================================\n")
        print(f"Distribution id: {dist_id}")
        print(f"Basic")

        print(
            f"Gas costs | Naive: {dist_stats['naive']}, Same amounts: {dist_stats['same_amounts']}, Permutations: {dist_stats['permutations']}, Referencing: {dist_stats['referencing']}")
        print(
            f"Savings naive v same amounts | Total:  {dist_stats['savings_naive_v_same_amounts']}, %: {dist_stats['savings_percent_naive_v_same_amounts']}")
        print(
            f"Savings naive v permutations | Total:  {dist_stats['savings_naive_v_permutations']}, %: {dist_stats['savings_percent_naive_v_permutations']}")
        print(
            f"Savings naive v referencing | Total:  {dist_stats['savings_naive_v_referencing']}, %: {dist_stats['savings_percent_naive_v_referencing']}\n")

        print(f"Cumulative")
        print(
            f"Gas costs | Naive: {dist_stats['naive_cumulative']}, Same amounts: {dist_stats['same_amounts_cumulative']}, Permutations: {dist_stats['permutations_cumulative']}, Referencing: {dist_stats['referencing_cumulative']}")
        print(
            f"Savings naive v same amounts | Total: {dist_stats['savings_naive_v_same_amounts_cumulative']}, %: {dist_stats['savings_percent_naive_v_same_amounts_cumulative']}")
        print(
            f"Savings naive v permutations | Total: {dist_stats['savings_naive_v_permutations_cumulative']}, %: {dist_stats['savings_percent_naive_v_permutations_cumulative']}")
        print(
            f"Savings naive v referencing | Total: {dist_stats['savings_naive_v_referencing_cumulative']}, %: {dist_stats['savings_percent_naive_v_referencing_cumulative']}\n")

    print("===========================================================================\n")

    last_dist_id = len(stats.keys()) - 1
    print("Total")
    print(
        f"Gas costs | Naive: {stats[last_dist_id]['naive_cumulative']}, Same amounts: {stats[last_dist_id]['same_amounts_cumulative']}, Permutations: {stats[last_dist_id]['permutations_cumulative']}, Referencing: {stats[last_dist_id]['referencing_cumulative']}")
    print(
        f"Savings naive v same amounts | Total: {stats[last_dist_id]['savings_naive_v_same_amounts_cumulative']}, %: {stats[last_dist_id]['savings_percent_naive_v_same_amounts_cumulative']}")
    print(
        f"Savings naive v permutations | Total: {stats[last_dist_id]['savings_naive_v_permutations_cumulative']}, %: {stats[last_dist_id]['savings_percent_naive_v_permutations_cumulative']}")
    print(
        f"Savings naive v referencing | Total: {stats[last_dist_id]['savings_naive_v_referencing_cumulative']}, %: {stats[last_dist_id]['savings_percent_naive_v_referencing_cumulative']}")


def make_stats_grouping(gas_costs_per_dist: Dict[int, int],
                        gas_cost_per_dist_same_amounts: Dict[int, int],
                        gas_cost_per_dist_grouped_by_value_range: Dict[int, Dict[int, int]],
                        gas_cost_per_dist_grouped_by_number_of_values: Dict[int, Dict[int, int]],
                        ):
    grouped_by_amount_value_stats = _make_stats_grouping(gas_costs_per_dist, gas_cost_per_dist_same_amounts,
                                                         gas_cost_per_dist_grouped_by_value_range,
                                                         GROUPING_BY_AMOUNT_RANGE_VALUES, 'group_range')
    grouped_by_amount_numbers_stats = _make_stats_grouping(gas_costs_per_dist, gas_cost_per_dist_same_amounts,
                                                           gas_cost_per_dist_grouped_by_number_of_values,
                                                           GROUPING_BY_NUMBER_OF_AMOUNTS_VALUES, 'group_numbers')
    return grouped_by_amount_value_stats, grouped_by_amount_numbers_stats


def print_stats_grouping(group_value_stats, name_key):

    for group_value, group_stats in group_value_stats.items():
        print(f"Stats for group value: {group_value}")

        last_dist_id = len(group_stats.keys()) - 1
        print(f"Gas costs | Naive: {group_stats[last_dist_id]['naive_cumulative']}, Same amounts: {group_stats[last_dist_id]['same_amounts_cumulative']}, {name_key}: {group_stats[last_dist_id][f'{name_key}_cumulative']}")
        print(f"Savings naive v same amounts | Total: {group_stats[last_dist_id]['savings_naive_v_same_amounts_cumulative']}, %: {group_stats[last_dist_id]['savings_percent_naive_v_same_amounts_cumulative']}")
        print(f"Savings naive v {name_key} | Total: {group_stats[last_dist_id][f'savings_naive_v_{name_key}_cumulative']}, %: {group_stats[last_dist_id][f'savings_percent_naive_v_{name_key}_cumulative']}")


def _make_stats_grouping(gas_costs_per_dist: Dict[int, int],
                         gas_cost_per_dist_same_amounts: Dict[int, int],
                         gas_costs_group: Dict[int, Dict[int, int]],
                         group_values: List[int],
                         name_key: str
                         ):
    group_values_stats = {
        g_value: {} for g_value in group_values
    }

    for g_value in group_values:
        for month_id, gas_cost_per_dist in gas_costs_per_dist.items():

            group_value_stats = group_values_stats[g_value]

            group_value_stats[month_id] = {
                'naive': gas_cost_per_dist,
                'same_amounts': gas_cost_per_dist_same_amounts[month_id],
                name_key: gas_costs_group[g_value][month_id]
            }

            group_value_stats[month_id]['savings_naive_v_same_amounts'] = group_value_stats[month_id]['naive'] - \
                                                                          group_value_stats[month_id]['same_amounts']
            group_value_stats[month_id]['savings_percent_naive_v_same_amounts'] = 100 * (
                        group_value_stats[month_id]['savings_naive_v_same_amounts'] / group_value_stats[month_id][
                    'naive'])

            group_value_stats[month_id][f'savings_naive_v_{name_key}'] = group_value_stats[month_id]['naive'] - \
                                                                         group_value_stats[month_id][name_key]
            group_value_stats[month_id][f'savings_percent_naive_v_{name_key}'] = 100 * (
                        group_value_stats[month_id][f'savings_naive_v_{name_key}'] / group_value_stats[month_id][
                    'naive'])

            if month_id != 0:
                group_value_stats[month_id]['naive_cumulative'] = group_value_stats[month_id - 1][
                                                                      'naive_cumulative'] + gas_cost_per_dist
                group_value_stats[month_id]['same_amounts_cumulative'] = group_value_stats[month_id - 1][
                                                                             'same_amounts_cumulative'] + \
                                                                         gas_cost_per_dist_same_amounts[month_id]
                group_value_stats[month_id][f'{name_key}_cumulative'] = group_value_stats[month_id - 1][
                                                                            f'{name_key}_cumulative'] + \
                                                                        gas_costs_group[g_value][month_id]

            else:
                group_value_stats[month_id]['naive_cumulative'] = gas_cost_per_dist
                group_value_stats[month_id]['same_amounts_cumulative'] = gas_cost_per_dist_same_amounts[month_id]
                group_value_stats[month_id][f'{name_key}_cumulative'] = gas_costs_group[g_value][month_id]

            group_value_stats[month_id]['savings_naive_v_same_amounts_cumulative'] = group_value_stats[month_id][
                                                                                         'naive_cumulative'] - \
                                                                                     group_value_stats[month_id][
                                                                                         'same_amounts_cumulative']
            group_value_stats[month_id]['savings_percent_naive_v_same_amounts_cumulative'] = 100 * (
                        group_value_stats[month_id]['savings_naive_v_same_amounts_cumulative'] /
                        group_value_stats[month_id]['naive_cumulative'])

            group_value_stats[month_id][f'savings_naive_v_{name_key}_cumulative'] = group_value_stats[month_id][
                                                                                        'naive_cumulative'] - \
                                                                                    group_value_stats[month_id][
                                                                                        f'{name_key}_cumulative']
            group_value_stats[month_id][f'savings_percent_naive_v_{name_key}_cumulative'] = 100 * (
                        group_value_stats[month_id][f'savings_naive_v_{name_key}_cumulative'] /
                        group_value_stats[month_id]['naive_cumulative'])

    return group_values_stats


def get_data_stats(txs: List[List[dict]]):
    unique_amounts = get_unique_amounts_for_all_distributions(txs)
    print("Unique amounts for distributions ")
    for distribution_id, distribution_unique_amounts in unique_amounts.items():
        unique_amounts_per_distribution_descending = {amount: times for amount, times in
                                                      sorted(distribution_unique_amounts.items(),
                                                             key=lambda item: item[1], reverse=True)}
        top_50_most_common = {amount: unique_amounts_per_distribution_descending[amount] for amount in
                              list(unique_amounts_per_distribution_descending.keys())[:50]}
        print(
            f"Distribution: {distribution_id}, number of unique amounts: {len(distribution_unique_amounts)}, Most common: {top_50_most_common}")


def compute_compression_stats(txs: List[List[dict]], airdrops_per_month: Dict[int, int]):
    print("Airdrops per month", airdrops_per_month)
    print("Total airdrops", sum(airdrops_per_month.values()))

    parsed_data = get_parsed_users_data(cached=False)
    max_karma = get_max_karma(parsed_data)
    max_karma_diff = get_max_karma_diff(parsed_data)

    print(f"Max karma: {max_karma}")
    print(f"Max karma diff: {max_karma_diff}")

    gas_cost_per_dist_naive = get_gas_costs_per_dist(airdrops_per_month)
    gas_cost_per_dist_compressed = get_gas_costs_per_dist_compressed(txs)
    gas_cost_per_dist_permutations = get_gas_costs_per_dist_permutations(txs)
    gas_cost_per_dist_referencing = get_gas_cost_dist_referencing(parsed_data)
    gas_cost_per_dist_grouped_by_value_range = get_gas_costs_per_dist_compressed_grouped_by_value_range(txs)
    gas_cost_per_dist_grouped_by_number_of_values = get_gas_costs_per_dist_compressed_grouped_by_number_of_values(txs)

    # stats = make_stats_compression(gas_cost_per_dist_naive, gas_cost_per_dist_compressed,
    #                                gas_cost_per_dist_permutations, gas_cost_per_dist_referencing)
    # print_compression_stats(stats)

    value_range_stats, num_values_stats = make_stats_grouping(gas_cost_per_dist_naive, gas_cost_per_dist_compressed, gas_cost_per_dist_grouped_by_value_range, gas_cost_per_dist_grouped_by_number_of_values)

    print_stats_grouping(value_range_stats, 'group_range')
    # print_stats_grouping(num_values_stats, 'group_numbers')


def get_gas_costs_per_dist_permutations(txs: List[List[dict]]) -> Dict[int, int]:
    user_data = get_user_data(txs)

    users = user_data['users']
    repeated_users = user_data['repeated_users']
    user_txs = user_data['user_txs']

    total_users = len(users.keys())
    total_repeated_users = len(repeated_users)

    print("Total users: ", total_users)
    print("Repeat users: ", total_repeated_users)

    print("Repeat users percent: ", (total_repeated_users / total_users) * 100)

    permutations = get_permutations_per_distribution(repeated_users, user_txs, len(txs))

    print("Permutations", permutations)

    # check_if_permutations_are_unique(permutations)
    sorted_permutations = {k: v for k, v in sorted(permutations.items(), key=lambda item: item[1], reverse=True)}
    # print("Sorted permutations", sorted_permutations)
    print("Total permutations", len(permutations.keys()))
    print("Total repeated users in permutations", sum(permutations.values()))

    permutations_savings, permutation_costs, repeating_users_per_dist = get_stats_for_reusing_groups_all_data(txs,
                                                                                                              permutations,
                                                                                                              repeated_users)
    distribution_costs = get_gas_costs_for_reusing_groups_all_data(txs, permutation_costs, repeating_users_per_dist)
    print("Total savings per distribution", permutations_savings)
    print("Total costs per distribution", distribution_costs)
    print("Permutation costs per distribution", permutation_costs)
    print("Permutation repeating users", repeating_users_per_dist)

    return distribution_costs


def get_permutations_per_distribution(repeated_users: List[str], user_txs: Dict[str, list], num_distributions: int) -> \
Dict[str, int]:
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


def get_stats_for_reusing_groups_all_data(txs: List[List[dict]], permutations: Dict[str, int],
                                          repeated_users: List[str]) -> Tuple[List[int], List[int], List[int]]:
    savings = [0] * (len(txs) + 1)
    costs_of_permutations = [0] * (len(txs) + 1)
    num_repeated_users_per_group = [0] * (len(txs) + 1)
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
                    cost_of_permutation = source * GAS_COST_BIT * BITS_PERMUTATION

                    savings[i] += (repeated_user_per_group * GAS_COST_BIT * BITS_USER_ID) - cost_of_permutation
                    costs_of_permutations[i] += cost_of_permutation
                    num_repeated_users_per_group[i] += repeated_user_per_group

                    source = len(txs[i])
            if x != 0:
                source = len(txs[i])

    return savings, costs_of_permutations, num_repeated_users_per_group


def get_gas_costs_for_reusing_groups_all_data(txs: List[List[dict]], permutations_costs_per_dist: List[int],
                                              repeating_users_per_dist: List[int]) -> Dict[int, int]:
    gas_costs_per_distribution = {}
    for i in range(0, len(permutations_costs_per_dist) - 1):
        permutations_cost = permutations_costs_per_dist[i]
        repeating_users = repeating_users_per_dist[i]
        total_users = len(txs[i])
        new_users = total_users - repeating_users

        repeating_users_cost = permutations_cost + (repeating_users * BITS_USER_BALANCE * 2)

        new_users_cost = TOTAL_GAS_COST_AIRDROP * new_users

        gas_costs_per_distribution[i] = repeating_users_cost + new_users_cost

    return gas_costs_per_distribution


def get_gas_cost_dist_referencing(parsed_data: dict) -> Dict[int, int]:
    total_unique_users = 0
    repeating_user_gas_cost = (BITS_USER_BALANCE + 1) * GAS_COST_BIT  # gas bits for the balance + the address reference
    unique_user_gas_cost = TOTAL_GAS_COST_AIRDROP
    for distribution_id, distribution_data in parsed_data.items():
        distribution_data['gas_cost'] = 0

        # handle the first distribution
        if distribution_id == 0:
            distribution_data['referencing_cost'] = 0
            distribution_data['repeating_users_cost'] = 0
            distribution_data['unique_users_cost'] = distribution_data['num_users'] * TOTAL_GAS_COST_AIRDROP
            distribution_data['gas_cost'] = distribution_data['unique_users_cost']
            total_unique_users += distribution_data['num_users']
            continue

        unique_users = 0
        repeating_users = 0
        for user_key, user_data in distribution_data['users'].items():
            num_repeats = sum(user_data['repeats_in_prev_months'])
            if num_repeats == 0:
                # unique user
                unique_users += 1
            else:
                repeating_users += 1

        num_unique_users_not_part_in_current_dist = total_unique_users - repeating_users

        distribution_data[
            'referencing_cost'] = num_unique_users_not_part_in_current_dist * BITS_PREV_REFERENCE * GAS_COST_BIT
        distribution_data['repeating_users_cost'] = repeating_user_gas_cost * repeating_users
        distribution_data['unique_users_cost'] = unique_user_gas_cost * unique_users
        distribution_data['gas_cost'] = distribution_data['referencing_cost'] + distribution_data[
            'repeating_users_cost'] + distribution_data['unique_users_cost']

        total_unique_users += unique_users

    total_gas_cost = 0
    total_repeating_user_cost = 0
    total_unique_user_cost = 0
    total_referencing_cost = 0
    gas_costs = {}
    for distribution_id, distribution_data in parsed_data.items():
        total_gas_cost += distribution_data['gas_cost']
        total_referencing_cost += distribution_data['referencing_cost']
        total_unique_user_cost += distribution_data['unique_users_cost']
        total_repeating_user_cost += distribution_data['repeating_users_cost']
        gas_costs[distribution_id] = distribution_data['gas_cost']
        print(
            f"Gas cost per distribution: {distribution_id}, GC: {distribution_data['gas_cost']}, RC: {distribution_data['referencing_cost']}, RUC: {distribution_data['repeating_users_cost']}, UUC: {distribution_data['unique_users_cost']}")

    print(
        f"Total: GC: {total_gas_cost}, RC: {total_referencing_cost}, RUC: {total_repeating_user_cost}, UUC: {total_unique_user_cost}")
    return gas_costs


def main():
    txs = get_transactions()
    num_distributions = len(txs)
    airdrops_per_month = get_airdrops_per_month(txs)

    print("Data stats:")
    print("\n===========================================================================\n")
    get_data_stats(txs)
    print("\n===========================================================================\n")

    print("Stats naive vs compressed vs permutations:")
    print("\n===========================================================================\n")
    compute_compression_stats(txs, airdrops_per_month)
    print("\n===========================================================================\n")

    # parsed_data = get_parsed_users_data(cached=False)
    # for distribution_id, distribution_data in parsed_data.items():
    #     print(distribution_id, distribution_data['num_users'], distribution_data['num_unique_users'], distribution_data['num_users'] - distribution_data['num_unique_users'], distribution_data['permutations'])
    # # print(txs_dict)
    # max_karma = get_max_karma(parsed_data)
    # print("Max karma: ", max_karma)

    # print("Savings from permutations compared to naive (previous data):")
    # print("\n===========================================================================\n")
    # get_permutations_savings_previous_data(parsed_data)
    # print("\n===========================================================================\n")

    # print(txs_dict)


if __name__ == '__main__':
    main()
