# Codec & Standards Reference

## Video Codecs

| Codec | Full Name | Notes |
|---|---|---|
| HEVC | High Efficiency Video Coding (H.265) | ~50% better compression than H.264 at equivalent quality; common for 4K/HDR broadcast. |
| H.264 | Advanced Video Coding (AVC) | Most widely supported codec; baseline for legacy compatibility. |
| VP9 | VP9 (Google) | Royalty-free, used heavily by YouTube and WebM delivery. |
| AV1 | AOMedia Video 1 | Royalty-free, next-gen successor to VP9; higher compression, higher encode cost. |
| MPEG-2 | MPEG-2 Part 2 | Legacy broadcast codec, still present in some cable/satellite feeds. |

## Audio Codecs

| Codec | Full Name | Notes |
|---|---|---|
| AAC | Advanced Audio Coding | Common streaming default; good quality at low bitrates. |
| AC-3 | Dolby Digital | 5.1 surround, widely used in broadcast. |
| E-AC-3 | Dolby Digital Plus | Extension of AC-3 supporting higher channel counts and bitrates. |
| Dolby Atmos | Object-based surround | Delivered over an E-AC-3 or TrueHD substream carrying spatial metadata. |
| DTS | Digital Theater Systems | Alternative surround codec to Dolby, common in Blu-ray/broadcast. |
| FLAC | Free Lossless Audio Codec | Lossless, used where bandwidth is not a constraint. |
| MP3 | MPEG-1 Audio Layer III | Legacy, low-complexity, broad compatibility. |
| Opus | Opus | Low-latency, royalty-free; strong for real-time/interactive streaming. |

## SCTE Standards Overview

- **SCTE-35**: Defines splice_info_section messages carried in-band in MPEG-TS streams to signal ad insertion points (cue-out/cue-in), program boundaries, and blackout events.
- **SCTE-104**: Defines the messaging protocol used by automation/traffic systems on the contribution side to trigger splice events, which are later encoded as SCTE-35 markers in the transport stream.
- **SCTE-224**: Defines the Event Scheduling and Notification Interface (ESNI) used for coordinating linear ad avail scheduling across systems.

This document will be expanded in Phase 2 with parsing details and links to the source specifications as the `mpeg_ts_parser` and `codec_analyzer` services are implemented.
