# -*- coding: utf-8 -*-
import os
import operator
from argparse import ArgumentParser
from get_vocabulary import get_word_vocab

def get_vocab_fromfile(pairvocab_path,word2index):
    pairvocab_file=open(pairvocab_path,'r',encoding='utf-8')
    dict_pairvocab={}
    for line in pairvocab_file:
        linesplit=line.strip().split("\t")
        word1=linesplit[0]
        word2=linesplit[1]
        if word1 in word2index and word2 in word2index:
            if word1 not in dict_pairvocab: dict_pairvocab[word1]=set()
            dict_pairvocab[word1].add(word2)
    return dict_pairvocab

def load_dictfreq_file(wordfreq_path):
    wordfreq_file=open(wordfreq_path,'r',encoding='utf-8')
    word2index={}
    index2word={}
    cont=0
    for line in wordfreq_file:
        linesplit=line.strip().split("\t")
        word=linesplit[0]
        word2index[word]=cont
        index2word[cont]=word
        cont+=1
    return word2index,index2word

def extract_context_pairs(corpus_path,dict_pairvocab,window_size,word2index,position='c'):
    dict_contexts={}
    for word1 in dict_pairvocab:
        index1=word2index[word1]
        dict_contexts[index1]={}
    corpus_file=open(corpus_path,'r',encoding='utf-8')
    for line in corpus_file:
      linesplit=line.strip().split(" ")
      for i in range(len(linesplit)):
        tokeni=linesplit[i]
        if tokeni in dict_pairvocab:
          indexi=word2index[tokeni]
          for j in range(i+1,min(i+1+window_size,len(linesplit))):
            tokenj=linesplit[j]
            if tokenj in dict_pairvocab[tokeni]:
                indexj=word2index[tokenj]
                if indexj not in dict_contexts[indexi]: dict_contexts[indexi][indexj]={}
                if position=='c': list_iterate=linesplit[i+1:j]
                elif position=='l': list_iterate=linesplit[max(i-10,0):i]
                else: list_iterate=linesplit[j+1:min(j+11,len(linesplit))]
                for token_cooc in list_iterate:
                    if token_cooc in word2index:
                        index_cooc=word2index[token_cooc]
                        if index_cooc not in dict_contexts[indexi][indexj]: dict_contexts[indexi][indexj][index_cooc]=1
                        else: dict_contexts[indexi][indexj][index_cooc]+=1
    return dict_contexts
                
def print_contexts(dict_contexts,output_folder_path,min_freq_cooc,index2word):
    if not os.path.exists(output_folder_path): os.mkdir(output_folder_path)
    else: print ("WARNING: "+output_folder_path+" already exists! Existing files will be overwritten.")
    for index1 in dict_contexts:
        word1=index2word[index1]
        output_folder_word1=output_folder_path+"/"+("%r"%word1)
        if not os.path.exists(output_folder_word1): os.makedirs(output_folder_word1)
        else: print ("WARNING: subfolder "+output_folder_word1+" already exists! Existing files will be overwritten.")
        for index2 in dict_contexts[index1]:
            word2=index2word[index2]
            if dict_contexts[index1][index2]=={}: continue
            txtfile=open(output_folder_word1+"/"+("%r"%word2)+".txt",'w',encoding='utf-8')
            list_sorted=sorted(dict_contexts[index1][index2].items(), key=operator.itemgetter(1), reverse=True)
            for index_cooc,times in list_sorted:
                if times>=min_freq_cooc:
                    txtfile.write(index2word[index_cooc]+"\t"+str(times)+"\n")
            txtfile.close()


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-corpus', '--corpus_file', help='Input corpus path (tokenized)', required=True)
    parser.add_argument('-pairvocab', '--input_vocab',
        help='Path of the input pair vocabulary file (tab-separated with at least two columns, one pair per line)', required=False, default="./vocab/pair_vocab_pmi.txt")
    parser.add_argument('-wordfreq', '--input_wordfrequency_file', help='Path of the frequency dictionary file', required=False, default="false")
    parser.add_argument('-min_freq', '--minimum_frequency',
        help='Minimum frequency of words (needed only if word frequency file is not given). If standard vocabulary, you can write ./vocab/word_frequency_all.txt', required=False, default=5)
    parser.add_argument('-pos_contexts', '--position_contexts', help='Type/s of context to extract ("central" or "all")', required=False, default="central")
    parser.add_argument('-output_contexts', '--output_folder', help='Output directory to store contexts (needed if only central)', required=False, default="./contexts/")
    parser.add_argument('-window', '--window_size', help='Co-ocurring window size', required=False, default=10)
    parser.add_argument('-min_freq_cooc', '--minimum_frequency_context',
        help='Minimum frequency of words between word pair: increasing the number can speed up the calculations and reduce memory but we would recommend keeping this number low', required=False, default=1)
    

    args = vars(parser.parse_args())

    # Main parameters
    corpus_path=args['corpus_file']
    pairvocab_path=args['input_vocab']
    wordfreq_path=args['input_wordfrequency_file']
    pos_contexts=args['position_contexts'].lower()
    if pos_contexts=="central": output_folder_path=os.path.realpath(args['output_folder'])+"/"
    window_size=int(args['window_size'])
    min_freq_cooc=int(args['minimum_frequency_context'])

    # Retrieve frequency dictionary
    print ("Loading frequency dictionary and retrieving vocabulary...\n")
    if wordfreq_path.lower()=="false":
        min_freq=int(args['minimum_frequency'])
        dict_freq=get_word_vocab(corpus_path)
        list_freq_sorted=sorted(dict_freq.items(), key=operator.itemgetter(1), reverse=True)
        cont=0
        word2index={}
        index2word={}
        for word,freq in list_freq_sorted:
            if freq<min_freq: break
            word2index[word]=cont
            index2word[cont]=word
            cont+=1
        list_freq_sorted.clear()
        dict_freq.clear()
    else: word2index,index2word=load_dictfreq_file(wordfreq_path)

    # Retrieve pair and word vocabulary (dictionary)
    dict_pairvocab=get_vocab_fromfile(pairvocab_path,word2index)

    print ("Vocabulary loaded. Now extracting contexts...(this can take a few hours depending on the size of the corpus)")
    
    # Extract and print contexts
    dict_contexts=extract_context_pairs(corpus_path,dict_pairvocab,window_size,word2index)
    if pos_contexts=="central":
        print ("Central contexts succesfully extracted. Now printing them in "+output_folder_path+" ...")
        print_contexts(dict_contexts,output_folder_path,min_freq_cooc,index2word)
        print ("\nFinished. All contexts have been already printed in "+output_folder_path)
        dict_contexts.clear()
    else:
        print ("\n")
        output_folder_path_central=os.path.realpath("./central_contexts/")
        print ("Central contexts succesfully extracted. Now printing them in "+output_folder_path_central+" ...")
        print_contexts(dict_contexts,output_folder_path_central,min_freq_cooc,index2word)
        print ("All central contexts have been already printed in "+output_folder_path_central+"\n")
    
    
    if pos_contexts!="central":
        #Extract and print left contexts
        dict_contexts_left=extract_context_pairs(corpus_path,dict_pairvocab,window_size,word2index,'l')
        output_folder_path_left=os.path.realpath("./left_contexts/")
        print ("Left contexts succesfully extracted. Now printing them in "+output_folder_path_left+" ...")
        print_contexts(dict_contexts_left,output_folder_path_left,min_freq_cooc,index2word)
        print ("All left contexts have been already printed in "+output_folder_path_left+"\n")
        dict_contexts_left.clear()

        #Extract and print right contexts
        dict_contexts_right=extract_context_pairs(corpus_path,dict_pairvocab,window_size,word2index,'r')
        output_folder_path_right=os.path.realpath("./right_contexts/")
        print ("Right contexts succesfully extracted. Now printing them in "+output_folder_path_right+" ...")
        print_contexts(dict_contexts_right,output_folder_path_right,min_freq_cooc,index2word)
        print ("FINISHED. All right contexts have been already printed in "+output_folder_path_right)
