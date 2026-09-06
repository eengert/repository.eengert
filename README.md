# Eengert Kodi Repository

Personal Kodi repository for maintained add-ons and builds.

## Kodi File Manager source

```text
https://eengert.github.io/repository.eengert/
```

In Kodi, add that URL as a File Manager source, install
`repository.eengert-1.0.0.zip`, then open **Install from repository** and choose
**Eengert Repository**.

## Arctic Fuse 3 Patch Service

Install **Arctic Fuse 3 Patch Service** from **Services** in the Eengert
Repository. Kodi will then receive future service versions through the normal
repository update mechanism.

The service preserves these local Arctic Fuse 3 customizations after skin
updates:

- configurable Top-menu Up action (Submenu or Options)
- Home startup/reload focus-transition workaround
- horizontal Top-menu `Icon + Text` presentation

## Skin Settings Backup

Install **Skin Settings Backup** from **Program add-ons** (also listed under
**Services**) in the Eengert Repository. Open it from Program add-ons, select
**Choose destination**, then **Back up now** to create a protected snapshot.

Settings lets you choose the backup interval and retention count. The add-on
backs up standard skin settings and appearance selections, plus Arctic Fuse 3
menus, widgets, views and skin profiles. It skips unchanged automatic backups
and preserves protected snapshots. Backups run while Kodi is awake and idle.

Use **Restore backup** to select a restore point, or **Import backup ZIP** for
a backup from another device. Accept Kodi's skin-change prompts during restore.
Run the built-in **self-test** and verify a restore on each Apple TV before
relying on it. Other skins' separately stored helper settings may require an
additional adapter.

## Publishing a TMDb Helper build

Run the **Publish Kodi repository** workflow and provide:

- the source branch or commit from `eengert/plugin.video.themoviedb.helper`
- a numeric Kodi add-on version such as `6.16.901`

The workflow changes the version only in a temporary packaging copy. It never
modifies the source branch used for an upstream pull request.

## TMDb Helper player bundle

Use the following URL in TMDb Helper's **Players URL** setting:

```text
https://eengert.github.io/repository.eengert/jsonplayers.zip
```

This is the Old Man Jax player bundle with a Red Light 2.2.7 compatibility fix
for episode playback through TMDb Helper. Select **Red Light - Auto Play
(Updated)** as the default episode player. Its unique filename prevents older
reconfigured player files from overriding it.

The corrected definitions, public installation instructions, upstream
attribution, and troubleshooting notes are available in [players](players/).
