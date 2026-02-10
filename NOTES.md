# Jianying Editor Usage Notes

## FFmpeg Limitations (macOS Homebrew)
- Homebrew bottle FFmpeg does NOT include libass — `subtitles` filter is unavailable.
- Workaround: `brew install ffmpeg --build-from-source` or use mpv for preview.

## Whisper API
- 25MB file size limit → split long audio into ~33min chunks (~20MB each)
- Use `verbose_json` response format + `segment` granularity for timestamps
