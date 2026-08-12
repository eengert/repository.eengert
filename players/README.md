# Red Light players for TMDb Helper

These player definitions address episode playback compatibility between TMDb
Helper and Red Light 2.2.7 by including the episode `playcount` parameter Red
Light expects.

They use unique filenames and display names so an older player in TMDb
Helper's `reconfigured_players` directory cannot silently override the fix.

## Install

1. In TMDb Helper settings, set **Players URL** to:

   `https://eengert.github.io/repository.eengert/jsonplayers.zip`

2. Download the players and allow TMDb Helper to remove the existing
   downloaded players first.
3. Set **Default player for episodes** to **Red Light - Auto Play (Eengert
   Fix)**.

For source selection instead of autoplay, choose **Red Light - Source Select
(Eengert Fix)**.

## Upstream

The complete ZIP is based on
[OldManJax/helperplayers](https://github.com/OldManJax/helperplayers), licensed
under the Apache License 2.0. The only added definitions are the two JSON files
in this directory. Once the Apple TV compatibility test is confirmed, the
equivalent correction can be proposed to the upstream Red Light definitions.
