from pathlib import Path
from urllib.parse import urlparse
import argparse
import re
import sys

from playwright.sync_api import sync_playwright

from .browser import (
	open_profile,
	resolve_video_fallbacks,
)
from .gallery import (
	get_post_count,
	load_gallery,
	analyze_gallery,
)
from .downloader import (
	create_download_session,
	download_images,
	download_videos,
	retry_failed_videos,
)


def parse_args():
	parser = argparse.ArgumentParser(
		prog="fap-dl",
		description="Download images and videos from a Fapello profile.",
	)

	parser.add_argument(
		"profile",
		help="Fapello profile name or full profile URL",
	)

	parser.add_argument(
		"--combined",
		action="store_true",
		help=(
			"Store images and videos together "
			"instead of separate folders."
		),
	)

	media_group = parser.add_mutually_exclusive_group()

	media_group.add_argument(
		"--images-only",
		action="store_true",
		help="Download images only.",
	)

	media_group.add_argument(
		"--videos-only",
		action="store_true",
		help="Download videos only.",
	)

	parser.add_argument(
		"--output",
		type=Path,
		default=Path.home() / "Downloads" / "fap-dl",
		help="Download directory. Default: ~/Downloads/fap-dl",
	)

	return parser.parse_args()


def normalize_profile(value):
	value = value.strip()

	if value.startswith(("http://", "https://")):
		parsed = urlparse(value)
		value = parsed.path.strip("/").split("/")[0]
	else:
		value = value.strip("/")

	return value


def print_summary(
	post_numbers,
	image_posts,
	video_posts,
	image_results,
	video_results,
	base_dir,
	args,
):
	print()
	print("==============================")
	print("Complete")
	print("==============================")

	print(f"Posts found:       {len(post_numbers)}")
	print(f"Images found:      {len(image_posts)}")
	print(f"Videos found:      {len(video_posts)}")
	print()

	if not args.videos_only:
		downloaded, skipped, failed = image_results

		print(f"Images downloaded: {downloaded}")
		print(f"Images skipped:    {skipped}")
		print(f"Images failed:     {failed}")

	if not args.images_only:
		downloaded, skipped, failed, recovered = video_results

		print(f"Videos downloaded: {downloaded}")
		print(f"Videos skipped:    {skipped}")
		print(f"Videos recovered:  {recovered}")
		print(f"Videos failed:     {failed}")

	print(f"\nSaved to:\n{base_dir.resolve()}")


def main():
	args = parse_args()

	model = normalize_profile(args.profile)

	if not model:
		print("No profile name supplied.")
		return 1

	profile_url = f"https://fapello.com/{model}/"
	base_dir = args.output.expanduser() / model

	if args.combined:
		image_dir = base_dir
		video_dir = base_dir
		layout_name = "combined"
	else:
		image_dir = base_dir / "images"
		video_dir = base_dir / "videos"
		layout_name = "separate images/videos"

	post_pattern = re.compile(
		rf"^https://fapello\.com/"
		rf"{re.escape(model)}/(\d+)/?$"
	)

	print()
	print("fap-dl")
	print("======")
	print(f"Profile: {model}")
	print(f"Output:  {base_dir.resolve()}")
	print(f"Layout:  {layout_name}")

	if args.images_only:
		print("Media:   images only")
	elif args.videos_only:
		print("Media:   videos only")
	else:
		print("Media:   images + videos")

	print("Browser: headed discovery")

	try:
		with sync_playwright() as p:

			# Discover gallery.
			context, page = open_profile(
				p,
				profile_url,
				model,
				post_pattern,
				get_post_count,
			)

			load_gallery(
				page,
				model,
				post_pattern,
			)

			print("\nAnalyzing gallery...")

			posts = analyze_gallery(
				page,
				model,
				post_pattern,
			)

			post_numbers = sorted(
				posts.keys(),
				reverse=True,
			)

			image_posts = [
				number
				for number in post_numbers
				if not posts[number]["video"]
			]

			video_posts = [
				number
				for number in post_numbers
				if posts[number]["video"]
			]

			print()
			print("Gallery Summary")
			print("------------------")
			print(f"Posts:   {len(post_numbers)}")
			print(f"Images:  {len(image_posts)}")
			print(f"Videos:  {len(video_posts)}")

			# Transfer browser session.
			cookies = context.cookies()

			download_session = create_download_session(
				cookies
			)

			context.close()

			print(
				"\nBrowser closed. "
				"Starting downloads..."
			)

			image_results = (0, 0, 0)

			if not args.videos_only:
				image_results = download_images(
					download_session,
					posts,
					image_posts,
					image_dir,
				)

			video_downloaded = 0
			video_skipped = 0
			video_failed = 0
			video_recovered = 0

			if not args.images_only:
				(
					video_downloaded,
					video_skipped,
					failed_videos,
				) = download_videos(
					download_session,
					posts,
					video_posts,
					video_dir,
				)

				if failed_videos:
					resolved_urls = resolve_video_fallbacks(
						p,
						failed_videos,
					)

					(
						video_recovered,
						video_failed,
					) = retry_failed_videos(
						download_session,
						failed_videos,
						resolved_urls,
					)

			video_results = (
				video_downloaded,
				video_skipped,
				video_failed,
				video_recovered,
			)

			download_session.close()

			print_summary(
				post_numbers,
				image_posts,
				video_posts,
				image_results,
				video_results,
				base_dir,
				args,
			)

			return 0

	except KeyboardInterrupt:
		print("\n\nStopped by user.")
		return 130

	except Exception as exc:
		print(f"\nError: {exc}")
		return 1


if __name__ == "__main__":
	sys.exit(main())