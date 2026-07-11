import asyncio
from adpilot.schemas.agent_schemas import CampaignInput, CampaignGoal, MarketingChannel, ToneOfVoice, OrchestratorInput
from adpilot.services.task_manager import TaskManager
from adpilot.core.database import create_tables

async def main():
    await create_tables()
    manager = TaskManager()
    campaign = CampaignInput(
        business_name="AdNova AI",
        product_description="AI-Powered Marketing Automation Platform",
        target_market="Tech enthusiasts",
        budget_usd=5000,
        goals=[CampaignGoal.brand_awareness],
        channels=[MarketingChannel.linkedin, MarketingChannel.instagram],
        tone_of_voice=ToneOfVoice.professional,
        competitors=[],
        campaign_duration_days=7
    )
    print("Running task manager...")
    try:
        result = await manager.run(OrchestratorInput(campaign=campaign))
        print("SUCCESS! Final summary:")
        print(result.final_campaign_summary.encode('ascii', errors='replace').decode('ascii'))
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
