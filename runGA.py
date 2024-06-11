# encoding: utf-8
import os
import random
import argparse

from algorithm.ga import GA

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
        os.system('mkdir '+LOG_DIR)


    make_params = {}
    pso_params = {}
    if args.execute_params:
        make_params['execute_params'] = args.execute_params
    make_params['src_path'] = args.src_path

    e = Executor(**make_params)
    tuning_list = e.opts

    print(len(tuning_list), tuning_list)

    GATuner = GA(tuning_list, e.get_objective_score)
    #重复实验次数
    begin2end = 1
    stats = []
    times = []
    for _ in range(begin2end):
        dep, ts = GATuner.GA_main()
        print('middle result')
        print(dep)
        stats.append(dep)
        times.append(ts)
    for j, v_tmp in enumerate(stats):
        max_s = 0
        for i, v in enumerate(v_tmp):
            max_s = max(max_s, v)
            v_tmp[i] = max_s
    print(times)
    print(stats)

    time_mean = []
    time_std = []
    stat_mean = []
    stat_std = []
    import numpy as np
    for i in range(10):
        time_tmp = []
        stat_tmp = []
        for j in range(begin2end):
            time_tmp.append(times[j][i])
            stat_tmp.append(stats[j][i])
        time_mean.append(np.mean(time_tmp))
        time_std.append(np.std(time_tmp))
        stat_mean.append(np.mean(stat_tmp))
        stat_std.append(np.std(stat_tmp))
    print(time_mean)
    print(time_std)
    print(stat_mean)
    print(stat_std)
