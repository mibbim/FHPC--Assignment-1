import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

file0 = "matrix0.out"
file1 = "matrix1.out"
file2 = "matrix2.out"
file3 = "matrix3.out"
file4 = "matrix4.out"


def get_data(file):
    with open(file, "r") as f:
        lines = f.readlines()

    runs = []
    for line in lines:
        if line == "\n":
            continue
        # time, mapping = float(line[7:13]), float()
        splitted = line.split(" ")
        time, p = splitted[6], splitted[-5]
        runs.append({"proc": int(p), "time": float(time)})

    df = pd.DataFrame(runs)
    return df


def plotter(df, ax=plt):
    serial = df.query("proc == 1").time[0]
    ax.plot(df.proc, serial / df.time)


if __name__ == "__main__":
    df0 = get_data(file0)
    # df1 = get_data(file1)
    df2 = get_data(file2)
    df3 = get_data(file3)
    df4 = get_data(file4)

    df_concat = pd.concat((df0, df2, df3, df4))
    by_row_index = df_concat.groupby(df_concat.index)
    df_means = by_row_index.mean()

    fig, ax = plt.subplots(1, 1)
    # plotter(df0, ax)
    # # # plotter(df1, ax)
    # plotter(df2, ax)
    # plotter(df3, ax)
    # plotter(df4, ax)
    plotter(df_means)
    plt.title("Strong Speedup")
    plt.xlabel("procs")
    plt.ylabel("T(1)/T(N)")
    print(df0)

    plt.show()
