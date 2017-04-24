import sys
import os
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
import urllib
import unicodedata

reload(sys)
sys.setdefaultencoding('utf-8')

files = [file for file in os.listdir('.') if file.startswith('tt')]
stop_words = set()
with open("SmartStoplist.txt", "r") as f:
    for line in f:
        stop_words.add(line.strip())


wnl = WordNetLemmatizer()

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFKD', s.decode('utf-8')) if unicodedata.category(c) != 'Mn')

def str_stem(s): 
    if isinstance(s, str):
        s = strip_accents(s)
        #return " ".join([stemmer.stem(re.sub('[^A-Za-z0-9-./]', ' ', word)) for word in s.lower().split()])
        return " ".join([wnl.lemmatize(re.sub('[^A-Za-z0-9_.?!;\']', ' ', word)) for word in s.lower().split()])
    else:
        return "" 

def extract_candidate_chunks(text, grammar=r'KT: {(<JJ>* <NN.*>{,3} <IN>)? <JJ>* <NN.*>{,3}}'):
    import itertools, nltk, string
    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    #stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenize, POS-tag, and chunk using regular expressions
    chunker = nltk.chunk.regexp.RegexpParser(grammar)
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tagged_sents = nltk.pos_tag_sents(tokenizer.tokenize(sent) for sent in nltk.sent_tokenize(text))
    all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent))
                                                    for tagged_sent in tagged_sents))
    # join constituent chunk words into a single chunked phrase
    candidates = [' '.join(word for word, pos, chunk in group).lower()
                  for key, group in itertools.groupby(all_chunks, lambda (word,pos,chunk): chunk != 'O') if key]

    return [cand for cand in candidates
            if cand not in stop_words and not all(char in punct for char in cand)]


def extract_candidate_words(text, good_tags=set(['JJ','JJR','JJS','NN','NNP','NNS','NNPS'])):
    import itertools, nltk, string

    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    #stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenize and POS-tag words
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tagged_words = itertools.chain.from_iterable(nltk.pos_tag_sents(tokenizer.tokenize(sent)
                                                                    for sent in nltk.sent_tokenize(text)))
    # filter on certain POS tags and lowercase all words
    candidates = [word.lower() for word, tag in tagged_words
                  if tag in good_tags and word.lower() not in stop_words if len(word) > 2 
                  and not all(char in punct for char in word)]

    return candidates

def score_keyphrases_by_tfidf(texts, candidates='chunks'):
    import gensim, nltk
    boc_texts = []
    # extract candidates from each text in texts, either chunks or words
    if candidates == 'chunks':
        boc_texts = [extract_candidate_chunks(text) for text in texts]
    elif candidates == 'words':
        boc_texts = [extract_candidate_words(text) for text in texts]
    # make gensim dictionary and corpus
    dictionary = gensim.corpora.Dictionary(boc_texts)
    corpus = [dictionary.doc2bow(boc_text) for boc_text in boc_texts]
    # transform corpus with tf*idf model
    tfidf = gensim.models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    
    return corpus_tfidf, dictionary

def score_keyphrases_by_textrank(text, n_keywords=10):
    from itertools import takewhile, tee, izip
    import networkx, nltk

    candidates = extract_candidate_words(text)

    # add a whitespace before dot so we can tokenize dot
    text=text.replace('.',' .').replace(',',' .')
    # tokenize for all words, and extract *candidate* words
    tokenizer = RegexpTokenizer(r'[a-zA-Z.]+')
    words = [word.lower()
             for sent in nltk.sent_tokenize(text)
             for word in tokenizer.tokenize(sent) if word not in stopwords.words('english') or word =='.']
    
    # build graph, each node is a unique candidate
    graph = networkx.Graph()
    graph.add_nodes_from(set(candidates))
    # iterate over word-pairs, add unweighted edges into graph
    def pairwise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        a, b = tee(iterable)
        next(b, None)
        return izip(a, b)
    for w1, w2 in pairwise(candidates):
        if w2:
            graph.add_edge(*sorted([w1, w2]))
    # score nodes using default pagerank algorithm, sort by score, keep top n_keywords
    ranks = networkx.pagerank(graph)
    if 0 < n_keywords < 1:
        n_keywords = int(round(len(candidates) * n_keywords))
    word_ranks = {word_rank[0]: word_rank[1]
                  for word_rank in sorted(ranks.iteritems(), key=lambda x: x[1], reverse=True)[:n_keywords]}
    keywords = set(word_ranks.keys())
    # merge keywords into keyphrases
    keyphrases = {}
    j = 0
    for i, word in enumerate(words):
        if i < j:
            continue
        if word in keywords:
            kp_words = list(takewhile(lambda x: x in keywords, words[i:i+10]))
            avg_pagerank = sum(word_ranks[w] for w in kp_words) / float(len(kp_words))
            keyphrases[' '.join(kp_words)] = avg_pagerank
            # counter as hackish way to ensure merged keyphrases are non-overlapping
            j = i + len(kp_words)

    return sorted(keyphrases.iteritems(), key=lambda x: x[1], reverse=True)

def score_keyphrases_by_singlerank(text):
    from itertools import takewhile, tee, izip
    import networkx, nltk

    candidates = extract_candidate_words(text)

    # add a whitespace before dot so we can tokenize dot
    text=text.replace('.',' .').replace(',',' .')
    # tokenize for all words, and extract *candidate* words
    tokenizer = RegexpTokenizer(r'[a-zA-Z.]+')
    words = [word.lower()
             for sent in nltk.sent_tokenize(text)
             for word in tokenizer.tokenize(sent) if word not in stopwords.words('english') or word =='.']
    
    # build graph, each node is a unique candidate
    graph = networkx.Graph()
    graph.add_nodes_from(set(candidates))
    # iterate over word-pairs, add weighted edges into graph
    def tenIteratorWise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        iterators = tee(iterable, 10)

        for i in range(len(iterators)):
            j = 0
            while j < i:
                next(iterators[i], None)
                j+=1

        return izip(*iterators)

    #Each edge in a SingleRank graph has a weight equal to the number of times the two corresponding word types co-occur
    counter = 0
    for i in tenIteratorWise(candidates):

        if i[9]:

            if counter == 0:

                for v1 in range(len(i)):

                    for v2 in range(v1 + 1, len(i)):

                        sortedVertices = sorted([i[v1], i[v2]])

                        if not graph.has_edge(sortedVertices[0], sortedVertices[1]):

                            graph.add_weighted_edges_from([(sortedVertices[0], sortedVertices[1], 1)])

                        else:

                            graph[sortedVertices[0]][sortedVertices[1]]["weight"] += 1

            else:

                for v in range(len(i) - 1):

                    sortedVertices = sorted([i[v], i[9]])

                    if not graph.has_edge(sortedVertices[0], sortedVertices[1]):

                        graph.add_weighted_edges_from([(sortedVertices[0], sortedVertices[1], 1)])

                    else:

                        graph[sortedVertices[0]][sortedVertices[1]]["weight"] += 1

            counter += 1

    # score nodes using default pagerank algorithm, sort by score
    ranks = networkx.pagerank(graph)

    word_ranks = {word_rank[0]: word_rank[1]
                  for word_rank in sorted(ranks.iteritems(), key=lambda x: x[1], reverse=True)}

    keywords = set(word_ranks.keys())
    # merge keywords into keyphrases
    keyphrases = {}
    j = 0
    for i, word in enumerate(words):
        if i < j:
            continue
        if word in keywords:
            kp_words = list(takewhile(lambda x: x in keywords, words[i:i+10]))
            avg_pagerank = sum(word_ranks[w] for w in kp_words) / float(len(kp_words))
            keyphrases[' '.join(kp_words)] = avg_pagerank
            # counter as hackish way to ensure merged keyphrases are non-overlapping
            j = i + len(kp_words)

    return sorted(keyphrases.iteritems(), key=lambda x: x[1], reverse=True)

def post_process(keyphrases, grammar=r'KT: {(<JJ>* <NN.*>{,3} <IN>)? <JJ>* <NN.*>{,3}}'):
    rules = re.compile(grammar)
    for phrase in keyphrases: 
        if rules.match(phrase[0]) == None:
            keyphrases.remove(phrase)                        
    return keyphrases


if __name__ == '__main__':

    keyphrasesMovieDic = {}

    for file in files:
        with open(file, "r") as f:
            doc = f.read().replace('\n', ' ')
            doc = str_stem(doc.encode('utf-8'))
        #print corpus
        # chunks = extract_candidate_chunks(doc)
        # print chunks

        keyphrases = score_keyphrases_by_textrank(doc)

        keyphrases = post_process(keyphrases)
        #print (str(file), [str(phrase[0]) for phrase in keyphrases]) + '\n'
        #print '\n'

        # build key phrases-movie dictionary
        for phrase in keyphrases:

            if phrase[0] in keyphrasesMovieDic:

                keyphrasesMovieDic[phrase[0]].append(file)

            else:

                keyphrasesMovieDic[phrase[0]] = []
                keyphrasesMovieDic[phrase[0]].append(file)

    inverseIndexFile = open("inverseIndex_textrank.csv", "w")
    for keyphrase, ids in keyphrasesMovieDic.items():

        inverseIndexFile.write(keyphrase + "|" + " ".join(ids) + "\n")



    # corpus = [] 
    # for file in files:
    #     with open(file, "r") as f:
    #         doc = f.read().replace('\n', ' ')
    #         doc = str_stem(doc.encode('utf-8'))
    #         corpus.append(doc)
    #     print corpus
    #     print len(corpus)
    #     sktf = score_keyphrases_by_tfidf(corpus, 'chunks')
    #     print sktf
