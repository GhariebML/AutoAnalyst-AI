"""Live performance analytics connectors mockup."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


class LiveAnalyticsConnector:
    """Mock connector to retrieve live marketing performance metrics from platforms."""

    @staticmethod
    def get_supported_platforms() -> List[str]:
        """Return the list of supported platforms."""
        return ["meta", "google_ads", "ga4", "linkedin"]

    def fetch_live_metrics(self, campaign_id: str, platform: str, days: int = 7) -> Dict[str, Any]:
        """Fetch live aggregated and daily time-series performance data for a campaign."""
        clean_platform = platform.strip().lower()
        if clean_platform not in self.get_supported_platforms():
            raise ValueError(
                f"Unsupported analytics platform '{platform}'. "
                f"Expected one of: {', '.join(self.get_supported_platforms())}"
            )

        # Seed based on campaign_id hash to keep mock data stable for the same campaign
        random.seed(hash(campaign_id) + hash(clean_platform))

        # Generate realistic metrics based on platform characteristics
        base_ctr = {
            "meta": 0.025,       # 2.5% CTR
            "google_ads": 0.045, # 4.5% CTR
            "ga4": 0.035,        # 3.5%
            "linkedin": 0.015,   # 1.5% CTR (expensive/niche)
        }.get(clean_platform, 0.02)

        base_cpc = {
            "meta": 1.20,
            "google_ads": 2.50,
            "ga4": 1.50,
            "linkedin": 6.50,
        }.get(clean_platform, 2.0)

        daily_data = []
        total_spend = 0.0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0

        for i in range(days):
            date_str = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            
            # Add some random daily variance
            daily_variance = random.uniform(0.8, 1.2)
            
            impressions = int(random.randint(5000, 15000) * daily_variance)
            ctr = base_ctr * random.uniform(0.9, 1.1)
            clicks = int(impressions * ctr)
            cpc = base_cpc * random.uniform(0.95, 1.05)
            spend = round(clicks * cpc, 2)
            
            # Conversion rate of 2% - 5% of clicks
            conv_rate = random.uniform(0.02, 0.05)
            conversions = int(clicks * conv_rate)
            
            # Revenue calculation for ROAS (e.g. average order value of $75)
            revenue = round(conversions * random.uniform(50.0, 100.0), 2)
            roas = round(revenue / spend, 2) if spend > 0 else 0.0
            cpa = round(spend / conversions, 2) if conversions > 0 else 0.0

            daily_data.append({
                "date": date_str,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr * 100, 2),
                "spend": spend,
                "conversions": conversions,
                "cpa": cpa,
                "roas": roas,
            })

            total_spend += spend
            total_impressions += impressions
            total_clicks += clicks
            total_conversions += conversions

        avg_ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions > 0 else 0.0
        avg_cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0.0
        avg_cpa = round(total_spend / total_conversions, 2) if total_conversions > 0 else 0.0
        
        # Total revenue generated
        total_revenue = sum(d["spend"] * d["roas"] for d in daily_data)
        avg_roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0.0

        return {
            "campaignId": campaign_id,
            "platform": clean_platform,
            "summary": {
                "totalSpend": round(total_spend, 2),
                "totalImpressions": total_impressions,
                "totalClicks": total_clicks,
                "totalConversions": total_conversions,
                "ctr": avg_ctr,
                "cpc": avg_cpc,
                "cpa": avg_cpa,
                "roas": avg_roas,
            },
            "dailySeries": daily_data,
        }
