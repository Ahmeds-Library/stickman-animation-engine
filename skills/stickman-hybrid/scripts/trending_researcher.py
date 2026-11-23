#!/usr/bin/env python3
"""trending_researcher.py: High-RPM YouTube Trending Topics & SEO Ranking Suite
Identifies high-performing, high-CPM/RPM evergreen and trending topics for 2D stickman explainers.
Provides:
1. High-CTR Title Formulas (Curiosity Gap, High Stakes, Numbers).
2. Barnum Effect Hook Formulations.
3. YouTube Search SEO Tags & Hash Clusters.
4. Estimated Monetization RPM ($12 - $28).
"""

import sys, json, argparse

TRENDING_NICHES = {
    "ancient_engineering": {
        "niche_name": "Ancient High-Tech & Lost Civilizations",
        "estimated_rpm": "$14.00 - $19.50",
        "audience_demographics": "Global 18-45, high US/UK/CA viewer retention",
        "topics": [
            {
                "id": "persian_ice",
                "title_options": [
                    "How Ancient Kings Made Ice in 45°C Deserts (Without Electricity)",
                    "The 2,400-Year-Old Desert Fridge Modern Science Can't Beat",
                    "How Persia Conquered Summer: The Yakhchal Mystery"
                ],
                "barnum_hook": "You check your fridge 5 times a day without thinking. But 400 years before Christ, doing this in the desert made you an emperor.",
                "thumbnail_text": "DESERT ICE?",
                "badge": "400 BC SECRET",
                "seo_tags": ["ancient engineering", "yakhchal", "persian history", "ancient technology", "how they made ice in desert", "stickman explainer", "radiative cooling", "ancient inventions"],
                "visual_props": ["elements/cut/dome.png", "elements/cut/ice.png", "elements/cut/clay_pot.png"]
            },
            {
                "id": "roman_concrete",
                "title_options": [
                    "Why Roman Concrete Gets STRONGER Under Water (2,000-Year Mystery)",
                    "The Lost Formula That Modern Engineers Still Can't Replicate",
                    "How Rome Built Underwater Harbors That Never Cracked"
                ],
                "barnum_hook": "Every modern sidewalk cracks within 10 years. But 2,000 years ago, Romans built underwater temples that get stronger every time a wave hits them.",
                "thumbnail_text": "STRONGER IN SEA?",
                "badge": "LOST RECIPE",
                "seo_tags": ["roman concrete", "ancient rome", "hot mixing", "volcanic ash", "self healing concrete", "pantheon", "engineering mystery"],
                "visual_props": ["elements/cut/roman_temple.png", "elements/cut/volcano.png", "elements/cut/trowel.png"]
            },
            {
                "id": "greek_fire",
                "title_options": [
                    "The Classified Weapon That Burned On Top of Water",
                    "Greek Fire: The Ancient Secret Weapon That Saved an Empire",
                    "Why The Byzantine Empire Guarded This Recipe With Death"
                ],
                "barnum_hook": "You probably think chemical warfare is modern. But 1,300 years ago, one secret liquid burned ships even under water.",
                "thumbnail_text": "BURNS ON WATER!",
                "badge": "STATE SECRET",
                "seo_tags": ["greek fire", "byzantine empire", "ancient weapons", "military history", "constantinople", "unsolved mystery"],
                "visual_props": ["elements/cut/flame_siphon.png", "elements/cut/warship.png"]
            }
        ]
    },
    "crisis_whatif": {
        "niche_name": "Catastrophic 'What If' & Survival Crises",
        "estimated_rpm": "$16.50 - $22.00",
        "audience_demographics": "High CTR 12-16%, massive viral Shorts sharing",
        "topics": [
            {
                "id": "power_blackout",
                "title_options": [
                    "What Happens to Humanity in a 48-Hour Global Blackout?",
                    "The First 72 Hours Without Electricity (Stickman Survival)",
                    "How Fragile Is Modern Civilization? The Danger Zone"
                ],
                "barnum_hook": "If you're like 99% of people, you think your city has weeks of food. But right now, you are 48 hours away from a total system collapse.",
                "thumbnail_text": "48 HOURS LEFT!",
                "badge": "GLOBAL SHUTDOWN",
                "seo_tags": ["global blackout", "what if electricity disappeared", "survival documentary", "power grid failure", "food danger zone", "modern fragility"],
                "visual_props": ["elements/cut/blackout_city.png", "elements/cut/fridge_rotten.png", "elements/cut/battery_zero.png"]
            },
            {
                "id": "all_ice_melts",
                "title_options": [
                    "What Happens If ALL Earth's Ice Melts Tomorrow?",
                    "The 66-Meter Sea Level Rise: Which Cities Drown First?",
                    "If Every Glacier Melted in 24 Hours"
                ],
                "barnum_hook": "Have you ever wondered what Earth actually looks like without ice? In 24 hours, 2 billion people would have to run.",
                "thumbnail_text": "CITIES SINK?",
                "badge": "66M WATER RISE",
                "seo_tags": ["all ice melts", "sea level rise", "what if ice melted", "geography documentary", "antarctica melting", "stickman science"],
                "visual_props": ["elements/cut/water_wave.png", "elements/cut/drowning_statue.png"]
            }
        ]
    },
    "biology_brain": {
        "niche_name": "Hidden Human Biology & Brain Secrets",
        "estimated_rpm": "$15.00 - $24.00",
        "audience_demographics": "Broad universal appeal, high replay rate",
        "topics": [
            {
                "id": "waking_up_ancient",
                "title_options": [
                    "How Humans Woke Up Before Alarm Clocks Existed",
                    "The Screaming Water Clocks & Candle Alarms of History",
                    "Why Your Ancestors Never Slept In (Ancient Biology)"
                ],
                "barnum_hook": "Notice how you can barely wake up after 3 alarms? Ancient warriors woke up at 4:30 AM with 100% accuracy using one simple biological trick.",
                "thumbnail_text": "NO ALARMS?",
                "badge": "WARRIOR SECRET",
                "seo_tags": ["how humans woke up", "history of alarm clocks", "circadian biology", "knocker uppers", "ancient inventions", "sleep science"],
                "visual_props": ["elements/cut/screaming_whistle.png", "elements/cut/candle_nail.png", "elements/cut/pea_shooter.png"]
            },
            {
                "id": "dopamine_trap",
                "title_options": [
                    "How Your Brain Gets Hijacked in the First 10 Minutes of Waking Up",
                    "The 2 AM Sleep Trap: Why Your Brain Won't Shut Off",
                    "What 30 Days of High Cortisol Does to Your Organs"
                ],
                "barnum_hook": "You probably think you chose to pick up your phone this morning. But your brain released a chemical trigger 20 minutes before your eyes opened.",
                "thumbnail_text": "BRAIN HIJACKED!",
                "badge": "NEUROSCIENCE",
                "seo_tags": ["dopamine loop", "neuroscience explainer", "brain chemistry", "cortisol wake up", "psychology tricks", "stickman biology"],
                "visual_props": ["elements/cut/brain_gears.png", "elements/cut/phone_glow.png"]
            }
        ]
    },
    "dark_economics": {
        "niche_name": "Dark Money, Empire Economics & Historical Scams",
        "estimated_rpm": "$18.00 - $28.00",
        "audience_demographics": "Peak finance advertiser CPM, high mature demographic",
        "topics": [
            {
                "id": "massa_musa_gold",
                "title_options": [
                    "How One Emperor Crashed the World's Economy by Being Too Generous",
                    "The Richest Man in History Who Ruined an Entire Empire's Currency",
                    "Mansa Musa: When Giving Away Free Gold Caused a 12-Year Depression"
                ],
                "barnum_hook": "You probably think inflation is created by modern banks. But in 1324, one man handed out so much pocket change that he collapsed gold prices for 12 years.",
                "thumbnail_text": "GOLD CRASH?",
                "badge": "$400 BILLION",
                "seo_tags": ["mansa musa", "richest man in history", "gold inflation", "economics explained", "history documentary", "cairo gold crash"],
                "visual_props": ["elements/cut/gold_camel.png", "elements/cut/falling_coins.png"]
            },
            {
                "id": "tulip_mania",
                "title_options": [
                    "When A Single Flower Cost More Than A 3-Story Mansion",
                    "The 1637 Tulip Mania: The First Financial Bubble in Human History",
                    "Why Wealthy Merchants Traded All Their Land For A Bulb"
                ],
                "barnum_hook": "If you think cryptocurrency or meme stocks are crazy, wait until you hear how Dutch millionaires went bankrupt over a single spotted flower.",
                "thumbnail_text": "COST A MANSION?",
                "badge": "FIRST BUBBLE",
                "seo_tags": ["tulip mania", "first financial bubble", "dutch golden age", "economics documentary", "market crash history", "money explained"],
                "visual_props": ["elements/cut/tulip_flower.png", "elements/cut/mansion.png"]
            }
        ]
    }
}

def get_trending_summary():
    """Returns top ranked trending topics for high YouTube ad monetization."""
    output = []
    for cat_id, cat in TRENDING_NICHES.items():
        output.append({
            "category": cat["niche_name"],
            "rpm": cat["estimated_rpm"],
            "demographics": cat["audience_demographics"],
            "top_topics": [t["title_options"][0] for t in cat["topics"]]
        })
    return output

def search_trending(query=None, niche=None):
    results = []
    for cat_id, cat in TRENDING_NICHES.items():
        if niche and niche.lower() not in cat_id.lower() and niche.lower() not in cat["niche_name"].lower():
            continue
        for topic in cat["topics"]:
            match = True
            if query:
                q = query.lower()
                all_text = " ".join(topic["title_options"] + topic["seo_tags"] + [topic["barnum_hook"]]).lower()
                if q not in all_text:
                    match = False
            if match:
                res_item = dict(topic)
                res_item["category"] = cat["niche_name"]
                res_item["estimated_rpm"] = cat["estimated_rpm"]
                results.append(res_item)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", "-q", default=None)
    parser.add_argument("--niche", "-n", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = search_trending(args.query, args.niche)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"🔥 Found {len(data)} High-RPM Trending Topics for YouTube Ranking:\n")
        for i, item in enumerate(data, 1):
            print(f"{i}. [{item['category']}] RPM: {item['estimated_rpm']}")
            print(f"   🎬 Title: {item['title_options'][0]}")
            print(f"   🪝 Barnum Hook: \"{item['barnum_hook']}\"")
            print(f"   🖼️ Thumbnail Text: \"{item['thumbnail_text']}\" | Badge: [{item['badge']}]")
            print(f"   🏷️ SEO Tags: {', '.join(item['seo_tags'][:5])}...")
            print()
