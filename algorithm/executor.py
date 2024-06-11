# encoding:utf-8
import sys, os, time, re
import numpy as np
import tempfile,subprocess,shlex

LOG_DIR = 'log' + os.sep
LOG_FILE = LOG_DIR + 'record.log'
COM_FILE = LOG_DIR + 'compare.log'
BOCA_FILE = LOG_DIR + 'boca.log'
PSO_FILE = LOG_DIR + 'pos.log'
RAN_FILE = LOG_DIR + 'random.log'
ERROR_FILE = LOG_DIR + 'err.log'
options_rec_file = lambda compiler: LOG_DIR + os.path.basename(os.path.normpath(compiler)) + '_options.txt'
execute_time_bounds = [0.1, 30]

llvm_tools_path = "/home/haolin/project/build-release-10.0.0/bin"  # 替换为你的实际路径

def get_instrcount(ll_code, *opt_flags, llvm_tools_path=None):
    if llvm_tools_path is None:
        raise ValueError("llvm_tools_path must be provided")

    try:
        # Create temporary files for LLVM IR code, optimized IR code, and object file
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as ll_file, \
             tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as opt_file, \
             tempfile.NamedTemporaryFile(suffix=".o", delete=False) as obj_file:
            
            # Write original LLVM IR code to temporary file
            ll_file.write(ll_code.encode())
            ll_file.flush()
            
            if len(opt_flags) == 1 and isinstance(opt_flags[0], str) and opt_flags[0].strip() == "":
                # No optimization flags provided, skip the opt step
                optimized_ll_code = ll_code
            else:
                # Prepare optimization flags
                opt_flags_list = opt_flags
                if len(opt_flags) == 1 and isinstance(opt_flags[0], str):
                    opt_flags_list = opt_flags[0].split()
                
                # Construct opt command
                opt_path = os.path.join(llvm_tools_path, "opt")
                flat_opt_options = [str(item) for sublist in opt_flags_list for item in (sublist if isinstance(sublist, list) else [sublist])]
                cmd_opt = [opt_path] + flat_opt_options + ["-S", ll_file.name, "-o", opt_file.name]

                # Run opt to optimize LLVM IR
                subprocess.run(cmd_opt, check=True)
                
                # Read optimized LLVM IR code from temporary file
                with open(opt_file.name, "r") as f:
                    optimized_ll_code = f.read()

            # Write optimized LLVM IR code to the temporary file (if not already done)
            with open(opt_file.name, "w") as f:
                f.write(optimized_ll_code)
                f.flush()

            # Construct clang command to compile LLVM IR to object file
            clang_path = os.path.join(llvm_tools_path, "clang")
            obj_file_path = obj_file.name
            cmd_clang = [clang_path, "-o", obj_file_path, "-c", "-Wno-override-module", opt_file.name]

            # Run clang to compile LLVM IR to object file
            subprocess.run(cmd_clang, check=True)

            # Construct llvm-size command to get the size of the object file
            llvm_size_path = os.path.join(llvm_tools_path, "llvm-size")
            cmd_size = [llvm_size_path, obj_file_path]

            # Run llvm-size and capture the output
            result = subprocess.run(cmd_size, stdout=subprocess.PIPE, check=True)
            output = result.stdout.decode()

        # Clean up temporary files
        os.remove(ll_file.name)
        os.remove(opt_file.name)
        os.remove(obj_file_path)

        # Extract the text size from llvm-size output
        for line in output.splitlines():
            if line.strip().endswith(os.path.basename(obj_file_path)):
                text_size = int(line.split()[0])
                return text_size

        # If we reach this point, something went wrong
        raise RuntimeError("Failed to extract text size from llvm-size output")
    
    except subprocess.CalledProcessError:
        # If any of the subprocess commands fail, return infinity
        return float(999999999)
    except Exception:
        # Clean up temporary files if an unexpected error occurs
        try:
            if os.path.exists(ll_file.name):
                os.remove(ll_file.name)
            if os.path.exists(opt_file.name):
                os.remove(opt_file.name)
            if os.path.exists(obj_file_path):
                os.remove(obj_file_path)
        except:
            pass
        return float(999999999)


def write_log(ss, file):
    log = open(file, 'a')
    log.write(ss + '\n')
    log.flush()
    log.close()


class Executor:
    def __init__(self, execute_params=[], src_path='.'):
        # self.bin_path = bin_path +os.sep
        # self.driver = bin_path + os.sep + driver
        # self.linker = bin_path + os.sep + linker
        self.src_path = src_path
        self.LOG_FILE = LOG_DIR + 'record' + os.path.splitext(os.path.basename(self.src_path))[0] + '.log'
        # self.obj_dir = obj_dir

        # assert os.path.exists(self.bin_path)
        # assert os.path.exists(self.driver)
        # assert os.path.exists(self.linker)
        # assert os.path.exists(self.src_path)

        # if not os.path.exists(self.obj_dir):
        #     os.makedirs(self.obj_dir)
        # self.libs = libs
        # self.LD_OPTS = '-o ' + output
        # self.output = output
        # self.execute_params = execute_params
        self.__genopts__()

    def __genopts__(self):
        self.opts = [
            "-add-discriminators",
            "-adce",
            "-aggressive-instcombine",
            "-alignment-from-assumptions",
            "-always-inline",
            "-argpromotion",
            "-attributor",
            "-barrier",
            "-bdce",
            "-break-crit-edges",
            "-simplifycfg",
            "-callsite-splitting",
            "-called-value-propagation",
            "-canonicalize-aliases",
            "-consthoist",
            "-constmerge",
            "-constprop",
            "-coro-cleanup",
            "-coro-early",
            "-coro-elide",
            "-coro-split",
            "-correlated-propagation",
            "-cross-dso-cfi",
            "-deadargelim",
            "-dce",
            "-die",
            "-dse",
            "-reg2mem",
            "-div-rem-pairs",
            "-early-cse-memssa",
            "-early-cse",
            "-elim-avail-extern",
            "-ee-instrument",
            "-flattencfg",
            "-float2int",
            "-forceattrs",
            "-inline",
            "-insert-gcov-profiling",
            "-gvn-hoist",
            # "-gvn",
            "-globaldce",
            "-globalopt",
            "-globalsplit",
            "-hotcoldsplit",
            "-ipconstprop",
            "-ipsccp",
            "-indvars",
            "-irce",
            "-infer-address-spaces",
            "-inferattrs",
            "-inject-tli-mappings",
            "-instsimplify",
            "-instcombine",
            "-instnamer",
            "-jump-threading",
            "-lcssa",
            "-licm",
            "-libcalls-shrinkwrap",
            "-load-store-vectorizer",
            "-loop-data-prefetch",
            "-loop-deletion",
            "-loop-distribute",
            "-loop-fusion",
            "-loop-idiom",
            "-loop-instsimplify",
            "-loop-interchange",
            "-loop-load-elim",
            "-loop-predication",
            "-loop-reroll",
            "-loop-rotate",
            "-loop-simplifycfg",
            "-loop-simplify",
            "-loop-sink",
            "-loop-unroll-and-jam",
            "-loop-unroll",
            "-loop-unswitch",
            "-loop-vectorize",
            "-loop-versioning-licm",
            # "-loop-versioning",
            "-loweratomic",
            "-lower-constant-intrinsics",
            "-lower-expect",
            "-lower-guard-intrinsic",
            "-lowerinvoke",
            "-lower-matrix-intrinsics",
            "-lowerswitch",
            "-lower-widenable-condition",
            "-memcpyopt",
            "-mergefunc",
            "-mergeicmps",
            "-mldst-motion",
            "-sancov",
            "-name-anon-globals",
            "-nary-reassociate",
            "-newgvn",
            "-pgo-memop-opt",
            "-partial-inliner",
            "-partially-inline-libcalls",
            "-post-inline-ee-instrument",
            "-functionattrs",
            "-mem2reg",
            "-prune-eh",
            "-reassociate",
            "-redundant-dbg-inst-elim",
            "-rpo-functionattrs",
            "-rewrite-statepoints-for-gc",
            "-sccp",
            "-slp-vectorizer",
            "-sroa",
            "-scalarizer",
            "-separate-const-offset-from-gep",
            "-simple-loop-unswitch",
            "-sink",
            "-speculative-execution",
            "-slsr",
            "-strip-dead-prototypes",
            "-strip-debug-declare",
            "-strip-nondebug",
            "-strip",
            "-tailcallelim",
            "-mergereturn"
        ]

        for opt in self.opts:
            write_log(opt, options_rec_file("llvm_opt"))

    def __genoptseq__(self, independent):
        """
        :param independent: 01 list of options
        :return: corresponding options sequence
        """
        # print(len(independent), independent)
        # print(len(self.opts), self.opts)
        if independent.__class__ == dict:
            independent = list(independent.values())
        opt_seq = []
        for k, s in enumerate(independent):
            if s == 1:
                opt_seq.append(self.opts[k])
        return opt_seq

    def get_objective_score(self, independent, k_iter=10086):
        """
        Get current optimization sequence speedup over -O3

        :param independent: 0-1 list, 0 for disable opt_k, 1 for enable opt_k
        :return: median speedup over -O3
        """
        independent = self.__genoptseq__(independent)

        with open(self.src_path, "r") as f:
            ll_code = f.read()

        score = get_instrcount(ll_code, " ".join([act for act in independent]), llvm_tools_path=llvm_tools_path)

        op_str = "iteration:{} speedup:{}".format(str(k_iter), str(score))
        write_log(op_str, self.LOG_FILE)
        return score


if __name__ == '__main__':

    automotive_bitcount_HOME = '/boca-test/benchmarks/cbench/automotive_bitcount'
    params_cbench = {
        'ZCC': ['gcc-4.5', 'clang-3.8'][1],
        'LDCC': ['gcc-4.5', 'clang-3.8'][1],
        'execute_params': '2000',
        'dir': automotive_bitcount_HOME
    }

    poly_HOME = '/boca-test/benchmarks/polybench/medley/nussinov'
    params_poly = {
        'ZCC': ['gcc-4.5', 'clang-3.8'][1],
        'LDCC': ['gcc-4.5', 'clang-3.8'][1],
        'CCC_OPTS': '-I /boca-test/benchmarks/polybench/utilities /boca-test/benchmarks/polybench/utilities/polybench.c',
        'dir': poly_HOME
    }

    e = Executor(**params_cbench)

    exe_cmd = 'time ./a.out 20000'
    # exe_cmd = 'time ./a.out'
    rec_file = 'compilationApproach.txt'
    o0o3 = []
    o0o1 = []
    o3o3 = []
    o3o1 = []
    for _ in range(1):
        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O0', opt_opts='-O3', )
        b1 = time.time()
        os.system(exe_cmd)
        ed1 = time.time()
        o0o3.append(ed1 - b1)

        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O0', opt_opts='-O1')
        b2 = time.time()
        os.system(exe_cmd)
        ed2 = time.time()
        o0o1.append(ed2 - b2)

        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O3', opt_opts='-O3')
        b3 = time.time()
        os.system(exe_cmd)
        ed3 = time.time()
        o3o3.append(ed3 - b3)

        e.__clean__()
        e.__compilellvmorig__(driver_opts='-O3', opt_opts='-O1')
        b2 = time.time()
        os.system(exe_cmd)
        ed2 = time.time()
        o3o1.append(ed2 - b2)

    write_log('O0-O3 average: ' + str(np.mean(o0o3)), rec_file)
    write_log('O0-O1 average: ' + str(np.mean(o0o1)), rec_file)
    write_log('O3-O3 average: ' + str(np.mean(o3o3)), rec_file)
    write_log('O3-O1 average: ' + str(np.mean(o3o1)), rec_file)
