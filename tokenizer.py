#1 Converting string into a list of raw byte integers
text = "aaabdaaabac"
tokens = list(text.encode('utf-8'))
print("Starting tokens:",tokens)

#Function to count how ofter token pair appear next to each other
def get_stats(ids):
    count = {}
    #zip(ids, ids[1:]) pairs up adjacent elements in the list
    for pair in zip(ids, ids[1:]):
        #add 1 to the current count of this pair , defaulting to 0 if its new
        count[pair] = count.get(pair, 0) + 1
    return count
stats = get_stats(tokens)
print("Pair frequencies:",stats)

top_pair = max(stats, key = stats.get)
print("Most frequent pair:",top_pair, "Frequency:", stats[top_pair])

def merge(ids, pair,idx):
    #we will build a brand new list of tokens here
    newids=[]
    i=0
    #A while loop lets us control the exactly how we move through the list
    while i<len(ids):
        #check if we are not at the very end and if the current and next token match our pair
        if i<len(ids)-1 and ids[i]==pair[0] and ids[i+1]==pair[1]:
            newids.append(idx) # add  our new token ID ( like 256)
            i+=2 # important : skip a head 2 spots because we merged two token into one
        else:
            newids.append(ids[i])#keep the original token
            i+=1
    return newids

#lets test it using the top_pair from our previous step!
# utf-8 ends at 255, so our first new token will be 256
token_after_merge = merge(tokens,top_pair,256)
print("Original length:",len(tokens))
print("New length:",len(token_after_merge))
print("Tokens after one merge:",token_after_merge)



#lets train on a slightly longer text
text = "The quick brown fox jumps over the lazy dog. The quick brown fox is quick."
ids = list(text.encode('utf-8'))

#we want 20 new tokens on the top of the base 256
vocab_size = 276
num_merges = vocab_size-256

# this dictionary will store our vocabulary rules ( eg = {(101,114): 256})
merges= {}

print("____STARTING BPE TRAINING____")

#'range' creates a sequence of numbers from 0 upto num_merges
for i in range(num_merges):
    stats = get_stats(ids)
    #max() looks through the stats. key  = stats.get tells it to judge by the highest count
    pair = max(stats, key = stats.get)
    
    idx = 256+i # our new token ID
    ids = merge(ids,pair,idx)
    merges[pair]= idx # store the rule to our dictionay

    print(f"Merge {i+1}: pair{pair}-> token {idx}")
print("Final compressed length:",len(ids))
