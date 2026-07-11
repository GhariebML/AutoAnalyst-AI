import pytest
from adpilot.services.analytics.connectors import LiveAnalyticsConnector


def test_live_analytics_metrics_generation():
    """Verify LiveAnalyticsConnector fetches aggregate and daily metrics for valid platforms."""
    connector = LiveAnalyticsConnector()
    
    # Test valid platform: meta
    res = connector.fetch_live_metrics(campaign_id="campaign-999", platform="meta", days=5)
    assert res["campaignId"] == "campaign-999"
    assert res["platform"] == "meta"
    
    # Verify summary metrics
    summary = res["summary"]
    assert "totalSpend" in summary
    assert "totalImpressions" in summary
    assert "totalClicks" in summary
    assert "totalConversions" in summary
    assert "ctr" in summary
    assert "cpc" in summary
    assert "cpa" in summary
    assert "roas" in summary
    
    # Verify types
    assert isinstance(summary["totalImpressions"], int)
    assert isinstance(summary["totalSpend"], float)
    assert isinstance(summary["ctr"], float)
    
    # Verify timeseries daily list
    daily = res["dailySeries"]
    assert len(daily) == 5
    for item in daily:
        assert "date" in item
        assert "impressions" in item
        assert "spend" in item
        assert "roas" in item


def test_live_analytics_rejects_invalid_platform():
    """Verify LiveAnalyticsConnector throws a ValueError for unknown platforms."""
    connector = LiveAnalyticsConnector()
    with pytest.raises(ValueError, match="Unsupported analytics platform"):
        connector.fetch_live_metrics(campaign_id="campaign-999", platform="twitter")
        
    with pytest.raises(ValueError, match="Unsupported analytics platform"):
        connector.fetch_live_metrics(campaign_id="campaign-999", platform="tiktok")
