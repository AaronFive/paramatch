import io, itertools, time
import multiprocessing
import os
import csv
from typing import List
from itertools import count
from multiprocessing import Process
from xml.dom import minidom
from unidecode import unidecode
from Levenshtein import distance
from utils import get_title, get_all_acts_dialogues, normalize_scene

"""
    fpt_alphabet_size v1.0, 2022-12-05
    Solving the parameterized matching problem between two strings,
    with Levenshtein distance and injective variable renaming functions
    Copyright (C) 2022 - Philippe Gambette
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
"""


def allPermutationsAfterElement(lst, i):
    """Returns the list of all permutations of lst keeping the i first elements in place.

    Args:
        lst (list): list of elements to permute
        i (int): Empty set to fill with all sources.

    Returns:
        list: List of permutations
    """
    result = []
    if i == len(lst) - 1:
        result = [lst]
    else:
        for j in range(i, len(lst)):
            list2 = lst.copy()
            list2[i] = lst[j]
            list2[j] = lst[i]
            permutations = allPermutationsAfterElement(list2, i + 1)
            for permutation in permutations:
                result.append(permutation)
    return result


def allPermutations(lst):
    """Returns the list of all permutations of lst """
    return allPermutationsAfterElement(lst, 0)


def allSubsets(s, n):
    """Return all subsets of s of size n """
    return list(itertools.combinations(s, n))


def characterList(a):
    """Returns the set of characters of string `a` """
    charList = []
    for i in range(0, len(a)):
        if a[i] not in charList:
            charList.append(a[i])
    return charList


def stringToIntegerList(a):
    """Returns a as a list of integers, each letter corresponding to an integer, ordered by first appearance in a.
    Args:
        a(str)
    Returns:
        list: a as a list of integers
    """
    integerList = []
    charSet = {}
    charNb = 0
    for letter in a:
        if letter not in charSet:
            charSet[letter] = charNb
            charNb += 1
        integerList.append(charSet[letter])
    return integerList


def buildString(integerList, characterIntegerList):
    """Inverse of stringToIntegerList. Rebuilds the string given in integerList using the translation given by characterIntegerList.
    Args:
        integerList(list): a string to be rebuilt, written as a list of integers
        characterIntegerList(list): a list of integers appearing in integerList
    Returns:
        str: integerList with integers replaced by letters of the alphabet.
    """
    characterTransformation = {}
    characterNb = 0
    string = ""
    for c in characterIntegerList:
        characterTransformation[c] = chr(65 + characterNb)
        characterNb += 1

    for c in range(0, len(integerList)):
        if c not in characterTransformation:
            characterTransformation[c] = chr(65 + characterNb)
            characterNb += 1
    for i in integerList:
        string += characterTransformation[i]
    return string


# FPT algorithm in the size of the alphabets of the two input strings
# Complexity if s1 is the size of the smallest alphabet of the two input strings
# and s2 is the size of the alphabet of the other input strings: 
# O(s1! * A(s2, s1) * poly(size of input strings)) where A(n,k) is the number of arrangements of k elements among n
def parameterizedAlignment(a, b, queue, pair_name=None):
    """Returns the Levenshtein parameterized distance between `a` and `b` if the variables are linked by an injection.
    Sends details about the instance up queue to be logged later.
    Args:
        a (str): string to be compared
        b (str): string to be compared
        queue(multiprocessing.queues.Queue) : queue used to pass results to parent caller
                characterIntegerList(list): a list of integers appearin in integerList
        pair_name(str): Name describing the instance, for logging purposes.
    Returns:
        str: integerList with integers replaced by letters of the alphabet.
    """
    startTime = time.time()

    # Put the smallest string in a
    aCharacterList = characterList(a)
    bCharacterList = characterList(b)

    if len(aCharacterList) > len(bCharacterList):
        a, b = b, a
        aCharacterList = characterList(a)
        bCharacterList = characterList(b)
    allSubs = allSubsets(set(stringToIntegerList(b)), len(aCharacterList))
    aIntegerList = stringToIntegerList(a)
    bIntegerList = stringToIntegerList(b)
    aCharacterIntegerList = list(range(0, len(aCharacterList)))
    bCharacterIntegerList = list(range(0, len(bCharacterList)))
    bCharacterIntegerListSubsets = allSubsets(set(bCharacterIntegerList), len(aCharacterList))

    # Build all permutations of the reference character list
    permutations = allPermutations(aCharacterIntegerList)

    # For all permutations, compute the Levenshtein distance with all subsets
    # of the characters of the other string of the reference string's size
    smallestDistance = len(b) + len(a)
    bestTransformedA = ""
    bestTransformedB = ""
    bestPerm = []
    bestSubset = []
    for perm in permutations:
        transformedA = buildString(aIntegerList, perm)
        for sub in allSubs:
            transformedB = buildString(bIntegerList, sub)
            # below, weights=(1,1,1) for classical Levenshtein distance, weights=(1,1,10) for deletion/insertion
            # distance
            dist = distance(transformedA, transformedB, weights=(1, 1, 10))
            if dist < smallestDistance:
                smallestDistance = dist
                bestTransformedA = transformedA
                bestTransformedB = transformedB
                bestPerm = perm
                bestSubset = sub

    print("Smallest distance: " + str(smallestDistance))

    csv_row = {"pair name": pair_name, "distance": str(smallestDistance), "input1": a, "input2": b,
               "renamed input 1": bestTransformedA, "renamed input 2": bestTransformedB,
               "bestPerm": str(bestPerm), "bestSubset": str(bestSubset),
               "bijection": str(list(zip(bestPerm, bestSubset))),
               "computing time": str(time.time() - startTime)}
    for x in csv_row:
        queue.put((x, csv_row[x]))
    return smallestDistance


def encode_scenes(scene1, scene2):
    """Given two files of plays, encodes them as parameterized words and saves the equivalences in dictionnaries."""
    u, d1 = normalize_scene(scene1, True)
    v, d2 = normalize_scene(scene2, True)
    return '', d1, d2, u, v


def compare_pieces(f1, f2, pair_name, gwriter, timeout=60):
    """Given two files of plays, run the parameterized matching comparison and logs the results.
    Logs the result in a csv file given by gwriter.
    Args:
        f1 (str): Path to first play
        f2 (str): Path to second play
        pair_name(str): Name of the two plays
        gwriter(csv.DictWriter) : Writer for the csv output
        timeout(int): Only used for logging purposes, when called with a timeout
        """
    # Getting plays, titles, and acts
    piece1 = minidom.parse(open(f1, 'rb'))
    piece2 = minidom.parse(open(f2, 'rb'))
    title1, title2 = unidecode(get_title(piece1)), unidecode(get_title(piece2))
    acts1, acts2 = get_all_acts_dialogues(piece1), get_all_acts_dialogues(piece2)

    # Comparing number of acts of each play
    if len(acts1) != len(acts2):
        m = min(len(acts1), len(acts2))
        acts1, acts2 = acts1[:m], acts2[:m]
        print(f" Warning : {title1} and {title2} do not have the same number of acts. Comparing only first {m} acts")

    # We compare act 1 with act 1, 2 with 2, etc
    for (act_number, (a1, a2)) in enumerate(zip(acts1, acts2)):
        # New act
        print(f'Act {act_number + 1}')

        # Encoding the acts as parameterized words
        input_name, d1, d2, normalized_a1, normalized_a2 = encode_scenes(a1, a2)
        smallest_alphabet_size = min(len(d1), len(d2))

        # Now we call the FPT algorithm
        # We execute it with a timeout. To do so, we use the multiprocessing library.
        print('Calling resolution algorithm ...')
        # What we want to get back from the call is a dictionnary. It is however unhashable, and therefore cannot be
        # obtained directly as a return of the call. Hence we use a queue to stock all the results and only put them
        # in a dictionnary aftewards.
        queue = multiprocessing.Queue()
        csv_row = dict()
        p1 = Process(target=parameterizedAlignment,
                     args=(normalized_a1, normalized_a2, queue, f'{pair_name}_{act_number + 1}'), name='FPTtry')
        p1.start()
        p1.join(timeout=timeout)
        # Case 1 : call has timed out, we fill the csv accordingly
        if p1.exitcode is None:
            p1.kill()
            # TODO: Log the best solution found instead
            csv_row = {"pair name": f'{pair_name}_{act_number + 1}', "distance": None, "input1": normalized_a1,
                       "input2": normalized_a2,
                       "renamed input 1": None, "renamed input 2": None,
                       "bestPerm": None, "bestSubset": None,
                       "bijection": None,
                       "computing time": 'TIMEOUT', "alphabet size": smallest_alphabet_size}
        # Case 2 : Success
        else:
            p1.kill()
            for i in range(10):
                k, v = queue.get()
                csv_row[k] = v
            queue.empty()
            csv_row["alphabet size"] = smallest_alphabet_size
        gwriter.writerow(csv_row)
        print(f'done for act {act_number + 1}')


def compare_pieces_corpus(folder, timeout=60, final_output_dir='Resultats FPT'):
    """Compare all pairs of plays in the specified folder by iterating compare_piece.
    Logs all the results in a csv file.
    Args:
        folder(str):path of the folder containing plays to compare. Must be a folder of folders containing 2 plays.
        timeout(int): How long to compute on each pair in seconds
        final_output_dir(str): path of the directory where to write the output
        """
    # Todo : Also log number of characters per play
    # Getting the folder of pairs to compare
    folders = os.listdir(folder)
    final_output_dir = os.path.join(os.getcwd(), final_output_dir)
    # Creating output csv file
    output_csv = open(os.path.join(final_output_dir, f'FPTcomparisons_tm{timeout}.csv'), 'w+')
    fieldnames = ["pair name", "distance", "input1", "input2", "renamed input 1", "renamed input 2", "bestPerm",
                  "bestSubset", "bijection", "computing time", "alphabet size"]
    gwriter = csv.DictWriter(output_csv, fieldnames=fieldnames)
    gwriter.writeheader()

    folders.sort(key=lambda x: os.path.getsize(os.path.join(folder, x)))
    for f in folders:
        pair_name = f
        print(f'Comparing {pair_name}')
        folder_path = os.path.join(folder, f)
        if os.path.isdir(folder_path):
            plays = os.listdir(folder_path)
            play1, play2 = os.path.join(folder_path, plays[0]), os.path.join(folder_path, plays[1])
            compare_pieces(play1, play2, pair_name, gwriter, timeout)


if __name__ == "__main__":
    # Parameters
    corpus_name = 'corpus11paires'
    timeout = 1200

    corpus_folder = os.path.join(os.getcwd(), corpus_name)
    print(f'comparing all plays of folder {corpus_name}')
    compare_pieces_corpus(corpus_folder, timeout)
    print('Done')
