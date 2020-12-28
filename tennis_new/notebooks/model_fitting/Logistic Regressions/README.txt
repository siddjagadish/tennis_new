The state of logistic regression model research is as follows:
* A simple main effect logistic regression with regularization works reasonably well, both through fitting in SKLearn and pytorch.
    * Such a regression is roughly three accuracy points worse than an ELO model on an apples-to-apples test set (only include players included in the logit training set).  We suspect the difference largely has to do with the ELO updates, compared with the static logit training set (also no recency weights yet).
        * A major TODO is trying out updating strategies for a logistic regression model (e.g. train for one epoch per day, including the new data).
* Surface information added only a little benefit, probably because of a lack of general information, as well as because we haven't yet properly tuned regularization differing between surface features and main effects.
* Surface information in the pytorch model needs some implementation work.