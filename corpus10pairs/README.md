# paramatch - corpus10pairs

Supplementary material used in experiments presented in the paper entitled *On Distances between Words with Parameters*, by Pierre Bourhis, Aaron Boussidan and Philippe Gambette, accepted at the CPM 2023 conference.


## About

### Corpus of plays

We selected a corpus of 10 pairs of plays where one inspired the other, from the *Hyperpièces* corpus available at https://celinefournial.github.io/hyperpieces/

### Formatting the plays

Our initial motivation to introduce parameterized matching under various distances is theater play comparison. To represent the structure of a theater play, we represent each character by a letter of the alphabet, and create the parameterized word obtained by considering the succession of all consecutive speakers. More precisely, we represent each act of each play of the corpus by a string corresponding to the sequence of speaking characters. A letter may be duplicated in this string if the corresponding characters has lines in the end of a scene and in the beginning of the next one. 

### Comparing the acts of the plays

For each pair of plays where one inspired the other, we compute the edit distance between the two parameter words s1 and s2 representing the first acts, then the one between the two parameter words representing the second act, etc. This distance will be small if both acts have a similar structure in terms of succession of speaking characters. We performed a total 47 comparisons between pairs of acts, whose results are shown below:

|pair name | distance | # of chars of s1 | # of chars of s2 | smallest alphabet size | computing time FPT (ms) | computing time maxSAT (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| ``Bradamante_1`` | 53 | 68 | 17 | 2 | 3 | 11861 |
| ``Bradamante_2`` | 144 | 61 | 151 | 5 | 1080 | >800000 |
| ``Bradamante_3`` | 32 | 40 | 40 | 5 | 64 | 45159 |
| ``Bradamante_4`` | 107 | 30 | 137 | 3 | 69 | 392294 |
| ``Bradamante_5`` | 84 | 69 | 97 | 8 | 298277 | >800000 |
| ``ClorindeMelite_1`` | 62 | 61 | 107 | 5 | 10 | >800000 |
| ``ClorindeMelite_2`` | 61 | 70 | 115 | 5 | 41 | >800000 |
| ``ClorindeMelite_3`` | 47 | 81 | 76 | 3 | 8 | >800000 |
| ``ClorindeMelite_4`` | 55 | 78 | 91 | 7 | 2108 | >800000 |
| ``ClorindeMelite_5`` | 67 | 44 | 93 | 8 | 2502 | >800000 |
| ``Diane Fils Supposé_1`` | 21 | 55 | 52 | 6 | 767 | 64435 |
| ``Diane Fils Supposé_2`` | 12 | 34 | 30 | 6 | 96 | 4786 |
| ``Diane Fils Supposé_3`` | 36 | 48 | 46 | 8 | 10211 | 112014 |
| ``Diane Fils Supposé_4`` | 41 | 61 | 68 | 7 | 5484 | 583547 |
| ``Diane Fils Supposé_5`` | 77 | 85 | 92 | 9 | 748326 | >800000 |
| ``Didon_1`` | 16 | 26 | 10 | 5 | 6 | 415 |
| ``Didon_2`` | 31 | 35 | 40 | 4 | 14 | 28213 |
| ``Didon_3`` | 18 | 37 | 31 | 5 | 109 | 11857 |
| ``Didon_4`` | 32 | 44 | 12 | 4 | 4 | 1097 |
| ``Didon_5`` | 13 | 28 | 15 | 3 | 1 | 1188 |
| ``Felismene_1`` | 65 | 83 | 36 | 3 | 0 | 162426 |
| ``Felismene_2`` | 64 | 85 | 55 | 5 | 14 | >800000 |
| ``Felismene_3`` | 55 | 99 | 66 | 3 | 2 | >800000 |
| ``Felismene_4`` | 55 | 91 | 72 | 5 | 68 | >800000 |
| ``Felismene_5`` | 94 | 120 | 54 | 9 | 67509 | >800000 |
| ``Illusion comique comédie comédiens_1`` | 26 | 1 | 27 | 1 | 0 | 24 |
| ``Illusion comique comédie comédiens_2`` | 100 | 31 | 119 | 8 | 56580 | >800000 |
| ``Illusion comique comédie comédiens_3`` | 82 | 47 | 95 | 8 | 89426 | >800000 |
| ``La Belle Egyptienne_1`` | 101 | 140 | 43 | 4 | 1 | >800000 |
| ``La Belle Egyptienne_2`` | 68 | 79 | 52 | 5 | 454 | >800000 |
| ``La Belle Egyptienne_3`` | 33 | 114 | 92 | 5 | 36 | >800000 |
| ``La Belle Egyptienne_4`` | 93 | 137 | 70 | 7 | 36680 | >800000 |
| ``La Belle Egyptienne_5`` | 94 | 156 | 78 | 7 | 7761 | >800000 |
| ``Mariane_1`` | 27 | 27 | 50 | 4 | 1 | 25683 |
| ``Mariane_2`` | 79 | 33 | 98 | 7 | 904 | >800000 |
| ``Mariane_3`` | 53 | 21 | 64 | 6 | 2151 | 28777 |
| ``Mariane_4`` | 28 | 30 | 36 | 6 | 525 | 28889 |
| ``Porcie_1`` | 19 | 39 | 22 | 4 | 9 | 2424 |
| ``Porcie_2`` | 17 | 19 | 22 | 5 | 487 | 1035 |
| ``Porcie_3`` | 27 | 42 | 29 | 5 | 9 | 30670 |
| ``Porcie_4`` | 23 | 35 | 30 | 5 | 7 | 15652 |
| ``Porcie_5`` | 32 | 41 | 27 | 5 | 303 | 18264 |
| ``Rodogune_1`` | 43 | 57 | 40 | 4 | 4 | 527394 |
| ``Rodogune_2`` | 42 | 26 | 68 | 4 | 1 | 35202 |
| ``Rodogune_3`` | 26 | 40 | 46 | 4 | 2 | 40536 |
| ``Rodogune_4`` | 45 | 70 | 55 | 5 | 6 | >800000 |
| ``Rodogune_5`` | 34 | 61 | 55 | 5 | 12 | 550939 |

Among those 47 comparisons, 26 were solved by the maxSAT algorithm and all by the FPT algorithm, with a 800 second timeout. The computation times are obtained on a XMG laptop running on Windows, with a 2.60 Ghz processor and 16 Gb RAM. Only the running time of MaxHS is provided, the encoding into a MaxSAT formula usually runs in approximately 1 second. 

Note that all instances are solved faster by the FPT algorithm than by the MaxSAT approach.

The analysis of running times depending on the product of the lengths of the input strings, illustrated in the figures below shows that the MaxSAT approach may be relevant for strings with more than 10 distinct characters, but where the product of the length of input strings may not exceed 2000.

![Computing time of the FPT algorithm (in ms) depending on the parameter, the minimum alphabet size of the two input strings!](computing-time-FPT.png "Computing time of the FPT algorithm (in ms) depending on the parameter, the minimum alphabet size of the two input strings")

![Computing time of the maxSAT (in ms) depending on the product of the sizes of the input strings!](computing-time-FPT.png "Computing time of the maxSAT (in ms) depending on the product of the sizes of the input strings")