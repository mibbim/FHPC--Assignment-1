data = "thin"

plot = False

plot_time_fit = True
lambda_barplot = not True
band_barplot = not True
triple_barplots = not True
triple_bw_plt = not True

make_csv = True
make_plot = True

print_table = True

if not plot:
    plot_time_fit = False
    lambda_barplot = False
    band_barplot = False
    triple_barplots = False
    triple_bw_plt = False

# path = "out1"
# path = "out1"
# path = "out1"
paths = {
    "gpu": "gpu_shared",
    "thin": "out",
}
output_path = {
    "gpu": "gpu_csv_and_plots",
    "thin": "thin_csv_and_plots",
}
path = paths[data]

out_path = output_path[data]
