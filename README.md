# paramatch
Scripts related to the parameterized matching under edit distance problems



## About

Code presented in the paper entitled *On Distances between Words with Parameters*



## `sat_instance.py`

### `compare_pieces_corpus`

Launches the experiments on the corpus described in the paper.

### `make_sat_instance`

Parameters:
* comments: an internal comment which will be inserted in the maxHS input file
* `string_1`: first input string of the parameterized matching under edit distance problem
* `string_2`: second input string of the parameterized matching under edit distance problem
* `bijective`: type of function associating the characters of the first input string with those of the second one (`False` by default, meaning not injective)
* `substitutions` (False by default): authorized operations (`False` by default, meaning only insertions and deletions allowed, no substitution)

Output: string of the maxHS input file

After putting the content of this output string into a file called `filename`, if MaxHS is available on your system (see http://www.maxhs.org/), you can start MaxHS on this file with the command `maxhs -printSoln *filename*`. The ouput of MaxHS can then be decoded with the function `decode_max_hs_output` to get the parameterized matching edit distance between the two strings.

### `decode_max_hs_output`

Parameters:
* d1: dictionary providing the constants corresponding to the letters in the first input string
* d2: dictionary providing the constants corresponding to the letters in the second input string
* u: first input string of the parameterized matching under edit distance problem
* v: second input string of the parameterized matching under edit distance problem
* maxhs_answer: file name of the output file produced by MaxHS
* name: output file name (`output_humain` will be added as a suffix)
* csv_dict: if true, the generated file will include the result of the renaming of variables on the first input file

Output: no output, metadata in a human readable format about the result of the distance computation will be added to the generated file



## `fpt_alphabet_size.py`

Solve the parameterized matching problem between two strings, with Levenshtein or insertion/deletion distance and injective variable renaming functions

FPT algorithm in the alphabet size, described in Section 5.1 of the paper.

### `parameterizedAlignment`

Parameters:
* `string_1`: first input string of the parameterized matching under edit distance problem
* `string_2`: second input string of the parameterized matching under edit distance problem

Output: edit distance between the two strings, in the context of parameterized matching