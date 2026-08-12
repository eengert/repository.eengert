# Red Light players for TMDb Helper

These player definitions address episode playback compatibility between TMDb
Helper and Red Light 2.2.7 by including the episode `playcount` parameter Red
Light expects.

They use neutral, unique filenames so older copies in TMDb Helper's
`reconfigured_players` directory cannot silently override the correction.

## Install

1. In TMDb Helper settings, set **Players URL** to:

   `https://eengert.github.io/repository.eengert/jsonplayers.zip`

2. Download the players and allow TMDb Helper to remove the existing
   downloaded players first.
3. Set **Default player for episodes** to **Red Light - Auto Play (Updated)**.

For source selection instead of autoplay, choose **Red Light - Source Select
(Updated)**.

## Upstream

The complete ZIP is based on
[OldManJax/helperplayers](https://github.com/OldManJax/helperplayers), licensed
under the Apache License 2.0. The updated Red Light definitions are the two
JSON files in this directory. The equivalent correction has been proposed to
the upstream project in
[OldManJax/helperplayers#4](https://github.com/OldManJax/helperplayers/pull/4).
