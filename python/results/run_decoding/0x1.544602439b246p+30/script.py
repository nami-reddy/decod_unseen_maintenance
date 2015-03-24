import os.path as op

import scipy.io as sio
import numpy as np

import mne
from mne.decoding import GeneralizationAcrossTime

from utils import get_data, resample_epochs, decim
from meeg_preprocessing import setup_provenance

from config import (
    open_browser,
    data_path,
    results_dir,
    subjects,
    preproc,
    decoding_params
)

report, run_id, results_dir, logger = setup_provenance(
                    script=__file__, results_dir=results_dir)

for subject in subjects:
    print(subject)
    # define paths
    meg_fname = op.join(data_path, subject, 'preprocessed', subject +
                        '_preprocessed')
    bhv_fname = op.join(data_path, subject, 'behavior', subject + '_fixed.mat')
    epochs, events = get_data(meg_fname, bhv_fname)

    # preprocess data for memory issue
    if 'resample' in preproc.keys():
        epochs = resample_epochs(epochs, preproc['resample'])
    if 'decim' in preproc.keys():
        epochs = decim(epochs, preproc['decim'])
    if 'crop' in preproc.keys():
        epochs.crop(preproc['crop']['tmin'],
                    preproc['crop']['tmax'])

    # retrieve contrast depending on classification type
    if type=='SVC'
        from config import (contrasts_svc)
    elif type=='SVR'
        from config import (contrasts_svr)

    # Apply each contrast
    for contrast in contrasts:
        print(contrast)
        # Find excluded trials
        exclude = np.any([events[x['cond']]==ii
                            for x in contrast['exclude']
                                for ii in x['values']],
                        axis=0)

        # Select condition
        include = list()
        cond_name = contrast['include']['cond']
        for value in contrast['include']['values']:
            # Find included trials
            include.append(events[cond_name]==value)
        sel = np.any(include,axis=0) * (exclude==False)
        sel = np.where(sel)[0]

        # reduce number or trials if too many
        if len(sel) > 400:
            import random
            random.shuffle(sel)
            sel = sel[0:400]

        y = np.array(events[cond_name].tolist())

        # Apply contrast
        gat = GeneralizationAcrossTime(**decoding_params)
        gat.fit(epochs[sel], y=y[sel])
        gat.score(epochs[sel], y=y[sel])

        # Plot
        fig = gat.plot_diagonal(show=False)
        report.add_figs_to_section(fig, ('%s %s: (decoding)'
                % (subject, cond_name)), subject)

        fig = gat.plot(show=False)
        report.add_figs_to_section(fig, ('%s %s: GAT'
                % (subject, cond_name)), subject)
        # Save contrast
        pkl_fname = op.join(data_path, subject, 'mvpas',
                            '{}-decod_{}.pickle'.format(subject, cond_name))

report.save(open_browser=open_browser)
