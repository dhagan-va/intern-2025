import os

from Config import Config
from Repository.Local_Database_Functions import LocalDBFunctions

INTRO = [
    "## What Are 834 and 270 EDI Files?\n\n",
    "**EDI 834 - Benefit Enrollment and Maintenance**  \n",
    "The 834 file is used to electronically transmit enrollment data between employers, insurance providers, "
    "and government agencies. It includes information about plan members (sponsors and beneficiaries), such as:\n",
    "- Enrollment or termination status (in our case it's enrollment)\n",
    "- Subscriber and dependent details\n",
    "- Coverage effective dates\n\n",
    "**EDI 270 - Eligibility Inquiry**  \n",
    "The 270 file is used to request information about a member's health insurance eligibility and benefits. "
    "It is typically sent by healthcare providers to insurers to confirm:\n",
    "- Active coverage\n",
    "- Service eligibility\n",
    "- Co-pays, deductibles, or benefit limits\n\n"
]

RELATIONSHIP_LABELS = {
    '01': 'Spouse (01)',
    '19': 'Child (19)',
    '26': 'Caregiver (26)',
    '25': 'Ex-Spouse (25)'
}

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
        "count": 0,
        "size_distribution": {
            1: 0,
            2: 0,
            3: 0,
            4: 0
        },
        "relationship_distribution": {
            '01': 0,
            '19': 0,
            '26': 0,
            '25': 0
        }
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

    message_types = [834, 270]
    message_count = [log_data["messages"]["count_834"], log_data["messages"]["count_270"]]
    total_messages = 0
    
    for key, value in log_data["messages"].items():
        if key.startswith("count_"):
            total_messages += value
    
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

        f.writelines(INTRO)

        f.write("## Transaction Counts\n")
        f.writelines(create_pie_chart(
            title="Message type distribution",
            labels=message_types,
            values=message_count
        ))

        f.write(f"Total Number of Messages Generated: **{total_messages}**\n")

        f.write("## Throughput\n")
        f.writelines(create_bar_graph(
            title="Throughput (Transactions per Second)",
            x=[834, 270],
            y="TPS",
            values=[throughput_834, throughput_270],
            y_max=max(throughput_834, throughput_270) + 1
        ))

        f.write("## Error Count\n")
        f.writelines(create_bar_graph(
            title="Error Count in Messages",
            x=[834, 270],
            y="Errors",
            values=[log_data["errors"]["error_ct_834"], log_data["errors"]["error_ct_270"]],
            y_max=max(log_data["errors"]["error_ct_834"], log_data["errors"]["error_ct_270"]) + 1
        ))

        f.write("## Error Rate\n")
        f.writelines(create_bar_graph(
            title="Error Rate (%)",
            x=[834, 270],
            y="Percent",
            values=[log_data["errors"]["error_rate_834"] * 100, log_data["errors"]["error_rate_270"] * 100],
            y_max=5
        ))

        f.write("## Family Size Distribution\n")
        size_dist = log_data["family"]["size_distribution"]
        size_labels = list(size_dist.keys())
        size_values = list(size_dist.values())

        f.writelines(create_bar_graph(
            title="Family Size Histogram",
            x=size_labels,
            y="Count",
            values=size_values,
            y_max=max(size_values) + 1
        ))

        f.writelines(create_pie_chart(
            title="Family Size Breakdown",
            labels=size_labels,
            values=size_values
        ))

        f.write("## Beneficiary Types\n")
        rel_dist = log_data["family"]["relationship_distribution"]
        rel_labels = [RELATIONSHIP_LABELS.get(code, code) for code in rel_dist.keys()]
        rel_values = list(rel_dist.values())

        f.writelines(create_bar_graph(
            title="Beneficiary Code Distribution",
            x=rel_labels,
            y="Count",
            values=rel_values,
            y_max=max(rel_values) + 1
        ))

        f.writelines(create_pie_chart(
            title="Beneficiary Relationship Types",
            labels=rel_labels,
            values=rel_values
        ))

        f.write("## AMT (deductible) Averages\n")
        f.writelines(create_bar_graph(
            title="AMT (deductible) Averages",
            x=["D2", "FK", "R"],
            y="Amount",
            values=[avg_d2, avg_fk, avg_r],
            y_max=max(avg_d2, avg_fk, avg_r) + 1000
        ))

        f.write("## AMT (visit) Averages\n")
        f.writelines(create_bar_graph(
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


def create_bar_graph(title, x, y, values, y_max):
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


def create_pie_chart(title, labels, values):
    segments = ["```mermaid\n",
                f'pie title {title}\n',
                ]
    for label, value in zip(labels, values):
        segments.append(f'    "{label}" : {value}\n')

    segments.append("```\n")
    segments.append("\n\n")

    return segments
