#!/usr/bin/env python

from random import randint
try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest

import json
import sys

# A trick for `input' to work for python 2 correctly, don bother too
# much with this.
try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass


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

    # The sum of points.
    s = 0
    accend_kv = []

    for k,v in d.items():
        # Sum of points so far
        s += v
        # Keep a mapping of each key and the sum of points when we
        # encountered it
        accend_kv.append((k,s))


    # If no player has points randint will be unable to provide us
    # with a random number so just return the first key.
    try:
        r = randint(1,s)
    except ValueError:
        return d.keys()[randint(0,len(keys)-1)]

    # Return the key which is mapped to the range in which r falls.
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
    # Map the prizes to the winners in ret dictionary
    ret = {}

    for p in prizes:
        # For each prize get a (biased) random winner
        winner = random_key(tmp)

        # and remove him or diminish his points depending on
        # configuration
        if remove:
            del tmp[winner]
        else:
            tmp[winner] = 0

        # also map him to his prize
        ret[p] = winner

    # return a tuple of the prizes and the new point distribution
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

    with open(fname) as fd:     # Open fname for reading
        d = json.load(fd)       # Read the contents using the json
                                # formatter


    # Read and return the result as a tuple.
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

    with open(fname, 'w') as fd: # Open file fname for writing

        # Write the dictionary
        # {'players': <players>,
        # 'prizes':<prizes>,
        # 'remove_winners:<wether to remove winners>}
        # in the open file as text using the json formatter.
        json.dump({'players': players,
                   'prizes':prizes,
                   'remove_winners':remove_winners}, fd)


def arguments():
    HELP_MESSAGE = "run like this: python ./randpoints.py infile.json [outfile.json]"

    # If inputs are too few just ask them interactively.
    if len(sys.argv) < 2:
        conf = ""
        while not conf:
            conf = str(input("Provide input configuration file: "))

            try:
                with open(conf) as fd:
                    pass
            except IOError:
                sys.stderr.write("No such file '%s'" % conf)
                conf = ""

        out = str(input("Provide output config file (blank for no output file): "))
        res = str(input("Provide a file to write the result (blank for no output file): "))

    else:
        conf,out,res = [v for k,v in zip_longest(range(3), sys.argv[1:])]

        # if the user asks for help show her help.
        if sys.argv[1] == '--help':
            sys.stdout.write(HELP_MESSAGE)
            exit(0)

    return conf,out,res


def main():
    """
    This is the main function.
    """
    conf, out, res = arguments()

    # Just read the configuration
    prizes, players, remove = read_config(conf)
    # Get the mapping of prizes to players and the new point
    # distribution.
    winners, new_players = prize_keys(prizes, players, remove)

    # For each prize show the corresponding winner
    for p in prizes :
        sys.stdout.write("Prize %s goes to %s\n" % (p, winners[p]))

    # You may want to run the same or very similar thing again so I
    # dump the new player point configuration with the rest of the
    # information the same. Also the user may have not provided a file
    # so forgive that and exit gracefully
    try:
        write_config(out, prizes, new_players, remove)
    except IndexError:
        pass

    try:

        s = sum([v for k,v in players.items()])

        with  open(res) as fd:
            for p in prizes:
                fd.write("%s -> %s (p: %d/%d)", p, winners[p], players[winners[p]], s)
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    main()
