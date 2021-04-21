import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Dict
from new.utils import get_parsed_users_data


def create_airdrops_chart(data: dict):
    ids = []
    airdrops = []
    unique_users = []
    for i, dist_data in data.items():
        ids.append(i + 1)
        airdrops.append(dist_data['num_users'])
        unique_users.append(dist_data['num_unique_users'])

    print("ids", ids)
    print("airdrops", airdrops)
    print("unique_users", unique_users)

    x = np.arange(len(ids))  # the ids locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width / 2, airdrops, width, label='Airdrops')
    rects2 = ax.bar(x + width / 2, unique_users, width, label='Unique users')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Airdrops')
    ax.set_xlabel('Dist IDs')
    ax.set_title('Airdrops and unique users per distribution')
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()

    ax.bar_label(rects1, padding=6)
    ax.bar_label(rects2, padding=6)

    fig.tight_layout()

    plt.show()

    fig.savefig("figs/new/airdrops.png")


def create_repeating_users_chart(data: dict):
    ids = []
    repeating_users = []
    unique_users = []
    for i, dist_data in data.items():
        ids.append(int(i) + 1)
        unique_users.append(dist_data['num_unique_users'])
        repeating_users.append(dist_data['num_users'] - dist_data['num_unique_users'])

    x = np.arange(len(ids))  # the ids locations
    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()

    rects1 = ax.bar(x, unique_users, width, label='Unique users')
    rects2 = ax.bar(x, repeating_users, width, label='Repeating users', bottom=unique_users)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Users')
    ax.set_xlabel('Dist IDs')
    ax.set_title('Users per distribution')
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()

    ax.bar_label(rects1, label_type='center')
    ax.bar_label(rects2, label_type='center')
    ax.bar_label(rects2)

    fig.tight_layout()

    plt.show()

    fig.savefig("figs/new/repeating_users.png")


def create_gas_costs_chart(data: dict):
    ids = []
    gas_costs = []
    for i, gas_cost in data.items():
        ids.append(int(i) + 1)
        gas_costs.append(gas_cost)
    print(gas_costs)

    x = np.arange(len(ids))  # the ids locations
    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()

    rects1 = ax.bar(x, gas_costs, width, label='Gas cost')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Gas Cost')
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))

    # ax.set_yscale('log')
    ax.set_xlabel('Dist IDs')
    ax.set_title('Gas cost per distribution')
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()

    # ax.bar_label(rects1, label_type='edge')

    fig.tight_layout()

    plt.show()

    fig.savefig("figs/new/gas_costs.png")


def create_frequencies_chart(unique_amounts: dict):
    amounts = [int(amount) for amount in unique_amounts.keys()]
    frequencies = unique_amounts.values()

    width = 0.1  # the width of the bars

    fig, ax = plt.subplots()

    rects1 = ax.bar(amounts, frequencies, label='Amount frequencies')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Airdrops')
    ax.set_yscale('log')
    ax.set_xscale('log')

    ax.set_xlabel('Amounts')
    ax.set_title('Airdrop amount frequences')
    ax.legend()

    # ax.bar_label(rects1, label_type='edge')

    fig.tight_layout()

    plt.show()

    fig.savefig("figs/new/amounts.png")


def create_gas_cost_diff_chart(gas_costs: Tuple[dict, dict],
                               labels: Tuple[str, str],
                               title: str,
                               ylabel: str,
                               xlabel: str,
                               set_bar_labels: Tuple[bool, bool] = (True, True)):
    gas_costs_1, gas_costs_2 = gas_costs
    label_1, label_2 = labels
    set_bar_label_1, set_bar_label_2 = set_bar_labels
    ids = [i + 1 for i in gas_costs_1.keys()]
    costs_1 = [gas_cost_dist for gas_cost_dist in gas_costs_1.values()]
    costs_2 = [gas_cost_dist for gas_cost_dist in gas_costs_2.values()]

    x = np.arange(len(ids))  # the ids locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width / 2, costs_1, width, label=label_1, color="lightblue")
    rects2 = ax.bar(x + width / 2, costs_2, width, label=label_2, color="orange")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()

    if set_bar_label_1:
        ax.bar_label(rects1, padding=1, fmt="%.0f", fontsize="small")
    if set_bar_label_2:
        ax.bar_label(rects2, padding=1, fmt="%.0f", fontsize="small")

    fig.tight_layout()

    plt.show()

    fig.savefig(f"figs/new/{title}.png")


def create_gas_costs_diff_groups_chart(
        naive_gas_cost: Dict[int, int],
        gas_costs: Dict[int, dict],
                                       title: str,
                                       ylabel: str,
                                       xlabel: str):
    num_gr = len(gas_costs.keys())

    labels = {gr: f"GR {gr} gas cost" for gr in gas_costs.keys()}
    ids = [i + 1 for i in naive_gas_cost.keys()]

    x = np.arange(len(ids))  # the ids locations
    width = 1/(num_gr*1.5)  # the width of the bars

    fig, ax = plt.subplots()

    ax.bar(x, naive_gas_cost.values(), width, label="Naive gas cost")

    i = 1
    for gr, gas_cost_gr in gas_costs.items():
        cost = gas_cost_gr.values()

        pos = (x + width*i)

        ax.bar(pos, cost, width, label=labels[gr])
        i+=1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()

    fig.tight_layout()

    plt.show()

    fig.savefig(f"figs/new/{title}.png")


def create_gas_costs_totals_groups_chart(
        naive_gas_cost: int,
        gas_cost_totals: Dict[int, int],
        title: str,
        ylabel: str,
        xlabel: str
):

    ids = ["Naive"]
    ids.extend([f"GR {gr}" for gr in gas_cost_totals.keys()])

    x = np.arange(len(ids))  # the ids locations
    width = 0.5

    fig, ax = plt.subplots()
    gas_costs = [naive_gas_cost]
    gas_costs.extend(gas_cost_totals.values())

    rect = ax.bar(x, gas_costs, width, label="Total gas cost", color="lightblue")
    ax.bar_label(rect, padding=1, fmt="%.0f", fontsize="small")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()
    fig.tight_layout()
    plt.show()

    fig.savefig(f"figs/new/{title}.png")


def create_gas_costs_totals_chart(
        gas_cost_totals: Dict[str, int],
        title: str,
        ylabel: str,
        xlabel: str
):

    ids=[key for key in gas_cost_totals.keys()]

    x = np.arange(len(ids))  # the ids locations
    width = 0.5

    fig, ax = plt.subplots()
    gas_costs = gas_cost_totals.values()
    print(gas_cost_totals)
    print(gas_costs)
    rect = ax.bar(x, gas_costs, width, label="Total gas cost", color="lightblue")
    ax.bar_label(rect, padding=1, fmt="%.0f", fontsize="small")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.legend()
    fig.tight_layout()
    plt.show()

    fig.savefig(f"figs/new/{title}.png")


def create_test_chart():
    labels = ['G1', 'G2', 'G3', 'G4', 'G5']
    men_means = [20, 34, 30, 35, 27]
    women_means = [25, 32, 34, 20, 25]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, men_means, width, label='Men')
    rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores')
    ax.set_title('Scores by group and gender')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

    fig.savefig("../figs/new/testChar2.png")

# if __name__ == '__main__':
#     parsed_user_data = get_parsed_users_data(cached=False)
#     create_airdrops_chart(parsed_user_data)
