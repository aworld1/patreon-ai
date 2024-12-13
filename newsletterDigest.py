import json
import re
import openai
from googleapiclient.discovery import build

#insert your openai api key here
OPENAI_API_KEY = "pseudo-openai-api-key"
#insert your youtube api key here
YOUTUBE_API_KEY = "pseudo-youtube-api-key"

openai.api_key = OPENAI_API_KEY

TITLE = "Creator Dispatch: Your Personalized Creator Update"
PROMPT_SECTION_1 = "Masterstrokes: What's Working (Last 7 Days)"
PROMPT_SECTION_2 = "Fine Lines: Areas to Refine (Last 7 Days)"
PROMPT_SECTION_3 = "The Blueprint: Strateic Adjustments (Next 7 Days)"
PROMPT_SECTION_4 = "Fresh Paint: News from Your Niche (last 7 days)"
PROMPT_SECTION_5 = "Monetization Ops: Current Opportunities"

def get_channel_id_by_name(channel_name):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if 'items' not in response or not response['items']:
        return None

    return response['items'][0]['id']['channelId']

def fetch_youtube_data(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    )
    response = request.execute()
    
    if 'items' not in response or not response['items']:
        return None

    channel_info = response['items'][0]
    snippet = channel_info['snippet']
    statistics = channel_info['statistics']
    
    return {
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "subscriberCount": statistics.get("subscriberCount"),
        "videoCount": statistics.get("videoCount"),
        "viewCount": statistics.get("viewCount")
    }

def generate_newsletter(youtube_data):
    prompt = f"""
        I want you to act as a content strategy analyst. Below is information about a YouTube creator:
        - Channel Name: {youtube_data['title']}
        - Description: {youtube_data['description']}
        - Subscriber Count: {youtube_data['subscriberCount']}
        - Video Count: {youtube_data['videoCount']}
        - Total Views: {youtube_data['viewCount']}

        Please scrape the youtube channel details for more accurate and personalized newsletter.

        Please generate a summary about this channel, including:
        1. {PROMPT_SECTION_1}.
        2. {PROMPT_SECTION_2}.
        3. {PROMPT_SECTION_3}.
        4. {PROMPT_SECTION_4}.
        5. {PROMPT_SECTION_5}.

        Output format:
        ### Summary of {youtube_data['title']} Channel

        #### 1. {PROMPT_SECTION_1}
        [List strengths here in bullet points]
        [sample:
                Let’s celebrate all the wins, everytime : 
                Authentic Voice: Your viewers love how genuine and relatable you are!
                Engaging Thumbnails: High click-through rates show your visuals grab attention.
                Niche Authority: Your deep dive into [your niche] sets you apart as an expert.]

        #### 2. {PROMPT_SECTION_2}
        [List areas for improvement here in bullet points]
        [sample: 
                Every masterpiece starts with some messy stroke:
                Inconsistent Upload Schedule: Posting irregularly can disrupt audience growth.
                Call-to-Action Engagement: Low interaction on CTAs could mean they’re unclear or too generic.
                Content Length: Some videos may run longer than necessary, causing drop-off rates.]

        #### 3. {PROMPT_SECTION_3}
        [List strategic recommendations here in bullet points]
        [sample: 
                Recommendations for next steps on your roadmap:
                Commit to a Posting Schedule: Choose one day/time per week to build audience trust.
                Experiment with CTAs: Try more engaging language like, “Comment your favorite part below!”
                Tighten Your Editing: Aim for videos around [optimal length] to keep retention high.]

        #### 4. {PROMPT_SECTION_4}
        [List news items or trends here in bullet points]
        [sample: 
                Keep your creative palette up-to-date with trends and innovations."
                New Tool Alert: [Tool Name]
                A game-changing low-code tool, [Tool Name], now offers [specific feature], making it easier to streamline your workflows. Perfect for creating polished content faster.
                Industry Trend: Short-form vs. Long-form Content
                Creators in [niche] are leaning into short-form videos to boost retention while keeping audiences engaged. Time to experiment with 60-second snippets!
                Inspirational Case Study: [Creator/Company Name]
                [Creator/Company Name] grew their audience by [X%] in [timeframe] by doing [specific strategy]. Could this work for your channel?
        ]

        #### 5. {PROMPT_SECTION_5}
        [List monetization tips or strategies here in bullet points]
        [sample: 
                Turn your creative strokes into income streams."
                Affiliate Marketing: Based on your niche, partner with brands like [Brand Name] to earn commissions on product referrals. Tools like [Affiliate Platform] can help you get started.
                Branded Content: With [current follower count], pitch micro-influencer deals to smaller brands that align with your audience. Use platforms like [Brand Partnership Tool] for connections.
                Ad Revenue Optimization: Check your CPM rates and try optimizing content around high-performing topics in your niche.
        ]

       
        Please adhere to this format strictly to ensure clear separation of sections and ease of parsing for automated processing.
        """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

def save_newsletter_to_json(newsletter, filename="newsletter.json"):
    newsletter = newsletter.strip()
    sections = newsletter.split("\n\n")
    extracted_data = {
        PROMPT_SECTION_1: [],
        PROMPT_SECTION_2: [],
        PROMPT_SECTION_3: [], 
        PROMPT_SECTION_4: [],
        PROMPT_SECTION_5: []
    }

    # Function to extract bullet points
    def extract_bullet_points(section_content):
        bullet_points = []
        for line in section_content.split("\n"):
            if line.startswith("- **"):  # Identify bullet-point lines
                match = re.match(r"- \*\*(.+?)\*\*: (.+)", line.strip())
                if match:
                    title, content = match.groups()
                    bullet_points.append((title.strip(), content.strip()))
        return bullet_points

    # Parse sections into structured JSON format
    for section in sections:
        section = section.strip()
        content = "\n".join(section.split("\n")[1:]).strip()

        if PROMPT_SECTION_1 in section:
            extracted_data[PROMPT_SECTION_1] = extract_bullet_points(content)
        elif PROMPT_SECTION_2 in section:
            extracted_data[PROMPT_SECTION_2] = extract_bullet_points(content)
        elif PROMPT_SECTION_3 in section:
            extracted_data[PROMPT_SECTION_3] = extract_bullet_points(content)
        elif PROMPT_SECTION_4 in section:
            extracted_data[PROMPT_SECTION_4] = extract_bullet_points(content)
        elif PROMPT_SECTION_5 in section:
            extracted_data[PROMPT_SECTION_5] = extract_bullet_points(content)

    # Save as JSON file
    with open(filename, "w") as json_file:
        json.dump(extracted_data, json_file, indent=4)
    print(f"JSON file saved as {filename}")

def main():
    channel_name = input("Enter the YouTube channel name: ")
    channel_id = get_channel_id_by_name(channel_name)
    
    if not channel_id:
        print("Can't find the channel ID for the given channel name.")
        return

    youtube_data = fetch_youtube_data(channel_id)
    
    if not youtube_data:
        print("Can't fetch data from YouTube API")
        return

    newsletter = generate_newsletter(youtube_data)
    print("\nNewsletter generated:\n")
    print(newsletter)

    save_newsletter_to_json(newsletter, "newsletter.json")


if __name__ == "__main__":
    main()