## RELATIVE

The following repository includes the code and pre-trained cross-lingual word embeddings from the paper *[A Latent Variable Model for Learning Distributional Relation Vectors](http://josecamachocollados.com/papers/relative_ijcai2019.pdf)*  (IJCAI 2019).


### Pre-trained embeddings

We release the 300-dimension word embeddings used in our experiments, trained on the English Wikipedia. \[Coming soon\]
In addition, we also release the English Wikipedia dump used in our experiments, and the 300-dimension pre-trained FastText embeddings trained on the same corpus. \[Coming soon\]

*Note 1:* All vocabulary words are lowercased.

### Code

Available now: relative-init

**Requirements:**

- Python 3
- NumPy
- Gensim

### Quick usage

```bash
python relative_init.py -corpus INPUT_CORPUS -embeddings INPUT_WORDEMBEDDINGS
```

With this command you can directly get your relation embeddings given a tokenized corpus as input. The input word embeddings can be *txt* or *bin*, as those formats accepted by gensim. The input word embeddings can be trained on the same corpus (as in the paper) or pre-trained on a different corpus.

Example:

```bash
python relative_init.py -corpus sample_wikipedia_corpus.txt -embeddings fasttext_wikipedia_en_300d.bin
```

#### Parameters

A number of optional parameters can be specified to your needs: 

-contexts: Path of the input contexts directory, so these do not need to be re-compiled (output of "context_extraction.py").

-norm: Output vectors normalized ("true") or not ("false"). Default: false

-wordfreq: Path of the frequency dictionary file.

-window: Co-ocurring window size. Default: 10

-min_freq_cooc: Minimum frequency of words between word pair: increasing the number can speed up the calculations and reduce memory but we would recommend keeping this number low. Default: 1

-pairvocab: Path of the input pair vocabulary file (tab-separated with at least two columns, one pair per line).

-wordsize: Maximum number of words considered (sorted by frequency). Default: 100000

-output_pairvocab: Co-ocurring window size. Default: 10

-stopwords: Path to stopwords file. Default: ./stopwords_en.txt

-min_freq: Minimum frequency of words. Default: 5

-smoothing: Alpha smoothing factor in the pmi calculation. Default: 1

-min_occ: Minimum number of occurrences required for word pairs. Default: 5

-max_pairsize: Maximum number of word pairs. Default: 3000000

##### Example:

For example, if you would like to give your own pair vocabulary as input and specify a shorter window size to 5 (instead of the default 10), you can type the following:

```bash
python relative_init.py -corpus sample_wikipedia_corpus.txt -embeddings fasttext_wikipedia_en_300d.bin -pairvocab pair_vocab.txt -window 5 
```

#### Working step by step

It is also possible to run relative-init step by step:

1. "get_vocabulary.py": This script outputs word vocabulary ("word_vocab.txt"), pair vocabulary ("pair_vocab_pmi.txt") and word frequency dictionary ("word_frequency_all.txt"), computed on the input corpus.
2. "context_extraction.py": This script extracts contexts for word pairs from the input corpus given a pair vocabulary file.
3. "relative_init.py": Instead of starting from scratch, contexts from the previous step can be directly provided.

Parameters are similar to the ones indicated above, check documentation in the script if in doubt. Some important notes/advice when working with the code:

*Note 1:* If you have memory issues when running the code, you can split your pair vocabulary files in several files and concatenate the resulting output vectors (computation is done independently for each pair).


### Reference paper

If you use any of these resources, please cite the following [paper](http://josecamachocollados.com/papers/relative_ijcai2019.pdf):
```bash
@InProceedings{camachocollados:relativeijcai2019,
  author = 	"Camacho-Collados, Jose and Espinosa-Anke, Luis and Shoaib, Jameel and Schockaert, Steven",
  title = 	"A Latent Variable Model for Learning Distributional Relation Vectors",
  booktitle = 	"Proceedings of IJCAI",
  year = 	"2019",
  location = 	"Macau, China"
}

```
