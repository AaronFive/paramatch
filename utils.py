from xml.dom import minidom
import doctest

def invert_dic(d, v):
    """Given a dictionnary and a value v, returns the first key such that d[k] = v, or None if it doesn't exist
    >>> invert_dic({1:'a',2:'b'},'b')
    2
    >>> invert_dic({1:'a',2:'b'},2)

    >>> invert_dic({1:'a',2:'a', 3:'b'},'a')
    1
    """
    for x in d:
        if d[x] == v:
            return x
    return None


def get_title(doc):
    """Returns the title of a play"""
    title_nodes = doc.getElementsByTagName('title')
    if len(title_nodes) > 0:
        return title_nodes[0].firstChild.nodeValue


def get_stances_succession(s):
    """Given a play, returns the succession of speakers"""
    repliques = s.getElementsByTagName('sp')
    scene = [r.getAttribute("who") for r in repliques]
    return scene


def normalize_scene(scene, return_dict = False):
    """Given a list of characters, transforms it in a parameterized word of the form ABABC"""
    character_normalizing = dict()
    order = 65
    normalized_scene = []
    for x in scene:
        if x not in character_normalizing:
            character_normalizing[x] = chr(order)
            order += 1
        normalized_scene.append(character_normalizing[x])
    if return_dict:
        return "".join(normalized_scene), character_normalizing
    else:
        return "".join(normalized_scene)


def get_all_acts_dialogues(doc):
    """Returns the succession of characters talking, in all acts"""
    scene_list = doc.getElementsByTagName('div') + doc.getElementsByTagName('div1') + doc.getElementsByTagName('div2')
    scene_list = [s for s in scene_list if s.getAttribute("type") in ["act", "acte"]]
    return [get_stances_succession(s) for s in scene_list]