from utils import * 
import pdb

txs = get_transactions()

# naive cost is 32 * num_drops_may + 32 * num_drops_june
# We assume the address size is 16 bits and the number size is 16 bits.

users , repeat_users, user_txs = make_user_data(txs)

total_airdrops = len(txs[0]) + len(txs[1]) + len(txs[2])
naive_cost = total_airdrops * 231
print("total airdrops ", total_airdrops)

(may, june, july, other) = hist_monthly(txs, repeat_users)

print(len(may), len(june), len(july))
compress_amount = sum([same_amount_monthly(x)for x in [may, june, july]])
print(compress_amount, " saved that naive is  ", naive_cost, (naive_cost - compress_amount) / naive_cost *100 , " % saved")

# Find bits to reuse group 

print(" repeat users " , len(repeat_users))
print(" % repeast users ", len(repeat_users) / len(users))

test = [] 
repeats = {} 
for user in repeat_users:
    user_repeat = [0]*3
    for tx in user_txs[user]:
        user_repeat[tx["month"]] = 1

    try:
        #convert to string format
        repeats[str(user_repeat)] += 1
    except:
        repeats[str(user_repeat)] = 1

# naive withour repeat compression 

print ("May ", len(may)*231)
print ("June ", len(june)*231)
print ("July ", len(july)*231)


all_txs = [may, june, july]

gas_per_bit = 2

savings = [0]*4

for key in repeats.keys():
   
    # back to list format
    key = key[1:-1].split(",")
    key = [int(x) for x in key]

    # we have to start by finding the source to permute
    source = 0 

    for i, x in enumerate(key):

        # find the group to permute
        if source != 0:
            if x == 0:
                continue
            else:
                destination = repeats[str(key)] 

               # calculate how much the permute costs
                cost_of_permutation = source * gas_per_bit *1

                savings[i] += (destination* gas_per_bit * 17 ) - cost_of_permutation
                source = len(all_txs[i])
                pass
        if x != 0 :          
            source = len(all_txs[i])

print ( "total saving v naive " , 100 - (naive_cost - sum(savings)) / naive_cost * 100) 
print ( "total saving including amount compress " , (naive_cost - (compress_amount - sum(savings))) / compress_amount)
pdb.set_trace()
