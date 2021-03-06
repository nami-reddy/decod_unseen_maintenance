# Author: Jean-Remi King <jeanremi.king@gmail.com>
#
# Licence: BSD 3-clause

"""Run decoding and temporal generalization analyses for each subject
separately.
"""
import numpy as np
from mne.decoding import GeneralizationAcrossTime
from config import subjects, load, save
from conditions import analyses


def _run(epochs, events, analysis):
    """Runs temporal generalization for a given subject and analysis"""
    print(subject, analysis['name'])

    # subselect the trials (e.g. exclude absent trials) with a
    # dataframe query defined in conditions.py
    query, condition = analysis['query'], analysis['condition']
    sel = range(len(events)) if query is None \
        else events.query(query).index
    sel = [ii for ii in sel if ~np.isnan(events[condition][sel][ii])]

    # The to-be-predicted value, for each trial:
    y = np.array(events[condition], dtype=np.float32)

    print analysis['name'], np.unique(y[sel]), len(sel)

    # Abort if there is no trial
    if len(sel) == 0:
        return

    # Apply analysis
    gat = GeneralizationAcrossTime(clf=analysis['clf'],
                                   cv=analysis['cv'],
                                   scorer=analysis['scorer'],
                                   n_jobs=-1)
    print(subject, analysis['name'], 'fit')
    gat.fit(epochs[sel], y=y[sel])
    print(subject, analysis['name'], 'score')
    score = gat.score(epochs[sel], y=y[sel])
    print(subject, analysis['name'], 'save')

    # save space
    if analysis['name'] not in ['probe_phase', 'target_circAngle']:
        # we'll need the estimator trained on the probe_phase and to generalize
        # to the target phase and prove that there is a significant signal.
        gat.estimators_ = None
    if analysis['name'] not in ['target_present', 'target_circAngle',
                                'probe_circAngle']:
        # We need these individual prediction to control for the correlation
        # between target and probe angle.
        gat.y_pred_ = None

    # Save analysis
    save([gat, analysis, sel, events], 'decod',
         subject=subject, analysis=analysis['name'], overwrite=True,
         upload=True)
    save([score, epochs.times], 'score',
         subject=subject, analysis=analysis['name'], overwrite=True,
         upload=True)
    return


for s, subject in enumerate(subjects):  # Loop across each subject
    print(subject)

    # load data
    epochs = load('epochs_decim', subject=subject, preload=True)

    # only analyze MEG from -100 ms to 1400 ms after target onset
    epochs.pick_types(meg=True, eeg=False, stim=False, eog=False, ecg=False)
    epochs.crop(-.1, 1.4)
    events = load('behavior', subject=subject)

    # Apply to each analysis (e.g. presence, orientation, ...)
    for analysis in analyses:
        _run(epochs, events, analysis)

    # Clear memory
    del epochs, events
