# Twitter Deanonymization

This project builds a network of Twitter data (based on a user's followers) and
demonstrates the potential of deanonymization attacks to reveal the identities
of those in anonymized datasets.

## Setup and Use

This project runs on Python 2.7, and has been tested with Linux and Windows.

Dependencies are listed in the included requirements.txt file, and can be
installed with pip using `pip install -r requirements.txt`.

To build a dataset from Twitter, run
`python TwitterScrapper.py RootTwitterHandle OutputFileName`. The dataset is
saved using YAML as a NetworkX graph, and is imported back into python by
`deanonymize.py`.

To run the deanonymization procedure, run
`python deanonymize.py DataSetFileName k`, where k is the size of the k-cliques
which will be used for seed selection. (If in doubt, set k to 3.)
