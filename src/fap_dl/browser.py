from pathlib import Path
import subprocess
import sys

from playwright.sync_api import (
	Error as PlaywrightError,
	TimeoutError as PlaywrightTimeoutError,
)

from .gallery import get_video_fallback_url


def get_browser_data_dir():
	return Path.home() / ".fap-dl" / "browser"


def install_chromium():
	print()
	print("Chromium is required for browser discovery.")
	print("Installing Chromium for fap-dl...")
	print()

	try:
		subprocess.run(
			[
				sys.executable,
				"-m",
				"playwright",
				"install",
				"chromium",
			],
			check=True,
		)
	except subprocess.CalledProcessError as exc:
		raise RuntimeError(
			"Unable to install Chromium automatically. "
			"Run: python -m playwright install chromium"
		) from exc

	print()
	print("Chromium installation complete.")


def launch_browser(p):
	browser_data_dir = get_browser_data_dir()
	browser_data_dir.mkdir(
		parents=True,
		exist_ok=True,
	)

	try:
		return p.chromium.launch_persistent_context(
			user_data_dir=str(browser_data_dir),
			headless=False,
		)

	except PlaywrightError as exc:
		message = str(exc)

		# Playwright gives an "Executable doesn't exist"
		# error when its Chromium build has not yet been installed.
		if "Executable doesn't exist" not in message:
			raise

		install_chromium()

		return p.chromium.launch_persistent_context(
			user_data_dir=str(browser_data_dir),
			headless=False,
		)


def get_page(context):
	if context.pages:
		return context.pages[0]

	return context.new_page()


def open_profile(
	p,
	profile_url,
	model,
	post_pattern,
	get_post_count,
):
	context = launch_browser(p)
	page = get_page(context)

	print(f"\nOpening {profile_url}")

	try:
		page.goto(
			profile_url,
			wait_until="domcontentloaded",
			timeout=60000,
		)
	except PlaywrightTimeoutError:
		print(
			"Initial page load timed out; "
			"checking page anyway."
		)

	page.wait_for_timeout(2000)

	initial_count = get_post_count(
		page,
		model,
		post_pattern,
	)

	if initial_count == 0:
		print()
		print("No profile posts detected yet.")
		print(
			"If browser verification is displayed, "
			"complete it in the browser."
		)
		print()

		input(
			"Press Enter here when the profile is visible..."
		)

		page.wait_for_timeout(1000)

		initial_count = get_post_count(
			page,
			model,
			post_pattern,
		)

		if initial_count == 0:
			context.close()

			raise RuntimeError(
				"Still unable to detect profile posts."
			)

	return context, page


def resolve_video_fallbacks(
	p,
	failed_videos,
):
	if not failed_videos:
		return {}

	print()
	print("Resolving failed video URLs...")
	print("Opening browser for fallback lookup...")

	context = launch_browser(p)
	page = get_page(context)

	resolved = {}

	try:
		for index, item in enumerate(
			failed_videos,
			start=1,
		):
			post_number = item["post_number"]
			post_url = item["post_url"]

			print(
				f"[{index}/{len(failed_videos)}] "
				f"Post {post_number}",
				end=" ",
				flush=True,
			)

			try:
				video_url = get_video_fallback_url(
					page,
					post_url,
				)

				if video_url:
					resolved[post_number] = video_url
					print("✓ found")
				else:
					print("✗ no MP4 source")

			except Exception as exc:
				print(f"✗ {exc}")

	finally:
		context.close()

	print("Fallback browser closed.")

	return resolved