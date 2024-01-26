# palworld-save-tools
Tools for converting Palworld .sav files to JSON and back.

> [!IMPORTANT]
> This tool has changed how the JSON files are formatted starting with v0.9.
> You cannot load JSON files created by older versions of the tool, and other tools that depend on the JSON output of `palworld-save-tools` will break.
> In exchange, you will no longer need `uesave-rs`, the tool runs faster, and doesn't use as much RAM.

> [!CAUTION]
> Any versions older than v0.4 will create corrupt `Level.sav` files when converting from JSON to SAV. Please make sure to update to avoid data corruption.

This tool currently supports additional parsing of the following data not handled by `uesave` or other non-Palworld aware Unreal save editors:

1. `Level.sav`:`GroupSaveDataMap`
    - Groups such as in-game organizations and guilds
1. `Level.sav`:`CharacterSaveParameterMap`
    - Characters such as players and pals

## Converting co-op saves to dedicated server saves

Please follow the instructions provided over at https://github.com/xNul/palworld-host-save-fix

## Instructions

> [!IMPORTANT]
> Converting `Level.sav` files to JSON will result in very large files, and may require significant amounts of RAM to process. Use a modern text editor such as Visual Studio Code or a Jetbrains IDE to open these files.

### Prerequisites

1. Python 3.9 or newer.
    - Windows users: You can install [Python 3.12 from the Microsoft Store](https://apps.microsoft.com/detail/9NCVDN91XZQP)

### Windows steps

1. Download the latest release from [https://github.com/cheahjs/palworld-save-tools/releases/latest].
1. Unzip the file into a folder.
1. Drag and drop your `.sav` file (for Steam on Windows, these are located at `%LOCALAPPDATA%\Pal\Saved\SaveGames\<SteamID>\<SaveID>`) onto `convert-single-sav-to-json.cmd`.
1. To convert the `.sav.json` file back into a `.sav` file, drag and drop your `.sav.json` file onto `convert-single-json-to-sav.cmd`.
