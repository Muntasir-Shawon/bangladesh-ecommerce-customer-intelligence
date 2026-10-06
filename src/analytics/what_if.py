"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/analytics/what_if.py
Purpose: Prescriptive analytics simulation engine modeling the financial
         and operational impact of 4 strategic business scenarios.
"""

import pandas as pd
from typing import Dict, Any


def run_prescriptive_simulations(
    baseline_revenue: float,
    baseline_profit: float,
    baseline_orders: int,
    baseline_customers: int,
    baseline_discount: float,
    repeat_customers: int,
    annual_churn_rate: float
) -> Dict[str, Any]:
    """
    Simulates top management strategic decisions:
    Scenario 1: Repeat purchase frequency increases by +10%
    Scenario 2: Annual churn rate decreases by -5% (retention uplift)
    Scenario 3: Average Order Value (AOV) increases by +10% (cross-selling/upselling)
    Scenario 4: Blanket discount spending is optimized/reduced by -15%
    """
    current_aov = baseline_revenue / baseline_orders
    gross_margin_pct = baseline_profit / baseline_revenue

    # ----------------------------------------------------
    # SCENARIO 1: +10% Repeat Purchase Frequency
    # ----------------------------------------------------
    # Additional orders = repeat_customers * (current_orders_per_repeat * 0.10)
    avg_repeat_orders = (baseline_orders - (baseline_customers - repeat_customers)) / repeat_customers
    additional_orders_s1 = int(repeat_customers * avg_repeat_orders * 0.10)
    incremental_rev_s1 = round(additional_orders_s1 * current_aov, 2)
    incremental_profit_s1 = round(incremental_rev_s1 * gross_margin_pct, 2)

    # ----------------------------------------------------
    # SCENARIO 2: -5% Customer Churn Reduction
    # ----------------------------------------------------
    # 5% relative reduction in churned customers saved
    saved_customers = int(baseline_customers * annual_churn_rate * 0.05)
    avg_annual_rev_per_cust = baseline_revenue / baseline_customers
    incremental_rev_s2 = round(saved_customers * avg_annual_rev_per_cust, 2)
    incremental_profit_s2 = round(incremental_rev_s2 * gross_margin_pct, 2)

    # ----------------------------------------------------
    # SCENARIO 3: +10% Average Order Value (AOV)
    # ----------------------------------------------------
    new_aov = current_aov * 1.10
    new_rev_s3 = round(baseline_orders * new_aov, 2)
    incremental_rev_s3 = round(new_rev_s3 - baseline_revenue, 2)
    # Variable cost remains roughly proportional, profit increases by margin
    incremental_profit_s3 = round(incremental_rev_s3 * gross_margin_pct, 2)

    # ----------------------------------------------------
    # SCENARIO 4: -15% Blanket Discount Optimization
    # ----------------------------------------------------
    # Recovered discount budget directly flows to EBITDA profit
    discount_savings = round(baseline_discount * 0.15, 2)
    # Slight elasticity effect: 0.5% volume drop assumption
    volume_elasticity_loss = round(baseline_revenue * 0.005 * gross_margin_pct, 2)
    net_profit_gain_s4 = round(discount_savings - volume_elasticity_loss, 2)

    # Combined Strategic Impact (Synergy)
    total_revenue_impact = incremental_rev_s1 + incremental_rev_s2 + incremental_rev_s3
    total_profit_impact = incremental_profit_s1 + incremental_profit_s2 + incremental_profit_s3 + net_profit_gain_s4

    return {
        "baseline": {
            "total_revenue_bdt": round(baseline_revenue, 2),
            "total_profit_bdt": round(baseline_profit, 2),
            "total_orders": baseline_orders,
            "total_customers": baseline_customers,
            "aov_bdt": round(current_aov, 2),
            "gross_margin_pct": round(gross_margin_pct * 100, 2),
            "total_discount_bdt": round(baseline_discount, 2)
        },
        "scenario_1_repeat_frequency": {
            "description": "Increase repeat customer purchase frequency by 10% via personalized WhatsApp & email re-engagement",
            "incremental_orders": additional_orders_s1,
            "incremental_revenue_bdt": incremental_rev_s1,
            "incremental_profit_bdt": incremental_profit_s1,
            "roi_recommendation": "Target 'Potential Loyalists' with bundle discounts rather than single-item promos."
        },
        "scenario_2_churn_reduction": {
            "description": "Reduce customer churn rate by 5% through early-warning intervention on 'At Risk' customers",
            "retained_customers": saved_customers,
            "incremental_revenue_bdt": incremental_rev_s2,
            "incremental_profit_bdt": incremental_profit_s2,
            "roi_recommendation": "Deploy proactive customer success calls and dynamic bKash cashback for dormant accounts."
        },
        "scenario_3_aov_expansion": {
            "description": "Increase Average Order Value (AOV) by 10% via checkout AI cross-sells and free-shipping thresholds",
            "incremental_revenue_bdt": incremental_rev_s3,
            "incremental_profit_bdt": incremental_profit_s3,
            "roi_recommendation": "Increase free-shipping minimum from 2,000 BDT to 2,500 BDT and promote mobile accessory add-ons."
        },
        "scenario_4_discount_rationalization": {
            "description": "Reduce blanket discounts by 15% and eliminate promotional subsidies for price-insensitive Champions",
            "discount_savings_bdt": discount_savings,
            "net_profit_gain_bdt": net_profit_gain_s4,
            "roi_recommendation": "Stop giving blanket 10% site-wide coupons. Re-allocate 30% of budget into VIP exclusive privileges."
        },
        "combined_synergy": {
            "total_incremental_revenue_bdt": round(total_revenue_impact, 2),
            "total_incremental_profit_bdt": round(total_profit_impact, 2),
            "profit_growth_pct": round(total_profit_impact / baseline_profit * 100, 2)
        }
    }
