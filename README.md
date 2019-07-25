## RELATIVE

The following repository includes the code and pre-trained cross-lingual word embeddings from the paper *[A Latent Variable Model for Learning Distributional Relation Vectors](http://josecamachocollados.com/papers/relative_ijcai2019.pdf)*  (IJCAI 2019).


### Pre-trained embeddings

We release the corpus and pre-trained embeddings used in our experiments, in both *txt* and *bin* formats:
- English **Wikipedia** corpus (tokenized and lowercased), January 2018: \[[zip](https://drive.google.com/file/d/17EBy4GD4tXl9G4NTjuIuG5ET7wfG4-xa/view?usp=sharing)\] ~4.3GB
- 300-dimension **FastText** word embeddings: \[[bin](https://drive.google.com/file/d/1dQm_haKr2ZrQBvyBlCVnwL2W8mwj0T4D/view?usp=sharing)\] ~ 2.6GB; \[[txt](https://drive.google.com/file/d/1r9RFdyqg998UaLA0huZc9PIwF8rBlITN/view?usp=sharing)\] ~5.1GB
- 300-dimension **Relative-init** relation embeddings: \[[bin](https://drive.google.com/file/d/1HVJnTjcaQ3aCLdwTZwiGLpMDyEylx-zS/view?usp=sharing)\] ~1.4GB; \[[txt](https://drive.google.com/file/d/1SFcW6MxQI5N38R3mG1Pe10AVWc38NGFI/view?usp=sharing)\] ~7.1GB
- 300-dimension **Relative** relation embeddings (normalized): \[[bin](https://drive.google.com/file/d/1-w39MIMUkYuy2wdVGwOcgKimUV1vPOxk/view?usp=sharing)\] ~1.4GB; \[[txt](https://drive.google.com/file/d/1q0HiGJh93ukHxh_acOuWQAdfyzX-6g_N/view?usp=sharing)\] ~7.1GB

*Note 1:* All vocabulary words are lowercased.

*Note 2:* Underscore "_" is used to separate tokens in a multiword expression (e.g. united_states) in the corpus. Double underscore ("__") is used to separate words within the word pair (e.g. paris__france) in the relation embedding files.

### Code

In the following you can find how to easily get your relation embeddings given a corpus.

**Requirements:**

- Python 3
- NumPy
- Gensim

### Quick start: Get your own relation embeddings

```bash
python relative_init.py -corpus INPUT_CORPUS -embeddings INPUT_WORDEMBEDDINGS
```

With this command you can directly get your relation embeddings given a tokenized corpus as input. You can use any word embeddings as input, either in *txt* or *bin* formats (those accepted by gensim). The input word embeddings can be trained on the same corpus (as in the reference paper) or pre-trained on a different corpus.

**Exectution time**: This will very much depend on the size of the corpus and other factors (computer power, parameters, etc.). As an indication, running the default code (as above) in a normal CPU with default parameters on the whole Wikipedia, the total running time is about six hours.

#### Example:

```bash
python relative_init.py -corpus wikipedia_en_preprocessed.txt -embeddings fasttext_wikipedia_en_300d.bin
```

### Parameters

A number of optional parameters can be specified to your needs: 

-contexts: Path of the input contexts directory, so these do not need to be re-compiled (output of "context_extraction.py").

-norm: Output vectors normalized ("true") or not ("false"). Default: false

-wordfreq: Path of the frequency dictionary file.

-window: Co-ocurring window size. Default: 10

-min_freq_cooc: Minimum frequency of words between word pair: increasing the number can speed up the calculations and reduce memory but we would recommend keeping this number low. Default: 1

-pairvocab: Path of the input pair vocabulary file (tab-separated with at least two columns, one word pair per line).

-wordsize: Maximum number of words considered (sorted by frequency). Default: 100000

-output_pairvocab: Co-ocurring window size. Default: 10

-stopwords: Path to stopwords file. Default: stopwords_en.txt

-min_freq: Minimum frequency of words. Default: 5

-smoothing: Alpha smoothing factor in the pmi calculation. Default: 1

-min_occ: Minimum number of occurrences required for word pairs. Default: 5

-max_pairsize: Maximum number of word pairs. Default: 3000000

#### Example:

For example, if you would like to give your own pair vocabulary as input and specify a shorter window size to 5 (instead of the default 10), you can type the following:

```bash
python relative_init.py -corpus wikipedia_en_preprocessed.txt -embeddings fasttext_wikipedia_en_300d.bin -pairvocab pair_vocab.txt -window 5 
```

### Working step by step

It is also possible to run relative-init step by step:

1. *get_vocabulary.py*: This script outputs word vocabulary ("word_vocab.txt"), pair vocabulary ("pair_vocab_pmi.txt") and word frequency dictionary ("word_frequency_all.txt"), computed on the input corpus.
2. *context_extraction.py*: This script extracts contexts for word pairs from the input corpus given a pair vocabulary file.
3. *relative_init.py*: Instead of starting from scratch, contexts from the previous step can be directly provided.

Parameters for each of these steps are similar to the ones indicated above, check documentation in the script if in doubt. Some important notes/advice when working with the code:

*Note 1:* If you have memory issues when running the code, you can split your pair vocabulary files in several files and concatenate the resulting output vectors (computation is done independently for each pair).

*Note 2:* If you would like to optimize for speed, you can play with the parameters by e.g. reducing the window size, max_pairsize or wordsize, or by augmenting min_occ, min_freq or min_freq_cooc. This will also have an effect on a reduced memory workload.


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
If you use FastText, please also cite its corresponding paper.

License
-------

Code and data in this repository are released open-source.

Copyright (C) 2019, Jose Camacho Collados.
