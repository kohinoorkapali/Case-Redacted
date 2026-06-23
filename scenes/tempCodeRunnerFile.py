def reset_video() -> None:
    """Reset frame index and start audio. Called by Game after pygame.init()."""
    global _video_frame_idx, _next_frame_at
    _video_frame_idx = 0
    _next_frame_at   = 0

    # Lazy-load on first call only — pygame is guaranteed to be up by now
    if not _VIDEO_LOADED:
        _try_load_video()

    _play_video_audio()