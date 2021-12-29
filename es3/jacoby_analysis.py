import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

core_vs_socket_plot = not False
across = True

path = "thin"
latency_thin = {"core": 0.30,# 0.2042,
                "socket": 0.50, #0.4120,
                "node": 1.0076,
                }

bw_thin = {"core": 6446,
           "socket": 5660,
           "node": 12169,
           }
latency_gpu = {"core": 0.2246,
               "socket": 0.4338,
               "node": 1.3828,
               }

bw_gpu = {"core": 6367.994729,
          "socket": 5579.555083,
          "node": 12164.955625,
          }

latency = latency_thin
bw = bw_thin

L = 600
mega = 1048576


def get_info_time(filename):
    keys = ("N", "n1", "n2", "n3")
    n1, n2, n3 = tuple(map(int, filename[:-4].split("_")))
    N = n1 * n2 * n3
    return dict(zip(keys, (N, n1, n2, n3)))


def get_metadata(filename):
    if filename[:4] == "time":
        return get_info_time(filename[5:])
    return get_info_time(filename)


def get_file_list(dir=path):
    file_names = [f for f in os.listdir(dir) if f[-4:] == ".out"]
    time_files = [f for f in file_names if f[:4] == "time"]
    out_files = [f for f in file_names if f[:4] != "time"]
    return time_files, out_files


def get_mapping_from_cmd(cmd):
    return cmd.split()[5]


def parse_time_file(filename, path=path):
    full_name = os.path.join(path, filename)
    with open(full_name, 'r') as file:
        lines = file.readlines()
    runs = []
    for line in lines:
        if line == "\n":
            continue
        # time, mapping = float(line[7:13]), float()
        splitted = line.split(", ")
        run = {k[:-1]: v for k, v in zip(splitted[0::2], splitted[1::2])}
        run["mapping"] = get_mapping_from_cmd(run["CMD"])
        runs.append(run)

    return runs


def make_observations(f, path=path):
    metadata = get_metadata(f)
    runs = parse_time_file(f, path=path)
    return [run | metadata for run in runs]


def make_time_df(time_files, dir=path):
    df = pd.DataFrame([obs for f in time_files for obs in make_observations(f, dir)])
    df["time"] = df["elapsed"].map(float)
    return df


def make_performance_plot(df, query=None, ax=plt, title=None):
    if query is None:
        dummy_true = np.repeat(True, len(df))
        query = "@dummy_true"

    df = df.query(query)
    ax.scatter(np.arange(len(df)), df.real_performance, label="Measured Performance")
    ax.scatter(np.arange(len(df)), df.P, label="Theoretical Performance")
    # ax.set_xlabel("Different runs with different topologies")
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_ylabel("Performance [MLUP/s]")

    ax.legend()
    if title:
        ax.set_title(title)


def evaluate_performance(df):
    serial_time = df.query("N == 1").time.min()

    df["k"] = df[["n1", "n2", "n3"]].apply(lambda x: 3 - np.sum(x == 1), axis=1)
    df["C"] = df["k"] * 2 * 2 * 8 * L * L / mega
    L_cubo = L * L * L
    P = lambda x: L_cubo * x["N"] / (
            serial_time + x["C"] / bw[x["mapping"]] + latency[x["mapping"]] * x["k"] / mega)
    df["P"] = df.apply(P, axis=1) / mega

    P0 = df.query("N == 1").P.values[0]
    df["P1 * N / P(N)"] = df["N"] * P0 / df["P"]
    # df["Efficiency"] = df["time"] / serial_time
    df["real_performance"] = L_cubo * df["N"] / (df["time"] * mega)
    return df


def get_extended_dataset(path):
    time_files, _ = get_file_list(path)

    df = make_time_df(time_files, dir=path)
    df.sort_values("user", inplace=True)
    df.sort_values("N",
                   ascending=False,
                   ignore_index=True,
                   inplace=True
                   )

    df = evaluate_performance(df)
    return df


if __name__ == "__main__":
    if core_vs_socket_plot:
        df = get_extended_dataset("thin")
        (_, socket), (_, core) = df.groupby("mapping")
        fig, axs = plt.subplots(1, 2)
        make_performance_plot(core, title="By Core binding", ax=axs[0])
        make_performance_plot(socket, title="By Socket binding", ax=axs[1])

    if across:
        thin_ac = get_extended_dataset("thin_ac")
        gpu = get_extended_dataset("gpu")
        fig, axs = plt.subplots(1, 2)
        make_performance_plot(thin_ac, title="Thin", ax=axs[0])
        latency = latency_gpu
        bw = bw_gpu
        make_performance_plot(gpu, title="GPU", ax=axs[1])

    print()

    plt.show()
    print()
