from xml.dom import minidom


def get_title(doc):
    """Returns the title of a play"""
    title_nodes = doc.getElementsByTagName('title')
    if len(title_nodes) > 0:
        return title_nodes[0].firstChild.nodeValue


def get_stances_succession(s):
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
