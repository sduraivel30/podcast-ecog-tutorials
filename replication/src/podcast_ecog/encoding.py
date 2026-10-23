"""Word-onset encoding of contextual embeddings -> high-gamma (tutorial 04, himalaya RidgeCV), plus a small CV helper."""
import numpy as np
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from himalaya.ridge import RidgeCV
from himalaya.scoring import correlation_score

def encoding_cv(X, Y, alphas=None, n_outer=2, n_inner=5):
    """Outer contiguous K-fold; inner 5-fold ridge CV over `alphas`; returns per-fold correlations (folds x Y columns) between predictions and held-out Y (Y standardised on the training fold)."""
    alphas = np.logspace(1, 10, 10) if alphas is None else alphas; out = []
    for tr, te in KFold(n_outer, shuffle=False).split(X):
        sc = StandardScaler().fit(Y[tr]); model = make_pipeline(StandardScaler(), RidgeCV(alphas, fit_intercept=True, cv=KFold(n_inner, shuffle=False)))
        model.fit(X[tr].astype(np.float32), sc.transform(Y[tr]).astype(np.float32)); out.append(np.asarray(correlation_score(sc.transform(Y[te]), model.predict(X[te].astype(np.float32)))))
    return np.stack(out)

def encode_subject(subject, layer=24, picks=None, tmin=-2.0, tmax=2.0, sfreq=32, root=None, **kw):
    """Tutorial 04 end to end for one subject: returns (corr [folds x electrodes x lags], channel names, lags in s)."""
    from .data import load_highgamma, word_embeddings, word_epochs
    emb, words = word_embeddings("gpt2-xl", layer, root); raw = load_highgamma(subject, picks=picks, preload=True, root=root); ep = word_epochs(raw, words, tmin, tmax, sfreq)
    Y = ep.get_data(copy=True); shape = Y.shape[1:]; X = emb[ep.selection]
    r = encoding_cv(X, Y.reshape(len(Y), -1), **kw).reshape((-1,) + shape)
    return r, ep.ch_names, ep.times
