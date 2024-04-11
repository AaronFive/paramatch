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


from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner



"""
    heuristic_parameterized_alignment v1.0, 2024-04-11
    A heuristic to solve the parameterized matching problem between two strings,
    with Levenshtein distance and injective variable renaming functions
    Copyright (C) 2024 - Philippe Gambette
    
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


def relabelIntegerList(list, relabelingDictionary):
    """Relabels the integerList using the relabelingDictionary whose images are integers from 0 to n, labeling as n+1 all characters which are not keys of the relabeling dictionary.
    Args:
        list(list): a list of integers
        relabelingDictionary(dict): a dictionary which associates integers to integers from 0 to n
    Returns:
        list: integerList containing integers from 0 to n+1
    """
    newList = []
    maxOutputLetter = 0
    for inputLetter in relabelingDictionary:
        maxOutputLetter = max(maxOutputLetter,relabelingDictionary[inputLetter])
    
    for char in list:
        if char in relabelingDictionary:
            newList.append(relabelingDictionary[char])
        else:
            newList.append(maxOutputLetter+1)    
    return newList

def integerListToString(list):
    """Transforms an integer list into a string with letters starting from A for 0, B for 1, etc.
    Args:
        list(list): a list of integers
    Returns:
        str: string
    """
    string = ""
    for i in list:
        string += chr(65+i)
    return string

def heuristicParameterizedAlignment(a, b):
    """Greedy heuristic to find an injection between the smallest alphabet of the two input strings to the largest alphabet, hoping to minimize the distance between the two parameterized words, computed with the "alignment" Python library (https://pypi.org/project/alignment/) with match score 2, mismatch score -1, gap opening score -2; aims to find, for each character of the first string, the remaining character of the second string which provides the best mapping with the first one, taking into account previously mapped characters and mapping all remaining characters to a single letter
    Args:
        list(list): a list of integers
    Returns:
        str: string
    """
    print("Looking for parameterized alignment for the following strings:")
    print(a)
    print(b)
    startTime = time.time()

    # Put the string with smallest alphabet in a
    aCharacterList = characterList(a)
    bCharacterList = characterList(b)

    if len(aCharacterList) > len(bCharacterList):
        a, b = b, a
        aCharacterList = characterList(a)
        bCharacterList = characterList(b)
    aIntegerList = stringToIntegerList(a)
    bIntegerList = stringToIntegerList(b)
    aCharacterIntegerList = list(range(0, len(aCharacterList)))
    bCharacterIntegerList = list(range(0, len(bCharacterList)))
    """
    print(aCharacterIntegerList)
    print(bCharacterIntegerList)
    print(stringToIntegerList(a))
    print(stringToIntegerList(b))
    """
    aRelabelingDictionary = {}
    bRelabelingDictionary = {}
    
    
    currentlyRelabeledCharacter = 0

    # Create a vocabulary to encode the sequences for their alignment
    v = Vocabulary()
    
    # While the set of remaining characters of the first string to map with characters of the second string is not empty
    while len(aCharacterIntegerList)>0:
        aBestRelabelingDictionary = aRelabelingDictionary.copy()
        bBestRelabelingDictionary = bRelabelingDictionary.copy()
        bestChar1 = aCharacterIntegerList[0]
        bestChar2 = bCharacterIntegerList[0]
        aBestRelabelingDictionary[bestChar1] = currentlyRelabeledCharacter;
        bBestRelabelingDictionary[bestChar2] = currentlyRelabeledCharacter;
        highestNumberOfCurrentlyRelabeledCharacters = 0
        # Test each character of the first string to check if it provides the best alignment with some character of the second string
        for char1 in aCharacterIntegerList:
          aTempRelabelingDictionary = aRelabelingDictionary.copy()
          aTempRelabelingDictionary[char1] = currentlyRelabeledCharacter;
          #print("Relabeling first word with dictionary " + str(aTempRelabelingDictionary))
          tempA = relabelIntegerList(stringToIntegerList(a), aTempRelabelingDictionary)
          aTempString = integerListToString(tempA)
          #print(aTempString)
          # Try to map each character of the second string with char1 
          for char2 in bCharacterIntegerList:
            bTempRelabelingDictionary = bRelabelingDictionary.copy()
            bTempRelabelingDictionary[char2] = currentlyRelabeledCharacter;
            #print("Relabeling second word with dictionary " + str(bTempRelabelingDictionary))
            tempB = relabelIntegerList(stringToIntegerList(b), bTempRelabelingDictionary)
            bTempString = integerListToString(tempB)
            #print(bTempString)
            
            # Encode the sequences to align them.
            aEncoded = v.encodeSequence(Sequence([*aTempString]))
            bEncoded = v.encodeSequence(Sequence([*bTempString]))
            
            # Create a scoring and align the sequences using global aligner.
            scoring = SimpleScoring(2, -1)
            aligner = GlobalSequenceAligner(scoring, -2)
            score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
            
            # Iterate over optimal alignments to count how often the currently relabeled character is properly aligned
            for encoded in encodeds:
               alignment = v.decodeSequenceAlignment(encoded)
               alignmentString = str(alignment).split("\n")
               # Count the number of aligned currently relabeled characters (occurrences of the character corresponding to char1)
               numberOfCurrentlyRelabeledCharacters = 0
               charNumber = 0
               for char in alignmentString[0]:
                   if ord(char) == 65+currentlyRelabeledCharacter and ord(alignmentString[1][charNumber]) == 65+currentlyRelabeledCharacter :
                       numberOfCurrentlyRelabeledCharacters += 1
                   charNumber += 1
               if(numberOfCurrentlyRelabeledCharacters > highestNumberOfCurrentlyRelabeledCharacters):
                   # Update information about the best character mapping found so far : char1 => char2
                   highestNumberOfCurrentlyRelabeledCharacters = numberOfCurrentlyRelabeledCharacters
                   aBestRelabelingDictionary = aTempRelabelingDictionary.copy()
                   bBestRelabelingDictionary = bTempRelabelingDictionary.copy()
                   bestChar1 = char1
                   bestChar2 = char2
                   """
                   print("Best character mapping found so far for first string: " + str(aBestRelabelingDictionary))
                   print("Best character mapping found so far for second string: " + str(bBestRelabelingDictionary))
                   print("Number of aligned currently relabeled characters: " + str(highestNumberOfCurrentlyRelabeledCharacters))
                   print(alignment)
                   print('Alignment score:', alignment.score)
                   print('Percent identity:', alignment.percentIdentity())
                   """
        
        # Prepare the next step, update the relabeling dictionary with the best pair char1 => char2 found in this step
        currentlyRelabeledCharacter += 1
        aRelabelingDictionary = aBestRelabelingDictionary.copy()
        bRelabelingDictionary = bBestRelabelingDictionary.copy()
        aCharacterIntegerList.remove(bestChar1)
        bCharacterIntegerList.remove(bestChar2)
        """
        print(aCharacterIntegerList)
        print(bCharacterIntegerList)

        print("Best character mapping found so far for first string: " + str(aRelabelingDictionary))
        print("Best character mapping found so far for second string: " + str(bRelabelingDictionary))
        """
    tempA = relabelIntegerList(stringToIntegerList(a), aRelabelingDictionary)
    tempB = relabelIntegerList(stringToIntegerList(b), bRelabelingDictionary)
    aTempString = integerListToString(tempA)
    bTempString = integerListToString(tempB)
    print("Strings obtained after applying the character relabeling found by the heuristic")
    print(aTempString)
    print(bTempString)
    aEncoded = v.encodeSequence(Sequence([*aTempString]))
    bEncoded = v.encodeSequence(Sequence([*bTempString]))
    # Create a scoring and align the sequences using global aligner.
    scoring = SimpleScoring(2, -1)
    aligner = GlobalSequenceAligner(scoring, -2)
    score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
    alignment = v.decodeSequenceAlignment(encodeds[0])
    print("Best alignment found (only a substring of the longest string may appear below):")
    print(alignment)
    print('Alignment score:', alignment.score)
    print('Percent identity:', alignment.percentIdentity())
    

heuristicParameterizedAlignment("TMTMTMTMTMMAUAUAUAUOUOJUJUJMJMJMJMJ","NMNMUMUMUMUMUMKUKUOUOKUUMUMUJUJUJJUJMJMJMJM")