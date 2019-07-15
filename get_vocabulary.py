# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import operator
import math


def pmi_smoothed(joint_cooc,total_cooc,freq_word1,freq_word2,alpha_smoothing=1):
  pmi_score=math.log((joint_cooc/total_cooc) / ((freq_word1/total_cooc) * ((freq_word2**alpha_smoothing)/(total_cooc**alpha_smoothing))))
  return pmi_score

def get_dict_weights(corpus_path,set_wordvocab,window_size,word2index):
  corpus_file=open(corpus_path,'r',encoding='utf-8')
  dict_weight={}
  dict_weight_word1={}
  dict_weight_word2={}
  total_cooc=0
  for word in set_wordvocab:
    index=word2index[word]
    dict_weight[index]={}
    dict_weight_word1[index]=0
    dict_weight_word2[index]=0
  for line in corpus_file:
      linesplit=line.strip().split(" ")
      for i in range(len(linesplit)):
        tokeni=linesplit[i]
        if tokeni in set_wordvocab:
          indexi=word2index[tokeni]
          for j in range(i+2,min(i+1+window_size,len(linesplit))):
            tokenj=linesplit[j]
            if tokenj in set_wordvocab and tokenj!=tokeni:
              indexj=word2index[tokenj]
              weight=1/(j-i)
              if indexj in dict_weight[indexi]:
                dict_weight[indexi][indexj][0]+=weight
                dict_weight[indexi][indexj][1]+=1
              else:
                dict_weight[indexi][indexj]=[weight,1]
              total_cooc+=weight
              dict_weight_word1[indexi]+=weight
              dict_weight_word2[indexj]+=weight
  return dict_weight,dict_weight_word1,dict_weight_word2,total_cooc

def get_pair_vocab(corpus_path,set_wordvocab,window_size,min_occ,max_pairsize,alpha_smoothing,word2index,index2word,output_path_pairvocab):
  max_neighbours_per_word=int(max_pairsize/len(set_wordvocab))
  dict_weight,dict_weight_word1,dict_weight_word2,total_cooc=get_dict_weights(corpus_path,set_wordvocab,window_size,word2index)
  dict_pmi={}
  set_pairs=set()
  if output_path_pairvocab!="False": output_file=open(output_path_pairvocab,'w',encoding='utf-8')
  for index1 in dict_weight:
    total_cooc_word1=0
    dict_pmi.clear()
    for index2 in dict_weight[index1]:
      if dict_weight[index1][index2][1]>=min_occ:
        pmi_score=pmi_smoothed(dict_weight[index1][index2][0],total_cooc,dict_weight_word1[index1],dict_weight_word2[index2],alpha_smoothing)
        dict_pmi[index2]=pmi_score
    list_pmi_sorted=sorted(dict_pmi.items(), key=operator.itemgetter(1), reverse=True)[:max_neighbours_per_word]
    word1=index2word[index1]
    for index2,pmi_score in list_pmi_sorted:
      word2=index2word[index2]
      set_pairs.add((word1,word2))
      if output_path_pairvocab!="False": output_file.write(word1+"\t"+word2+"\t"+str(round(pmi_score,3))+"\n")
  if output_path_pairvocab!="False":output_file.close()
  return set_pairs

def get_dict_pairvocab_fromset(set_pairs,word2index):
  dict_pairvocab={}
  for word1,word2 in set_pairs:
      if word1 in word2index and word2 in word2index:
          if word1 not in dict_pairvocab: dict_pairvocab[word1]=set()
          dict_pairvocab[word1].add(word2)
  return dict_pairvocab


#Store the pair vocabulary in a txt file
def print_pairs(set_pairs,output_path):
  output_file=open(output_path,'w',encoding='utf-8')
  for pair in set_pairs:
    output_file.write(pair[0]+"\t"+pair[1]+"\n")
  output_file.close()

def print_wordvocab(set_wordvocab,output_path):
  output_file=open(output_path,'w',encoding='utf-8')
  for word in set_wordvocab:
    output_file.write(word+"\n")
  output_file.close()
      
def get_stopwords(stopwords_path):
    set_stopwords=set()
    stopwords_file=open(stopwords_path,encoding='utf-8').readlines()
    for line in stopwords_file:
        set_stopwords.add(line.strip())
    return set_stopwords


def get_word_vocab(corpus_path):
    corpus_file=open(corpus_path,'r',encoding='utf-8')
    dict_freq={}
    for line in corpus_file:
        linesplit=line.strip().split(" ")
        for token in linesplit:
            if token in dict_freq: dict_freq[token]+=1
            else: dict_freq[token]=1
    return dict_freq


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-corpus', '--corpus_file', help='Input corpus path (tokenized)', required=True)
    parser.add_argument('-wordsize', '--wordvocabulary_size', help='Maximum number of words considered (sorted by frequency)', required=True)
    parser.add_argument('-output', '--output_folder', help='Output directory to store vocabulary files', required=False, default="./vocab/")
    parser.add_argument('-stopwords', '--stopwords_path', help='Path to stopwords file. Write "false" if no stopwords to be used', required=False, default="./stopwords_en.txt")
    parser.add_argument('-window', '--window_size', help='Co-ocurring window size', required=False, default=10)
    parser.add_argument('-min_occ', '--min_occurrences_pairs', help='Minimum number of occurrences required for word pairs', required=False, default=20)
    parser.add_argument('-max_pairsize', '--max_pairvocabulary_size', help='Maximum number of word pairs', required=False, default=3000000)
    parser.add_argument('-smoothing', '--alpha_smoothing_factor', help='Alpha smoothing factor in the pmi calculation (default=1)', required=False, default=0.75)
    parser.add_argument('-min_freq', '--minimum_frequency', help='Minimum frequency of words', required=False, default=5)

    args = vars(parser.parse_args())

    corpus_path=args['corpus_file']
    num_words=int(args['wordvocabulary_size'])
    output_path=args['output_folder']
    stopwords_path=args['stopwords_path']
    window_size=int(args['window_size'])
    min_occ=int(args['min_occurrences_pairs'])
    max_pairsize=int(args['max_pairvocabulary_size'])
    alpha_smoothing=float(args['alpha_smoothing_factor'])
    min_freq=int(args['minimum_frequency'])


    print ("Loading word frequency dictionary...")
    
    #Get frequency dictionary from corpus
    dict_freq=get_word_vocab(corpus_path)
    
    #Ouput file frequency dictionary
    output_path_dictfreq=output_path+"word_frequency_all.txt"
    dictfreq_file=open(output_path_dictfreq,'w',encoding='utf-8')

    if stopwords_path.lower()=="false": set_stopwords=set()
    else: set_stopwords=get_stopwords(stopwords_path)

    #Print word frequency dictionary. Extract word vocabulary set.
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
        dictfreq_file.write(word+"\t"+str(freq)+"\n")
    
    dictfreq_file.close()
    list_freq_sorted.clear()
    dict_freq.clear()

    print ("Done loading word frequency dictionary. Stored in "+output_path_dictfreq+ "\n")
    
    print ("Now computing pair vocabulary... (this can take a couple of hours depending on the size of the corpus)")
    
    #Get and print pair vocabulary
    output_path_pairvocab=output_path+"pair_vocab_pmi.txt"
    set_pairvocab=get_pair_vocab(corpus_path,set_wordvocab,window_size,min_occ,max_pairsize,alpha_smoothing,word2index,index2word,output_path_pairvocab)
    print ("The pair vocabulary has been printed in "+output_path_pairvocab)
    
    #Print final word vocabulary
    final_set_wordvocab=set()
    for word1,word2 in set_pairvocab:
      final_set_wordvocab.add(word1)
      final_set_wordvocab.add(word2)
    
    output_path_wordvocab=output_path+"word_vocab.txt"
    print_wordvocab(final_set_wordvocab,output_path_wordvocab)
    print ("Finished. Word vocabulary printed in "+output_path_wordvocab)
    
    
    
    
    
