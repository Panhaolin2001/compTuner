import argparse
import os, sys
import time
import random
import numpy as np
from hyperopt import fmin, tpe, hp, space_eval, rand, Trials, partial, STATUS_OK
random.seed(123)
iters = 1800
begin2end = 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Args needed for BOCA tuning compiler.")
    parser.add_argument('-o', '--output',
                        help='Write output to <file>.',
                        default='a.out', metavar='<file>')
    parser.add_argument('-p', '--execute-params',
                        help='Pass comma-separated <options> on to the executable file.',
                        nargs='+', metavar='<options>')
    parser.add_argument('-src', '--src-path',
                        help='Specify path to the source file.',
                        required=True, metavar='<directory>')
    args = parser.parse_args()

    from algorithm.executor import Executor, LOG_DIR

    if not os.path.exists(LOG_DIR):
        os.system('mkdir ' + LOG_DIR)

    make_params = {}
    if args.execute_params:
        make_params['execute_params'] = args.execute_params
    make_params['src_path'] = args.src_path

    e = Executor(**make_params)
    space = {}
    stats = []
    times = []
    for option in e.opts:
        space[option] = hp.choice(option, [0, 1])

    random.seed(123)
    algo = partial(tpe.suggest, n_startup_jobs=1)
    for i in range(begin2end):
        ts = []
        b = time.time()
        best = fmin(e.get_objective_score, space, algo=algo, max_evals=iters)
        print(e.get_objective_score(best))
        stats.append(e.get_objective_score(best))
        times.append(ts)
        # print(best)

    vals = []
    for j, v_tmp in enumerate(stats):
        max_s = 0
        for i, v in enumerate(v_tmp):
            max_s = min(max_s, v)
            v_tmp[i] = max_s
    # print(times)
    print(stats)

    # for i in range(iters):
    #     tmp = []
    #     for j in range(begin2end):
    #         tmp.append(times[j][i])
    #     vals.append(-np.mean(tmp))

    # print(vals) 

    # vals = []
    # for i in range(iters):
    #     tmp = []
    #     for j in range(begin2end):
    #         tmp.append(stats[j][i])
    #     vals.append(-np.mean(tmp))

    # print(vals)

    # vals = []
    # for i in range(iters):
    #     tmp = []
    #     for j in range(begin2end):
    #         tmp.append(stats[j][i])
    #     vals.append(-np.std(tmp))

    # print(vals)
