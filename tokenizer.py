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

#1. Start with the base 256 individual byte tokens
#bytes([idx]) creates a python bytes object of a single byte (0 to 255)
vocab = {idx: bytes([idx]) for idx in range(256)}

#2. for every merge we learned, build up its full byte representatin
for(p0,p1), idx in merges.items():
    vocab[idx]= vocab[p0]+vocab[p1]

def decode(ids):
    #lookup the bytes for each token ID
    tokens = b"".join(vocab[idx] for idx in ids)
    #convert rew bytes back to human string 
    #errors = "replace" replaces invalid bytes sequences with the unicode replacement character instead of crashing
    text =  tokens.decode("utf-8", errors="replace")
    return text

#quick test on our trained ids:
print("\n____TESTING DECODE_____")
reconstructed_text = decode(ids)
print("Decoded Text:",reconstructed_text)
print("Matches original:",reconstructed_text==text)

def encode(text):
    #1. Convert the text to initial list of raw byte integers
    tokens = list(text.encode("utf-8"))

    # A text needs at least 2 tokens to have any adjacent pairs
    while len(tokens)>=2:
        #Get counts of all adjacent pairs currently in our text 
        stats = get_stats(tokens)

        #Find the pair in 'stats' that has the LOWEST merge index in our merges dict.
        #If a pair was never merged during training, we treat its rank as infinity (float("inf"))
        pair = min(stats, key = lambda p: merges.get(p,float("inf")))

        # If the  best pair is not in merges, nothing else can be merged!
        if pair not in merges:
            break

        #Get the new ID assigned to this pair and merge it
        idx = merges[pair]
        tokens = merge(tokens,pair,idx)
    return tokens

print("\n____TESTING ENCODE & ROUND_TRIP_____")
test_phrase = "The quick fox is quick."
encoded_tokens = encode(test_phrase)
decoded_phrase = decode(encoded_tokens)

print("Original phrase:",test_phrase)
print("Encoded tokens:",encoded_tokens)
print("Decoded phrase:",decoded_phrase)

#verify looslessness
assert decoded_phrase==test_phrase, "Round trip failed! Decoded phrase does not match original."
print("Success! ENCODE-> Decode is 100% looseless")