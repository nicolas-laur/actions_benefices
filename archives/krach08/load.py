"""Charge CAC 40 et S&P 500 quotidiens (paquet CRAN smqf, source Yahoo, jusqu'au 31/12/2015) -> csv"""
import rdata, pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
def load(path):
    p = rdata.parser.parse_file(path); v = p.object.value[0]
    x = v.attributes; idx = None
    while x is not None and x.value:
        if x.tag is not None and getattr(x.tag.value, 'value', None) == b'index': idx = x.value[0].value
        x = x.value[1] if len(x.value) > 1 else None
    d = pd.to_datetime(idx, unit='s').normalize()
    return pd.Series(np.asarray(v.value).ravel(), index=d)
for f, n in (('CAC', 'cac'), ('SP500', 'spx')):
    s = load(f'/tmp/k08/dl/{f}.rda'); s.to_csv(f'/home/claude/krach08/{n}.csv', header=['close']); print(n, s.index[0].date(), s.index[-1].date(), len(s))
