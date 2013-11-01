#!/usr/bin/env python

from random import randint
import json
import sys

def random_key(d):
    """
    Select a random key based on weights of the values. Let s be the
    sum of all points. We will separate the range [1-s] in subranges
    each of which we will map to a key. We make a list of tuples: the
    first element of each tuple is a key and the next is the end of
    the range that represents that key. The beginning of that range is
    the previous key or 1 f it is the first. Then we get a random
    number and iterate over the tuples findig when we crossed r. We
    could do that with binary search and it would be much faster but
    it is clearer this way.
    """

    s = 0
    accend_kv = []
    for k,v in d.items():
        s += v
        accend_kv.append((k,s))

    try:
        r = randint(1,s)
    except ValueError:
        return d.keys()[0]

    for k,v in accend_kv:
        if r <= v:
            return k

# If you provide only prizes and
def prize_keys(prizes, players, remove=False):
    """
    Give out the prizes to the participants. The participants are the
    keys of dict players whose values are the points they have
    collected (eg. {'mary':10, 'george':20}). Prizes should be
    provided in descending order of value. The return value is a dict
    that maps participants to prizes.

    eg.
    play_round(['gold','silver'], {'mary':100, 'george':10, 'alfred':50}, removed=True)
    => ({'gold':'mary', 'silver':'alfred'}, {'george':10})
    """

    # Use tmp in order to not change the original player dict.
    tmp = players.copy()
    ret = {}

    for p in prizes:
        winner = random_key(tmp)
        if remove:
            del tmp[winner]
        else:
            tmp[winner] = 0

        ret[p] = winner

    return (ret, tmp)


# File IO

def read_config(fname):
    """
    Read the prizes, the candidates and their points, and wether we
    should remove the winners or just take all their points. The
    format of the json file is (see json format for allowed
    modifications, eg comment syntax):

    {
      'players': {'p1':10, 'p2':1000, p3:200},
      'prizes': ['p1', 'p2'],
      'remove_winners': false
    }
    """

    with open(fname) as fd:
        d = json.load(fd)

    players = d['players']
    prizes = d['prizes']
    remove_winners = d['remove_winners']

    return prizes, players, remove_winners

def write_config(fname, prizes, players, remove_winners):
    """
    Write the config to a file in a format readable by
    read_config. Note that json format allows some lieberties in
    format so the format output of this may deviate from the format of
    the examples. They are both correct.
    """

    with open(fname, 'w') as fd:
        json.dump({'players': players,
                   'prizes':prizes,
                   'remove_winners':remove_winners}, fd)

if __name__ == '__main__':
    HELP_MESSAGE = "run like this: python ./randpoints.py infile.json [outfile.json]"

    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        sys.stdout.write(HELP_MESSAGE)
        exit(0)

    prizes, players, remove = read_config(sys.argv[1])
    winners, new_players = prize_keys(prizes, players, remove)

    for p in prizes :
        sys.stdout.write("Prize %s goes to %s\n" % (p, winners[p]))

    # You may want to run the same or very similar thing again so I
    # dump the new player point configuration with the rest of the
    # information the same. Also the user may have not provided a file
    # so forgive that and exit gracefully
    try:
        write_config(sys.argv[2], prizes, new_players, remove)
    except IndexError:
        pass