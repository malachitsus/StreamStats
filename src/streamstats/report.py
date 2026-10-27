import json


def build_report(total_stats):

    if total_stats.first_ts is not None:
        first_str = total_stats.first_ts.isoformat()
    else:
        first_str = None

    if total_stats.last_ts is not None:
        last_str = total_stats.last_ts.isoformat()
    else:
        last_str = None

    top_list = []

    for source, count in total_stats.top_errors():
        item_dict = {"source": source, "count": count}
        top_list.append(item_dict)

    report_dict = {
        "total": total_stats.total,
        "by_level": total_stats.by_level,
        "by_source": total_stats.by_source,
        "top_errors": top_list,
        "first_timestamp": first_str,
        "last_timestamp": last_str,
        "skipped": total_stats.skipped
    }

    return report_dict

def write_report(report_dict, r_path):
    with open(r_path, mode="w", encoding='utf-8') as report:
        json.dump(report_dict, report, ensure_ascii=False, indent=2)

    

    
