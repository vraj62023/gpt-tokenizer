import re

def get_stats(ids):
    counts = {}
    for pair in zip(ids,ids[1:]):
        counts[pair]= counts.get(pair,0)+1
    return counts

def merge(ids,pair,idx):
    newids = []
    i =0
    while i<len(ids):
        if i<len(ids)-1 and ids[i]==pair[0] and ids[i+1]==pair[1]:
            newids.append(idx)
            i+=2
        else:
            newids.append(ids[i])
            i+=1
    return newids

class BasicTokenizer:
    def __init__(self):
        self.merges = {}
        self.vocab = {}
        #This is a simplified regex pattern to split words, punctuations,and spaces
        self.pattern = re.compile(r"""\s+|[a-zA-Z]+|[0-9]+|[^\s\w]+""")
    def train(self,text,vocab_size, verbose =False):
        #1. Pre-tokenize the text using our Regex pattern
        text_chunks = re.findall(self.pattern,text)

        #2 Convert each chunk into raw bytes independently
        #we store chunks as lists of byte integers
        chunk_ids = [list(chunk.encode('utf-8')) for chunk in text_chunks]
        num_merges = vocab_size-256

        for i in range(num_merges):
            #3.we must count pair frequencies Across all chunks independently
            stats= {}
            for chunk in chunk_ids:
                #Get stats for this specific chunk 
                chunk_stats = get_stats(chunk)

                #add them to our global state
                for pair,count in chunk_stats.items():
                    stats[pair] = stats.get(pair,0)+count
                
            if not stats:
                break #no more pairs left to merge

            pair = max(stats,key=stats.get)
            idx = 256 +i
            #4 Apply the merge independently to every chunk 
            chunk_ids = [merge(chunk,pair,idx) for chunk in chunk_ids]
            self.merges[pair]=idx

            if verbose:
                print(f"Merge{i+1}: pair{pair}->token{idx}")
        #Build Vocabulary
        self.vocab = {idx: bytes([idx]) for idx in range(256)}
        for(p0,p1), idx in self.merges.items():
            self.vocab[idx]= self.vocab[p0]+self.vocab[p1]
    def decode(self,ids):
        tokens = b"".join(self.vocab[idx] for idx in ids)
        text = tokens.decode("utf-8",errors="replace")
        return text
    def encode(self,text):
        #split incoming text using same regex pattern
        text_chunks = re.findall(self.pattern,text)

        find_ids = []

        for chunk in text_chunks:
            tokens = list(chunk.encode("utf-8"))
            while len(tokens)>=2:
                stats = get_stats(tokens)
                pair = min(stats,key=lambda p: self.merges.get(p,float("inf")))
                if pair not in self.merges:
                    break
                idx = self.merges[pair]
                tokens = merge(tokens,pair,idx)
            #Add the processed chunk tokens to our final list
            find_ids.extend(tokens)
        return find_ids

# --- Test the new Class ---
if __name__ == "__main__":
    tokenizer = BasicTokenizer()
    text = "Hello world! How are you doing today? I'm doing great. 12345"
    print("Training on text...")
    tokenizer.train(text, vocab_size=276, verbose=True)
    
    test_text = "Hello today!"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)
    print("\nEncoded:", encoded)
    print("Decoded:", decoded)
