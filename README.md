# Eengert Kodi Repository

Personal Kodi repository for maintained builds of TMDb Helper.

## Kodi File Manager source

```text
https://eengert.github.io/repository.eengert/
```

In Kodi, add that URL as a File Manager source, install
`repository.eengert-1.0.0.zip`, then open **Install from repository** and choose
**Eengert Repository**.

## Publishing a TMDb Helper build

Run the **Publish Kodi repository** workflow and provide:

- the source branch or commit from `eengert/plugin.video.themoviedb.helper`
- a numeric Kodi add-on version such as `6.16.901`

The workflow changes the version only in a temporary packaging copy. It never
modifies the source branch used for an upstream pull request.
