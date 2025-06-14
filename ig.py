from instagrapi import Client
import logging
import time
import random
import requests
import os
from db import log_action, init_db
import pytz
from datetime import datetime, timedelta
import string

logging.basicConfig(filename='instabot.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

SESSION_FILE = "session.json"

def random_device_settings():
    # Generate random device settings for instagrapi Client
    # (instagrapi auto-generates if not set, but we can randomize)
    brands = ["Samsung", "Google", "OnePlus", "Huawei", "Xiaomi", "Oppo", "Vivo", "Sony", "LG"]
    brand = random.choice(brands)
    model = brand + random.choice([" Galaxy S21", " Pixel 6", " 9 Pro", " P40", " Mi 11", " Reno 6", " X60", " Xperia 5", " G8"]) 
    android_version = random.randint(24, 33)  # Android 7.0 to 13
    android_release = f"{random.randint(7, 13)}.{random.randint(0, 3)}"
    device_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    user_agent = f"Instagram 250.0.0.17.111 Android ({android_version}/{android_release}; 420dpi; 1080x1920; {brand}; {model}; {model.replace(' ', '')}; qcom; en_US)"
    return {
        "manufacturer": brand,
        "model": model,
        "android_version": android_version,
        "android_release": android_release,
        "device_id": device_id,
        "user_agent": user_agent
    }

def login_instagram(username, password):
    cl = Client()
    # Try to load session if it exists
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            # Validate session by making a real API call
            try:
                cl.get_timeline_feed()
            except Exception as e:
                # If any login/auth error, force re-login
                if 'login_required' in str(e).lower() or 'authentication' in str(e).lower():
                    logging.warning(f"Session invalid or expired (login_required), logging in again: {e}")
                    cl.login(username, password)
                    cl.dump_settings(SESSION_FILE)
                    return cl
                else:
                    raise
            return cl
        except Exception as e:
            logging.warning(f"Session file could not be loaded, logging in again: {e}")
            try:
                cl.login(username, password)
                cl.dump_settings(SESSION_FILE)
                return cl
            except Exception as e2:
                # Handle 2FA/MFA
                if "challenge_required" in str(e2) or "two_factor" in str(e2):
                    code = input("Enter your Instagram 2FA/MFA code: ")
                    cl.login(username, password, verification_code=code)
                    cl.dump_settings(SESSION_FILE)
                    return cl
                else:
                    raise e2
    else:
        try:
            cl.login(username, password)
            cl.dump_settings(SESSION_FILE)
            return cl
        except Exception as e:
            if "challenge_required" in str(e) or "two_factor" in str(e):
                code = input("Enter your Instagram 2FA/MFA code: ")
                cl.login(username, password, verification_code=code)
                cl.dump_settings(SESSION_FILE)
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

def like_and_comment(cl, hashtags, like_limit, comment_limit, openai_comment_fn, allow_sensitive=True, avoid_hashtags=None):
    import math
    import datetime
    import time
    import random
    import pytz
    import os
    import logging
    from db import log_action
    # --- Humanization/anti-blocking ---
    # Shuffle hashtags and randomize post order
    hashtags = list(hashtags)
    random.shuffle(hashtags)
    liked, commented = 0, 0
    avoid_hashtags = [h.lower() for h in (avoid_hashtags or [])]
    total_actions = like_limit + comment_limit
    seconds_in_day = 24 * 60 * 60
    min_gap = int(seconds_in_day / (total_actions + 1))
    def next_delay():
        # Add jitter and simulate human reading time
        base = min_gap
        jitter = random.uniform(0.7, 1.3)
        # Simulate reading captions, scrolling, etc.
        human_browse = random.uniform(2, 8)
        return int(base * jitter + human_browse)
    def random_long_break():
        # Occasionally take a longer break (simulate switching apps, etc.)
        if random.random() < 0.12:
            break_time = random.uniform(60, 180)
            logging.info(f"Taking a long break for {break_time:.1f} seconds to simulate human behavior.")
            time.sleep(break_time)
    # --- Time-of-day clustering ---
    def is_waking_hours():
        # Cluster actions between 8am and 11pm local time
        now = datetime.datetime.now()
        return 8 <= now.hour <= 23
    last_action_time = time.time()
    for hashtag in hashtags:
        medias = cl.hashtag_medias_recent(hashtag.strip(), amount=10)
        medias = list(medias)
        random.shuffle(medias)
        for media in medias:
            # Sometimes just "view" the post and do nothing
            if random.random() < 0.08:
                logging.info(f"Simulated viewing post {media.id} (no action taken)")
                time.sleep(random.uniform(3, 10))
                continue
            # Only act during waking hours (else, wait until morning)
            while not is_waking_hours():
                logging.info("Sleeping until morning to avoid night-time bot activity.")
                time.sleep(60 * 15)  # Sleep 15 minutes
            details = get_media_details(cl, media)
            img_path = download_image(details.get('media_url'), media.id)
            details['image_path'] = img_path
            post_link = f"https://www.instagram.com/p/{media.code}/"
            details['post_link'] = post_link
            caption = (details.get('caption') or '').lower()
            media_hashtags = [h.lower() for h in getattr(media, 'hashtags', [])]
            # --- Avoid commenting on giveaways ---
            if 'giveaway' in caption or any('giveaway' in h for h in media_hashtags) or 'giveaway' in hashtag.lower():
                logging.info(f"Skipped post {media.id} due to 'giveaway' in caption or hashtags. | Link: {post_link}")
                if liked < like_limit and not has_action(media.id, 'like') and random.random() > 0.15:
                    try:
                        cl.media_like(media.id)
                        logging.info(f"Liked post {media.id} (hashtag: {hashtag}) | Link: {post_link}")
                        log_action('like', media_id=media.id, hashtag=hashtag, post_link=post_link)
                        liked += 1
                    except Exception as e:
                        logging.error(f"Failed to like post {media.id}: {e}")
                        log_action('error', media_id=media.id, hashtag=hashtag, error=str(e), post_link=post_link)
                if img_path and os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except Exception as e:
                        logging.warning(f"Could not delete image {img_path}: {e}")
                last_action_time += next_delay()
                time_to_wait = max(0, last_action_time - time.time())
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                random_long_break()
                continue
            # --- Avoid commenting if avoid hashtag present ---
            if any(h in media_hashtags for h in avoid_hashtags):
                logging.info(f"Skipped commenting on post {media.id} due to avoid hashtag in hashtags. | Link: {post_link}")
                if liked < like_limit and not has_action(media.id, 'like') and random.random() > 0.15:
                    try:
                        cl.media_like(media.id)
                        logging.info(f"Liked post {media.id} (hashtag: {hashtag}) | Link: {post_link}")
                        log_action('like', media_id=media.id, hashtag=hashtag, post_link=post_link)
                        liked += 1
                    except Exception as e:
                        logging.error(f"Failed to like post {media.id}: {e}")
                        log_action('error', media_id=media.id, hashtag=hashtag, error=str(e), post_link=post_link)
                if img_path and os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except Exception as e:
                        logging.warning(f"Could not delete image {img_path}: {e}")
                last_action_time += next_delay()
                time_to_wait = max(0, last_action_time - time.time())
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                random_long_break()
                continue
            # --- Like action (randomly skip some) ---
            if liked < like_limit and not has_action(media.id, 'like') and random.random() > 0.10:
                try:
                    cl.media_like(media.id)
                    logging.info(f"Liked post {media.id} (hashtag: {hashtag}) | Link: {post_link}")
                    log_action('like', media_id=media.id, hashtag=hashtag, post_link=post_link)
                    liked += 1
                except Exception as e:
                    logging.error(f"Failed to like post {media.id}: {e}")
                    log_action('error', media_id=media.id, hashtag=hashtag, error=str(e), post_link=post_link)
                last_action_time += next_delay()
                time_to_wait = max(0, last_action_time - time.time())
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                random_long_break()
            # --- Comment action (randomly skip some) ---
            if commented < comment_limit and not has_action(media.id, 'comment') and random.random() > 0.18:
                try:
                    comment = openai_comment_fn(details, allow_sensitive=allow_sensitive)
                    if comment is None:
                        logging.info(f"Skipped commenting on post {media.id} due to sensitive image. | Link: {post_link}")
                        last_action_time += next_delay()
                        time_to_wait = max(0, last_action_time - time.time())
                        if time_to_wait > 0:
                            time.sleep(time_to_wait)
                        random_long_break()
                        continue
                    cl.media_comment(media.id, comment)
                    logging.info(f"Commented on post {media.id}: {comment} | Link: {post_link}")
                    log_action('comment', media_id=media.id, hashtag=hashtag, comment=comment, post_link=post_link)
                    commented += 1
                except Exception as e:
                    logging.error(f"Failed to comment on post {media.id}: {e}")
                    log_action('error', media_id=media.id, hashtag=hashtag, error=str(e), post_link=post_link)
                last_action_time += next_delay()
                time_to_wait = max(0, last_action_time - time.time())
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                random_long_break()
            if img_path and os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception as e:
                    logging.warning(f"Could not delete image {img_path}: {e}")
            if liked >= like_limit and commented >= comment_limit:
                break

if __name__ == "__main__":
    init_db()
