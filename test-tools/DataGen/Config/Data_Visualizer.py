from Config import Config
import os

log_data = {
    "num_834": 0,
    "num_270": 0,
    "time_834": 0,
    "time_270": 0,
    "avg_270_per_bene": 0,
    "throughput_834": 0,
    "throughput_270": 0,
    "error_rate_834": 0,
    "error_rate_270": 0,
    "error_ct_834": 0,
    "error_ct_270": 0,
    "family_size": 0,
    "sum_amt_D2": 0,
    "count_amt_D2": 0,
    "sum_amt_FK": 0,
    "count_amt_FK": 0,
    "sum_amt_R": 0,
    "count_amt_R": 0,
    "sum_amt_C1": 0,
    "count_amt_C1": 0,
    "sum_amt_P3": 0,
    "count_amt_P3": 0,
    "sum_amt_B9": 0,
    "count_amt_B9": 0
}


def create_md():
    if not os.path.exists(Config.MARKDOWN_DIRECTORY):
        os.makedirs(Config.MARKDOWN_DIRECTORY)
    path = os.path.join(Config.MARKDOWN_DIRECTORY, Config.STATISTICS_MD)

    with open(path, "w") as f:
        f.write("# Data Visualizer \n\n")

        f.write("## Transaction Counts\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "Number of Messages"\n')
        f.write('    x-axis ["834", "270"]\n')
        f.write('    y-axis "Count" 0 --> {}\n'.format(max(log_data['num_834'], log_data['num_270']) + 100))
        f.write(f'    bar [{log_data["num_834"]}, {log_data["num_270"]}]\n')
        f.write("```\n\n")

