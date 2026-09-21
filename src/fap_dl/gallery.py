import re

from urllib.parse import urlparse


def get_post_count(page, model, post_pattern):
	"""
	Count unique numbered profile posts currently loaded
	into the gallery.
	"""

	links = page.locator(
		f'a[href*="fapello.com/{model}/"]'
	)

	post_numbers = set()

	for i in range(links.count()):
		href = links.nth(i).get_attribute("href")

		if not href:
			continue

		match = post_pattern.match(href)

		if match:
			post_numbers.add(
				int(match.group(1))
			)

	return len(post_numbers)


def load_gallery(page, model, post_pattern):
	"""
	Scroll until the number of discovered posts remains
	unchanged for several consecutive rounds.
	"""

	print("\nLoading gallery...")

	previous_count = -1
	unchanged_rounds = 0
	required_unchanged_rounds = 4

	while unchanged_rounds < required_unchanged_rounds:

		current_count = get_post_count(
			page,
			model,
			post_pattern,
		)

		print(
			f"  {current_count} posts discovered"
		)

		if current_count == previous_count:
			unchanged_rounds += 1
		else:
			previous_count = current_count
			unchanged_rounds = 0

		page.evaluate(
			"window.scrollTo(0, document.body.scrollHeight)"
		)

		page.wait_for_timeout(1500)

	print("Gallery complete.")


def analyze_gallery(page, model, post_pattern):
	"""
	Analyze all loaded gallery posts.

	Video posts are identified by Fapello's play-icon
	overlay.
	"""

	posts = {}

	links = page.locator(
		f'a[href*="fapello.com/{model}/"]'
	)

	for i in range(links.count()):

		link = links.nth(i)

		href = link.get_attribute("href")

		if not href:
			continue

		match = post_pattern.match(href)

		if not match:
			continue

		post_number = int(match.group(1))

		images = link.locator("img")

		thumbnail_url = None
		is_video = False

		for j in range(images.count()):

			src = images.nth(j).get_attribute("src")

			if not src:
				continue

			if "icon-play.svg" in src:
				is_video = True

			if (
				f"/{model}/" in src
				and "_300px" in src
			):
				thumbnail_url = src

		if not thumbnail_url:
			continue

		posts[post_number] = {
			"url": href,
			"thumbnail": thumbnail_url,
			"video": is_video,
		}

	return posts


def image_url_from_thumbnail(thumbnail_url):
	"""
	Convert a gallery thumbnail URL into its full-size
	image URL.
	"""

	return re.sub(
		r"_300px(?=\.[A-Za-z0-9]+$)",
		"",
		thumbnail_url,
	)


def video_url_from_thumbnail(thumbnail_url):
	"""
	Predict the CDN MP4 URL from the gallery thumbnail.
	"""

	video_url = re.sub(
		r"_300px\.[A-Za-z0-9]+$",
		".mp4",
		thumbnail_url,
	)

	parsed = urlparse(video_url)

	return parsed._replace(
		netloc="cdn.fapello.com"
	).geturl()


def get_video_fallback_url(page, post_url):
	"""
	Visit an individual post and retrieve its MP4 source.

	Used only when the predictable CDN URL fails.
	"""

	page.goto(
		post_url,
		wait_until="domcontentloaded",
		timeout=60000,
	)

	source = page.locator(
		'video source[type="video/mp4"]'
	)

	if source.count() == 0:
		source = page.locator(
			'source[type="video/mp4"]'
		)

	if source.count() == 0:
		return None

	video_url = source.first.get_attribute("src")

	if not video_url:
		return None

	hostname = urlparse(video_url).hostname or ""

	if not (
		hostname == "fapello.com"
		or hostname.endswith(".fapello.com")
	):
		return None

	return video_url