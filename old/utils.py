import csv
import pdb
import datetime
import matplotlib.pyplot as plt
import statistics as stats
from math import log

n_bins = 20
start = 1
stop = 20


def get_transactions():
    filenames = [
        "round_1_finalized",
        "round_2_finalized",
        "round_3_finalized",
    ]

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
                month_count+=1
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
    for i, day in enumerate(txs): 
        for tx in day: 

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
    return(users, repeat_users, user_txs)


def hist_monthly(txs, repeat_users):
    months = [[],[], [], []]
    may = [] 
    june = []
    is_repeat_users = [[],[],[]]
    for i, monthly_txs in enumerate(txs):
        for tx in monthly_txs:
            months[i].append(float(tx["karma"]))

    return(months)


def same_amount_monthly(month):
    start = 1
    stop = 20 
    fig, axs = plt.subplots(1, sharey=True, tight_layout=True)
    hist_may = axs.hist(month, bins=len(set(month)), range=((start, stop)))
    axs.set_title('May drops')
    axs.set_xlabel('Bins')
    axs.set_ylabel('Drops')
    fig.savefig("./figs/histMayAmounts.png")

    total = 0 
    gas_cost = 0

    for amount in hist_may[0][:stop]: 
        total+=amount
        gas_cost = amount*16*7
 
    total_gas_cost = (len(month) - total) * 33 * 7 
    return(total_gas_cost)


