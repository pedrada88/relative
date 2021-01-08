# -*- coding: utf-8 -*-
import os
import operator
import sys
from argparse import ArgumentParser
from get_vocabulary import get_word_vocab, get_pair_vocab, get_dict_pairvocab_fromset, get_stopwords
from context_extraction import extract_context_pairs,load_dictfreq_file,get_vocab_fromfile
import gensim
import numpy as np


def load_embeddings(embeddings_path):
    print('Loading embeddings:',embeddings_path)
    try:
        model=gensim.models.KeyedVectors.load_word2vec_format(embeddings_path,binary=True)
    except:
        try:
            model=gensim.models.KeyedVectors.load_word2vec_format(embeddings_path)
        except:
            print ("ERROR! Couldnt load embeddings from "+embeddings_path)
            sys.exit('Couldnt load embeddings')
    vocab=model.wv.index2word
    dims=model.__getitem__(vocab[0]).shape[0]
    vocab=set(vocab)
    return model,vocab,dims

def insert(original_path,string):
    with open(original_path,'r') as f:
        with open(original_path+".temp",'w') as f2: 
            f2.write(string)
            for line in f:
                f2.write(line)
    os.rename(original_path+".temp",original_path)

def relativeinit_fromcontexts_file(output_path,input_contexts_path,modelwords,vocabwords,dimwords,norm_vectors):
    txtfile=open(output_path,'w',encoding='utf-8')
    cont_lines=0
    listing=os.listdir(input_contexts_path)
    for in_folder in listing:
        word1=in_folder[1:-1]
        input_folder_word=input_contexts_path+in_folder+"/"
        listing_word=os.listdir(input_folder_word)
        for in_file in listing_word:
            word2=in_file[1:-5]
            pair=word1+"__"+word2
            pair_cooc_file=open(input_folder_word+in_file,encoding='utf-8').readlines()
            processed=False
            vector_pair=np.zeros(dimwords)
            for line in pair_cooc_file:
                linesplit=line.replace("\n","").split("\t")
                word_cooc=linesplit[0]
                freq=float(linesplit[1])
                #if freq<min_freq_cooc_pairs: break
                if word_cooc in vocabwords:
                    processed=True
                    vector_word_cooc=modelwords.__getitem__(word_cooc)
                    vector_pair=vector_pair+(freq*vector_word_cooc)
            if processed==True:
                cont_lines+=1
                if norm_vectors==True: vector_pair=vector_pair/np.linalg.norm(vector_pair)
                txtfile.write(pair)
                for dim in vector_pair:
                    txtfile.write(" "+str(dim))
                txtfile.write("\n")
    txtfile.close()
    print ("Done computing relative_init relation embeddings, adding first line to file...")
    first_line=str(cont_lines)+" "+str(dimwords)+"\n"
    insert(output_path,first_line)
    print ("Finished. The new embeddings are available at "+output_path)

def relativeinit_fromcontexts_dict(output_path,dict_contexts,modelwords,vocabwords,dimwords,norm_vectors,index2word,min_freq_cooc):
    txtfile=open(output_path,'w',encoding='utf-8')
    cont_lines=0
    for index1 in dict_contexts:
        for index2 in dict_contexts[index1]:
            if dict_contexts[index1][index2]=={}: continue
            processed=False
            vector_pair=np.zeros(dimwords)
            cont_pair_cooc=0
            for index_cooc in dict_contexts[index1][index2]:
                freq=dict_contexts[index1][index2][index_cooc]
                if freq>=min_freq_cooc:
                    word_cooc=index2word[index_cooc]
                    if word_cooc in vocabwords:
                        processed=True
                        vector_word_cooc=modelwords.__getitem__(word_cooc)
                        vector_pair=vector_pair+(freq*vector_word_cooc)
                        cont_pair_cooc+=1
            if processed==True:
                pair=index2word[index1]+"__"+index2word[index2]
                cont_lines+=1
                txtfile.write(pair)
                if norm_vectors==True:
                    vector_pair=vector_pair/np.linalg.norm(vector_pair)
                    for dim in vector_pair:
                        txtfile.write(" "+str(dim))
                else:
                    for dim in vector_pair:
                        txtfile.write(" "+str(dim/cont_pair_cooc))
                txtfile.write("\n")               
    txtfile.close()
    print ("Done computing relative_init relation embeddings, adding first line to file...")
    first_line=str(cont_lines)+" "+str(dimwords)+"\n"
    insert(output_path,first_line)
    print ("Finished. The new embeddings are available at "+output_path)

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-embeddings', '--input_embeddings', help='Input word embeddings path', required=True)
    parser.add_argument('-norm', '--normalization', help='Output vectors normalized ("true") or not ("false")', required=False, default="false")
    parser.add_argument('-output', '--output_vectors_path', help='Output file path to store relation vectors', required=False, default="./relative_init_vectors.txt")
    parser.add_argument('-contexts', '--input_contexts_path', help='Path of the input contexts directory. Write "false" if not provided', required=False, default="false")

    # The following parameters are needed if contexts are not provided

    parser.add_argument('-corpus', '--corpus_file', help='Input corpus path (tokenized)', required=False)
    parser.add_argument('-wordfreq', '--input_wordfrequency_file', help='Path of the frequency dictionary file', required=False, default="false")
    parser.add_argument('-window', '--window_size', help='Co-ocurring window size', required=False, default=10)
    parser.add_argument('-min_freq_cooc', '--minimum_frequency_context',
        help='Minimum frequency of words between word pair: increasing the number can speed up the calculations and reduce memory but we would recommend keeping this number low', required=False, default=1)
    parser.add_argument('-pairvocab', '--input_vocab',
        help='Path of the input pair vocabulary file (tab-separated with at least two columns, one pair per line)', required=False, default="false")
    parser.add_argument('-symmetry', '--symmetry', help='Indicates whether pairs are symmetric (true) or not (false)', required=False, default="false")

    # The following parameters are needed if pair vocabulary is not provided
    
    parser.add_argument('-wordsize', '--wordvocabulary_size',
                        help='Maximum number of words considered (sorted by frequency)', required=False, default=100000)
    parser.add_argument('-stopwords', '--stopwords_path',
                        help='Path to stopwords file. Write "false" if no stopwords to be used', required=False, default="./stopwords_en.txt")
    parser.add_argument('-min_freq', '--minimum_frequency',
                        help='Minimum frequency of words', required=False, default=5)
    parser.add_argument('-smoothing', '--alpha_smoothing_factor', help='Alpha smoothing factor in the pmi calculation', required=False, default=1)
    parser.add_argument('-min_occ', '--min_occurrences_pairs', help='Minimum number of occurrences required for word pairs', required=False, default=20)
    parser.add_argument('-max_pairsize', '--max_pairvocabulary_size', help='Maximum number of word pairs', required=False, default=3000000)
    
    args = vars(parser.parse_args())

    corpus_path=args['corpus_file']
    embeddings_path=args['input_embeddings']
    input_contexts_path=args['input_contexts_path']
    norm_vectors=args['normalization']
    
    output_path=args['output_vectors_path']
    window_size=int(args['window_size'])
    min_freq=int(args['minimum_frequency'])
    num_words=int(args['wordvocabulary_size'])
    
    print ("Loading embeddings...")
    modelwords,vocabwords,dimwords=load_embeddings(embeddings_path)
    print ("Embeddings with "+str(dimwords)+" dimensions, loaded.\n")
    
    if input_contexts_path=="false":
        pairvocab_path=args['input_vocab']
        stopwords_path=args['stopwords_path']
        symmetry=args['symmetry'].lower()
        min_freq_cooc=int(args['minimum_frequency_context'])
        #Get frequency dictionary from corpus
        print ("Loading word frequency dictionary...")
        dict_freq=get_word_vocab(corpus_path)
        if stopwords_path.lower()=="false": set_stopwords=set()
        else: set_stopwords=get_stopwords(stopwords_path)
        word2index={}
        index2word={}
        list_freq_sorted=sorted(dict_freq.items(), key=operator.itemgetter(1), reverse=True)
        cont_wordvocab=0
        set_wordvocab=set()
        for word,freq in list_freq_sorted:
            if freq<min_freq: break
            if cont_wordvocab<num_words and word not in set_stopwords and "__" not in word and not word.isdigit():
                set_wordvocab.add(word)
                word2index[word]=cont_wordvocab
                index2word[cont_wordvocab]=word
                cont_wordvocab+=1
        if pairvocab_path.lower()=="false":
            print ("Done loading word frequency dictionary. Now creating word and pair vocabularies (this can take a couple of hours depending on the size of the corpus)...")
            alpha_smoothing=float(args['alpha_smoothing_factor'])
            min_occ=int(args['min_occurrences_pairs'])
            max_pairsize=int(args['max_pairvocabulary_size'])
            set_pairvocab=get_pair_vocab(corpus_path,set_wordvocab,window_size,min_occ,max_pairsize,alpha_smoothing,word2index,index2word,"false",symmetry)
            dict_pairvocab=get_dict_pairvocab_fromset(set_pairvocab,word2index)
        else:
            print ("Done loading word frequency dictionary. Now loading input pair file")
            # Retrieve pair and word vocabulary (dictionary)
            dict_pairvocab=get_vocab_fromfile(pairvocab_path,word2index)
        #Extend word2index to words in word embedding vocabulary
        for word in vocabwords:
            if word not in word2index:
                word2index[word]=cont_wordvocab
                index2word[cont_wordvocab]=word
                cont_wordvocab+=1
        #Extract contexts
        print ("Vocabulary loaded. Now extracting contexts...(this can take a few hours depending on the size of the corpus)\n")
        dict_contexts=extract_context_pairs(corpus_path,dict_pairvocab,window_size,word2index,symmetry)
        #Get relative_init vectors
        print ("All central contexts have been already loaded. Now computing relative-init vectors...")
        relativeinit_fromcontexts_dict(output_path,dict_contexts,modelwords,vocabwords,dimwords,norm_vectors,index2word,min_freq_cooc)
    else:
        relativeinit_fromcontexts_file(output_path,input_contexts_path,modelwords,vocabwords,dimwords,norm_vectors)
    print ("FINISHED. Relative-init vectors are available at "+output_path)


    
        
    
