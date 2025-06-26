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
        f.writelines(create_mermaid_bar_graph(
            title="Number of Messages",
            x=[834, 270],
            y="Count",
            values=[log_data["messages"]["count_834"], log_data["messages"]["count_270"]],
            y_max=max(log_data["messages"]["count_834"], log_data["messages"]["count_270"]) + 100
        ))

        f.write("## Throughput\n")
        f.writelines(create_mermaid_bar_graph(
            title="Throughput (Transactions per Second)",
            x=[834, 270],
            y="TPS",
            values=[throughput_834, throughput_270],
            y_max=max(throughput_834, throughput_270) + 1
        ))

        f.write("## Error Count\n")
        f.writelines(create_mermaid_bar_graph(
            title="Error Count in Messages",
            x=[834, 270],
            y="Errors",
            values=[log_data["errors"]["error_ct_834"], log_data["errors"]["error_ct_270"]],
            y_max=max(log_data["errors"]["error_ct_834"], log_data["errors"]["error_ct_270"]) + 1
        ))

        f.write("## Error Rate\n")
        f.writelines(create_mermaid_bar_graph(
            title="Error Rate (%)",
            x=[834, 270],
            y="Percent",
            values=[log_data["errors"]["error_rate_834"] * 100, log_data["errors"]["error_rate_270"] * 100],
            y_max=5
        ))

        f.write("## AMT (deductible) Averages\n")
        f.writelines(create_mermaid_bar_graph(
            title="AMT (deductible) Averages",
            x=['D2', 'FK', 'R'],
            y="Amount",
            values=[avg_d2, avg_fk, avg_r],
            y_max=max(avg_d2, avg_fk, avg_r) + 1000
        ))

        f.write("## AMT (visit) Averages\n")
        f.writelines(create_mermaid_bar_graph(
            title="AMT (visit) Averages",
            x=["C1", "P3", "B9"],
            y="Number of Visits",
            values=[avg_c1, avg_p3, avg_b9],
            y_max=max(avg_c1, avg_p3, avg_b9) + 1
        ))

        f.write("## Average 270s per Beneficiary\n")
        bene_count = len(localdb.all_bene)
        avg_270s_per_bene = log_data["messages"]["count_270"] / bene_count if bene_count else 0
        f.write(f"- Average 270s per Beneficiary: **{avg_270s_per_bene:.2f}**\n")


def create_mermaid_bar_graph(title, x, y, values, y_max):
    x = "[" + ", ".join(f'"{str(item)}"' for item in x) + "]"

    segments = ["```mermaid\n",
                "xychart-beta\n",
                f'    title "{title}"\n',
                f'    x-axis {x}\n',
                f'    y-axis "{y}" 0 --> {y_max}\n',
                f'    bar {values}\n',
                "```\n",
                "\n\n"]

    return segments
