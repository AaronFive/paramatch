# -*- coding: utf-8 -*-
"""
@author: aaron
Collection of functions used to parse XML-TEI plays
"""
import glob, os, re, sys, requests, math, csv,warnings
import ast
#import enchant
from xml.dom import minidom



# Get the current folder
folder = os.path.abspath(os.path.dirname(sys.argv[0]))
corpus = 'CorpusDracor'
outputDir = 'Output'
corpusFolder = os.path.join(folder, 'Corpus', corpus)
outputFolder = os.path.join(folder, outputDir)

corpuscsv = 'Dracor_parameterized_plays.csv'
corpus_plays = 'Pickled Dracor/full_plays_dracor.pkl'
corpus_acts_merged = 'Pickled Dracor/merged_acts_dracor.pkl'
corpus_acts_separed = 'Pickled Dracor/separed_acts_dracor.pkl'


#Temp : Marianne
# marianne_file = os.path.join(folder,'Corpus', 'Marianne', 'EMOTHE0544_Mariamne.xml')
# marianne_doc = minidom.parse(open(marianne_file, 'rb'))
# marianne_tristan_file = os.path.join(corpusFolder, 'tristan-mariane.xml')
# marianne_tristan_doc = minidom.parse(open(marianne_tristan_file, 'rb'))



# Fetching data from a play. Inputs are XML-TEI files parsed by minidom
def get_genre(doc):
    """Returns the genre of the play : Tragedie, Comédie, Tragi-Comédie."""
    genre_list = ["Tragédie", "Tragedie", "Comedie", "Comédie", "Tragicomédie", "Tragi-comédie"]
    genre = ""
    genre_entry = doc.getElementsByTagName('genre')
    if len(genre_entry) >= 1:
        genre = genre_entry[0].firstChild.nodeValue

    firstgenre = ""
    if genre == "":
        term = doc.getElementsByTagName("term")
        for c in term:
            typ = c.getAttribute("type")
            possible_genre = c.firstChild.nodeValue
            if typ == "genre":
                genre = possible_genre
            elif possible_genre in ["Tragédie", "Tragedie", "Comedie", "Comédie", "Tragicomédie", "Tragi-comédie",
                                    "Pastorale"]:
                genre = c.firstChild.nodeValue
            if firstgenre == "" and possible_genre not in ["vers", "prose", "mixte"]:
                firstgenre = possible_genre

    if genre == "":
        genre = firstgenre

    if genre == "":
        title = doc.getElementsByTagName('title')
        firstgenre = ""
        for c in title:
            typ = c.getAttribute("type")
            if genre not in genre_list and typ == "sub" and c.firstChild is not None:
                if firstgenre == "":
                    firstgenre = c.firstChild.nodeValue
                genre = c.firstChild.nodeValue
                if genre not in genre_list:
                    for x in genre_list:
                        if x in genre:
                            genre = x

        genre = firstgenre
    return genre


def get_title(doc):
    """Returns the title of a play"""
    title_nodes = doc.getElementsByTagName('title')
    if len(title_nodes) > 0:
        return title_nodes[0].firstChild.nodeValue
    else:
        warnings.warn("No title found")


def get_date(doc):
    """Returns date of printing of a play"""
    date_nodes = doc.getElementsByTagName('date')
    print_date = None
    if date_nodes:
        print_date = date_nodes[0].getAttribute("when")
    return print_date


# Characters can be declared in two ways in an XML-TEI files : either in a <ListPerson> section or in a <castList> section
# The <castList> corresponds to the declaration of characters as it is printed in a paper edition of the book, presenting the characters
# The <ListPerson> is an internal XML list
# Both these sections contain identifiers for the characters, but they do not necesarily match
# All Dracor files contain both a <ListPerson> and a <castList>.
# The <ListPerson> has been generated from the file, and uses the <castList> to infer character full names in French
# In general, the ListPerson section is more coherent with the XML document and should be chosen first
def get_characters_by_cast(doc):
    """Returns the list of identifiers of characters, when the list is declared at the start"""
    id_list = []
    listperson = doc.getElementsByTagName('listPerson')
    if listperson:
        char_list = listperson[0].getElementsByTagName('person')
        return ["".join(["#", c.getAttribute("xml:id")]) for c in char_list]  # prefixing every name by #
    else:
        # if there is no listPerson we use the the castList
        char_list = doc.getElementsByTagName('role')
        for c in char_list:
            name_id = c.getAttribute("corresp")
            if name_id == "":
                name_id = c.getAttribute("id")
            if name_id == "":
                name_id = c.getAttribute("xml:id")
            if name_id == "":
                title = get_title(doc)
                warnings.warn(f" Play {title} :Role has no id nor xml:id nor corresp attribute")
            id_list.append(name_id)
        return id_list


def get_characters_by_bruteforce(doc):
    """Returns the list of identifiers of characters, by looking at each stance"""
    id_list = []
    repliques = doc.getElementsByTagName('sp')
    for r in repliques:
        speaker_id = r.getAttribute("who")
        if speaker_id not in id_list:
            id_list.append(speaker_id)
    return id_list


def get_characters(doc):
    """Returns the list of identifiers of characters"""
    char_list = get_characters_by_cast(doc)
    if not char_list:
        char_list = get_characters_by_bruteforce(doc)
    return char_list


def get_scenes(doc):
    """"Given a play, returns the list of the successions of characters"""
    scene_list = doc.getElementsByTagName('div2')
    scene_list = scene_list + doc.getElementsByTagName('div')
    scene_list = [s for s in scene_list if s.getAttribute("type") == "scene"]
    return [get_characters_in_scene(s) for s in scene_list]


def get_all_scenes_dialogues(doc):
    """Returns the succession of characters talking, in all scenes"""
    scene_list = doc.getElementsByTagName('div2')
    scene_list = scene_list + doc.getElementsByTagName('div')
    scene_list = [s for s in scene_list if s.getAttribute("type") == "scene"]
    return [get_stances_succession(s) for s in scene_list]


def get_all_acts_dialogues(doc):
    """Returns the succession of characters talking, in all acts"""
    scene_list = doc.getElementsByTagName('div') + doc.getElementsByTagName('div1') + doc.getElementsByTagName('div2')
    scene_list = [s for s in scene_list if s.getAttribute("type") in ["act", "acte"]]
    return [get_stances_succession(s) for s in scene_list]


def get_fixed_parameterized_play(play):
    """Returns a paramterized play after correction of character names """
    sc = get_scenes(play)
    return fix_character_names(sc)


# Functions that try to fix typos in character names, and split list of characters
def approximate_renaming(name1, name2, tolerance):
    """Tries to check for typos and variance in character names.
    Checks if candidate is a substring or is at distance <tolerance of real name
    Might rename characters with names too close"""
    edit = False
    if enchant.utils.levenshtein(name1, name2) <= tolerance:
        if not (name1[-1].isnumeric() or name2[-1].isnumeric()):
            edit = True
    return edit or (name1 in name2) or (name1 in name2)


def is_list_of_characters(name, characters):
    """ Checks if a string is a list of characters i.e. "Character 1 Character 2 Character 3"
    Useful for stances said by multiple characters at once"""
    chars_in_name = name.split(" ")
    return len(chars_in_name) > 1 and all([c in characters for c in chars_in_name])


def fix_character_names(play):
    """Tries to fix typos in the name of characters in a play by
        the specification given by approximate_renaming """
    characters = dict()  # dictionnary counting number of occurences
    for s in play:
        for c in s:
            characters[c] = characters.get(c, 0) + 1
    # Either a character is renamed because it's acually a list of characters name
    # Or because there's a typo
    # We indicate the list of character case by True and the typo case by False
    renaming_dict = {c: [False] for c in characters}

    # Splitting character names that are a list of characters
    for c in characters:
        if is_list_of_characters(c, characters):
            renaming_dict[c][0] = True
            renaming_dict[c] = renaming_dict[c] + c.split(" ")
    for c in characters:
        for d in characters:
            if not renaming_dict[d][0] and characters[c] < characters[d] and approximate_renaming(d, c, 0):
                renaming_dict[c].append(d)
    # If multiple candidates are possible for the renaming, we pick the most frequent one
    for c in renaming_dict:
        if not (renaming_dict[c][0]) and len(renaming_dict[c]) > 1:
            most_frequent = max(renaming_dict[c][1:], key=(lambda x: characters[x]))
            renaming_dict[c] = [False, most_frequent]
            # print(c, " renommé en ", renaming_dict[c][1])
    for s in play:
        for c in s.copy():
            if len(renaming_dict[c]) > 1:  # If c is renamed
                s.remove(c)
                for new_name in renaming_dict[c][1:]:
                    s.add(new_name)
    return play


# Fetching data from scene nodes directly
def get_characters_in_scene(s):
    """Given a scene node s, returns a set of its characters"""
    characters = set()
    repliques = s.getElementsByTagName('sp')
    for r in repliques:
        speaker_id = r.getAttribute("who")
        characters.add(speaker_id)
    return characters


def get_stances_succession(s):
    repliques = s.getElementsByTagName('sp')
    scene = [r.getAttribute("who") for r in repliques]
    return scene


def get_characters_in_scene_from_header(s):
    """Reads the declaration of the form 1 'SCENE II. Perso1, Perso2, Perso3,...'
        And returns [Perso1, Perso2, Perso3,...]"""
    characters = set()
    head = s.getElementsByTagName('head')
    if len(head) == 0:
        warnings.warn("Scene has no header")
    else:
        header = head[0].firstChild.nodeValue
        characters = header.split(".")[1]
        characters = characters.split(",")
    return characters


def get_acts(doc):
    """"Given a play, returns the list of the acts"""
    act_list = doc.getElementsByTagName('div1')
    act_list = act_list + doc.getElementsByTagName('div')
    act_list = [a for a in act_list if a.getAttribute("type") in ["act", "acte", "ACTE"]]
    return [get_scenes(a) for a in act_list]


def fixed_cast(play):
    """Returns the set of characters appearing in the play after correction"""
    c = set()
    play = fix_character_names(play)
    for sc in play:
        for char in sc:
            c.add(char)
    return c


def differences_cast_declaration(doc):
    """Checks for the difference in cast between the initial list of characters and the character names appearing.
    Useful to check for typos in TEI"""

    declared_characters = get_characters_by_cast(doc)
    if declared_characters:
        declared_characters.sort()
        title = get_title(doc)
        play = get_scenes(doc)
        cast_list = list(fixed_cast(play))
        cast_list.sort()
        if not all([x == '' for x in declared_characters]) and declared_characters != cast_list:
            print(title, "\n", "declared_characters : ", declared_characters, "\n", "cast_list :", cast_list)
            return False
        return True
    return True


def get_corpus_parameterized_plays(corpus):
    """Returns a dictionnary whose keys are play names and values are paramaterized plays"""
    res = dict()
    for c in os.listdir(corpus):
        play = minidom.parse(open(os.path.join(corpus, c), 'rb'))
        play_name = get_title(play)
        res[play_name] = get_parameterized_play(play)
        print('Parsing ' + play_name)
    return res


def get_corpus_parameterized_acts(corpus, act_types="separate"):
    """Returns a dictionnary whose keys are play names and act number and values are parameterized plays (default)
        If act_types is "merged", keys are play_name and values are list of acts """
    res = dict()
    for c in os.listdir(corpus):
        play = minidom.parse(open(os.path.join(corpus, c), 'rb'))
        play_name = get_title(play)
        print('Parsing ' + play_name)
        acts = get_acts(play)
        if act_types == "separate":
            for (i, a) in enumerate(acts):
                res[play_name + str(i + 1)] = a
        elif act_types == "merged":
            res[play_name] = acts
        else:
            ValueError(f"Unkwon argument for act_types : {act_types} (must be separate or merged)")
    return res


def get_rich_dictionnary_play(play):
    d = dict()
    play_name = get_title(play)
    print('Parsing ' + play_name)
    d['Nom'] = play_name
    d['Genre'] = get_genre(play)
    d['Date'] = get_date(play)
    acts = get_acts(play)
    nb_scenes = 0
    full_play = []
    for (i, a) in enumerate(acts):
        d["Acte " + str(i + 1)] = a
        nb_scenes += len(a)
        full_play.extend(a)
    d['Nombre actes'] = len(acts)
    d['Nombre de scenes'] = nb_scenes
    d['Piece'] = full_play
    d['Personnages'] = fixed_cast(full_play)
    return d


def same_play(play_name1, play_name2):
    """Checks if play_name1 and play_name2 are acts from the same play"""
    return play_name1[:-1] == play_name2[:-1]


def generic_corpus_traversal_1(corpus, f_list, output_name, acts=False):
    """Iterates functions in f_list over given corpus and saves the output as a csv file"""
    output = open(os.path.join(outputFolder, " ".join(["Output ", output_name, corpus, ".csv"])), 'w+')
    fieldnames = ['Nom'] + [f.__name__ for f in f_list]
    gwriter = csv.DictWriter(output, fieldnames=fieldnames)
    gwriter.writeheader()
    if acts:
        pp_corpus = get_corpus_parameterized_acts(corpus, "merged")
    else:
        pp_corpus = get_corpus_parameterized_plays(corpus)

    for play_name in pp_corpus:
        d = dict()
        d['Nom'] = play_name
        for f in f_list:
            res_f = f(pp_corpus[play_name])
            if res_f[0]:
                d[f.__name__] = str(res_f[1])
                # output.write(" ".join([play_name, ':', f.__name__, str(res_f[1]), '\n']))
        gwriter.writerow(d)


def create_csv_output(corpus, output_name):
    output = open(output_name + '.csv', mode='w')
    fieldnames = ['Nom', 'Genre', 'Date', 'Nombre actes', 'Nombre de scenes', 'Acte 1', 'Acte 2', 'Acte 3', 'Acte 4',
                  'Acte 5', 'Piece', 'Personnages']
    gwriter = csv.DictWriter(output, fieldnames=fieldnames)
    gwriter.writeheader()
    for c in os.listdir(corpus):
        play = minidom.parse(open(os.path.join(corpus, c), 'rb'))
        d = get_rich_dictionnary_play(play)
        for f in fieldnames:
            if f not in d:
                d[f] = []
        if d['Nombre actes'] > 5:
            print(f"{d['Nom']} a  {d['Nombre actes']} actes")
        else:
            gwriter.writerow(d)
        if all([x == '' for x in d.values()]):
            print('empty_dict')


def generic_corpus_traversal_2(corpus, f_list, output_name, acts=False, rename=False):
    """Iterates functions in f_list over pairs in the given corpus and saves the output as a text file
        Function should return a boolean and a result (eventually None).
        Only calls returning True as their first value will be taken into account. """
    # Initializing
    output = open(os.path.join(outputFolder, " ".join(["Output ", output_name, corpus, ".txt"])), 'w+')
    seen = set()
    incompatibles, total = 0, 0

    # Getting parameterized plays or acts
    if acts:
        pp_corpus = get_corpus_parameterized_acts(corpus)
    else:
        pp_corpus = get_corpus_parameterized_plays(corpus)

    # Renaming characters by prefixing them with the play they come from
    if rename:
        for play_name in pp_corpus:
            pp_corpus[play_name] = annotate_characters(pp_corpus[play_name], play_name)

    # Iterating over all pairs of plays in the corpus
    for play_name1 in pp_corpus:
        seen.add(play_name1)
        print(play_name1)
        play1 = pp_corpus[play_name1]
        for play_name2 in pp_corpus:
            # Checking if the play hasn't already been seen, and if we're working with acts, that both acts are not
            # from the same play
            if play_name2 not in seen and (not acts or not same_play(play_name1, play_name2)):
                total += 1
                play2 = pp_corpus[play_name2]
                for f in f_list:
                    res_f = f(play1, play2)
                    if res_f[0]:
                        to_output = [play_name1, "et", play_name2, ":", f.__name__, str(res_f[1]), '\n']
                        output.write(" ".join(to_output))
                    else:
                        incompatibles += res_f[1]
    print('incompatibles : ', incompatibles)
    print('total :', total)


def check_corpus(corpus):
    mismatches = 0
    size = 0
    for c in os.listdir(corpus):
        size += 1
        doc = minidom.parse(open(os.path.join(corpus, c), 'rb'))
        if differences_cast_declaration(doc):
            mismatches += 1
    print("size : ", size, "mismatches : ", mismatches)


def create_outputs_structure(corpus):
    """Generates two outputs, one for acts, and one for complete plays"""
    output_scene = open(os.path.join(outputFolder, "Outputscenes") + corpus + ".txt", 'w+')
    output_acts = open(os.path.join(outputFolder, "Outputactes") + corpus + ".txt", 'w+')
    all_acts = []
    for c in os.listdir(corpus):
        play = minidom.parse(open(os.path.join(corpus, c), 'rb'))
        play_name = get_title(play)
        print(play_name)
        acts = get_acts(play)
        all_acts = all_acts + acts
        pl = []
        for a in acts:
            output_acts.write(play_name + " Acte " + str(acts.index(a) + 1) + " :" + str(a) + '\n')
            pl = pl + a
        fixed_play = fix_character_names(pl)
        output_scene.write(play_name + " : " + str(fixed_play) + '\n')
    return all_acts


def create_output_pathwidth(corpus):
    output_pathwidth = open(os.path.join(outputFolder, "Outputpathwidth") + corpus + ".txt", 'w+')
    for c in os.listdir(corpus):
        play = minidom.parse(open(os.path.join(corpus, c), 'rb'))
        play_name = get_title(play)
        print(play_name)
        scenes = get_scene(play)
        nb_cast = len(fixed_cast(scenes))
        bags, pw = pathwidth(scenes)
        output_pathwidth.write(play_name + " : " + "Cast size " + str(nb_cast) + ", Pathwidth : " + str(pw) + '\n')


def list_to_dict(l, characters, name):
    d = {name: l[characters.index(name)] for name in characters}
    d['VALEUR'] = name
    return d


def table_to_dict(l, characters, value):
    d = {name: name for name in characters}
    d['VALEUR'] = value
    dicts = [d]
    for c in l:
        dicts.append(list_to_dict(c, characters, characters[l.index(c)]))
    return dicts


def check_character_rule(c, genre):
    output_char_rule = open(os.path.join(outputFolder, "Output apparition persos " + genre) + corpus + ".txt", 'w+')
    nb_genre = 0
    nb_wrong = 0
    for d in c:
        if d['Genre'] == genre and d['Date'] != '' and 1700 >= int(d['Date']) >= 1600 and int(d['Nombre actes']) > 1:
            nb_genre += 1
            wrong = False
            for i in range(1, 5):
                check, s = parameterized_matching.check_character_apperance_rules(ast.literal_eval(d['Acte ' + str(i)]))
                wrong = wrong or check
                if check:
                    output_char_rule.write(" ".join([d['Nom'], "Acte ", str(i), str(s), '\n']))
            if wrong:
                nb_wrong += 1
    output_char_rule.write(f"{nb_wrong} {genre} brisent les règles sur {nb_genre}\n")


def test( siecle_1, siecle_2, corpus):
    compteur_siecle_1, compteur_siecle_2 = 0,0
    for piece in corpus:
        date = get_date(piece)
        for scene in piece:
            persos = get_characters_in_scene(scene)
            if all () : #vérifie si chacun des personnages est une femme
               if date >= siecle_1 and date<= siecle_1:
                   compteur_siecle_1 += 1
               if date >= siecle_2 and date <= siecle_2:
                   compteur_siecle_2 += 1
    return compteur_siecle_1, compteur_siecle_2


if __name__ == "__main__":
    # print("Loading")
    # docs = pickle.load(open(corpus_docs, 'rb'))
    # print('Done')
    # print (get_genre(docs['Mariamne']))
    marianne_play = get_fixed_parameterized_play(marianne_doc)
    print(marianne_play)

    # c_a = open(corpus_acts_merged,'rb')
    # plays = pickle.load(c_a)
    # for x in plays:
    #     if "Mariane" in x:
    #         print(x, plays[x])
    # with open(corpuscsv, newline='') as csvfile:
    #     d = csv.DictReader(csvfile, dialect='unix')
    #     check_character_rule(d,"Tragi-comédie")
    # generic_corpus_traversal_1(corpus, [parameterized_matching.check_character_apperance_rules], 'censor', True)
    # pp_corpus = get_corpus_parameterized_plays(corpus)
    # generic_corpus_traversal_2(corpus, [spm_hamming], 'SPM_Hamming_1', True)
    # create_csv_output(corpus, 'Dracord_parameterized_plays')
    # r = get_corpus_parameterized_acts(corpus)
    # print(r)
    # create_csv_output(corpus, "Dracor_parameterized_plays")
    # generic_corpus_traversal_1(corpus, [check_rule_1_play, check_rule_2_play, check_rule_4_play, check_rule_5_play ],'rules_douguet', True)

