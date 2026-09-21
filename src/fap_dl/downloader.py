from pathlib import Path
from urllib.parse import urlparse

import requests

from .gallery import (
	image_url_from_thumbnail,
	video_url_from_thumbnail,
)


def create_download_session(cookies):
	session = requests.Session()

	session.headers.update({
		"User-Agent": (
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
			"AppleWebKit/537.36 (KHTML, like Gecko) "
			"Chrome/153.0.0.0 Safari/537.36"
		),
		"Referer": "https://fapello.com/",
	})

	for cookie in cookies:
		session.cookies.set(
			cookie["name"],
			cookie["value"],
			domain=cookie.get("domain"),
			path=cookie.get("path", "/"),
		)

	return session


def download_file(session, url, destination):
	temp_destination = destination.with_suffix(
		destination.suffix + ".part"
	)

	try:
		with session.get(
			url,
			stream=True,
			timeout=(30, 120),
		) as response:

			if not response.ok:
				return False, f"HTTP {response.status_code}"

			destination.parent.mkdir(
				parents=True,
				exist_ok=True,
			)

			with open(temp_destination, "wb") as file:
				for chunk in response.iter_content(
					chunk_size=1024 * 1024
				):
					if chunk:
						file.write(chunk)

		if (
			not temp_destination.exists()
			or temp_destination.stat().st_size == 0
		):
			temp_destination.unlink(missing_ok=True)
			return False, "empty response"

		temp_destination.replace(destination)

		size_mb = (
			destination.stat().st_size
			/ 1024
			/ 1024
		)

		return True, size_mb

	except Exception as exc:
		temp_destination.unlink(missing_ok=True)
		return False, str(exc)


def download_images(
	session,
	posts,
	image_posts,
	image_dir,
):
	downloaded = 0
	skipped = 0
	failed = 0

	print()
	print("Images")
	print("------------------")

	for index, post_number in enumerate(
		image_posts,
		start=1,
	):
		post = posts[post_number]

		image_url = image_url_from_thumbnail(
			post["thumbnail"]
		)

		filename = Path(
			urlparse(image_url).path
		).name

		destination = image_dir / filename

		print(
			f"[{index}/{len(image_posts)}] "
			f"{filename}",
			end=" ",
			flush=True,
		)

		if (
			destination.exists()
			and destination.stat().st_size > 0
		):
			print("✓ already exists")
			skipped += 1
			continue

		success, result = download_file(
			session,
			image_url,
			destination,
		)

		if success:
			print(f"✓ {result:.1f} MB")
			downloaded += 1
		else:
			print(f"✗ {result}")
			failed += 1

	return downloaded, skipped, failed


def download_videos(
	session,
	posts,
	video_posts,
	video_dir,
):
	downloaded = 0
	skipped = 0
	failed_videos = []

	print()
	print("Videos")
	print("------------------")

	for index, post_number in enumerate(
		video_posts,
		start=1,
	):
		post = posts[post_number]

		video_url = video_url_from_thumbnail(
			post["thumbnail"]
		)

		filename = Path(
			urlparse(video_url).path
		).name

		destination = video_dir / filename

		print(
			f"[{index}/{len(video_posts)}] "
			f"{filename}",
			end=" ",
			flush=True,
		)

		if (
			destination.exists()
			and destination.stat().st_size > 0
		):
			print("✓ already exists")
			skipped += 1
			continue

		success, result = download_file(
			session,
			video_url,
			destination,
		)

		if success:
			print(f"✓ {result:.1f} MB")
			downloaded += 1
		else:
			print(f"↻ {result}; queued for fallback")

			failed_videos.append({
				"post_number": post_number,
				"post_url": post["url"],
				"destination": destination,
			})

	return downloaded, skipped, failed_videos


def retry_failed_videos(
	session,
	failed_videos,
	resolved_urls,
):
	recovered = 0
	failed = 0

	if not failed_videos:
		return recovered, failed

	print()
	print("Video Fallback Downloads")
	print("------------------")

	for index, item in enumerate(
		failed_videos,
		start=1,
	):
		post_number = item["post_number"]
		destination = item["destination"]

		print(
			f"[{index}/{len(failed_videos)}] "
			f"{destination.name}",
			end=" ",
			flush=True,
		)

		video_url = resolved_urls.get(post_number)

		if not video_url:
			print("✗ unresolved")
			failed += 1
			continue

		success, result = download_file(
			session,
			video_url,
			destination,
		)

		if success:
			print(f"✓ {result:.1f} MB")
			recovered += 1
		else:
			print(f"✗ {result}")
			failed += 1

	return recovered, failed