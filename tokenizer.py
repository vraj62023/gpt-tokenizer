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
