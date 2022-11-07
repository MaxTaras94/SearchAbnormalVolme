from data.config import APP_DIR
import datetime
import os
import linecache
import tracemalloc


def display_top(snapshot, key_type='lineno', limit=10, print_flag=False):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)
    log = ""

    text = "Top %s lines" % limit
    log += text + "\n"
    if print_flag:
        print(text)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        text = "#%s: %s:%s: %.1f KiB" % (index,
                                         frame.filename,
                                         frame.lineno,
                                         stat.size / 1024)
        log += text + "\n"
        if print_flag:
            print(text)
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            text = '    %s' % line
            log += text + "\n"
            if print_flag:
                print(text)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        text = "%s other: %.1f KiB" % (len(other), size / 1024)
        log += text + "\n"
        if print_flag:
            print(text)
    total = sum(stat.size for stat in top_stats)
    text = "Total allocated size: %.1f KiB" % (total / 1024)
    log += text + "\n\n"
    if print_flag:
        print(text)

    dt = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(APP_DIR, "utils/tracemalloc/total_memory_log.txt")
    total_log_file = open(path, 'a')
    total_log_file.write(dt + "; "
                         + "%.1f" % (total / 1024) + "; "
                         + "Total allocated size: %.1f KiB\n" % (total / 1024))
    total_log_file.close()

    path = os.path.join(APP_DIR, "utils/tracemalloc/memory_log.txt")
    log_file = open(path, 'a')
    log_file.write(dt + "\n" + log)
    log_file.close()
