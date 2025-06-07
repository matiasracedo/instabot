import openai
import base64

def set_api_key(api_key):
    openai.api_key = api_key

def generate_comment(details, allow_sensitive=True):
    prompt = (
        f"Generate a thoughtful Instagram comment for this post.\n"
        f"Caption: '{details['caption']}'\n"
        f"Posted by: {details['username']} ({details['full_name']})\n"
        f"Likes: {details.get('like_count', 'N/A')} | Comments: {details.get('comment_count', 'N/A')}\n"
    )
    image_analysis = None
    sensitive = False
    if details.get('image_path'):
        # Read image and send to OpenAI for vision analysis
        with open(details['image_path'], 'rb') as img_file:
            img_bytes = img_file.read()
        # GPT-4o vision API expects image as base64 or file, here we use base64
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        vision_prompt = (
            "Analyze this Instagram image. "
            "Is there anything harmful, offensive, graphically sexual, or NSFW in this image? "
            "Reply with 'safe' if the image is safe, or 'sensitive' if it is not. "
            "Then, provide a short description of the image."
        )
        vision_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": vision_prompt},
                {"role": "user", "content": [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}]}
            ],
            max_tokens=100,
            temperature=0.2,
        )
        vision_content = vision_response.choices[0].message.content.strip()
        # Parse for 'safe' or 'sensitive'
        if vision_content.lower().startswith('sensitive'):
            sensitive = True
        # Extract description after first line
        image_analysis = '\n'.join(vision_content.split('\n')[1:]).strip()
    if sensitive and not allow_sensitive:
        return None  # Signal to skip commenting
    if image_analysis:
        prompt += f"Image description: {image_analysis}\n"
    prompt += "Comment:"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=40,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
