




"""
=============================================================================
 BeautyReel AI — Brand Reel Joiner
 Joins all 4 product videos into ONE professional brand reel
 Output: ~16 seconds | 9:16 Vertical | Instagram Ready | No music
=============================================================================
"""

from moviepy.editor import (
    VideoFileClip, concatenate_videoclips,
    ColorClip, CompositeVideoClip
)
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("BeautyReelJoiner")

# =============================================================================
#  ⚙️  VIDEO PATHS — Final_reels_videos_dataset folder
# =============================================================================

VIDEO_FILES = [
    r"Final_reels_videos_dataset\emani_powder_4s_reel.mp4",
    r"Final_reels_videos_dataset\flawless_lip_pencil_4s_reel.mp4",
    r"Final_reels_videos_dataset\luxury_concealer_4s_reel.mp4",
    r"Final_reels_videos_dataset\luxury_lipstick_4s_reel.mp4",
]

OUTPUT_FILE = r"Final_reels_videos_dataset\BeautyReel_Brand_Final.mp4"

TARGET_W = 1080
TARGET_H = 1920

# =============================================================================
#  🎬  Load & Resize Each Clip to 9:16
# =============================================================================

def prepare_clip(video_path: str) -> VideoFileClip:
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(
            f"\n❌ Video not found: {path.resolve()}"
            f"\n   Check that this file exists in Final_reels_videos_dataset folder."
        )

    clip    = VideoFileClip(str(path)).without_audio()
    scale   = min(TARGET_W / clip.w, TARGET_H / clip.h)
    resized = clip.resize(scale)

    bg = ColorClip(
        size     = (TARGET_W, TARGET_H),
        color    = (8, 8, 8),
        duration = clip.duration
    )

    x = (TARGET_W - resized.w) // 2
    y = (TARGET_H - resized.h) // 2

    composed = CompositeVideoClip([bg, resized.set_position((x, y))])
    log.info(f"✅ Loaded: {Path(video_path).name} ({clip.duration:.1f}s)")
    return composed


# =============================================================================
#  🔗  Join All Clips
# =============================================================================

def join_videos():
    print("\n" + "=" * 60)
    print("  💄  BeautyReel AI — Brand Reel Joiner")
    print("  Joining: Powder → Lip Pencil → Concealer → Lipstick")
    print("=" * 60 + "\n")

    clips = []
    for video_file in VIDEO_FILES:
        try:
            clip = prepare_clip(video_file)
            clips.append(clip)
        except FileNotFoundError as e:
            log.error(str(e))
            return

    log.info(f"\n🔗 Joining {len(clips)} clips...")
    final = concatenate_videoclips(clips, method="compose")

    total_duration = sum(c.duration for c in clips)
    log.info(f"📏 Total duration: {total_duration:.1f} seconds")
    log.info(f"💾 Exporting → {OUTPUT_FILE}")

    final.write_videofile(
        OUTPUT_FILE,
        fps     = 30,
        codec   = "libx264",
        bitrate = "8000k",
        audio   = False,
        logger  = None
    )

    print("\n" + "=" * 60)
    print("  ✅  BRAND REEL READY!")
    print(f"  🎥  File    : {OUTPUT_FILE}")
    print(f"  ⏱️   Duration: {total_duration:.1f} seconds")
    print(f"  📐  Format  : {TARGET_W}x{TARGET_H} (9:16 Vertical)")
    print(f"  🎵  Music   : Add your own in CapCut or Instagram!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    join_videos()



