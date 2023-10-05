#!/usr/bin/env python3

import sys


def main():
    genre = ''
    count = 0
    for line in sys.stdin:
        try:
            g, c = line.split('\t')
            c = int(c)
        except:
            continue

        if not genre:
            genre = g
            count = 1
        elif genre == g:
            count += c
        else:
            print('{}\t{}'.format(genre, count))
            genre = g
            count = 1

    if genre:
        print('{}\t{}'.format(genre, count))


if __name__ == '__main__':
    main()
