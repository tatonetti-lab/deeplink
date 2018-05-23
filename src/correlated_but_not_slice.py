import os
import sys
import csv
import gzip
import tqdm

import scipy.stats as stats

from collections import defaultdict

jobslice = map(int, sys.argv[1].split(':'))

print >> sys.stderr, "Running for slice: %s" % jobslice

fh = 'data/project_aers_10q4.pred_drug_events_e5.txt.gz'
reader = csv.reader(gzip.open(fh), delimiter='\t')
header = reader.next()
#print header

drugs = set()
events = set()

means = defaultdict(dict)

print >> sys.stderr, "Loading FAERS data..."

for row in tqdm.tqdm(reader):
    data = dict(zip(header, row))
    drugs.add(data['stitch_id'])
    events.add(data['umls_id'])
    means[data['umls_id']][data['stitch_id']]= float(data['drug_mean'])


events = sorted(events)
drugs = sorted(drugs)

correlations = dict()
for i, e1 in tqdm.tqdm(enumerate(events[jobslice[0]:jobslice[1]]), total=(jobslice[1]-jobslice[0])):
    for j, e2 in enumerate(events):
        if j <= i:
            continue
        
        e1drugs = set(means[e1].keys())
        e2drugs = set(means[e2].keys())
        common_drugs = sorted(e1drugs & e2drugs)
        if len(common_drugs) < 3:
            continue
        
        mus1 = [means[e1][d] for d in common_drugs]
        mus2 = [means[e2][d] for d in common_drugs]
        r, p = stats.pearsonr(mus1, mus2)
        
        correlations[(e1,e2)] = (r, p, len(common_drugs))

ofh = gzip.open('results/event_means_correlations_%d_%d.txt.gz' % (jobslice[0], jobslice[1]),'w')
writer = csv.writer(ofh, delimiter='\t')
writer.writerow(['umls_id1', 'umls_id2', 'r', 'pvalue', 'n'])

for (e1, e2) in correlations.keys():
    r, p, n = correlations[(e1, e2)]
    writer.writerow([e1, e2, r, p, n])

ofh.close()


