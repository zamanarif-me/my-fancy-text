"""Static configuration: CTAs, platform limits, emoji/hashtag library, sample."""

DEFAULT_CTA = {
    "Facebook": (
        "👍 Like this if it was helpful!\n"
        "💬 Drop your thoughts in the comments.\n"
        "🔁 Share it with someone who needs to see this."
    ),
    "LinkedIn": (
        "♻️ Repost to share with your network.\n"
        "💬 Share your experience in the comments.\n"
        "🔔 Follow for more insights like this."
    ),
    "Pinterest": (
        "📌 Save this pin to read it later!\n"
        "🔗 Check the link in bio for the full guide.\n"
        "✨ Follow for more tips."
    ),
    "X": (
        "🔁 RT if this was useful.\n"
        "💬 Reply with your thoughts.\n"
        "👤 Follow for more content like this."
    ),
    "Twitter": (
        "🔁 RT if this was useful.\n"
        "💬 Reply with your thoughts.\n"
        "👤 Follow for more content like this."
    ),
}

PLATFORM_LIMIT = {
    "Facebook":  63206,
    "LinkedIn":  3000,
    "Pinterest": 500,
    "X":         280,
    "Twitter":   280,
}

# Per-tweet budget in X's *weighted* units (see mft.textmetrics.x_len).
# 270 leaves >= 10 units of headroom for the "(n/N)\n" prefix (ASCII, weight 1).
X_LIMIT = 270


# ── Emoji + hashtag library (curated, copy or insert into content) ────

EMOJI_LIBRARY = {
    "Reactions":        ["👍", "❤️", "🔥", "👏", "🙌", "💯", "😍", "🤯", "🥳", "😂", "✅", "👀"],
    "Arrows & Points":  ["➡️", "⬇️", "👉", "👇", "🔝", "↗️", "▶️", "➤", "✔️", "☑️", "🔻", "⏬"],
    "Business":         ["💼", "📈", "📊", "💡", "🎯", "🚀", "💰", "🏆", "📌", "🔑", "⏰", "📣"],
    "Marketing/Social": ["📱", "💬", "🔁", "🔔", "📢", "✨", "🌟", "🎁", "🎉", "🔗", "#️⃣", "📲"],
    "Nature & Misc":    ["🌸", "🌿", "☀️", "🌈", "⭐", "💎", "🪄", "🧠", "❄️", "🌊", "🍀", "🔆"],
}

HASHTAG_LIBRARY = {
    "SEO": [
        "#SEO", "#SEOTips", "#SearchEngineOptimization", "#OrganicTraffic",
        "#GoogleRanking", "#SEOStrategy", "#KeywordResearch", "#OnPageSEO",
        "#TechnicalSEO", "#LinkBuilding",
    ],
    "Digital Marketing": [
        "#DigitalMarketing", "#MarketingStrategy", "#ContentMarketing",
        "#SocialMediaMarketing", "#OnlineMarketing", "#MarketingTips",
        "#GrowthHacking", "#BrandStrategy", "#EmailMarketing", "#PPC",
    ],
    "Content Creation": [
        "#ContentCreator", "#ContentStrategy", "#ContentWriting", "#Copywriting",
        "#Blogging", "#ContentTips", "#Storytelling", "#CreatorEconomy",
    ],
    "Business & Startup": [
        "#Entrepreneur", "#SmallBusiness", "#Startup", "#BusinessTips",
        "#Hustle", "#BusinessGrowth", "#Leadership", "#Success",
    ],
    "Motivation": [
        "#Motivation", "#MondayMotivation", "#Inspiration", "#Mindset",
        "#GrowthMindset", "#SelfImprovement", "#Discipline", "#NeverGiveUp",
    ],
    "Freelancing": [
        "#Freelancer", "#FreelanceLife", "#WorkFromHome", "#RemoteWork",
        "#FreelanceTips", "#DigitalNomad", "#SideHustle",
    ],
    "Bangla / Local": [
        "#বাংলা", "#ডিজিটালমার্কেটিং", "#ফ্রিল্যান্সিং", "#এসইও",
        "#অনলাইনইনকাম", "#বাংলাদেশ",
    ],
}

SAMPLE = """Title: Day 1: SEO Patience & Trust
Facebook
Body:
Real talk about SEO: most people quit too soon.
Rankings take months, not days. Trust the process and keep publishing.
Media: Follow me on LinkedIn: https://linkedin.com/in/yourname
#SEOStrategy #DigitalMarketing #YourName
LinkedIn
Body:
Real talk about SEO: most people quit too soon.
Rankings take months, not days. Trust the process and keep publishing.
Media: Follow me on LinkedIn: https://linkedin.com/in/yourname
#SEOStrategy #DigitalMarketing #YourName
---
Title: Day 2: ধৈর্যই আসল কৌশল
X
Body:
High volume keywords feel great, but intent is what converts.
সঠিক কিওয়ার্ড মানেই সঠিক ক্রেতা — শুধু সংখ্যা নয়।
Media: More tips →
#SEO #ContentMarketing
"""
