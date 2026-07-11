import sys
sys.path.insert(0, "src")
from adpilot.services.demo_content import generate_demo_content

c = generate_demo_content({
    "businessName": "AdNova AI",
    "productName": "AI Marketing Platform",
    "productDescription": "AI-Powered Marketing",
    "targetAudience": "Tech enthusiasts",
    "goals": ["Brand Awareness"],
    "tone": "Professional",
    "budget": 5000,
})

print(f"Ads: {len(c['ads'])}")
print(f"Emails: {len(c['emailSequences'])}")
print(f"Social: {len(c['socialPosts'])}")
print(f"Summary length: {len(c['summary'])}")
print(f"Insights keys: {list(c['insights'].keys())}")
print(f"First ad headline: {c['ads'][0]['headline']}")
print(f"First ad body length: {len(c['ads'][0]['body'])}")
print("SUCCESS!")
