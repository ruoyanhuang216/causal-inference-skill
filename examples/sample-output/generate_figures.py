"""
Generate publication-quality PDF figures for the causal inference sample output.
Minimum wage → restaurant employment (staggered DiD example).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import os

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': False,
    'pdf.fonttype': 42,  # TrueType fonts in PDF
    'ps.fonttype': 42,
})

OUTDIR = os.path.dirname(os.path.abspath(__file__)) + '/figures'
os.makedirs(OUTDIR, exist_ok=True)

# Color palette
C_BLUE = '#2563EB'
C_BLUE_LIGHT = '#93C5FD'
C_GRAY = '#9CA3AF'
C_GRAY_DARK = '#6B7280'
C_RED = '#DC2626'
C_RED_LIGHT = '#FCA5A5'
C_GREEN = '#059669'
C_ORANGE = '#F59E0B'
C_BG = '#FAFBFC'


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Event Study
# ══════════════════════════════════════════════════════════════════════════════
def fig1_event_study():
    quarters = np.arange(-8, 13)  # 21 values: -8 to 12
    # Pre-treatment (quarters -8 to -1): 8 values, near zero
    pre_coefs = [0.0012, -0.0005, 0.0018, 0.0008, -0.0003, -0.0012, 0.0005, 0.0014]
    # Post-treatment (quarters 0 to 12): 13 values
    post_coefs = [-0.0045, -0.0078, -0.0112, -0.0138, -0.0151, -0.0147, -0.0155,
                  -0.0149, -0.0142, -0.0131, -0.0118, -0.0125, -0.0108]
    coefs = np.array(pre_coefs + post_coefs)

    # SEs
    pre_se = [0.0055, 0.0048, 0.0052, 0.0045, 0.0042, 0.0044, 0.0041, 0.0043]
    post_se = [0.0048, 0.0050, 0.0052, 0.0054, 0.0056, 0.0054, 0.0058,
               0.0060, 0.0062, 0.0065, 0.0068, 0.0070, 0.0072]
    se = np.array(pre_se + post_se)
    ci_lo = coefs - 1.96 * se
    ci_hi = coefs + 1.96 * se

    fig, ax = plt.subplots(figsize=(8, 4.5))

    # Treatment indicator (shaded region)
    ax.axvspan(-0.5, 12.5, color='#EFF6FF', alpha=0.6, zorder=0)

    # Zero line
    ax.axhline(0, color=C_GRAY, linewidth=0.8, linestyle='-', zorder=1)

    # Treatment line
    ax.axvline(-0.5, color=C_RED, linewidth=1.5, linestyle='--', zorder=2, alpha=0.8)

    # Pre-treatment
    pre_mask = quarters < 0
    ax.fill_between(quarters[pre_mask], ci_lo[pre_mask], ci_hi[pre_mask],
                    color=C_GRAY, alpha=0.15, zorder=2)
    ax.plot(quarters[pre_mask], coefs[pre_mask], 'o-', color=C_GRAY_DARK,
            markersize=5, linewidth=1.5, zorder=3)
    ax.vlines(quarters[pre_mask], ci_lo[pre_mask], ci_hi[pre_mask],
              color=C_GRAY_DARK, linewidth=0.8, zorder=2)

    # Post-treatment
    post_mask = quarters >= 0
    ax.fill_between(quarters[post_mask], ci_lo[post_mask], ci_hi[post_mask],
                    color=C_BLUE, alpha=0.12, zorder=2)
    ax.plot(quarters[post_mask], coefs[post_mask], 'o-', color=C_BLUE,
            markersize=5, linewidth=1.5, zorder=3)
    ax.vlines(quarters[post_mask], ci_lo[post_mask], ci_hi[post_mask],
              color=C_BLUE, linewidth=0.8, zorder=2)

    # Annotations
    ax.annotate('MW increase', xy=(-0.5, 0.025), fontsize=9, color=C_RED,
                fontweight='bold', ha='center')
    ax.annotate('Pre-trends: F = 0.87, p = 0.54', xy=(-5, -0.018),
                fontsize=8.5, color=C_GRAY_DARK, style='italic', ha='center')
    ax.annotate('ATT $\\approx$ −0.015', xy=(6, -0.020),
                fontsize=9, color=C_BLUE, fontweight='bold', ha='center')

    ax.set_xlabel('Quarters relative to MW increase')
    ax.set_ylabel('ATT (log restaurant employment)')
    ax.set_title('Event Study — Dynamic Treatment Effects')
    ax.set_xlim(-8.5, 12.5)
    ax.set_ylim(-0.030, 0.030)
    ax.set_xticks(np.arange(-8, 13, 2))

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color=C_GRAY_DARK, markersize=5, linewidth=1.5, label='Pre-treatment'),
        Line2D([0], [0], marker='o', color=C_BLUE, markersize=5, linewidth=1.5, label='Post-treatment'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True,
              fancybox=True, framealpha=0.9, edgecolor='#E5E7EB')

    fig.savefig(f'{OUTDIR}/fig1_event_study.pdf')
    fig.savefig(f'{OUTDIR}/fig1_event_study.png')
    plt.close(fig)
    print('  ✓ fig1_event_study')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Specification Curve
# ══════════════════════════════════════════════════════════════════════════════
def fig2_specification_curve():
    np.random.seed(42)
    n_specs = 48

    # Generate 48 estimates in [-0.0203, -0.0071], sorted
    estimates = np.sort(np.random.uniform(-0.0203, -0.0071, n_specs))
    ses = np.random.uniform(0.0040, 0.0078, n_specs)

    # Determine significance: 42 of 48 significant
    pvals = 2 * (1 - _norm_cdf(np.abs(estimates / ses)))
    significant = pvals < 0.05

    # Force exactly 42 significant (sort p-values, mark top 6 as non-significant)
    sig_order = np.argsort(pvals)
    significant[:] = True
    for idx in sig_order[-6:]:
        significant[idx] = False

    # Mark preferred specification (CS, log, DR, state cluster)
    preferred_idx = np.argmin(np.abs(estimates - (-0.0147)))

    ci_lo = estimates - 1.96 * ses
    ci_hi = estimates + 1.96 * ses

    fig, ax = plt.subplots(figsize=(9, 4.5))

    # Zero reference line
    ax.axhline(0, color=C_GRAY, linewidth=0.8, linestyle='-', alpha=0.4)

    # Shade the range of estimates
    ax.axhspan(estimates.min(), estimates.max(), color=C_BLUE, alpha=0.04, zorder=0)

    for i in range(n_specs):
        c = C_BLUE if significant[i] else C_GRAY
        alpha = 1.0 if significant[i] else 0.45
        ax.vlines(i, ci_lo[i], ci_hi[i], color=c, linewidth=0.8, alpha=alpha * 0.4)

        if i == preferred_idx:
            ax.plot(i, estimates[i], 'o', color=C_RED, markersize=8, zorder=5)
        else:
            ax.plot(i, estimates[i], 'o', color=c, markersize=4, alpha=alpha, zorder=4)

    # Annotation for preferred spec — place it in upper-left to avoid the zero line
    ax.annotate('Preferred spec.\n(CS, log, DR, state cluster)',
                xy=(preferred_idx, estimates[preferred_idx]),
                xytext=(5, -0.004),
                fontsize=8.5, color=C_RED, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.2))

    ax.set_ylabel('Estimate (ATT)')
    ax.set_xlabel('Specification (sorted by estimate)')
    ax.set_title('Specification Curve — 48 Specifications')
    ax.set_xlim(-1, n_specs)

    # Summary box — top-right
    ax.text(0.98, 0.97,
            '42/48 significant (88%)\nRange: [\u22120.020, \u22120.007]\nAll 48 negative',
            transform=ax.transAxes, fontsize=9, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#E5E7EB', alpha=0.9))

    fig.savefig(f'{OUTDIR}/fig2_specification_curve.pdf')
    fig.savefig(f'{OUTDIR}/fig2_specification_curve.png')
    plt.close(fig)
    print('  ✓ fig2_specification_curve')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Sensitivity Contour (Cinelli & Hazlett)
# ══════════════════════════════════════════════════════════════════════════════
def fig3_sensitivity_contour():
    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    # The contour: combinations of partial R2 with treatment and outcome
    # that would reduce estimate to zero. For a hyperbolic-ish curve:
    # R2_Y * R2_D >= threshold (approximately)
    r2d = np.linspace(0, 0.20, 300)
    # RV = 0.089 means the curve passes through (0.089, 0.089)
    # Use: r2y = (0.089^2) / r2d as a rough approximation, capped
    rv = 0.089
    # More accurate: the bias-zero contour is roughly r2y = k / (1 - r2d) where
    # k is calibrated so that the curve passes through (rv, rv)
    k = rv * rv / (1 - rv)  # ≈ 0.0087
    r2y_contour = k / (np.maximum(r2d, 0.001) * (1 - r2d))
    r2y_contour = np.clip(r2y_contour, 0, 0.25)

    # Fill regions
    # Robust region: below and left of the contour
    ax.fill_between(r2d, 0, np.minimum(r2y_contour, 0.22),
                    color='#D1FAE5', alpha=0.35, zorder=0)
    # Null region: above the contour
    ax.fill_between(r2d, np.minimum(r2y_contour, 0.22), 0.22,
                    color='#FEE2E2', alpha=0.35, zorder=0)

    # Contour line
    mask = r2y_contour <= 0.22
    ax.plot(r2d[mask], r2y_contour[mask], '--', color=C_RED, linewidth=2.5, zorder=3,
            label='Estimate = 0 contour')

    # Benchmark points
    benchmarks = [
        (0.023, 0.041, 'GDP growth'),
        (0.010, 0.020, 'Pop. density'),
    ]
    for bx, by, label in benchmarks:
        ax.plot(bx, by, 'o', color='#1F2937', markersize=9, zorder=4)
        ax.annotate(label, xy=(bx, by), xytext=(bx + 0.012, by + 0.005),
                    fontsize=9, fontweight='bold', color='#1F2937',
                    arrowprops=dict(arrowstyle='->', color='#6B7280', lw=1))

    # Region labels
    ax.text(0.03, 0.01, 'ROBUST REGION', fontsize=10, fontweight='bold',
            color=C_GREEN, alpha=0.8)
    ax.text(0.12, 0.19, 'NULL REGION', fontsize=10, fontweight='bold',
            color=C_RED, alpha=0.8)

    # RV marker
    ax.plot(rv, rv, 'D', color=C_ORANGE, markersize=8, zorder=5)
    ax.annotate(f'RV = {rv}', xy=(rv, rv), xytext=(rv + 0.015, rv - 0.015),
                fontsize=9, color=C_ORANGE, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=C_ORANGE, lw=1))

    # Summary box
    summary = "Oster's δ = 2.34\nRobustness Value = 0.089\nMax observed partial R² = 0.041"
    ax.text(0.98, 0.02, summary, transform=ax.transAxes, fontsize=8.5,
            va='bottom', ha='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#E5E7EB', alpha=0.95))

    ax.set_xlabel('Partial R² of confounder with Treatment')
    ax.set_ylabel('Partial R² of confounder with Outcome')
    ax.set_title('Sensitivity Contour (Cinelli & Hazlett 2020)')
    ax.set_xlim(0, 0.20)
    ax.set_ylim(0, 0.22)

    fig.savefig(f'{OUTDIR}/fig3_sensitivity_contour.pdf')
    fig.savefig(f'{OUTDIR}/fig3_sensitivity_contour.png')
    plt.close(fig)
    print('  ✓ fig3_sensitivity_contour')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Placebo Tests (two panels)
# ══════════════════════════════════════════════════════════════════════════════
def fig4_placebo_tests():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={'wspace': 0.40})

    # ── Left panel: Placebo outcomes ──
    outcomes = ['Restaurant emp.\n(real)', 'Mining emp.', 'Finance emp.', 'Government emp.']
    estimates = [-0.0147, 0.0023, -0.0011, 0.0008]
    ses = [0.0054, 0.0062, 0.0054, 0.0061]
    ci_lo = [e - 1.96 * s for e, s in zip(estimates, ses)]
    ci_hi = [e + 1.96 * s for e, s in zip(estimates, ses)]
    is_real = [True, False, False, False]
    pvals = [0.007, 0.71, 0.84, 0.92]

    y_pos = np.arange(len(outcomes))
    for i, (est, lo, hi, real) in enumerate(zip(estimates, ci_lo, ci_hi, is_real)):
        c = C_RED if real else C_BLUE
        alpha = 1.0 if real else 0.6
        ax1.barh(i, est, height=0.5, color=c, alpha=alpha * 0.3, edgecolor=c, linewidth=1.2)
        ax1.plot([lo, hi], [i, i], '-', color=c, linewidth=2, alpha=alpha)
        ax1.plot(est, i, 'o', color=c, markersize=7, zorder=5)
        # p-value annotation
        star = '***' if pvals[i] < 0.01 else ('**' if pvals[i] < 0.05 else '')
        ax1.text(max(hi, 0) + 0.001, i, f'{est:.4f}{star}',
                 va='center', fontsize=8.5, color=c, fontweight='bold' if real else 'normal')

    ax1.axvline(0, color=C_GRAY, linewidth=0.8, linestyle='-')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(outcomes, fontsize=9)
    ax1.set_xlabel('Estimate (ATT)')
    ax1.set_title('Placebo Outcomes', fontsize=12)
    ax1.invert_yaxis()

    # ── Right panel: Placebo timing ──
    shifts = [-6, -4, -2, 0]
    shift_labels = ['t − 6', 't − 4', 't − 2', 't = 0\n(actual)']
    timing_est = [-0.0014, 0.0031, -0.0019, -0.0147]
    timing_se = [0.0058, 0.0060, 0.0055, 0.0054]
    timing_lo = [e - 1.96 * s for e, s in zip(timing_est, timing_se)]
    timing_hi = [e + 1.96 * s for e, s in zip(timing_est, timing_se)]
    timing_pvals = [0.81, 0.58, 0.73, 0.007]

    y_pos2 = np.arange(len(shifts))
    for i, (est, lo, hi) in enumerate(zip(timing_est, timing_lo, timing_hi)):
        is_actual = (shifts[i] == 0)
        c = C_RED if is_actual else C_BLUE
        alpha = 1.0 if is_actual else 0.6
        ax2.barh(i, est, height=0.5, color=c, alpha=alpha * 0.3, edgecolor=c, linewidth=1.2)
        ax2.plot([lo, hi], [i, i], '-', color=c, linewidth=2, alpha=alpha)
        ax2.plot(est, i, 'o', color=c, markersize=7, zorder=5)
        star = '***' if timing_pvals[i] < 0.01 else ('**' if timing_pvals[i] < 0.05 else '')
        xtext = max(hi, 0) + 0.001
        ax2.text(xtext, i, f'{est:.4f}{star}',
                 va='center', fontsize=8.5, color=c, fontweight='bold' if is_actual else 'normal')

    ax2.axvline(0, color=C_GRAY, linewidth=0.8, linestyle='-')
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(shift_labels, fontsize=9)
    ax2.set_xlabel('Estimate (ATT)')
    ax2.set_title('Placebo Timing', fontsize=12)
    ax2.invert_yaxis()

    # Shared note
    fig.text(0.5, -0.02, 'All 6 placebo tests pass — no spurious effects detected',
             ha='center', fontsize=9, style='italic', color=C_GRAY_DARK)

    fig.savefig(f'{OUTDIR}/fig4_placebo_tests.pdf')
    fig.savefig(f'{OUTDIR}/fig4_placebo_tests.png')
    plt.close(fig)
    print('  ✓ fig4_placebo_tests')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Cross-Method Forest Plot
# ══════════════════════════════════════════════════════════════════════════════
def fig5_cross_method_forest():
    methods = [
        'Callaway & Sant\'Anna',
        'Sun & Abraham',
        'TWFE',
        'Synthetic DiD',
        'OLS + controls',
    ]
    estimates = [-0.0147, -0.0139, -0.0098, -0.0161, -0.0089]
    ses =       [0.0054,  0.0058,  0.0047,  0.0067,  0.0043]
    ci_lo = [e - 1.96 * s for e, s in zip(estimates, ses)]
    ci_hi = [e + 1.96 * s for e, s in zip(estimates, ses)]
    is_primary = [True, False, False, False, False]

    fig, ax = plt.subplots(figsize=(7.5, 3.8))

    y_pos = np.arange(len(methods))

    # Zero line
    ax.axvline(0, color=C_GRAY, linewidth=0.8, linestyle='--')

    # Pooled estimate band
    ax.axvspan(-0.0165, -0.0085, color=C_BLUE, alpha=0.06, zorder=0)

    for i, (est, lo, hi, primary) in enumerate(zip(estimates, ci_lo, ci_hi, is_primary)):
        # Gradient: primary method is darkest
        if primary:
            c = C_BLUE
            ms = 10
            lw = 2.5
            fw = 'bold'
        else:
            shade = 0.4 + 0.15 * i
            c = C_BLUE
            ms = 7
            lw = 1.8
            fw = 'normal'

        alpha = 1.0 if primary else 0.55 + 0.1 * (len(methods) - i) / len(methods)

        # CI line
        ax.plot([lo, hi], [i, i], '-', color=c, linewidth=lw, alpha=alpha, solid_capstyle='round')
        # Point estimate
        ax.plot(est, i, 'o', color=c, markersize=ms, zorder=5, alpha=alpha)

        # Estimate + SE text on right
        ax.text(0.018, i, f'{est:.4f} ({ses[i]:.4f})',
                va='center', fontsize=9.5, fontweight=fw, color='#374151')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(methods, fontsize=10)
    ax.set_xlabel('Estimate (ATT)')
    ax.set_title('Cross-Method Comparison — Forest Plot\n', fontsize=13, fontweight='bold')
    # Subtitle with summary
    ax.text(0.5, 1.01, 'All 5 methods: negative, statistically significant',
            transform=ax.transAxes, fontsize=9.5, va='bottom', ha='center',
            color=C_GREEN, fontweight='bold')
    ax.set_xlim(-0.035, 0.025)
    ax.invert_yaxis()

    fig.savefig(f'{OUTDIR}/fig5_cross_method_forest.pdf')
    fig.savefig(f'{OUTDIR}/fig5_cross_method_forest.png')
    plt.close(fig)
    print('  ✓ fig5_cross_method_forest')


# ── Helper: approximate normal CDF (avoid scipy dependency) ──────────────────
def _norm_cdf(x):
    """Approximate standard normal CDF using error function approximation."""
    return 0.5 * (1 + _erf(x / np.sqrt(2)))

def _erf(x):
    """Abramowitz & Stegun approximation for erf."""
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = np.sign(x)
    x = np.abs(x)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
    return sign * y


# ══════════════════════════════════════════════════════════════════════════════
# Generate all
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Generating figures...')
    fig1_event_study()
    fig2_specification_curve()
    fig3_sensitivity_contour()
    fig4_placebo_tests()
    fig5_cross_method_forest()
    print(f'\nAll figures saved to {OUTDIR}/')
