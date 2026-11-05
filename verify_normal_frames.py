#!/usr/bin/env python3
"""Reproduce exact algebra and sanity examples in the normal-frame manuscript.

Run: python research_bundle/normal_frames/verify_normal_frames.py

Only the Python standard library is required. Fraction arithmetic verifies the
original Gramian series calculation exactly. Composite Simpson integration
provides independent numerical checks of the displayed finite examples. These
checks neither verify the abstract proof nor prove infinite-dimensional limits.
"""

import argparse
import cmath
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys

class VerificationError(RuntimeError):
    """Scientific check failure, including under Python optimisation."""


def require(condition, context):
    if not condition:
        raise VerificationError(str(context))


def multiply_series(left, right, degree):
    return [sum((left[j] * right[k - j] for j in range(k + 1)), F(0))
            for k in range(degree + 1)]


def simpson(function, endpoint, panels=4096):
    """Composite Simpson rule, independent of the closed integral formulas."""
    require(isinstance(panels, int) and panels > 0 and panels % 2 == 0, 'Simpson panels must be a positive even integer')
    step = endpoint / panels
    odd = math.fsum(function(k * step) for k in range(1, panels, 2))
    even = math.fsum(function(k * step) for k in range(2, panels, 2))
    return (step / 3) * (function(0.0) + function(endpoint) + 4 * odd + 2 * even)


def require_close(actual, expected, tolerance=2e-11):
    error = abs(actual - expected)
    require(error <= tolerance * max(1.0, abs(expected)), ('numerical agreement', actual, expected, error))
    return error


def exact_gramian_series():
    degree = 8
    one = [F(int(k == 0)) for k in range(degree + 1)]
    first = [F(int(k == 1)) for k in range(degree + 1)]
    exp_minus_t = [F((-1) ** k, math.factorial(k)) for k in range(degree + 1)]
    exp_minus_2t = [F((-2) ** k, math.factorial(k)) for k in range(degree + 1)]
    cross = [a - b for a, b in zip(one, exp_minus_t)]
    second = [(a - b) / 2 for a, b in zip(one, exp_minus_2t)]
    product = multiply_series(first, second, degree)
    square = multiply_series(cross, cross, degree)
    determinant = [a - b for a, b in zip(product, square)]
    trace = [a + b for a, b in zip(first, second)]
    require(determinant[:4] == [F(0)] * 4, 'determinant vanishing coefficients')
    require(determinant[4] == F(1, 12), 'determinant leading coefficient')
    require(determinant[5] == F(-1, 12), 'determinant fifth coefficient')
    require(trace[0] == 0 and trace[1] == 2, 'trace leading coefficients')
    small_eigenvalue_leading = determinant[4] / trace[1]
    require(small_eigenvalue_leading == F(1, 24), 'small eigenvalue leading coefficient')
    return {
        "kind": "exact Fraction arithmetic",
        "reference": "Section 6.3, equations (6.2)-(6.3)",
        "determinant_coefficients_T_power": {
            str(k): str(determinant[k]) for k in range(4, degree + 1)},
        "trace_leading_coefficient_T": str(trace[1]),
        "lambda_min_leading_coefficient_T_cubed": str(small_eigenvalue_leading),
        "reason_for_eigenvalue_coefficient":
            "det/trace^2 tends to zero; the larger eigenvalue is asymptotic to trace, "
            "so the smaller eigenvalue is asymptotic to det/trace.",
        "scope": "Exact Taylor coefficients of this 2-by-2 Gramian, not a general lower frame bound.",
    }


def gramian_quadrature():
    errors = []
    for duration in (0.125, 0.6, 1.0):
        closed = (duration, -math.expm1(-duration), -math.expm1(-2 * duration) / 2)
        integrated = tuple(simpson(lambda t, r=rate: math.exp(-r * t), duration)
                           for rate in (0, 1, 2))
        errors.extend(require_close(a, b) for a, b in zip(integrated, closed))
        require(closed[0] * closed[2] - closed[1] ** 2 > 0, ('Gramian positivity', duration))
    return {
        "kind": "floating-point integration sanity check",
        "reference": "Section 6.3, equation (6.2)",
        "durations": [0.125, 0.6, 1.0],
        "scalar_integrals_checked": 9,
        "max_absolute_error": max(errors),
        "comparison_tolerance": "2e-11 * max(1, abs(closed_form))",
        "scope": "Three finite observation windows; positivity for every T is proved in the manuscript.",
    }


def scalar_orthonormal_sensors():
    vector = (1 + 0j, -0.5 + 0.25j, 0.75j, -0.125 + 0j)
    norm_squared = math.fsum(abs(x) ** 2 for x in vector)
    duration = 0.6
    cases = ((0.0, 0.0), (0.0, -math.pi), (0.0, math.pi / 2),
             (-2.0, 0.4), (0.3, -0.7))
    errors = []
    for log_radius, argument in cases:
        def energy(t):
            evolution = cmath.exp(t * complex(log_radius, argument))
            return math.fsum(abs(evolution * x) ** 2 for x in vector)
        coefficient = (duration if log_radius == 0 else
                       math.expm1(2 * log_radius * duration) / (2 * log_radius))
        errors.append(require_close(simpson(energy, duration), coefficient * norm_squared))
    return {
        "kind": "floating-point integration sanity check",
        "reference": "Identity/unitary orthonormal observations; Section 6.5",
        "operator": "A=cI with orthonormal sensors",
        "cases_log_modulus_and_argument": cases,
        "duration": duration,
        "formula": "Q_T(x)=T||x||^2 when |c|=1; otherwise "
                   "Q_T(x)=expm1(2T log|c|)/(2 log|c|) * ||x||^2",
        "max_absolute_error": max(errors),
        "scope": "Four coordinates and five scalar operators; Parseval gives the infinite-basis formula.",
    }


def diagonal_finite_energy():
    vector = (1 + 0j, -0.5 + 0.25j, 0.75j, -0.125 + 0j)
    duration = 0.37
    def energy(t):
        return math.fsum(2 * n * math.exp(-2 * n * t) * abs(x) ** 2
                         for n, x in enumerate(vector, 1))
    closed = math.fsum(-math.expm1(-2 * n * duration) * abs(x) ** 2
                      for n, x in enumerate(vector, 1))
    error = require_close(simpson(energy, duration), closed)
    indices = (1, 2, 4, 8, 16, 64)
    lower_bound = -math.expm1(-2 * duration)
    coefficients = [-math.expm1(-2 * n * duration) for n in indices]
    require(all(lower_bound <= value <= 1.0 for value in coefficients), 'diagonal coefficient bounds')
    require(coefficients[0] == lower_bound, 'diagonal optimal lower bound')
    return {
        "kind": "floating-point integration and sampled coefficient checks",
        "reference": "Section 6.1, equation (6.1)",
        "operator_and_sensors": "A e_n=exp(-n)e_n; g_n=sqrt(2n)e_n",
        "duration": duration,
        "max_absolute_quadrature_error": error,
        "sample_indices": indices,
        "sample_coefficients": coefficients,
        "exact_sensor_squared_norms": [2 * n for n in indices],
        "analytic_bounds": "1-exp(-2T) <= 1-exp(-2nT) < 1 for n>=1",
        "scope": "Finite integration check and finite samples only; monotonicity and the limit "
                 "n->infinity establish the infinite-family optimal bounds analytically. "
                 "Rounded coefficients may equal 1 even though the exact coefficient is below 1.",
    }


def negative_axis_branch():
    duration = 0.5
    power = cmath.exp(-1j * math.pi * duration)
    adjoint_then_power = power  # A*=A=-I, with the same argument -pi.
    power_then_adjoint = power.conjugate()
    conjugate_log_evolution = cmath.exp(1j * math.pi * duration)
    require_close(power, -1j, 1e-14)
    require_close(power_then_adjoint, 1j, 1e-14)
    require_close(conjugate_log_evolution, power_then_adjoint, 1e-14)
    require_close(abs(adjoint_then_power - power_then_adjoint), 2.0, 1e-14)
    return {
        "kind": "floating-point complex-exponential sanity check",
        "reference": "Section 3, branch-convention example",
        "argument_at_minus_one": "-pi",
        "time": duration,
        "expected_adjoint_then_power": "-iI",
        "expected_power_then_adjoint": "+iI",
        "difference_norm": abs(adjoint_then_power - power_then_adjoint),
        "conjugate_log_evolution_matches_power_then_adjoint": True,
        "scope": "The scalar branch counterexample only; no operator functional-calculus test.",
    }


def delayed_coefficients():
    start, end = 0.25, 0.75
    indices = (1, 2, 4, 8, 16, 32, 64, 128)
    values = [math.exp(-2 * n * start) * -math.expm1(-2 * n * (end - start))
              for n in indices]
    for n, value in zip(indices, values):
        require(0 <= value <= math.exp(-2 * n * start), ('delayed coefficient bound', n))
    error = require_close(
        simpson(lambda s: 6 * math.exp(-6 * (start + s)), end - start),
        math.exp(-6 * start) - math.exp(-6 * end))
    return {
        "kind": "floating-point integration and sampled coefficient checks",
        "reference": "Section 6.4, equation (6.4)",
        "interval": [start, end],
        "sample_indices": indices,
        "sample_coefficients": values,
        "n_3_quadrature_absolute_error": error,
        "analytic_limit_argument": "0 <= c_n=exp(-2na)-exp(-2nb) <= exp(-2na)->0 for a>0. "
                                   "Testing on e_n therefore rules out a positive lower bound.",
        "scope": "Finite samples check the formula and inequality; the displayed exponential bound proves the limit.",
    }


def infinite_window_coefficients():
    duration = F(3, 5)
    indices = (1, 2, 10, 100, 1000, 1000000)
    finite = []
    infinite = []
    for n in indices:
        rate = F(1, n)
        sensor_squared = F(2, n)
        infinite_coefficient = sensor_squared / (2 * rate)
        require(infinite_coefficient == 1, ('infinite coefficient', n))
        infinite.append(str(infinite_coefficient))
        coefficient = -math.expm1(-float(2 * duration / n))
        require(0 < coefficient <= float(2 * duration / n), ('finite coefficient bound', n))
        finite.append(coefficient)
    identity_times = (F(1), F(2), F(4), F(8))
    identity_energies = [t * F(7, 3) for t in identity_times]
    require(all(b > a for a, b in zip(identity_energies, identity_energies[1:])), 'identity energy monotonicity')
    return {
        "kind": "exact rational infinite-integral coefficients and sampled finite coefficients",
        "reference": "Section 6.5, both finite/infinite-window counterexamples",
        "operator_and_sensors": "A e_n=exp(-1/n)e_n; g_n=sqrt(2/n)e_n",
        "duration": str(duration),
        "sample_indices": indices,
        "exact_infinite_coefficients": infinite,
        "sample_finite_coefficients": finite,
        "analytic_limit_argument": "c_n(T)=1-exp(-2T/n) <= 2T/n -> 0. The infinite-time "
                                   "coefficient is (2/n)/(2/n)=1 for every n.",
        "identity_times": [str(t) for t in identity_times],
        "exact_identity_energies_for_norm_squared_7_over_3": [str(q) for q in identity_energies],
        "identity_infinite_failure": "For A=I and orthonormal sensors, Q_T=T||x||^2 diverges as T->infinity when x!=0.",
        "scope": "Exact rational checks concern the displayed scalar coefficients. No finite truncation "
                 "can establish an infinite-dimensional frame inequality; the stated analytic formulas do that work.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("verification_results.json"))
    args = parser.parse_args()
    tests = (exact_gramian_series, gramian_quadrature, scalar_orthonormal_sensors,
             diagonal_finite_energy, negative_axis_branch, delayed_coefficients,
             infinite_window_coefficients)
    checks = []
    for test in tests:
        try:
            checks.append({"name": test.__name__, "passed": True, **test()})
        except Exception as error:
            checks.append({"name": test.__name__, "passed": False,
                           "error": f"{type(error).__name__}: {error}"})
    report = {
        "schema_version": 1,
        "manuscript": "Finite observation windows for continuous powers of normal operators, 1 November 2026",
        "python_version": sys.version.split()[0],
        "dependencies": "Python standard library only",
        "all_passed": all(check["passed"] for check in checks),
        "checks": checks,
        "limitations": [
            "These are explicit-example and algebra checks, not verification of the abstract theorem or its novelty.",
            "Fraction coefficients are exact. Simpson integrations and complex exponentials use binary floating point.",
            "The integration tolerance is an empirical comparison threshold, not a certified quadrature error bound.",
            "Infinite-dimensional assertions require the analytic formulas and limiting arguments stated in the manuscript.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_passed": report["all_passed"], "checks": len(checks),
                      "output": str(args.output)}, ensure_ascii=False))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
