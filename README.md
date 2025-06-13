![header](https://capsule-render.vercel.app/api?type=venom&height=150&color=gradient&text=UTP&fontColor=0:8871e5,100:b678c4&fontSize=50&desc=A%20de-commanded%20teleportation%20collection%20plug-in.&descAlignY=80&descSize=20&animation=fadeIn)

****

<code><a href="https://github.com/umarurize/UTP"><img height="25" src="https://github.com/umarurize/UTP/blob/master/logo/UTP.png" alt="UTP" /></a>&nbsp;UTP</code>

![Total Git clones](https://img.shields.io/badge/dynamic/json?label=Total%20Git%20clones&query=$&url=https://cdn.jsdelivr.net/gh/umarurize/UTP@master/clone_count.txt&color=brightgreen)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/umarurize/UTP/total)

### :bell:Introductions
* **Rich features:**
- [x] Home
- [x] Warp
- [x] TPA
- [x] TPAHere
- [x] TPSetting
- [x] TPR
- [x] Back (back to the last death point.)
- [x] Home & Warp navigation (distance and yaw angle)
- [x] Death penalty (UMoney required)
* **Full GUI:** Beautiful GUI forms for easy operation rather than commands.
* **Hot reload support:** Operators can edit/update `config.json` in game directly.
* **Localized languages support**

### :hammer:Installation
[Optional pre-plugin] ZX_UI
[Optional pre-plugin] UMoney

Put `.whl` file into the endstone plugins folder, and then start the server. Enter the command `/utp` to call out the main form.

### :computer:Download
Now, you can get the release version form this repo or <code><a href="https://www.minebbs.com/resources/utp.10159/"><img height="20" src="https://github.com/umarurize/umaru-cdn/blob/main/images/minebbs.png" alt="Minebbs" /></a>&nbsp;Minebbs</code>.

### :file_folder:File structure
```
Plugins/
├─ utp/
│  ├─ config.json
│  ├─ home.json
│  ├─ warp.json
│  ├─ tp_setting.json
│  ├─ lang/
│  │  ├─ zh_CN.json
│  │  ├─ en_US.json
```

### :pencil:Configuration
UTP allows operators or players to edit/update relevant settings through GUI forms with ease, here are just simple explanations for these configurations.

`config.json`
```json5
{
    "max_home_per_player": 10,  // the max number of homes a player can posses
    "tpr_range": 2000,  // the max random teleportation range
    "tpr_cool_down": 60,  // the cooldown time in seconds for calling the random teleportation
    "tpr_protect_time": 25,  // the protection time in seconds after calling the random teleportation
    "back_valid_time": 60,  // the valid time in seconds for calling the back
    "navigation_valid_time": 300,  // the valid time in seconds for every single navigation
    "death_penalty_money": 500,    // the money reduced by death penalty
    "death_penalty_money_threshold": 10000,    // the money threshold of death penalty
    "is_enable": {
        "home": true,
        "warp": true,
        "tpa_and_tpahere": true,
        "tpr": true,
        "back": true,
        "death_penalty": false
    }
}
```

`home.json`
```json5
{
    "umaru rize": {    // Home owner
        "test home": { // Home name
            "loc": [    // Home coordinates
                -285,
                49,
                -250
            ],
            "dim": "Nether"    // Home dimension
        }
    }
}
```

`warp.json`
```json5
{
    "test warp": {    // Warp name
        "loc": [    // Warp coordinates
            437,
            71,
            249
        ],
        "dim": "Overworld"    // Warp dimension
    }
}
```

`tp_setting.json`
```json5
{
    "umaru rize": true,    // if false, TPA or TPAHere requests from other players will be blocked
    "handaozhang520": true
}
```

### :globe_with_meridians:Languages
- [x] `zh_CN`
- [x] `en_US`

Off course you can add your mother language to UTP, just creat `XX_XX.json` (such as `ja_JP.json`) and translate value with reference to `en_US.json`.

You can also creat a PR to this repo to make your mother language one of the official languages of UTP.


### :camera:Screenshots
Due to the extreme ease of use of UTP, there is no wiki available. You can view related screenshots of UTP from images folder of this repo.

![](https://img.shields.io/badge/language-python-blue.svg) [![GitHub License](https://img.shields.io/github/license/umarurize/UTP)](LICENSE)

