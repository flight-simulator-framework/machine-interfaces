"""Entrance factory with an explicit absolute momentum-spread contract.

The historical ATF2LinacBTDRRFTrack.make_entrance_bunch passes its purported
MeV/c value directly to RF-Track sigma_pt (per mille). Keep that implementation
frozen for archived experiments; new experiments can use this corrected factory.
"""
import math


def momentum_rms_to_sigma_pt(sigma_p_mev_c, momentum_mev_c, mass_mev):
    """Linear small-spread conversion: 1000 sigma_E/P0 = 1000 sigma_p/E0."""
    if not all(math.isfinite(v) for v in (sigma_p_mev_c,momentum_mev_c,mass_mev)):
        raise ValueError('Finite beam parameters required')
    if sigma_p_mev_c<0 or momentum_mev_c<=0 or mass_mev<=0:
        raise ValueError('Nonnegative spread and positive momentum/mass required')
    return 1000.*sigma_p_mev_c/math.hypot(momentum_mev_c,mass_mev)


def make_entrance_bunch_absolute(machine,twiss,*,particles,charge_e=1e9):
    """Create the stated entrance distribution with sigma_p in MeV/c.

As with RF-Track's Twiss interface, the energy-to-momentum RMS conversion is
linear in the small energy spread. Direct phase-space input is preferable
when specifying a broad or non-Gaussian momentum distribution.
"""
    if particles<1 or charge_e<0:raise ValueError('Positive particle count and nonnegative charge required')
    import RF_Track as rft
    distribution=rft.Bunch6d_twiss()
    for name in ('alpha_x','alpha_y','mean_x','mean_xp','mean_y','mean_yp'):
        source=name if name.startswith('alpha') else name+('_mrad' if name.endswith('p') else '_mm')
        setattr(distribution,name,getattr(twiss,source))
    distribution.emitt_x=twiss.emitt_x_norm_mm_mrad;distribution.emitt_y=twiss.emitt_y_norm_mm_mrad
    distribution.beta_x=twiss.beta_x_m;distribution.beta_y=twiss.beta_y_m
    distribution.sigma_t=twiss.sigma_t_mm_c
    distribution.sigma_pt=momentum_rms_to_sigma_pt(twiss.sigma_p_mev_c,machine.input_momentum_mev_c,rft.electronmass)
    return rft.Bunch6d_QR(rft.electronmass,charge_e,-1.,machine.input_momentum_mev_c,distribution,particles)
