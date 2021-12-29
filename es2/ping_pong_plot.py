import matplotlib.pyplot as plt
import os
import numpy as np
import scipy.optimize as optimization
import pandas as pd
from dati_schiantati import *
from control_parameter import *

c = 0


def get_values(filename, all=False):
    with open(filename, 'r') as file:
        lines = file.readlines()

    values = [[float(i) for i in l[:-2].split(",") if i != ""] for l in lines if l[0] != "#"]
    if all:
        values = [[size, rep, time, bw] for size, rep, time, bw in values]
        return np.array(values)

    values = [[size, time] for size, _, time, _ in values]
    return np.array(values)


def fit(values):
    xdata = values.T[0]
    ydata = values.T[1]

    # Fitting lamtency
    sel_idx = xdata < 16
    sel_x = xdata[sel_idx]
    sel_y = ydata[sel_idx]
    l = np.mean(sel_y)

    def func(x, bw):
        return l + x / bw

    x0 = [12000]
    bw, (cov) = optimization.curve_fit(func, xdata, ydata, x0, bounds=(0, np.inf))
    # slope, intercept, r, p, se = ss.linregress(xdata, ydata)
    return l, bw[0]

    # fitting lambda


def plot(f, ax=plt, c=0):
    values = get_values(f)
    l, bw = fit(values)
    xdata, ydata = values.T[0], values.T[1]
    plt.scatter(xdata, ydata, label=f, c=colors[c])
    xx = np.logspace(-9, 0, 1000, endpoint=True) * 3e8
    ax.plot(xx, l + xx / bw, c=colors[c])
    ax.xscale("log")
    ax.yscale("log")


def get_label(df, complete=True):
    if complete is True:
        return df.map + " | " + df.pml + " " + df.btl + " | " + [c[0] for c in df.compiler]
    return df.index


def add_values(df, key, ax, scale=1.0, unit=""):
    for i, v in enumerate(df[key]):
        ax.text(scale * v, i, f" {scale * v:.2f} " + unit, color='blue', va='center',
                fontweight='bold')


def build_barplot(df, key, title=None, scale=1.0, ax=None, label_list=None):
    if ax is None:
        fig, ax = plt.subplots()

    ascending = True
    if key == "bw":
        ascending = False
    df.sort_values(key, inplace=True, ascending=ascending)

    if label_list is None:
        label_list = [labels[i] for i in df.index]

    ax.barh(label_list, scale * df[key], align='center')
    ax.invert_yaxis()  # labels read top-to-bottom
    if title is not None:
        ax.set_title(title, fontsize=20)

    add_values(df, key, ax, scale, unit=units[key])

    plt.subplots_adjust(top=0.9,
                        bottom=0.08,
                        left=0.1,
                        right=0.96,
                        hspace=0.17,
                        wspace=0.0)
    plt.yticks(fontsize=10)
    plt.xticks(fontsize=10)


def get_param(file_list, query=None):
    df = pd.DataFrame(info).T
    df.columns = metadata_key

    latencies = []
    bws = []

    if query is None:
        studied = file_list
    else:
        studied = df.query(query)

    for f in studied:
        color = c
        f = os.path.join(path, f)
        l, bw = fit(np.array(get_values(f)))
        latencies.append(l)
        bws.append(bw)
        if plot_time_fit:
            plot(f, c=color)
            color = (color + 1) % len(colors)

    df["bw"] = pd.Series(bws, index=studied)
    df["lambda"] = pd.Series(latencies, index=studied)
    return df


def df_filter(df, file_list_to_ignore):
    for f in file_list_to_ignore:
        df = df[df.index != f]

    return df


def get_full_df(file_names, all=False):
    if all:
        cols = ('size', 'time', 'map', 'pml', 'btl', 'compiler', "rep", "bw")
    else:
        cols = ('size', 'time', 'map', 'pml', 'btl', 'compiler')
    full_df = pd.DataFrame(columns=cols)

    for file in file_names:
        metadata = info[file]
        f = os.path.join(path, file)
        if all:
            values = get_values(f, all=all)
            df = pd.DataFrame(values)
            df.columns = ["size", "rep", "time", "bw"]

        else:
            size_and_time = get_values(f)
            df = pd.DataFrame(size_and_time)
            df.columns = ["size", "time"]
        for k, v in zip(metadata_key, metadata):
            df[k] = v

        full_df = full_df.merge(df, 'outer')

    return full_df


def get_mean_df(file_names):
    df = get_full_df(file_names, all=True)
    sizes = sorted(set(df["size"]))
    v = []
    for f in file_names:
        mapby, pml, btl, comp = info[f]
        # if mapby == "core" and pml == 'ob1' and btl == "tcp":
        # print()
        f_query = "map == @mapby and btl == @btl and pml == @pml and compiler == @comp"
        latency = param_df.query(f_query)["lambda"].values[0]
        bw = param_df.query(f_query)["bw"].values[0]

        sel = df.query(f_query)
        for size in sizes:
            queried = sel.query("size == @size")
            if queried.size == 0:
                continue
            mean_time = queried.time.mean()
            mean_bw = queried.bw.mean()
            rep = int(queried.rep.mean())
            try:
                computed_time = latency + size / bw
            except ZeroDivisionError:
                computed_time = latency

            computed_bw = size / computed_time
            v.append([mean_time, size, computed_time, computed_bw, mean_bw, rep, *info[f], f])

    df = pd.DataFrame(v)
    df.columns = ["time", "size", "comp_time", "comp_bw", "bw", "rep", *metadata_key, "file"]
    return df


def produce_csv(df):
    """
    #header_line 1: command line used
    #header_line 2: list of nodes involved
    #header_line 3: lamba, bandwith computed by fitting data
    """

    grouped = df.groupby("file")
    header_prefix = "#header_line "
    for key, group in grouped:
        CMD = commands[key]
        out_filename = os.path.join(out_path, key[:-3] + "csv").replace("self", "")
        Bandwidth, Latency = param_df[["bw", "lambda"]].query("index == @key").values[0]

        line1 = header_prefix + "1: " + CMD
        line2 = header_prefix + "2: " + "ct1pt-tnode007.hpc"
        line3 = header_prefix + f"3: {Latency=:.4f} {Bandwidth=:.4f}"

        legend_header = header_prefix + ":#bytes, #repetitions,t[usec],Mbytes/sec,t[usec](computed),Mbytes/sec(computed)"

        if key[0] == "n":
            line2 = line2 + "ct1pt-tnode010.hpc"

        with open(out_filename, "w") as f:
            f.write(line1 + "\n")
            f.write(line2 + "\n")
            f.write(line3 + "\n")
            f.write(legend_header + "\n")

        group = group[["size", "rep", "time", "bw", "comp_time", "comp_bw"]]
        group.to_csv(out_filename, index=False, header=False, mode="a", float_format='%.3f')

        pass


def produce_plot(df):
    grouped = df.groupby("file")

    for key, group in grouped:
        fig, ax = plt.subplots(1, 1)
        group.plot(x="size", y="bw", label="Bandwidth", ax=ax)
        # group.plot(x="size", y="comp_bw", label="Computed Bandwith", ax=ax)
        ax.set_xscale("log")
        title = key[:-3].replace("self", "")
        ax.set_title(title)
        plt.savefig(os.path.join(out_path, title + '.png'))

    plt.show()


if __name__ == "__main__":
    file_names = [f for f in os.listdir(path) if f[-4:] == ".out" and f != "node_ucx_mlx5.out"]

    full = get_full_df(file_names)

    open_query = "compiler == 'open'"
    intel_query = "compiler == 'intel'"
    open_ib_query = "compiler == 'open' & pml == 'ib'"

    param_df = get_param(file_names, query=None)

    # param_df = param_df[param_df.index != "node_ucx_mlx5.out"]
    # param_df = df_filter(param_df, ["node_ucx_mlx5.out"])

    # Lambda barplot
    if lambda_barplot:
        build_barplot(param_df, key="lambda", title="Latency", scale=0.5)

    if band_barplot:
        build_barplot(param_df, key="bw", title="Bandwidth")
        plt.tight_layout()

    if triple_barplots:

        key = "lambda"
        fig, axs = plt.subplots(2, 3)
        plt.suptitle("Latency and Bandwidth", fontsize=20)
        ((ax1, ax2, ax3), (ax4, ax5, ax6)) = axs
        axes = [ax1, ax2, ax3, ax4, ax5, ax6]
        mappings = ["core", "socket", "node"]

        if path == "gpu":
            fig, axs = plt.subplots(2, 2)
            ((ax1, ax2), (ax4, ax5)) = axs
            axes = [ax1, ax2, ax4, ax5]
            mappings = ["core", "socket"]

        sub_title_font = 10

        for m, ax in zip(mappings, axs[0]):
            df = param_df.query("map == '" + m + "'")
            # l = [labels[i] for i in df.index]
            # build_barplot(df, key=key, ax=ax, label_list=l)
            build_barplot(df, key=key, ax=ax)

        ax1.set_title("Latency by Core", fontsize=sub_title_font)
        ax2.set_title("Latency by Socket", fontsize=sub_title_font)
        ax4.set_title("Bandwidth by Core", fontsize=sub_title_font)
        ax5.set_title("Bandwidth by Socket", fontsize=sub_title_font)
        if path != "gpu":
            ax3.set_title("Latency by  Node", fontsize=sub_title_font)
            ax6.set_title("Bandwidth by Node", fontsize=sub_title_font)

        key = "bw"
        for m, ax in zip(mappings, axs[1]):
            df = param_df.query("map == '" + m + "'")
            l = [labels[i] for i in df.index]
            build_barplot(df, key=key, ax=ax)

        # plt.tight_layout()
        # plt.show()

    mean_df = get_mean_df(file_names)
    # mean_df["bw"] = mean_df.size / mean_df.time

    if triple_bw_plt:
        fig, axs = plt.subplots(1, 3)
        (ax1, ax2, ax3) = axs
        mappings = ["core", "socket", "node"]
        if path == "gpu":
            fig, axs = plt.subplots(1, 2)
            (ax1, ax2) = axs
            mappings = ["core", "socket"]

        fig.suptitle("Computed and esitimated Bandwidth", fontsize=20)

        for m, ax in zip(mappings, axs):
            df = mean_df.query("map == @m")
            grouped = df.groupby("file")
            c = 0
            ax.set_title(f"map by {m}", fontsize=15)
            plt.yticks(fontsize=10)
            plt.xticks(fontsize=10)
            for key, group in grouped:
                c = (c + 1) % len(colors)
                group.plot(ax=ax, kind='line',
                           x='size', y='bw',
                           c=colors[c],
                           logx=True,
                           # title=,
                           legend=True,
                           label=labels[key],
                           )

                group.plot(ax=ax, kind='line',
                           x='size', y='comp_bw',
                           c=colors[c],
                           logx=True,
                           # title=f"map by {m}",
                           legend=False,
                           linestyle="dashed"
                           )

    print(param_df)

    plt.show()

    if make_csv:
        produce_csv(mean_df)
        pass

    if make_plot:
        produce_plot(mean_df)
    print()

    pass
