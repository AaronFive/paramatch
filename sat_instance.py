import os, csv
import time

from utils import *
import re
import doctest
from xml.dom import minidom
from unidecode import unidecode
import subprocess


# This file implements the max-sat reduction

# Alphabetical parameterized word: word of the form ABABCBD... where letters appear consecutively by order of the
# alphabet. May use other symbols if there are more than 26 letters : the ord() of all characters must be consecutive
# and start at 65 (ord('A') = 65)


def get_max_alphabet_size(s_1, s_2):
    """Given two alphabetical parameterized words, returns the size of the alphabet needed to write both of them
     i.e. the rank in the alphabet of the largest letter appearing in both.
    >>> get_max_alphabet_size('ABABC','ABABCBAB')
    4"""
    return max(max(ord(x) for x in s_1), max(ord(x) for x in s_2)) - 64


def get_pi(alphabet_size):
    """ Returns an alphabet ['A', 'B', 'C',...] up until the alphabet_size-th letter of the alphabet
    >>> get_pi(0)
    []
    >>> get_pi(3)
    ['A','B','C']
    """
    pi = []
    for i in range(alphabet_size):
        pi.append(chr(65 + i))
    return pi


# We index variables x_i{i,j} and y_{a,b} and keep them in two dictionnaries
def make_corresp_dictionnaries(string_1, string_2):
    """Given two alphabetical parameterized words, fix an enumeration of the variables that will be used in the sat reduction.
    Args:
        string_1(str): First alphabetical parameterized word
        string_2(str): Second alphabetical parameterized word
    Returns:
        (dict,dict): Dictionnaries which keys are variables x_{i,j} and y_{a,b} respectively and values are corresponding integers"""
    n, m = len(string_1), len(string_2)
    pi_size = get_max_alphabet_size(string_1, string_2)
    pi = get_pi(pi_size)
    x_dict, y_dict = dict(), dict()
    value = 0
    for i in range(n):
        for j in range(m):
            if (i, j) not in x_dict:
                value += 1
                x_dict[i, j] = value
    for a in pi:
        for b in pi:
            if (a, b) not in y_dict:
                value += 1
                y_dict[a, b] = value
    return x_dict, y_dict


def no_double_i_clause(x_dict, i, j1, j2):
    return " ".join([str(-x_dict[i, j1]), str(-x_dict[i, j2]), "0"])


def no_double_j_clause(x_dict, i1, i2, j):
    return " ".join([str(-x_dict[i1, j]), str(-x_dict[i2, j]), "0"])


def no_crossing_clause(x_dict, i1, i2, j1, j2):
    return " ".join([str(-x_dict[i1, j1]), str(-x_dict[i2, j2]), "0"])


def function_clause(y_dict, a, b1, b2):
    return " ".join([str(-y_dict[a, b1]), str(-y_dict[a, b2]), "0"])


def bijective_clause(y_dict, a1, a2, b):
    return " ".join([str(-y_dict[a1, b]), str(-y_dict[a2, b]), "0"])


def match_clause(x_dict, y_dict, i, j, u, v):
    return " ".join([str(-x_dict[i, j]), str(y_dict[u[i], v[j]]), "0"])


# The SAT instance is generated in the WDIMacs format. Description avaiblable at http://www.maxhs.org/docs/wdimacs.html
def make_sat_instance(comments: list, string_1, string_2, bijective=False, substitutions=False):
    """ Create the Max-SAT instance associated to two strings.
    Args:
        comments(str): Comment lines to be added to the top of the file.
        string_1(str): First alphabetical parameterized word
        string_2(str): Second alphabetical parameterized word
        bijective(bool): When True, encodes the problem for PM^d, and for FM^d when False.
        substitutions(bool) : When True, encode the problem with substitutions (unsupported for now).
    Returns:
        final_string(str): content of the WDIMacs file
    """

    # Getting the alphabets of both strings
    n, m = len(string_1), len(string_2)
    pi_size = get_max_alphabet_size(string_1, string_2)
    pi = get_pi(pi_size)
    # Making the dictionnaries to enumerate the variables we will need
    x_dict, y_dict = make_corresp_dictionnaries(string_1, string_2)

    # Comments in the output have to be prefixed by c
    # comments is a list of strings
    # unidecode suppresses weird characters that may trip up maxhs parsing (?)
    comments_list = [" ".join(["c", unidecode(x)]) for x in comments]
    comment_string = "\n".join(comments_list)

    # top is the weight we use to specify a clause is hard in max sat.
    # The sum of the weights of soft clauses is enough
    top = n * m

    # No_Double_i clauses
    clauses_i = []
    for i in range(n):
        for j1 in range(m):
            for j2 in range(m):
                if j1 != j2:
                    clauses_i.append((" ".join([f"{top}", no_double_i_clause(x_dict, i, j1, j2)])))
    clauses_i_string = "\n".join(clauses_i)

    # No_Double_j clauses
    clauses_j = []
    for j in range(m):
        for i1 in range(n):
            for i2 in range(n):
                if i1 != i2:
                    clauses_j.append((" ".join([f"{top}", no_double_j_clause(x_dict, i1, i2, j)])))
    clauses_j_string = "\n".join(clauses_j)

    # No_Crossing clauses
    clauses_crossings = []
    for i1 in range(n):
        for i2 in range(i1 + 1, n):
            for j1 in range(m):
                for j2 in range(j1):
                    clauses_crossings.append(" ".join([f"{top}", no_crossing_clause(x_dict, i1, i2, j1, j2)]))
    clauses_crossings_string = "\n".join(clauses_crossings)

    # Function clauses
    clauses_function = []
    for a in pi:
        for b in pi:
            for c in pi:
                if b != c:
                    clauses_function.append(" ".join([f"{top}", function_clause(y_dict, a, b, c)]))
    clauses_function_string = "\n".join(clauses_function)

    # Bijective clauses
    if bijective:
        clauses_bijective = []
        for a in pi:
            for b in pi:
                for c in pi:
                    if a != b:
                        clauses_bijective.append(" ".join([f"{top}", bijective_clause(y_dict, a, b, c)]))
        clauses_bijective_string = "\n".join(clauses_bijective)

    # Match clauses
    clauses_match = []
    if substitutions:
        sub_weight = 1
    else:
        sub_weight = top
    for i in range(n):
        for j in range(m):
            clauses_match.append((" ".join([f"{sub_weight}", match_clause(x_dict, y_dict, i, j, string_1, string_2)])))
    clauses_match_string = "\n".join(clauses_match)

    nbvar = len(string_1) * len(string_2) + pi_size ** 2
    nb_clauses = len(clauses_match) + len(clauses_function) + len(clauses_crossings) + len(clauses_j) + len(clauses_i)

    header = f"p wcnf {nbvar} {nb_clauses} {top}"

    # To maximize

    clauses_max = []
    for i in range(n):
        for j in range(m):
            clauses_max.append(" ".join(["1", str(x_dict[i, j]), "0"]))
    clauses_max_string = "\n".join(clauses_max)
    all_clauses = [comment_string, header, clauses_i_string, clauses_j_string, clauses_crossings_string,
                   clauses_function_string, clauses_match_string, clauses_max_string]
    if bijective and clauses_bijective_string:
        all_clauses.append(clauses_bijective_string)

    all_clauses = [x for x in all_clauses if x != ""]  # Some clauses may not appear on very small inputs
    final_string = "\n".join(all_clauses)

    return final_string


def encode_scenes(scene1, scene2, name='test', bijective=False, substitutions=False):
    """ Given two scenes, create the maxhs input file.
    Args:
        scene1(list): First scene, as a list of characters.
        scene2(list): Second scene, as a list of characters.
        name(str): Name of the file to create.
        bijective(bool): When True, encodes the problem for PM^d, and for FM^d when False.
        substitutions(bool) : When True, encode the problem with substitutions (unsupported for now).
    Returns:
        (str,dict,dict,str,str): File name produced, dictionnaries indexing sat variables, normalized scenes.

    """
    u, d1 = normalize_scene(scene1, True)
    v, d2 = normalize_scene(scene2, True)
    output_for_maxhs = open(name + '_maxhs', 'w')
    s = make_sat_instance([str(d1), str(d2)], u, v, bijective, substitutions)
    output_for_maxhs.write(s)
    output_for_maxhs.close()
    return name + '_maxhs', d1, d2, u, v


# The output format of MAXhs is described at the same adress http://www.maxhs.org/docs/wdimacs.html
def decode_max_hs_output(d1, d2, u, v, maxhs_answer, name, csv_dict=False):
    """ Given a maxhs output file, translate it into a human readable output and save it in a separate file.
    Args:
        d1(dict): Dictionnary indexing x_{i,j} variables
        d2(dict): Dictionnary indexing y_{a,b} variables
        maxhs_answer(str): Path of the wdimacs file to read from
        name(str): name of the output to create
        csv_dict(dict): Used for logging purposes
    """
    answer = open(maxhs_answer, 'r')
    output_human = open(name + 'output_humain', 'w')
    positives = None
    for x in answer:
        if x[0] == 'v':
            x = re.sub('[^0,1]', '', x)
            positives = list(x)
            positives = [int(x) for x in positives]
            break
    if positives is None:
        raise ValueError('no timeout given but no solution found')
    x_dict, y_dict = make_corresp_dictionnaries(u, v)
    output_human.write(f'Input 1 :{u} \n')
    output_human.write(f'Input 2 :{v}\n')
    output_human.write("Littéraux vrais :\n")
    match_number = 0
    if csv_dict:
        renamed_characters = []
        renamed_letters = dict()
    for (i, truth_value) in enumerate(positives):
        if truth_value == 1:
            pos = invert_dic(x_dict, i + 1)
            if pos is not None:
                output_human.write(f"Match between positions {pos[0]} et {pos[1]}\n")
                match_number += 1
            else:
                pos = invert_dic(y_dict, i + 1)
                if pos is not None:
                    a, b = invert_dic(y_dict, i + 1)
                    character_a, character_b = invert_dic(d1, a), invert_dic(d2, b)
                    output_human.write(f"y_{a, b} ({character_a} renommé en {character_b})\n")
                    if csv_dict:
                        renamed_letters[a] = b
                        renamed_characters.append(f'{character_a} : {character_b}')
                else:
                    print('warning : too many variables')
    distance = (len(u) + len(v) - 2 * match_number)
    if csv_dict:
        csv_dict['Distance'] = distance
        renamed_characters_string = ','.join(renamed_characters)
        csv_dict['Renaming'] = renamed_characters_string
        renamed_u = [renamed_letters.get(x, x) for x in u]
        renamed_u = "".join(renamed_u)
        csv_dict['Input 1 renamed'] = renamed_u
        output_human.write(f" First input after renaming :{renamed_u}")
    output_human.write(f" Number of matches : {match_number}, distance ID with bijection : {distance}")
    # TODO : Appropriate logging of bijection and distance type


def compare_pieces(f1, f2, pair_name, logs_files, csv_writer, final_output_dir, timeout=800):
    """Given two files of plays, run the comparison between them with MaxHS and logs the results.
    Logs the details of computation in logs_files and writes the results in a given csv file.
    Args:
        f1 (str): Path to first play
        f2 (str): Path to second play
        pair_name(str): Name of the two plays compared
        logs_files(_io.TextIOWrapper) : log file
        csv_writer(csv.DictWriter) : Writer for the csv output
        final_output_dir(str):Path to the directory where to save results
        timeout(int): Time in seconds to execute MaxHS before timing out
        """
    # Getting plays, titles, and acts
    piece1 = minidom.parse(open(f1, 'rb'))
    piece2 = minidom.parse(open(f2, 'rb'))
    title1, title2 = unidecode(get_title(piece1)), unidecode(get_title(piece2))
    acts1, acts2 = get_all_acts_dialogues(piece1), get_all_acts_dialogues(piece2)

    # Preparing csv output
    csv_dict = dict()
    csv_dict['Pair name'] = pair_name

    # Comparing number of acts of each play
    if len(acts1) != len(acts2):
        m = min(len(acts1), len(acts2))
        acts1, acts2 = acts1[:m], acts2[:m]
        print(f" Warning : {title1} and {title2} do not have the same number of acts. Comparing only first {m} acts")

    # We compare act 1 with act 1, 2 with 2, etc
    for (act_number, (a1, a2)) in enumerate(zip(acts1, acts2)):
        # New act
        print(f'Act {act_number + 1}')
        csv_dict['Act Number'] = act_number + 1

        # Encoding the acts as parameteried words, and creating the maxhs input file
        t1 = time.time()  # Measuring computing time of MaxHS on this instance
        input_name, d1, d2, normalized_a1, normalized_a2 = encode_scenes(a1, a2, f'{pair_name}_acte_{act_number + 1}',
                                                                         True)
        csv_dict['Input_1'] = normalized_a1
        csv_dict['Input_2'] = normalized_a2
        csv_dict['Input 1 length'] = len(normalized_a1)
        csv_dict['Input 2 length'] = len(normalized_a2)
        csv_dict['Personnages 1'] = d1
        csv_dict['Personnages 2'] = d2

        # Preparing maxHS output file
        output_name = f"{input_name}_output"

        # Now we call MaxHS
        print('Calling MaxHS ...')

        try:  # Case with a succes before timeout
            maxhs_answer = subprocess.run(['/usr/local/MaxHS-2021_eval/build/release/bin/maxhs', '-printSoln',
                                           input_name], capture_output=True, text=True, timeout=timeout)
            # Logging computing time
            computing_time = time.time() - t1
            logs_files.write(f'{pair_name}, acte {act_number + 1} : MaxHS execution time : {computing_time} \n')

            # Saving MaxHS answer
            output_file = open(output_name, 'w')
            output_file.write(maxhs_answer.stdout)
            output_file.close()

            # Decoding MaxHS answer
            # (MaxHS gives us true literals, we now get back to actual character renaming and alignement)

            print('Success, decoding MaxHS output ...')

            human_readable_output = os.path.join(f'{final_output_dir}',
                                                 f'Comparaison {pair_name}  actes {act_number + 1}')
            decode_max_hs_output(d1, d2, normalized_a1, normalized_a2, output_name, human_readable_output, csv_dict)
        except subprocess.TimeoutExpired:  # Case with a timeout
            computing_time = f' {timeout} (Timeout)'
            logs_files.write(f' {pair_name}, acte {act_number + 1} : Timeout after {timeout} s \n')
            print('Timeout')
            csv_dict['Distance'] = None
            csv_dict['Input 1 renamed'] = None
            csv_dict['Renaming'] = None
        csv_dict['Computing time'] = computing_time
        csv_writer.writerow(csv_dict)
        print(f'done for act {act_number + 1}')


def compare_pieces_corpus(folder, final_output_dir='Resultats comparaison'):
    """Compare all pairs of plays in the specified folder by iterating compare_piece.
    Logs all the results in a csv file.
    Args:
        folder(str):path of the folder containing plays to compare. Must be a folder of folders containing 2 plays.
        final_output_dir(str): path of the directory where to write the output
        """
    # Getting the folder of pairs to compare
    folders = os.listdir(folder)
    # Creating output csv file
    output_csv = open(os.path.join(final_output_dir, 'comparisons.csv'), 'w')
    fieldnames = ['Pair name', 'Act Number', 'Distance', 'Input_1', 'Input_2', 'Renaming', 'Input 1 renamed',
                  'Input 1 length', 'Input 2 length', 'Computing time', 'Personnages 1', 'Personnages 2']
    # todo : ajouter nombre de persos
    gwriter = csv.DictWriter(output_csv, fieldnames=fieldnames)
    gwriter.writeheader()

    folders.sort(key=lambda x: os.path.getsize(os.path.join(folder, x)))
    logs_file = open(os.path.join(final_output_dir, 'Logs maxHS comparison'), 'w')
    for f in folders:
        pair_name = f
        print(f'Comparing {pair_name}')
        folder_path = os.path.join(folder, f)
        if os.path.isdir(folder_path):
            plays = os.listdir(folder_path)
            play1, play2 = os.path.join(folder_path, plays[0]), os.path.join(folder_path, plays[1])
            compare_pieces(play1, play2, pair_name, logs_file, gwriter, final_output_dir)


if __name__ == "__main__":
    compare_pieces_corpus(os.path.join(os.getcwd(), 'corpus11paires'))
