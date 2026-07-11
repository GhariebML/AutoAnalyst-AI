from adpilot.services.ai_optimizer import AIOptimizer, CampaignMetrics, CampaignTargets


def test_ai_optimizer_rules():
    optimizer = AIOptimizer()

    # Case 1: ROAS is higher than target, others are optimal
    metrics = CampaignMetrics(ctr=5.0, cpa=2.0, roas=4.0)
    targets = CampaignTargets(ctr_target=4.0, cpa_target=3.0, roas_target=3.5)
    recs = optimizer.evaluate(metrics, targets)
    assert len(recs) == 1
    assert recs[0].action_type == "increase_budget"
    assert "ROAS" in recs[0].condition

    # Case 2: Low CTR and High CPA
    metrics = CampaignMetrics(ctr=2.0, cpa=5.0, roas=3.0)
    targets = CampaignTargets(ctr_target=4.0, cpa_target=3.0, roas_target=3.5)
    recs = optimizer.evaluate(metrics, targets)
    assert len(recs) == 2
    action_types = {r.action_type for r in recs}
    assert "regenerate_content" in action_types
    assert "reduce_budget" in action_types
