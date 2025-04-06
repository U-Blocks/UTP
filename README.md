![header](https://capsule-render.vercel.app/api?type=venom&height=150&color=gradient&text=UTP&fontColor=0:8871e5,100:b678c4&fontSize=50&desc=A%20de-commanded%20teleportation%20collection%20plug-in.&descAlignY=80&descSize=20&animation=fadeIn)

****

<code><a href="https://github.com/umarurize/UTP"><img height="25" src="https://github.com/umarurize/UTP/blob/master/logo/UTP.png" alt="UTP" /></a>&nbsp;UTP</code>

[![Minecraft - Version](https://img.shields.io/badge/minecraft-v1.21.60_(Bedrock)-black)](https://feedback.minecraft.net/hc/en-us/sections/360001186971-Release-Changelogs)
[![PyPI - Version](https://img.shields.io/pypi/v/endstone)](https://pypi.org/project/endstone)
![Total Git clones](https://img.shields.io/badge/dynamic/json?label=Total%20Git%clones&query=$&url=https://cdn.jsdelivr.net/gh/umarurize/UTP@master/clone_count.txt&color=brightgreen)

### Introductions
* **Rich features:** `Home`, `Warp`, `TPA`, `TPAHere`, `TPSetting`, `TPR`, `Back` (back to the last death point.)
* **Full GUI:** Beautiful GUI forms for easy operation rather than commands.
* **Hot reload support:** Operators can edit/update `config.json` in game directly.
* **Localized languages support**

### Installation
Put `.whl` file into the endstone plugins folder, and then start the server. Enter the command `/utp` to call out the main form.

### Download
Now, you can get the release version form this repo or <code><a href="https://www.minebbs.com/resources/utp.10159/"><img height="20" src="https://github.com/umarurize/umaru-cdn/blob/main/images/minebbs.png" alt="Minebbs" /></a>&nbsp;Minebbs</code>.

### File structure
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

### Configuration
UTP allows operators or players to edit/update relevant settings through GUI forms with ease, here are just simple explanations for these configurations.

`config.json`
```json
{
    "max_home_per_player": 10,  // the max number of homes a player can posses
    "tpr_range": 2000,  // the max random teleportation range
    "tpr_cool_down": 60,  // the cooldown time for calling the random teleportation
    "tpr_protect_time": 25,  // the protection time after calling the random teleportation
    "back_to_death_point_cool_down": 60  // the cooldown time for calling the back
    "is_enable": {
        "home": true,
        "warp": true,
        "tpa_and_tpahere": true,
        "tpr": true,
        "back": true
    }
}
```

### Languages
- [x] `zh_CN`
- [x] `en_US`

Off course you can add your mother language to UTP, just creat `XX_XX.json` (such as `ja_JP.json`) and translate value with reference to `en_US.json`.

You can also creat a PR to this repo to make your mother language one of the official languages of UTP.


### Screenshots
Due to the extreme ease of use of UTP, there is no wiki available. You can view related screenshots of UTP from images folder of this repo.

![](https://img.shields.io/badge/language-python-blue.svg) [![GitHub License](https://img.shields.io/github/license/umarurize/UTP)](LICENSE)

