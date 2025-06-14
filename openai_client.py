import openai
import base64
from langdetect import detect
import random

def set_api_key(api_key):
    openai.api_key = api_key

def generate_comment(details, allow_sensitive=True, goodreads_books=None):
    # Do not comment on own posts
    if details.get('is_own_post'):
        return None
    caption = details['caption']
    try:
        language_code = detect(caption)
    except Exception:
        language_code = 'en'  # fallback
    # Alternate word limit between 10 and 20
    word_limit = random.choice([10, 20])
    prompt = (
        f"Generate a thoughtful Instagram comment for this post.\n"
        f"Caption: '{caption}'\n"
        f"Posted by: {details['username']} ({details['full_name']})\n"
        f"Likes: {details.get('like_count', 'N/A')} | Comments: {details.get('comment_count', 'N/A')}\n"
    )
    # Add language and tone instructions
    if language_code == 'es':
        prompt += ("Reply in Argentinian Spanish, making sure the comment sounds like a native Argentinian speaker. ")
    else:
        prompt += ("Reply in English, regardless of the caption's language. ")
    # Tone based on following status
    if details.get('is_following'):
        prompt += ("Make the comment warm, friendly, and supportive, as if you know the person. ")
    else:
        prompt += ("Make the comment polite, positive, and not too familiar, as if you don't know the person. ")
    prompt += (f"The comment must be short (between 10 and {word_limit} words), and should never start with quote marks or quotation marks unless it is intentional.\n")
    image_analysis = None
    sensitive = False
    if details.get('image_path'):
        with open(details['image_path'], 'rb') as img_file:
            img_bytes = img_file.read()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        vision_prompt = (
            "Analyze this Instagram image. "
            "Is there anything harmful, offensive, graphically sexual, or NSFW in this image? "
            "Reply with 'safe' if the image is safe, or 'sensitive' if it is not. "
            "Then, provide a short description of the image."
        )
        vision_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": vision_prompt},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]}
            ],
            max_tokens=100,
            temperature=0.2,
        )
        vision_content = vision_response.choices[0].message.content.strip()
        if vision_content.lower().startswith('sensitive'):
            sensitive = True
        image_analysis = '\n'.join(vision_content.split('\n')[1:]).strip()
    if sensitive and not allow_sensitive:
        return None  # Signal to skip commenting
    if image_analysis:
        prompt += f"Image description: {image_analysis}\n"

    # --- Goodreads personalization ---
    if goodreads_books and caption:
        # Try to find a book title in the caption (simple match)
        found_book = None
        for book in goodreads_books:
            title = book.get('title', '').strip()
            if title and title.lower() in caption.lower():
                found_book = book
                break
        if found_book:
            # If user has read the book, add rating/review info to prompt
            rating = found_book.get('rating')
            review = found_book.get('review')
            if rating:
                prompt += f"I have read the book '{found_book['title']}' and gave it a {rating}/5 rating on Goodreads. "
            if review:
                prompt += f"My review: {review[:200]}\n"  # Limit review length
            prompt += "If this post is a review of the book, make my comment more personal, reflecting that I have read it. Do not mention my actual rating in the comment.\n"
        else:
            # If not read, instruct not to give a false opinion
            prompt += "If this post is about a book I have not read, do not give a personal opinion about the book.\n"

    prompt += "Comment:"
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
