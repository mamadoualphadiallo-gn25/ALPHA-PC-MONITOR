import csv, json
from pathlib import Path

def export_snapshot_csv(sample, destination):
    row = {k:v for k,v in sample.items() if k != "disks"}
    row["disks_json"] = json.dumps(sample.get("disks",[]),ensure_ascii=False)
    with Path(destination).open("w",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,fieldnames=list(row))
        writer.writeheader(); writer.writerow(row)
