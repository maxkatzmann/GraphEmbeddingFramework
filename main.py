import sys
import os

def main(argv):
    """
    Expects 2 args:
    1- Data type of the input data -> -edl: Edge List
    2- Relative or real path name of the input data
    """

    if len(argv) != 2:
        raise ValueError(print(main.__doc__))

    path_name = os.path.realpath(argv[1])

    if argv[0] == '-edl':
        print()


if __name__ == "__main__":
    main(sys.argv[1:])