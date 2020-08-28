import os
import json
import sys

from matplotlib import pyplot as plt
import numpy as np
import math
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--plots', nargs='+', help='''
                        One or more plots to be shown.
                        Available: latency, throughput, overhead, messages.
                        ''')

    return parser.parse_args()

# def groupby(arr, key):
#     res = {}
#     for l in arr:
#         if !l[]
#         if len(res[""])
def process_result_line(l):
    l = json.loads(l)
    name = l["name"].split('/')
    value = (l["measures"])["value"]
    item = {}
    for attr in name:
        attr = attr.split(":")
        item[attr[0]] = attr[1]
    item["value"] = value
    return item

def aggregate_results():
    res = []
    for subdir, _, files in os.walk('./results'):
        for filename in files:
            filepath = subdir + os.sep + filename
            if filepath.split("/")[-1] == "results.out":
                print (filepath)
                resultFile = open(filepath, 'r')
                for l in resultFile.readlines():
                    res.append(process_result_line(l))
    return res, len(os.listdir("./results"))

def groupBy(agg, metric):
    res = {}
    for item in agg:
        if not item[metric] in res:
            res[item[metric]] = []
        res[item[metric]].append(item)
    return res

def plot_latency(byLatency, byBandwidth, byFileSize):

    plt.figure()

    p1, p2 = len(byLatency), len(byBandwidth)
    pindex = 1
    x = []
    y = {}
    tc = {}
    for l in byLatency:
    
        for b in byBandwidth:
            ax =plt.subplot(p1, p2, pindex)
            ax.set_title("latency: "+l + " bandwidth: " + b)
            ax.set_xlabel('File Size (MB)')
            ax.set_ylabel('time_to_fetch (ms)')

            for f in byFileSize:
                
                x.append(int(f)/1e6)
                
                y[f] = []
                tc[f] = []
                for i in byFileSize[f]:
                    if i["latencyMS"] == l and i["bandwidthMB"] == b and\
                            i["nodeType"]=="Leech":
                            if i["name"] == "time_to_fetch":
                                y[f].append(i["value"])
                            if i["name"] == "tcp_fetch":
                                tc[f].append(i["value"])

                avg = []
                for i in y:
                    scaled_y = [i/1e6 for i in y[i]]
                    ax.scatter([int(i)/1e6]*len(y[i]), scaled_y, marker="+")
                    avg.append(sum(scaled_y)/len(scaled_y))
                avg_tc = []
                for i in tc:
                    scaled_tc = [i/1e6 for i in tc[i]]
                    ax.scatter([int(i)/1e6]*len(tc[i]), scaled_tc, marker="*")
                    avg_tc.append(sum(scaled_tc)/len(scaled_tc))

            # print(x, tc)
            ax.plot(x, avg_tc, label="TCP fetch")

            ax.plot(x, avg, label="Bitswap fetch")
            ax.legend()

            pindex+=1
            x = []
            y = {}
            tc = {}


def plot_tcp_latency(byLatency, byBandwidth, byFileSize):

    plt.figure()

    p1, p2 = len(byLatency), len(byBandwidth)
    pindex = 1
    x = []
    tc = {}
    for l in byLatency:
    
        for b in byBandwidth:
            ax =plt.subplot(p1, p2, pindex)
            ax.set_title("latency: "+l + " bandwidth: " + b)
            ax.set_xlabel('File Size (MB)')
            ax.set_ylabel('time_to_fetch (ms)')

            for f in byFileSize:
                
                x.append(int(f)/1e6)

                tc[f] = []
                for i in byFileSize[f]:
                    if i["latencyMS"] == l and i["bandwidthMB"] == b and\
                            i["nodeType"]=="Leech":
                            if i["name"] == "tcp_fetch":
                                tc[f].append(i["value"])


                avg_tc = []
                for i in tc:
                    scaled_tc = [i/1e6 for i in tc[i]]
                    ax.scatter([int(i)/1e6]*len(tc[i]), scaled_tc, marker="*")
                    avg_tc.append(sum(scaled_tc)/len(scaled_tc))

            # print(x, tc)
            ax.plot(x, avg_tc, label="TCP fetch")
            ax.legend()

            pindex+=1
            x = []
            tc = {}

def autolabel(ax, rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


# TODO: This is wrong. Here we only accoun for the data exchanged using Bitswap.
def plot_messages(byFileSize, byTopology):

    # plt.figure()
    

    for t in byTopology:
        labels = []
        arr_blks_sent = []
        arr_blks_rcvd = []
        arr_dup_blks_rcvd = []
        arr_msgs_rcvd = []
        for f in byFileSize:
            labels.append(int(f)/1e6)
            x = np.arange(len(labels))  # the label locations
            blks_sent = blks_rcvd = dup_blks_rcvd = msgs_rcvd = 0
            blks_sent_n = blks_rcvd_n = dup_blks_rcvd_n = msgs_rcvd_n = 0
            width = 1/4

            for i in byFileSize[f]:
                if i["topology"]==t:
                    if i["name"] == "blks_sent":
                        blks_sent += i["value"]
                        blks_sent_n += 1
                    if i["name"] == "blks_rcvd":
                        blks_rcvd += i["value"]
                        blks_rcvd_n += 1
                    if i["name"] == "dup_blks_rcvd":
                        dup_blks_rcvd += i["value"]
                        dup_blks_rcvd_n += 1
                    if i["name"] == "msgs_rcvd":
                        msgs_rcvd += i["value"]
                        msgs_rcvd_n += 1

            # Computing averages
            # Remove the division if you want to see total values 
            arr_blks_rcvd.append(round(blks_rcvd/blks_rcvd_n,1))
            arr_blks_sent.append(round(blks_sent/blks_sent_n,1))
            arr_dup_blks_rcvd.append(round(dup_blks_rcvd/dup_blks_rcvd_n,1))
            arr_msgs_rcvd.append(round(msgs_rcvd/msgs_rcvd_n,1))
            blks_sent = blks_rcvd = dup_blks_rcvd = msgs_rcvd = 0
            blks_sent_n = blks_rcvd_n = dup_blks_rcvd_n = msgs_rcvd_n = 0


        fig, ax = plt.subplots()
        bar1 = ax.bar(x-(3/2)*width, arr_msgs_rcvd, width, label="Msgs Received")
        bar2 = ax.bar(x-width/2, arr_blks_rcvd, width, label="Blocks Rcv")
        bar3 = ax.bar(x+width/2, arr_blks_sent, width, label="Blocks Sent")
        bar4 = ax.bar(x+(3/2)*width, arr_dup_blks_rcvd, width, label="Duplicates blocks")

        autolabel(ax, bar1)
        autolabel(ax, bar2)
        autolabel(ax, bar3)
        autolabel(ax, bar4)

        ax.set_ylabel('Number of messages')
        ax.set_ylabel('File Size (MB)') 
        ax.set_title('Average number of blocks exchanged ' + t)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        fig.tight_layout()

# TODO: This is wrong. Here we only accoun for the data exchanged using Bitswap.
def plot_bw_overhead(byFileSize, byTopology):

    # plt.figure()
    

    for t in byTopology:
        labels = []
        arr_control_rcvd = []
        arr_block_data_rcvd = []
        arr_dup_data_rcvd = []
        arr_overhead = []
        for f in byFileSize:
            #TODO: Considering a 5.5% overhead of TPC
            leechCount = t.replace("(", "").replace(")", "").split(",")[1]
            TCP_BASELINE = int(leechCount)*1.055*int(f)
            labels.append(int(f)/1e6)
            x = np.arange(len(labels))  # the label locations
            data_rcvd = block_data_rcvd = dup_data_rcvd = overhead = 0
            data_rcvd_n = block_data_rcvd_n = dup_data_rcvd_n = overhead_n = 0
            width = 1/4

            for i in byFileSize[f]:
                # We are only interested in leechers so we don't duplicate measurements.
                if i["nodeType"] == "Leech" and i["topology"]==t:
                    if i["name"] == "data_rcvd":
                        data_rcvd += i["value"]
                        data_rcvd_n += 1
                        overhead = (data_rcvd-TCP_BASELINE)*100/TCP_BASELINE
                        overhead_n += 1
                    if i["name"] == "block_data_rcvd":
                        block_data_rcvd += i["value"]
                        block_data_rcvd_n += 1
                    if i["name"] == "dup_data_rcvd":
                        dup_data_rcvd += i["value"]
                        dup_data_rcvd_n += 1

            control_rcvd = data_rcvd - block_data_rcvd
            # Computing averages
            # Remove the division if you want to see total values 
            arr_control_rcvd.append(round(control_rcvd/data_rcvd_n/1e6,3))
            arr_block_data_rcvd.append(round(block_data_rcvd/block_data_rcvd_n/1e6,3))
            arr_dup_data_rcvd.append(round(dup_data_rcvd/dup_data_rcvd_n/1e6,3))
            arr_overhead.append(round(overhead/overhead_n,3))
            control_rcvd = data_rcvd = block_data_rcvd = dup_data_rcvd = overhead = 0
            data_rcvd_n = block_data_rcvd_n = dup_data_rcvd_n = overhead_n = 0


        fig, ax = plt.subplots()
        bar1 = ax.bar(x-(3/2)*width, arr_control_rcvd, width, label="Control data received (MB)")
        bar2 = ax.bar(x-width/2, arr_block_data_rcvd, width, label="Total data received from blocks (MB)")
        bar3 = ax.bar(x+width/2, arr_dup_data_rcvd, width, label="Total data received from duplicates (MB)")
        bar4 = ax.bar(x+(3/2)*width, arr_overhead, width, label="Bandwidth overhead (%)")
        
        autolabel(ax, bar1)
        autolabel(ax, bar2)
        autolabel(ax, bar3)
        autolabel(ax, bar4)

        ax.set_ylabel('Number of messages')
        # ax.set_ylabel('File Size (MB)') 
        ax.set_title('Data received '+ t)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        fig.tight_layout()


def plot_througput(byLatency, byBandwidth, byFileSize, byTopology, testcases):

    plt.figure()

    p1, p2 = 2, math.ceil(testcases/2)
    pindex = 1
    x = []
    y = {}
    toPlot = False

    for t in byTopology:
        for l in byLatency:
        
            for b in byBandwidth:
                ax =plt.subplot(p1, p2, pindex)
                ax.set_title("Average Throughput - latency: "+l + "ms bandwidth: " + b + "MB topology: " + t)
                ax.set_xlabel('File Size (MB)')
                ax.set_ylabel('throughput (Mbps)')

                for f in byFileSize:
                    time_to_fetch = block_data_rcvd = dup_data_rcvd = 0
                    time_to_fetch_n = block_data_rcvd_n = dup_data_rcvd_n = 0
                    x.append(int(f)/1e6)
                    
                    y[f] = []
                    for i in byFileSize[f]:
                        if i["latencyMS"] == l and i["bandwidthMB"] == b and\
                            i["topology"] == t and i["nodeType"]=="Leech":
                                if i["name"] == "time_to_fetch":
                                    time_to_fetch += i["value"]/1e6  #Get in ms
                                    time_to_fetch_n +=1
                                if i["name"] == "block_data_rcvd":
                                    block_data_rcvd += i["value"]
                                    block_data_rcvd_n +=1
                                if i["name"] == "dup_data_rcvd":
                                    dup_data_rcvd += i["value"]
                                    dup_data_rcvd_n +=1
                    
                    if time_to_fetch_n != 0:
                        avg_time_to_fetch = time_to_fetch / time_to_fetch_n / 1e3   # Use it in s
                        avg_data = ((block_data_rcvd/block_data_rcvd_n)-(dup_data_rcvd/dup_data_rcvd_n)) / 1e6   # IN MB
                        y[f].append(avg_data / avg_time_to_fetch)

                        time_to_fetch = block_data_rcvd = dup_data_rcvd = 0
                        time_to_fetch_n = block_data_rcvd_n = dup_data_rcvd_n = 0
                        toPlot = True

                avg = []
                if toPlot:
                    for i in y:
                        ax.scatter([int(i)/1e6]*len(y[i]), y[i], marker="+")
                        avg.append(sum(y[i])/len(y[i]))

                    ax.plot(x, avg)
                    pindex+=1
                    toPlot = False

                x = []
                y = {}


if __name__ == "__main__":
    args = parse_args()
    print("Starting to run...")
    agg, testcases = aggregate_results()
    byLatency = groupBy(agg, "latencyMS")
    byNodeType = groupBy(agg, "nodeType")
    byFileSize = groupBy(agg, "fileSize")
    byBandwidth = groupBy(agg, "bandwidthMB")
    byTopology = groupBy(agg, "topology")
    if args.plots is None:
        print("[!!] No plots provided...")
        sys.exit()

    if "latency" in args.plots:
        plot_latency(byLatency, byBandwidth, byFileSize)
    if "messages" in args.plots:
        plot_messages(byFileSize, byTopology)
    if "overhead" in args.plots:
        plot_bw_overhead(byFileSize, byTopology)
    if "throughput" in args.plots:
        plot_througput(byLatency, byBandwidth, byFileSize, byTopology, testcases)
    if "tcp" in args.plots:
        plot_tcp_latency(byLatency, byBandwidth, byFileSize)

    plt.show()
