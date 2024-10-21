"""
Turn:

.. code:: ipython3

    do some python

.. code:: literal

    result

Into:

.. parsed-literal:: 

    >>> do some python
    result
"""

import sys


def reformat_file(filename: str, ofile: str = None):
    """
    Reformat a generated file to use as documentation with testing
    """

    with open(filename) as f:
        lines = [r.replace('\n','') for r in f.readlines()]

    rst = []
    in_code_block = False
    python = False
    literal = False
    for x, l in enumerate(lines):

        if not bool(l):
            if not in_code_block:
                rst.append(l)
            continue
        elif '.. code::' in l or '.. parsed-literal::' in l:
            if not in_code_block or literal:
                if literal:
                    rst.append('')
                l = '.. code::'
                in_code_block = True
                python = True
                literal = False
                rst.append(l)
                rst.append('')
            else:
                literal = True
                python = False
        elif not l.startswith(' '):
            if in_code_block:
                in_code_block = False
                rst.append('')
            rst.append(l)
        else:
            if python:
                rst.append(f'   >>> {l[4:]}')
            else:
                rst.append(l[1:])

    if ofile is None:
        ofile = filename

    with open(ofile, 'w') as f:
        f.write('\n'.join(rst))

    print(f'Written to output file: {ofile}')

if __name__ == '__main__':
    reformat_file(sys.argv[-1])
