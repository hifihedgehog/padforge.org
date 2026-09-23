# Updates Internals

*How PadForge finds a newer build, proves the download, and replaces its own running exe.*

For the user-facing side see [Updates](../features/updates.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Services/UpdateService.cs` | The check, the download and its checksum, the record of an install waiting for the next launch, the handover to the helper, the swap, the lease, and the cleanup. |
| `PadForge.App/Services/UpdateController.cs` | The Updates card: the timer, Check Now, Install and Restart, the background download, and every status line. UI thread only. |
| `PadForge.App/App.xaml.cs` | `OnStartup`: helper mode, the lease check, the single-instance lock, and the waiting install. The helper's two dialogs. |
| `PadForge.App/PadForge.App.csproj` | `StampBuildIdentity`, which writes the build's commit count and hash into the assembly. |
| `.github/workflows/build.yml` | The rolling dev release the pre-release channel reads. |

---

## Build identity

`StampBuildIdentity` runs before `CoreCompile` and writes `PadForgeBuildIdentity.g.cs` into the intermediate folder with three `AssemblyMetadata` attributes:

| Key | Value |
| --- | --- |
| `PadForgeBuildNumber` | `git rev-list --count HEAD`, the commit count |
| `PadForgeCommit` | `git rev-parse --short=7 HEAD` |
| `PadForgeCommitSha` | `git rev-parse HEAD`, all 40 characters |

It stamps nothing unless git answers, the repository's top level is the solution folder, the clone is not shallow, and `HEAD` holds `PadForge.App/PadForge.App.csproj`. A shallow clone would report a wrong count, and a checkout nested in another repository would report that repository's. The target empties the three properties before it reads git, so `/p:PadForgeBuildNumber=...` on the command line changes nothing. To make a build that counts as newer for a test, commit locally, publish, and reset back.

`BuildIdentity` reads the attributes. `Display` is `4.5.3 (r3682@176208e)`, or the version alone for a build with no count. The version comes from `SharedVersion.cs`, and releases compare its first three parts, since the fourth is always 0 and never appears in a tag.

---

## Channels

| Channel | Endpoint | Newer means |
| --- | --- | --- |
| Releases | `repos/hifihedgehog/PadForge/releases/latest` | A higher version than this build's. GitHub never answers this endpoint with a pre-release. |
| Pre-releases | `repos/hifihedgehog/PadForge/releases/tags/latest-v{major}-dev` | A higher commit count, parsed from the title `PadForge r{count}@{hash}`. |

`build.yml` republishes the dev release for each push to the dev branch, unless a newer commit is already published, with exactly that title and the assets `PadForge.zip` and, when the ARM64 build succeeded, `PadForge-arm64.zip`. A comment there says the updater depends on all three.

`IsNewerDevBuild` counts a published build as newer when this build has no count, when its count is higher, or when the count is the same and the commit differs, which is a rewritten history. The check and the launch-time install both ask it, so they never disagree.

With **Include Pre-Releases** on, `CheckAsync` reads the dev feed first and then `releases/latest` as well, because the feed is one per major version and a copy on the old major's feed would never hear of the next major. A newer release is offered when the dev feed has nothing newer, or when its major version is higher than this build's. The card says up to date only when both reads found nothing newer: a release read that failed, was rate limited, or found no build for this PC is reported instead. After a rate-limited answer, nothing more is asked.

### A release replaced under its own version

A release is sometimes pulled and published again, fixed, under the same version, as 4.5.2 was. A build of the first one would compare equal and never hear of the fix. So when the release channel finds this build's own version, Include Pre-Releases is off, and this build carries a full commit hash, `LookUpReplacementAsync` resolves the release tag to its commit, following up to four annotated tag objects, and reads that commit's history, 100 commits deep (`HistoryDepth`). `PlaceInHistory` then places this build:

- first in the list: the release is this build, so it is up to date
- further down: the release descends from this build, so it is newer and is offered as *4.5.3 (1a2b3c4)*
- absent: this build is ahead, on another line, or more than 100 commits behind, and nothing is offered

Only public data leaves the machine. The tag and the commit came from GitHub, and this build's own commit is looked for locally, never sent. Before offering, the check reads `releases/latest` a second time and requires the same release id, the same tag, and the same asset name, digest and URL for this machine (`SameRelease`), so a release replaced while the requests ran is judged at the next check rather than paired with the wrong commit.

---

## Picking and proving the file

`SelectAsset` takes the asset for the machine, not the process: `-win-arm64.zip` or `PadForge-arm64.zip` on an ARM64 machine, `-win-x64.zip` or `PadForge.zip` elsewhere. An x64 copy running under emulation on ARM64 therefore moves to the native build, the same rule the MIDI Services installer follows.

An asset is offered only with a GitHub `digest` of the form `sha256:<64 hex>` and a download URL that is HTTPS on `github.com` under `/hifihedgehog/PadForge/releases/download/`. GitHub computes the digest on upload and serves it over the same API the check reads.

`DownloadAsync` streams the zip into the offer's staging folder and hashes it as the bytes arrive (`CopyAndHashAsync`). Every read has its own 60-second deadline (`DownloadStallTimeout`), because `HttpClient`'s own timeout stops counting once the headers arrive on a streamed body. A mismatch throws `UpdateVerificationException` and the folder is deleted. `ExtractExe` then takes the zip's root `PadForge.exe` only, hashing it as it is written, and the zip is deleted.

The API client times out after 15 seconds and the download client after 30 seconds for the response headers. Both send `PadForge/{version}` as the User-Agent, which GitHub requires, and that version is the only data PadForge sends.

GitHub allows 60 unauthenticated API requests an hour per address. `IsRateLimited` reads a 429, or a 403 carrying `Retry-After`, `x-ratelimit-remaining: 0`, or a body naming the secondary rate limit, as a rate limit. Any other 403 is a failure.

---

## The staging folder

Everything lives under `%TEMP%\PadForge_Update`, never beside `PadForge.exe`:

```
%TEMP%\PadForge_Update\
    <install key>\                 one per installed copy
        target.txt                 the exe this folder belongs to
        pending.json               an install waiting for the next launch
        v4.5.4-1a2b3c4d5e6f\       a release download: version and 12 hex of its SHA-256
            PadForge.exe
        r3700-1a2b3c4d5e6f\        a dev download: commit count and 12 hex
            PadForge.exe
        recovery-<attempt>\        the previous exe, kept by the last install
            PadForge.exe
```

The install key is the first 16 hex characters of the SHA-256 of the installed exe's full path, taken in upper case, so two portable copies never install, delete or reuse each other's files.

---

## Installing

Windows will not overwrite an exe while it runs. PadForge follows two references here: DS4Windows hands the swap to a helper that waits for the app to close, and OpenTabletDriver's elevated path runs its own binary with an update verb. The downloaded exe runs from the staging folder as the helper. OpenTabletDriver's other approach, moving the running files aside, only works on the same volume and would leave a file beside `PadForge.exe`, so PadForge does not use it.

### This copy's side

`StartHelper` creates two named events for the attempt, `Local\PadForge_Update_<attempt>_Ready` and `_Commit`. It hashes the staged exe through a handle that denies writes and deletion, compares the result with the hash recorded when the file was written, and starts the helper while that handle is still open:

```
PadForge.exe --apply-update <installed exe> <this PID> --handshake <attempt> <SHA-256> <commit or -> [original arguments]
```

The commit is the one the offer named, a dev build's or a replaced release's, or `-` when it named none. The original arguments come from `App.StartupArgs`, without any `--updated` marker a previous update left.

The helper has 60 seconds (`HelperReadyTimeout`) to set Ready. If it does not, exits first, or the operation is canceled, it is killed and waited for up to ten seconds, and unless the operation was canceled, the card says why. A helper that will not stop is reported as `HelperFailure.NotStopped`. Once Ready is set, `UpdateController` sets Commit on the UI thread and exits through the app's normal shutdown. The channel switch also runs on that thread, so a change to Include Pre-Releases lands either before the commit, which it then stops, or after it, when PadForge is already on its way out.

### The helper's side

`App.OnStartup` calls `TryRunApplyMode` before anything else, because the old copy still holds the single-instance lock while it closes. When the first argument is `--apply-update`, the process is the helper and never goes on to start PadForge from the staging folder.

1. **Right build.** When the offer named a commit, the helper compares it with its own stamped commit, which must be at least as long and start with it. Anything else exits with code 3 (`WrongBuildExitCode`), and the old copy reports that the download is a different build from the one the update names. This catches a tag moved before its file was replaced, or a dev title published before its zip.
2. **Lease.** It creates the named mutex `Global\PadForge_UpdateLease_<install key>` exclusively. Global, so a launch in another session sees it too. A second helper for the same exe finds it taken and stops before it reports ready, and an ordinary launch of that exe (`IsUpdateInProgress` in `OnStartup`) leaves quietly while the lease exists.
3. **Handshake.** It sets Ready and waits for Commit for as long as the old copy runs. The old copy exiting without a commit means install nothing.
4. **Wait for the old copy.** Every two minutes (`OldCopyNoticeInterval`) it asks whether to keep waiting, in a small window that answers itself once the old copy exits. Cancel skips the update, and PadForge still starts again once the old copy has closed.
5. **Swap.** `Swap` copies the installed exe into `recovery-<attempt>` and checks it against its hash, then copies itself over the installed exe and checks that against the payload hash. If the second step fails, the old exe goes back and is checked again. Each step makes up to 60 attempts, 500 ms apart, while antivirus or the loader holds a file, and no retry writes over the only good copy.
6. **Restart.** On success it starts the installed exe with `--updated` in front of the original arguments, and the new copy's status bar says it was updated. A failure to start names the recovery folder. A failed swap that restored the old exe restarts it and reports the error. A swap that could not restore it names the folder that holds the copy, and starts nothing.

The helper runs before settings load and before any window exists, so its two dialogs follow the Windows display language rather than PadForge's own.

A dev build from before the handshake (`c935af76`, the feature's first commit) starts the helper without `--handshake` and exits at once, so for it the helper treats its own start as the commit.

---

## Installing at the next launch

With **Install Updates Automatically** on, a check that finds a newer build downloads it and writes `pending.json`: the offer, the channel it was staged for, the installed exe it replaces, the staged exe and its hash, and `Attempted`. A replaced release also records this build's full commit, because it is newer only while this copy is still that exact commit. The record is written to a `.tmp` file and moved over, so a crash never leaves half a record.

`TryStartPendingInstall` runs in `OnStartup` after the single-instance lock and before the engine, the drivers or any window start. `DecidePending` settles it:

| Record | Action |
| --- | --- |
| Not newer than this build | Deleted quietly. That attempt worked, and only deleting the record failed. |
| Newer, and `Attempted` set | Deleted, and reported once: the last attempt never finished. |
| Settings file unreadable | Left for the next launch. |
| Either automatic switch now off, or the other channel | Deleted. |
| For another exe, or its staged exe gone | Deleted. |
| Otherwise | `Attempted` is written, then the helper starts and is committed at once. |

Setting `Attempted` before the helper starts is what keeps a broken download from restarting PadForge in a loop. `ReadUpdatePreferences` reads the three switches straight from `PadForge.xml` because the settings service has not loaded yet. A missing element takes the default: checking on, installing off, releases only.

---

## The card

`UpdateController` runs one operation at a time: a check, which also stages what it finds while Install Updates Automatically is on, a background staging, or an install. What an operation writes to the card after an await lands only while it is still the running operation and its offer is still the offer. An automatic check asked for while busy runs once idle.

The first timer tick comes 20 seconds after launch and later ticks every 12 hours. The shape, a check at start plus a timer, follows HandheldCompanion's UpdateManager at a slower cadence, since GitHub's unauthenticated allowance is 60 requests an hour per address.

The first tick also asks for the cleanup, since a copy that has run 20 seconds from this exe shows the exe works. The cleanup waits until no operation runs, and every download that starts after it waits for it to finish.

| Setting change | Effect |
| --- | --- |
| Include Pre-Releases | Cancels the running operation, clears the offer, deletes the pending record, and checks again if the automatic check is on. |
| Install Updates Automatically off | Deletes the pending record, so nothing installs at the next launch. |
| Install Updates Automatically on, with an offer | Stages the offer now. |
| Check for Updates Automatically off | Drops a queued check and deletes the pending record. |

A check that comes back up to date, or finds no build for this PC, deletes the pending record too, so a pulled release never installs behind the card.

Every line is worded when it is shown, so the card follows a language change. The reasons for a stalled download and for an installer that failed are translated. Any other reason, an HTTP status, a note from the check such as `unexpected release data`, or an error from Windows or the network, is shown as it came.

---

## Cleanup

`CleanupStagingAsync` never runs from inside the staging folder, nor while a helper holds the lease. It deletes what the feature's first dev builds left at the top level (a shared `pending.json` and `r…` or `v…` folders), then deletes every subfolder of this copy's folder except the download the pending record names, recovery copies included. A record it cannot read, because antivirus or a backup holds it, leaves the folder alone. A record that reads but does not parse was not written by PadForge and is deleted. Other copies' folders are never touched: their exe may sit on a drive that is not plugged in, and their recovery copy may be the only good one. A locked folder is tried again, up to ten passes three seconds apart.

---

## Couplings

Renaming any of these breaks updating for every installed copy:

- Release tags `vX.Y.Z` with no suffix. `ParseTag` refuses anything like `-rc1` rather than guess.
- Release assets `PadForge-vX.Y.Z-win-x64.zip` and `PadForge-vX.Y.Z-win-arm64.zip`, each with `PadForge.exe` at the root.
- The dev release's tag `latest-v{major}-dev`, its title `PadForge r{count}@{hash}`, and its assets `PadForge.zip` and `PadForge-arm64.zip`.
- A GitHub `digest` on every asset. An asset without one is never offered.

---

## Limits

- A helper from a dev build before the handshake still installs when the copy that started it crashes before stopping it.
- A release rebuilt from the same commit under the same version is not offered.
- The replaced-release lookup reads 100 commits. A build further behind than that is not offered the replacement.
- Nothing has run on ARM64 hardware.

Tests: `UpdateServiceTests`, `UpdateControllerTests` and `UpdateStatusCultureTests` in `PadForge.Tests`.

---

## Related pages

- [Updates](../features/updates.md)
- [Settings and Serialization](settings-and-serialization.md): the three switches in `PadForge.xml`.
- [Build and Publish](build-and-publish.md): how releases are built.
- [Services Layer](services-layer.md)

---

*Last updated for PadForge 4.5.3.*
