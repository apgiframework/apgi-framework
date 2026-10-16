import numpy as np
P = dict(tau0=15.0, rho=0.9, Pi=1.0, theta=1.0, G=1.0, M=3.0, Ms=0.2, A=1.5, k=30.0, tauS=300.0, T=600.0, dt=0.25,
         tgt=50.0, msk=50.0)

def sim(isi, **kw):
    p = dict(P); p.update(kw)
    dt = p['dt']; t = np.arange(0, p['T'], dt)
    tau_r = p['tau0'] / (1 - p['rho'])
    gain = 1.0 / (1 - p['rho'])            # reservoir amplification of a sustained input
    m0 = p['tgt'] + isi; m1 = m0 + p['msk']
    r = np.zeros_like(t); S = np.zeros_like(t)
    for i in range(1, len(t)):
        ti = t[i - 1]
        I = p['Pi'] if ti < p['tgt'] else 0.0
        mask = p['M'] if (m0 <= ti < m1) else 0.0
        dr = (-r[i - 1] + I * (1 - p['rho']) * gain - mask * r[i - 1]) / tau_r
        r[i] = r[i - 1] + dt * dr
        drive = p['G'] * r[i - 1] * 0.05 * p['tauS']
        sig = 1 / (1 + np.exp(-p['k'] * (S[i - 1] - p['theta'])))
        dS = (-S[i - 1] + drive + p['A'] * sig * p['theta']) / p['tauS'] - (p['Ms'] * S[i-1] * (1 - sig) if mask else 0.0)
        S[i] = S[i - 1] + dt * dS
    return t, S, r

def ignited(isi, **kw):
    t, S, r = sim(isi, **kw)
    p = dict(P); p.update(kw)
    return S[-1] > p['theta']

def crit_isi(lo=0.0, hi=600.0, **kw):
    if ignited(lo, **kw):
        return lo
    if not ignited(hi, **kw):
        return np.nan
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if ignited(mid, **kw): hi = mid
        else: lo = mid
    return hi

if __name__ == '__main__':
    print('ref crit', crit_isi())
    for rho in (0.7, 0.8, 0.9, 0.95):
        print('rho', rho, crit_isi(rho=rho))
    for Pi in (0.8, 1.2):
        print('Pi', Pi, crit_isi(Pi=Pi))
    for th in (0.9, 1.1):
        print('theta', th, crit_isi(theta=th))
