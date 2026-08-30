"""
Step 5 -- theoretical figures (Figures 1-4 of the paper).

Input   none (the theoretical figures are pure simulations of the model)
Output  output/figures/fig1_threshold_known_costs_homogeneous.png
        output/figures/fig2_threshold_known_costs_heterogeneous.png
        output/figures/fig3_threshold_uncertain_varying_z.png
        output/figures/fig4_threshold_uncertain_varying_alpha.png

The figures are deterministic: they evaluate closed-form expressions on a
100-point grid p in [0, 1].  No random numbers are drawn anywhere in the
theoretical part of the paper, so no seed is required.

Objects plotted
---------------
  q(p)      = C(n-1, k-1) p^(k-1) (1-p)^(n-k)          known threshold k
  omega(p)  = F_theta(p(n-1) + 1) - F_theta(p(n-1))    uncertain threshold,
                                                        theta ~ N(z, alpha^2)
  G^{-1}(p)                                             inverse cdf of the
                                                        cost distribution

An interior equilibrium is a crossing of G^{-1}(p) with q(p) (Figure 2) or
with omega(p) (Figures 3 and 4).

"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import comb
from scipy.stats import norm, uniform

from config import FIGURES

P = np.linspace(0, 1, 100)
CYCLE = plt.rcParams["axes.prop_cycle"].by_key()["color"]

# Use every third color for each family of dashed lines.
IDX = lambda i, j: CYCLE[i * 3 + j]


def q(p, n, k):
    """Probability that exactly k-1 of the other n-1 agents contribute."""
    return comb(n - 1, k - 1) * p ** (k - 1) * (1 - p) ** (n - k)


def omega(p, n, z, alpha):
    """F_theta(p(n-1)+1) - F_theta(p(n-1)) for theta ~ N(z, alpha^2)."""
    return (norm.cdf((n - 1) * p + 1, loc=z, scale=alpha)
            - norm.cdf((n - 1) * p, loc=z, scale=alpha))


def inv_norm(p, mu, sigma):
    return norm.ppf(p, loc=mu, scale=sigma)


def inv_unif(p, a, b):
    return uniform.ppf(p, loc=a, scale=b - a)


def inv_expon(p, lam):
    with np.errstate(divide="ignore"):
        return -np.log(1 - p) / lam


# --------------------------------------------------------------------------
# Figure 1 -- q(p) for a known threshold, varying k (left) and n (right)
# --------------------------------------------------------------------------
def figure1() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for k in [5, 10, 15, 20, 25]:
        axes[0].plot(P, q(P, 30, k), label=f"$k = {k}$")
    axes[0].set_ylabel(r"$C_{29}^{k-1} p^{k-1} (1-p)^{30-k}$", fontsize=14)

    for n in [30, 40, 50, 60, 100]:
        axes[1].plot(P, q(P, n, 25), label=f"$n = {n}$")
    axes[1].set_ylabel(r"$C_{n-1}^{25-1} p^{25-1} (1-p)^{n-25}$", fontsize=14)

    for ax in axes:
        ax.set_xlabel("$p$", fontsize=15)
        ax.set_ylim(0, 0.25)
        ax.grid(True)
        ax.legend(fontsize=13)
        ax.tick_params(labelsize=12)

    fig.tight_layout()
    fig.savefig(FIGURES / "fig1_threshold_known_costs_homogeneous.png",
                dpi=100, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# shared styling for the three-panel figures
# --------------------------------------------------------------------------
def _style(ax, title, ylim, legend_loc):
    ax.set_xlabel("$p$", fontsize=24)
    ax.set_title(title, fontsize=28)
    ax.set_ylim(0, ylim)
    ax.tick_params(labelsize=20)
    ax.grid(True)
    ax.legend(fontsize=18.5, loc=legend_loc)


def _panels(solid, ylim, fname, figsize=(28, 11)):
    """Build the Normal / Uniform / Exponential three-panel layout.

    ``solid`` is a list of (label, y) pairs drawn identically in all panels.
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)

    for ax in axes:
        for label, y in solid:
            ax.plot(P, y, label=label, linewidth=2.5)

    # Normal costs
    for i, mu in enumerate([0.05, 0.1, 0.15] if ylim == 0.25 else [0.1, 0.2, 0.3]):
        for j, sd in enumerate([0.05, 0.15]):
            axes[0].plot(P, inv_norm(P, mu, sd), "--", color=IDX(i, j), linewidth=2.5,
                         label=rf"$G^{{-1}}(p)$, $\mathcal{{N}}({mu}, {sd}^2)$")

    # Uniform costs
    for i, a in enumerate([0, 0.05] if ylim == 0.25 else [0, 0.15]):
        for j, b in enumerate([0.5, 1, 1.5]):
            axes[1].plot(P, inv_unif(P, a, b), "--", color=IDX(i, j), linewidth=2.5,
                         label=rf"$G^{{-1}}(p)$, $\mathcal{{U}}({a}, {b})$")

    # Exponential costs -- colours continue the default cycle after the solid lines
    lams = [0.5, 1.5, 2.5, 5, 10, 25] if ylim == 0.25 else [0.5, 1.5, 2.5, 5, 10]
    for lam in lams:
        axes[2].plot(P, inv_expon(P, lam), "--", linewidth=2.5,
                     label=rf"$G^{{-1}}(p)$, $EXP({lam})$")

    _style(axes[0], "Normal Distribution", ylim, "upper left")
    _style(axes[1], "Uniform Distribution", ylim, "upper right")
    _style(axes[2], "Exponential Distribution", ylim, "upper right")

    fig.tight_layout()
    fig.savefig(FIGURES / fname, dpi=100, bbox_inches="tight")
    plt.close(fig)


def figure2() -> None:
    solid = [(rf"$q(p)$, $k = {k}$", q(P, 30, k)) for k in [5, 10, 15, 20, 25]]
    _panels(solid, 0.40, "fig2_threshold_known_costs_heterogeneous.png")


def figure3() -> None:
    solid = [(rf"$\omega(p)$, $z = {z}$, $\alpha = 5$", omega(P, 30, z, 5))
             for z in [5, 15, 25]]
    _panels(solid, 0.25, "fig3_threshold_uncertain_varying_z.png")


def figure4() -> None:
    solid = [(rf"$\omega(p)$, $z = 15$, $\alpha = {a}$, n=30", omega(P, 30, 15, a))
             for a in [3.25, 5, 10, 15]]
    _panels(solid, 0.25, "fig4_threshold_uncertain_varying_alpha.png", figsize=(29, 11))


def main() -> None:
    figure1(); figure2(); figure3(); figure4()
    for f in sorted(FIGURES.glob("fig*.png")):
        print("wrote", f)


if __name__ == "__main__":
    main()
