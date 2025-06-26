import os

from Config import Config
from Repository.Local_Database_Functions import LocalDBFunctions

# relationship map
log_data = {
    "messages": {
        "count_834": 0,
        "count_270": 0,
        "time_834": 0,
        "time_270": 0,
    },
    "errors": {
        "error_ct_834": 0,
        "error_ct_270": 0,
        "error_rate_834": 0,
        "error_rate_270": 0
    },
    "family": {
        "size": 0,
        "count": 0
    },
    "amt": {
        "D2": {"sum": 0, "count": 0},
        "FK": {"sum": 0, "count": 0},
        "R": {"sum": 0, "count": 0},
        "C1": {"sum": 0, "count": 0},
        "P3": {"sum": 0, "count": 0},
        "B9": {"sum": 0, "count": 0}
    }
}


def create_md():
    if not os.path.exists(Config.MARKDOWN_DIRECTORY):
        os.makedirs(Config.MARKDOWN_DIRECTORY)
    path = os.path.join(Config.MARKDOWN_DIRECTORY, Config.STATISTICS_MD)

    localdb = LocalDBFunctions()

    avg_family_size = log_data["family"]["size"] / log_data["family"]["count"]
    throughput_834 = log_data["messages"]["count_834"] / log_data["messages"]["time_834"]
    throughput_270 = log_data["messages"]["count_270"] / log_data["messages"]["time_270"]
    avg_d2 = log_data["amt"]["D2"]["sum"] / log_data["amt"]["D2"]["count"]
    avg_fk = log_data["amt"]["FK"]["sum"] / log_data["amt"]["FK"]["count"]
    avg_r = log_data["amt"]["R"]["sum"] / log_data["amt"]["R"]["count"]
    avg_c1 = log_data["amt"]["C1"]["sum"] / log_data["amt"]["C1"]["count"]
    avg_p3 = log_data["amt"]["P3"]["sum"] / log_data["amt"]["P3"]["count"]
    avg_b9 = log_data["amt"]["B9"]["sum"] / log_data["amt"]["B9"]["count"]

    with open(path, "w") as f:
        f.write("# Data Visualizer \n\n")

        f.write("## Transaction Counts\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "Number of Messages"\n')
        f.write('    x-axis ["834", "270"]\n')
        f.write('    y-axis "Count" 0 --> {}\n'.format(
            max(log_data["messages"]["count_834"], log_data["messages"]["count_270"]) + 100))
        f.write(f'    bar [{log_data["messages"]["count_834"]}, {log_data["messages"]["count_270"]}]\n')
        f.write("```\n\n")

        f.write("## Throughput\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "Throughput (Transactions per Second)"\n')
        f.write('    x-axis ["834", "270"]\n')
        f.write('    y-axis "TPS" 0 --> {}\n'.format(
            max(throughput_834, throughput_270) + 1))
        f.write(f'    bar [{throughput_834:.2f}, {throughput_270:.2f}]\n')
        f.write("```\n\n")

        f.write("## Error Count\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "Error Count in Messages"\n')
        f.write('    x-axis ["834", "270"]\n')
        f.write('    y-axis "Errors" 0 --> {}\n'.format(
            max(log_data["errors"]["error_ct_834"], log_data["errors"]["error_ct_270"]) + 1))
        f.write(f'    bar [{log_data["errors"]["error_ct_834"]}, {log_data["errors"]["error_ct_270"]}]\n')
        f.write("```\n\n")

        f.write("## Error Rate\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "Error Rate (%)"\n')
        f.write('    x-axis ["834", "270"]\n')
        f.write('    y-axis "Percent" 0 --> 5\n')
        f.write(f'    bar [{log_data["errors"]["error_rate_834"] * 100:.2f}, {log_data["errors"]["error_rate_270"] * 100:.2f}]\n')
        f.write("```\n\n")

        f.write("## AMT (Deductible) Averages\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "AMT Averages"\n')
        f.write('    x-axis ["D2", "FK", "R"]\n')
        f.write('    y-axis "Amount" 0 --> {}\n'.format(
            int(max(avg_d2, avg_fk, avg_r)) + 1000))
        f.write(f'    bar [{avg_d2:.2f}, {avg_fk:.2f}, {avg_r:.2f}]\n')
        f.write("```\n\n")

        f.write("## AMT (Visit) Averages\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "AMT Averages"\n')
        f.write('    x-axis ["D2", "FK", "R"]\n')
        f.write('    y-axis "Amount" 0 --> {}\n'.format(
            int(max(avg_c1, avg_p3, avg_b9)) + 1))
        f.write(f'    bar [{avg_c1:.2f}, {avg_p3:.2f}, {avg_b9:.2f}]\n')
        f.write("```\n\n")

        f.write("## Average 270s per Beneficiary\n")
        bene_count = len(localdb.all_bene)
        avg_270s_per_bene = log_data["messages"]["count_270"] / bene_count if bene_count else 0
        f.write(f"- Average 270s per Beneficiary: **{avg_270s_per_bene:.2f}**\n")

