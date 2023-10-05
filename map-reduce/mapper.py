#!/usr/bin/env python3
import sys


def main():
    for line in sys.stdin:
        try:
            _, genre, _, status = line.split(',')
    
            status = status.rstrip()

            if status == '4':
                print('{}\t1'.format(genre))
        except:
            print('ошибка')
            continue


if __name__ == '__main__':
    main()
