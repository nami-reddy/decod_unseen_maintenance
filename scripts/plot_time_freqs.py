# Author: Jean-Remi King <jeanremi.king@gmail.com>
#
# Licence: BSD 3-clause

"""Plot the time-frequency decoding for each analysis.

Used to generate Figure 3.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from jr.plot import pretty_plot, pretty_colorbar
from base import stats
from conditions import analyses
from config import load, subjects, report

fig = plt.figure(figsize=[18, 5])
axes = gridspec.GridSpec(2, 5, left=0.05, right=.95, hspace=0.35, wspace=.25)
for ii, (analysis, ax) in enumerate(zip(analyses, axes)):
    ax = fig.add_subplot(ax)
    scores = list()
    for subject in subjects:
        score, times, freqs = load('score_tfr', subject=subject,
                                   analysis=analysis['name'])
        scores.append(score)
    scores = np.array(scores)
    if 'circAngle' in analysis['name']:
        scores /= 2
    # compute stats
    p_val = stats(scores - analysis['chance'])
    sig = p_val < .05

    # plot effect size
    scores = np.mean(scores, axis=0)
    im = ax.matshow(scores, aspect='auto', origin='lower',
                    extent=[times[0], times[-1], 0, len(freqs)],
                    vmin=analysis['chance'], vmax=np.max(scores),
                    cmap=analysis['cmap'])

    # plot stats
    xx, yy = np.meshgrid(times, range(len(freqs)), copy=False, indexing='xy')
    ax.contour(xx, yy, sig, colors='black', levels=[0],
               linestyles='dotted')

    # pretty plot
    pretty_plot(ax)
    ticks = [0]
    for freq in np.arange(10, 71, 10):
        ticks.append(np.where(np.round(freqs) >= freq)[0][0])
    ticks.append(len(freqs))
    ax.set_yticks(ticks)
    ax.set_yticklabels([])
    if ii in [0, (len(analyses)//2)]:
        ax.set_yticklabels([int(freqs[0]), 10, '', 30, '',
                            '', '', '', int(freqs[-1] + .1)])
    xticks = np.arange(-.200, 1.301, .100)
    ax.set_xticks(xticks)
    ax.set_xticklabels([])
    if ii >= (len(analyses)//2):
        ax.set_xticklabels([int(tim * 1e3) if tim in [.0, .800] else ''
                            for tim in xticks])
    ax.axvline([0.], color='k')
    ax.axvline([.800], color='k')
    ax.set_title(analysis['title'])
    pretty_colorbar(im, ax=ax, ticks=[analysis['chance'], np.max(scores)])

report.add_figs_to_section([fig], ['all freqs'], 'all')
report.save()
