import io, itertools, time
from Levenshtein import distance

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

def allPermutationsAfterElement(list,i):
   result = []
   if i==len(list)-1:
      result = [list]
   else :
      for j in range(i,len(list)):
         list2 = list.copy()
         list2[i] = list[j]
         list2[j] = list[i]
         permutations = allPermutationsAfterElement(list2,i+1)
         for permutation in permutations:
            result.append(permutation)
   return result
     
def allPermutations(list):
   return allPermutationsAfterElement(list,0);
   
# Return all subsets of `s` of size `n`
def allSubsets(s, n):
   return list(itertools.combinations(s, n))

# Return the set of characters of string `a`
def characterList(a):
   charList = []
   for i in range(0, len(a)):
      if a[i] not in charList:
         charList.append(a[i])
   return charList

def stringToIntegerList(a):
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

# Return the Levenshtein parameterized distance between `a` and `b` if the variables are linked by an injection
# FPT algorithm in the size of the alphabets of the two input strings
# Complexity if s1 is the size of the smallest alphabet of the two input strings
# and s2 is the size of the alphabet of the other input strings: 
# O(s1! * A(s2, s1) * poly(size of input strings)) where A(n,k) is the number of arrangements of k elements among n
def parameterizedAlignment(a, b):
   startTime = time.time()
   
   # Put the smallest string in a
   aCharacterList = characterList(a)
   bCharacterList = characterList(b)
   
   if len(aCharacterList) > len(bCharacterList):
      a, b = b, a
      aCharacterList = characterList(a)
      bCharacterList = characterList(b)
   
   print("Character list of a: " + str(aCharacterList))
   print("Character list of b: " + str(bCharacterList))

   allSubs = allSubsets(set(stringToIntegerList(b)), len(aCharacterList))
   aIntegerList = stringToIntegerList(a)
   bIntegerList = stringToIntegerList(b)
   aCharacterIntegerList = list(range(0, len(aCharacterList)))
   bCharacterIntegerList = list(range(0, len(bCharacterList)))
   bCharacterIntegerListSubsets = allSubsets(set(bCharacterIntegerList), len(aCharacterList))

   
   #print("a's integer list: " + str(aIntegerList))
   #print("b's integer list: " + str(bIntegerList))
   
   #print("a's character integer list: " + str(aCharacterIntegerList)) 

   #print("Subsets of b's integer list: " + str(bCharacterIntegerListSubsets))
   
   # Build all permutations of the reference character list
   permutations = allPermutations(aCharacterIntegerList)
   #print(permutations)
   
   # For all permutations, compute the Levenshtein distance with all subsets 
   # of the characters of the other string of the reference string's siz
   smallestDistance = len(b)+len(a)
   bestTransformedA = ""
   bestTransformedB = ""
   bestPerm = []
   bestSubset = []
   for perm in permutations:
      transformedA = buildString(aIntegerList, perm)
      for sub in allSubs:
         transformedB = buildString(bIntegerList, sub)
         # below, weights=(1,1,1) for classical Levenshtein distance, weights=(1,1,10) for deletion/insertion distance
         dist = distance(transformedA, transformedB, weights=(1,1,10))
         if dist < smallestDistance:
            smallestDistance = dist
            bestTransformedA = transformedA
            bestTransformedB = transformedB
            bestPerm = perm
            bestSubset = sub
         
   print(bestTransformedA)
   print(bestTransformedB)
   
   print("Smallest distance: " + str(smallestDistance))
   
   output.writelines("\t".join([str(smallestDistance), a, b, bestTransformedA, bestTransformedB, str(bestPerm), str(bestSubset), str(list(zip(bestPerm, bestSubset))), str(time.time()-startTime)])+"\n")
   return smallestDistance
      
"""
Acte V, Médée, Pierre Corneille : 
TMTMTMTMTMMAUAUAUAUOUOJUJUJMJMJMJMJ
Acte V, Médée, Thomas Corneille : 
TMTMUMUMUMUMUMKUKUOUOKUUMUMUJUJUJJUJMJMJMJM
parameterizedAlignment("TMTMTMTMTMMAUAUAUAUOUOJUJUJMJMJMJMJ","TMTMUMUMUMUMUMKUKUOUOKUUMUMUJUJUJJUJMJMJMJM")

"""

output = open("results.csv", "w", encoding="utf-8", errors = "ignore")
output.writelines("\t".join(["distance", "input1", "input2", "renamed input 1", "renamed input 2", "bestPerm", "bestSubset", "bijection", "computing time"]) + "\n")

parameterizedAlignment("ABABABABACABABADDEDEDEDEDFDGDGDGDG","ABABABABABABABCDCDCDCDCEFEFEFE")
parameterizedAlignment("ABCBCBCBCBCBCBCBCBCBCBCDCBCBDCDCDCDEDEDEDEFEFEFEFEFEFEF","ABABABABABABABABABABABACACDADAEFEFEFEFEGEFEFEHGFGFGF")
parameterizedAlignment("ABABABABABABABABABABACABABADCBEBFAGAH","ABABACBCDCDCDCDCDCDCDCDCDCDCDCE")
parameterizedAlignment("ABACDADABDBDBDBDBCDCBCDCBDCE","ABACBCBCBCBCBCB")
parameterizedAlignment("ABABAACACADAEAEDADAEAEADADEDEDEDEDEDEDED","ABABAACADADACACDAADADADADADADADADAACACACACACAC")
parameterizedAlignment("ABACACACACACACACDCDCDCAEAFAFAFAFAFFGFGF","ABABACACACACAADADADADA")
parameterizedAlignment("ABABABABABCCBCBCBCBCCDCDCBC","ABACACACACACACADADCADCDADADACADACACDACADADADADADCA")
parameterizedAlignment("ABABABCACBCABDABDABDABEFEFEFEFEFEFE","ABABABCBCBCBCBDBDBDBDBDBDEDBDB")
parameterizedAlignment("ABABABCDABAEFEBEBEBEBEACACACADACACDBEBFEFE","ABABACACABAADBDBDEDEDEDEDEDED")
parameterizedAlignment("ABABCBCBCBACACBDEFGBABGCGFEAFGBGBGFBEBFG","ABABABABABABABABABABCADCDCDCECECECECECBC")
parameterizedAlignment("ABABCDCDCDCDCDCDCDCDCEFGFGFGFGFDGFH","ABACADCDADBDBDBDBDBDBDBDBDBDBDBDBDBDBDBA")
parameterizedAlignment("ABACABCAADBDABDBDBDBDEBAFADBDB","ABCABABACBCACBCBADEDEDFGFHDHDFDHDHIF")
parameterizedAlignment("ABABACABCABADEDEDEDEDEDEDF","ABCBACBADE")
parameterizedAlignment("AABABABABABAACDADADCDCDCDC","AABABABABABABABABABABABABABABAACADACADADCDCDCDCDCDCDCDCDCDCDCDCDCDCD")
parameterizedAlignment("ABCBCDBDBDBDBDBDBDBDBDBDBDBDBDBDEDEDEDEDEDEF","ABABABABCACD")
parameterizedAlignment("ABABABABABABABABCDCDEFGFGFGFGFGFEFEEAEAEAEAEECACECACAHFHFHFGFGEAFACA","AABABABABABABABAB")
parameterizedAlignment("A","ABABABABAACBCBCBCBCBACCBCBC")
parameterizedAlignment("ABABABABABABABABABABABABABABABABABABABABCABACACACACBAACACACACACACACACACBABADBADBABADABABABADADABADADBDBDBDABDBADBADBADBADADADADBDABABADBABAB","ABABABACABACACACACACABCABABACACBACACBABABCD")
parameterizedAlignment("ABABABABABABABACDBECDCACACAECDAEACEECDEDECECEDDEDEDEDEDEDEDEDEDEDEDEDEDEDEDEDEEEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAE","ABCABACABACABDEFEBEAEAEFAEAEDEFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDADADADADADADADADADADADAD")
parameterizedAlignment("ABABABABABCBCBABCADADADADADADACACACACACACACADADADADACDADCADACACADADACACACDCACAABABABCBDCABABCBDBABCBACBCBCBEBEBCBEBEBEBAEBCEBACEBEAECECECECDEDCDBEAEBFBGBFHB","ABCBDBDBDBDBDBDBDBDBDBDBDBDBDEFGFGFGBDBDBEDBDBDBCBCBCBCDCDCBCDCFCFCFCFCFCFCDFC")
parameterizedAlignment("ABABABABABABCBCBCBCBCBCBCBCBCBCBCBCBCBCDCDCDCDCDCECEDEDEDEDED","ABABABABABABABABABABACBCACACACACACABACBCBCBABCACABABABABABABDEDEDEDEDEDEDEDEDEDEBDBEBEBEBEBEBEBDBEBEBEDEDED")
parameterizedAlignment("ABCAACACDCDCDCDCDCDCDCDCDCDCDCDCDCDCDCDEDEDEDEDEDEDBEBABAADADADADADADA","AABABABABABABABABABACDCDCDCDCDCDCDCDCDCDCDCDCDCDCDCDCDAEAEAEAEFEFEFEAFAFAFAFAFAFAFAFAFAFEACACBCACBCBCBCBCBCBCBCBCBC")
parameterizedAlignment("ABABABACACACACACACACACACACADCADADCDCDCDACBBECECECEACEAEACFGFGFGFGAGAGAGAGAGCGCFCG","ABABABABABABABABABABABABABABABABABABAABABABABAABABABABCBCBCBCBCCACACACACACAC")
parameterizedAlignment("ABABABABABCBCBCBCDCDCDCDCBEBBCBCBECECEBCEEECBECBECECECECBCBECBFFGFFFEFEFEGFGFG","ABABABABABABABABABABABABABABABCBCBCBCBCBCBCBCBCBCBCBCBCDBDBCEFCADECGEGEGEGEGEGEGHGHGHGDCDCD")
parameterizedAlignment("ABACACACDAEDADABDADADABFDFBAFAFAGHGBGHDCGCGA","ABABABCABABCBCBCBCBCBCBCBDEDEDEDEDEDEDEDFGFGFGFDFDGDFDGDGDGDGDGDGDGDFBCGFCGCHCFDFDFCDFDGFCDFB")
parameterizedAlignment("AAAAAAAAAAAAAAAAAAAAAAAABABABABABABABAABABABABABABABABABABCBCBCBCBCBCBCABABABAABABA","ABABABABABABACACADCDCDCDCDCDCDCDCDCD")
parameterizedAlignment("ABABABABABABABCCCDCDCDCDCABABABABABABABABABABABABABABABABABCBCACABAEABFAFABFAFAFBAFEC","ABCBCBCBCBCBCACACACACACACACACADEDEDEDEDBEBEBEBEBEBEBEDE")
parameterizedAlignment("ABABABABABABABABABABACACACACACACACACACACACADDADADADADADADADADADADADACECECECECECECECEFEFEFEFEFEFEFEF","ABABABABABABABABABABABABABABABABABABACACACACACACACACACACACACACACAC")
parameterizedAlignment("ABABCDCABABCABCBCBCBCBCBDCBCBDBDCBCBDBEBEBEBEBEBEBAFAFAFAFAFAFAFAFAFAFFBFBFBFBFBFBFBFBFBGBB","ABABABABABABCBCBCBCBCBCBCBCBCBCBCBCBDCDCDABABABABABABABABAEBAEAEAEABABAB")
parameterizedAlignment("ABACBCDCDCDCDCDCDCDCDCDCDCDCDCDCDABABABEAEAEAEAEAEAEAEAEA","ABACABACABABABABCBCABCBAADACADABADCBACDA")
parameterizedAlignment("ABABABABABABABABCBCBCBCBCBCBCBCBCBCBCBCBCBDCDCCCECECECECECECECECECECEC","ABABABABABABABABCACBCABABCBACBACBCABABABABABDEDEDEDEDED")
parameterizedAlignment("AABACADAEADADADFAFDFDFDFDFAFAFADFDACDFDCFDADACDCDCACADCDADAED","AABABABABABABACACACACACDCDADADADADCACDADAAEADCEADCEACAE")
parameterizedAlignment("ABABABABABABABCBCBCBCBCBCBCBCBCDEFGHIHIHDHIDIDID","ABABACDCECECEDEFCGCGCGCGECGEHEHFHEFHEFEFHGHGCF")
parameterizedAlignment("AABABABABABABCDCDEDCFBGBGBGBGGCGCGCGCGCGCGCGCGCGCFCFCFEFECFCF","ABABABABACDCDCDCEFGDFDFDFDFDGDHIHIHICDCGFDGCDFCFCFCFCFCFCFCFCFCFCGCF")
parameterizedAlignment("ABABABACACDCDCACBEBFGFGFBFEFFCFAF","ABABABABABABABABABABACACACACACACACACACACACACACACACACACACACACDCDCDCDCDECECECECECECECFECEDECEGHCHECE")

#"""
# 10 letters in one of the two strings
parameterizedAlignment("ABACDCDCDCDEFAGAHABABABABGHCICEFEFEJFJEFE","ABACACACACACAADEAEAEABABABA")
parameterizedAlignment("ABABABABCDCECEFCDEDEC","AABABABACACBCBABABADEFGABABABABABABABAHABABABAAIAIAIAIAIAIAHAAJA")
parameterizedAlignment("ABCBDADADBABABABABABABDCADABABABEBCBADADADADADADADADADADADADADADADADADADADADADA","ABABCABACBABDEDEDEDEDFGFGFGFGFGHDADHDIHJAJAJAJAJAJAJ")
parameterizedAlignment("ABABABABABCBCBCBCBCBCBCDEFDEDEDFDCECDCDCDCDCDCDCDCDCDCDBCBDBDBDBDCBCBCDBGAGAGAGAGAGAGAGADHDGBGBCDGDGDHBGBGDAGAHDCHIACIDH","ABCABADEFGHEHEHFDGFGFDIABDJDADADICDIDIDIDIDIDIDIDIDIJI")
parameterizedAlignment("ABABABCDEDEDEDEFEFEFEGEGEGEHCDCHIHCGJHIBHCICHCDGBEIGBECHEGBHC","ABABABABABABABABABABABBABABABABABABABABABCACACACACACACACACACACACACACACACACACACACACACACACACACACDACADADACABEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEBEB")
#"""

"""
# 11 letters in one of the two strings
parameterizedAlignment("ABCBCBABABABDADBDCDCDCEFEABEADAEFEFGAGAEGEGAFBDAEGACHDHAHEHEHAFDBEHAD","ABABABABACDCDEFEFEFEFGEADAFHABDADADFCBCBAGIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJIJKDFDBFBJGDADA")
parameterizedAlignment("ABABABABAABABACBABCBCAACACACACACACACACACACACACACBABABABABABABABABABCDCDCDCEBAEBAFDFDABEDCACACACABABDCDFCABCACACACBACACDACAGBADADACDCDBDCD","ABCBCBCBCBCBCACACACACACACACDEFGAGHIAJCDGKFCDACACGAGACDACACACDAGCIDCIHG")
parameterizedAlignment("ABACACACACACACACACACACACACACAC","ABABABACBABABABCBABABCBDEFEFEFGEGEGEGEGEGEGEGEGEGEGEFGEGEGFGHIHIBHIBICHBIGJGCBCIBCGJIGCGHJGIGIBGIGBIGBGBHIHHKHKHKHKHKHKHKHKHKHKHKHKHKHKHK")
parameterizedAlignment("ABABACADAEAFAGHIGJKHJGHIGJIHJGHIGJIHJAFAFADABAF","ABABABABAACDCACACACACACACACDCDCDCDEDEDEDEDEDEDEDEDECBDBDBCBDCDCDCDCDCDCDCDCDCDBCBDCBDFCDADAGHGH")
parameterizedAlignment("ABCBDEFGHIAICAJKJKAJAJAJAJAJAJA","ABACDCDCDCDCDCDCDCDCDCDCDCDCDCEFEFEFEFEFEFEFEFDFDFDFDFDCDFDGDGDGDCFCDFCFCFCFCFCFECECECECECECEHEHEHEHEHEHEHEHEHEHEHABABA")
parameterizedAlignment("AABABBCBCBCBCDADADADDEDEDEDEEFDFDGAHGHGFDHGGHEHFHECIFEAJHKEKHGKGDEFEBIBBCGHAFADJIHIHA","ABABACACABADEDEDEDEDEDEFGHIDFEFEFDEFEFEFEFEFEFEFEFEDGHIDEAFIGDEFADADEICEFIEGDGBDEFAEDHAIBGBG")
parameterizedAlignment("ABCDAAEFAGHIJGKLKLK","ABABABAACACACDCDCCECEC")
"""

output.close()