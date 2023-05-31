import time
import sys

import json

table = [[1, 2222, 30, 500], [4, 55, 6777, 1]]
for row in table:
    print('| {:1} | {:^4} | {:>5} | {:<3} |'.format(*row))
