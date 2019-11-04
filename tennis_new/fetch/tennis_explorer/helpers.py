import re


def regex_strip_string(string):
    string = re.sub('\n', '', string).strip()
    string = re.sub('\r', '', string).strip()
    string = re.sub('\t', '', string).strip()
    return string


def _text(elem):
    t = elem.text
    if t:
        return regex_strip_string(t)
    else:
        return None


def _tail(elem):
    t = elem.tail
    if t:
        return regex_strip_string(t)
    else:
        return None


EXPECTED_HEADER_CLASSES = [
    't-name',
    'score',
    'score',
    'score',
    'score',
    'score',
    'score',
    'course',
    'course',
    'icons',
    'icons'
]


def get_tourney_name_type(span_children):
    assert len(span_children) == 2
    tourney_name = span_children[1].tail
    tourney_type = span_children[1].attrib['class']
    return tourney_name, tourney_type


def parse_head_flags(tr):
    # TODO: Parse headers?
    children = tr.getchildren()
    assert all([child.tag == 'td' for child in children])
    classes = [child.attrib['class'] for child in children]
    assert classes == EXPECTED_HEADER_CLASSES
    tourney_name = children[0]
    maybe_link = tourney_name.getchildren()
    tourney_link = None
    if len(maybe_link) == 1:
        assert maybe_link[0].tag == 'a'
        tourney_link = maybe_link[0].attrib['href']
        tourney_name, tourney_type = get_tourney_name_type(maybe_link[0].getchildren())
    else:
        tourney_name, tourney_type = get_tourney_name_type(maybe_link)
    return {
        'tourney_name': tourney_name,
        'tourney_type': tourney_type,
        'tourney_link': tourney_link
    }


def _parse_time(time_elem):
    assert time_elem.attrib['class'] == "first time"
    return _text(time_elem)


def _parse_player(player_elem):
    assert player_elem.attrib['class'] == 't-name'
    _ch = player_elem.getchildren()
    assert len(_ch) <= 1
    if len(_ch) == 1:
        link = _ch[0]
        assert link.tag == 'a'
        player_link = link.attrib['href']
        player_name = _text(link)
        player_maybe_seed = _tail(link)
    else:
        player_name = _text(player_elem)
        player_link = None
        player_maybe_seed = _tail(player_elem)
    return player_link, player_name, player_maybe_seed


def _parse_set_result(set_elem):
    elem_class = set_elem.attrib['class']
    if elem_class == 'result':
        return _text(set_elem)
    elif elem_class == 'nbr':
        return None
    else:
        raise ValueError("Unexpected class %s" % elem_class)


def _parse_set_score(score_elem):
    elem_class = score_elem.attrib['class']
    if elem_class == 'score':
        return _text(score_elem)
    elif elem_class == 'score nbr':
        return None
    else:
        raise ValueError("Unexpected class %s" % elem_class)
    return _text(score_elem)


def _parse_home_odds(odds_elem):
    assert odds_elem.attrib['class'] == 'coursew'
    return _text(odds_elem)


def _parse_away_odds(odds_elem):
    assert odds_elem.attrib['class'] == 'course'
    return _text(odds_elem)


def _parse_match_link(match_link_elem):
    ch = match_link_elem.getchildren()
    assert len(ch) == 1
    assert ch[0].tag == 'a'
    match_link = ch[0].attrib['href']
    assert _text(ch[0]) == 'info'
    return {
        'match_link': match_link
    }

def parse_bott_row(tr):
    ret = {}
    ch = tr.getchildren()
    match_time = _parse_time(ch[0])
    ret.update({'match_time': match_time})
    player_link, player_name, player_maybe_seed = _parse_player(ch[1])
    ret.update({
        'p1_link': player_link,
        'p1_name': player_name,
        'p1_seed': player_maybe_seed
    })
    ret.update({
        'p1_sets_won': _parse_set_result(ch[2])
    })
    for set_idx, entry in enumerate(ch[3:8]):
        ret.update({'p1_set%d' % (set_idx + 1): _parse_set_score(entry)})
    ret.update({'p1_odds': _parse_home_odds(ch[8])})
    ret.update({'p2_odds': _parse_away_odds(ch[9])})
    ret.update(_parse_match_link(ch[11]))
    if ret['p1_sets_won'] is None:
        ret['comment'] = 'MATCH_NOT_PLAYED'
    return ret


def parse_nonbott_row(tr, player_idx=2):
    ret = {}
    ch = tr.getchildren()
    player_link, player_name, player_maybe_seed = _parse_player(ch[0])
    ret.update({
        'p2_link': player_link,
        'p2_name': player_name,
        'p2_seed': player_maybe_seed
    })
    ret.update({'p2_sets_won': _parse_set_result(ch[1])})
    for set_idx, entry in enumerate(ch[2:7]):
        ret.update({'p2_set%d' % (set_idx + 1): _parse_set_score(entry)})
    if ret['p2_sets_won'] is None:
        ret['comment'] = 'MATCH_NOT_PLAYED'
    return ret


def check_no_results(tr):
    # Checks if the first row in the table says 'No Results Available for this day...'
    ch = tr.getchildren()
    if len(ch) == 1:
        return _text(ch[0]) == 'No results for this day yet.'
    else:
        return False
