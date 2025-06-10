from instagrapi import Client
import logging
import time
import random
import requests
import os
from db import log_action, init_db

logging.basicConfig(filename='instabot.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def login_instagram(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        return cl
    except Exception as e:
        # If MFA is enabled, instagrapi will prompt for verification_code
        if "challenge_required" in str(e) or "two_factor" in str(e):
            code = input("Enter your Instagram 2FA/MFA code: ")
            cl.login(username, password, verification_code=code)
            return cl
        else:
            raise e

def has_action(media_id, action_type):
    import sqlite3
    conn = sqlite3.connect('instabot.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM actions WHERE media_id=? AND action_type=? LIMIT 1', (str(media_id), action_type))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_media_details(cl, media):
    # Fetch extra details for personalization
    user = cl.user_info(media.user.pk)
    # Determine if this is the user's own post
    is_own_post = False
    is_following = False
    try:
        # cl.user_id is the logged-in user's id
        is_own_post = (media.user.pk == cl.user_id)
        # Check if the logged-in user is following the post's author
        # cl.user_following returns a dict of user_id: UserShort
        following_dict = cl.user_following(cl.user_id)
        is_following = str(media.user.pk) in [str(uid) for uid in following_dict.keys()]
    except Exception:
        pass
    details = {
        'username': user.username,
        'full_name': user.full_name,
        'caption': media.caption_text or "",
        'like_count': getattr(media, 'like_count', None),
        'comment_count': getattr(media, 'comment_count', None),
        'media_url': media.thumbnail_url if hasattr(media, 'thumbnail_url') else None,
        'is_own_post': is_own_post,
        'is_following': is_following
    }
    return details

def download_image(url, media_id):
    if not url:
        return None
    img_dir = 'media_images'
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, f'{media_id}.jpg')
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(img_path, 'wb') as f:
                f.write(response.content)
            return img_path
    except Exception as e:
        logging.error(f"Failed to download image for {media_id}: {e}")
    return None

def like_and_comment(cl, hashtags, like_limit, comment_limit, openai_comment_fn, allow_sensitive=True):
    liked, commented = 0, 0
    for hashtag in hashtags:
        medias = cl.hashtag_medias_recent(hashtag.strip(), amount=10)
        for media in medias:
            details = get_media_details(cl, media)
            img_path = download_image(details.get('media_url'), media.id)
            details['image_path'] = img_path
            if liked < like_limit and not has_action(media.id, 'like'):
                try:
                    cl.media_like(media.id)
                    logging.info(f"Liked post {media.id} (hashtag: {hashtag})")
                    log_action('like', media_id=media.id, hashtag=hashtag)
                    liked += 1
                except Exception as e:
                    logging.error(f"Failed to like post {media.id}: {e}")
                    log_action('error', media_id=media.id, hashtag=hashtag, error=str(e))
                time.sleep(random.randint(20, 60))
            if commented < comment_limit and not has_action(media.id, 'comment'):
                try:
                    comment = openai_comment_fn(details, allow_sensitive=allow_sensitive)
                    if comment is None:
                        logging.info(f"Skipped commenting on post {media.id} due to sensitive image.")
                        continue
                    cl.media_comment(media.id, comment)
                    logging.info(f"Commented on post {media.id}: {comment}")
                    log_action('comment', media_id=media.id, hashtag=hashtag, comment=comment)
                    commented += 1
                except Exception as e:
                    logging.error(f"Failed to comment on post {media.id}: {e}")
                    log_action('error', media_id=media.id, hashtag=hashtag, error=str(e))
                time.sleep(random.randint(40, 90))
            if liked >= like_limit and commented >= comment_limit:
                break

if __name__ == "__main__":
    init_db()
