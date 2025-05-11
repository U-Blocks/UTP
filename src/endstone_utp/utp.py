import os
import json
import time
import math

from endstone import Player, ColorFormat
from endstone.plugin import Plugin
from endstone.level import Location
from endstone.scheduler import Task
from endstone.event import event_handler, PlayerJoinEvent, PlayerDeathEvent, PlayerQuitEvent
from endstone.command import Command, CommandSender, CommandSenderWrapper
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput, Toggle

from endstone_utp.lang import lang

current_dir = os.getcwd()

first_dir = os.path.join(current_dir, 'plugins', 'utp')
if not os.path.exists(first_dir):
    os.mkdir(first_dir)

lang_dir = os.path.join(first_dir, 'lang')
if not os.path.exists(lang_dir):
    os.mkdir(lang_dir)

home_data_file_path = os.path.join(first_dir, 'home.json')
warp_data_file_path = os.path.join(first_dir, 'warp.json')
tp_setting_file_path = os.path.join(first_dir, 'tp_setting.json')
config_data_file_path = os.path.join(first_dir, 'config.json')
menu_file_path = os.path.join('plugins', 'zx_ui')


class utp(Plugin):
    api_version = '0.7'

    def __init__(self):
        super().__init__()
        # Load home data
        if not os.path.exists(home_data_file_path):
            home_data = {}
            with open(home_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(
                    home_data,
                    indent=4,
                    ensure_ascii=False
                )
                f.write(json_str)
        else:
            with open(home_data_file_path, 'r', encoding='utf-8') as f:
                home_data = json.loads(f.read())
        self.home_data = home_data

        # Load warp data
        if not os.path.exists(warp_data_file_path):
            warp_data = {}
            with open(warp_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(
                    warp_data,
                    indent=4,
                    ensure_ascii=False
                )
                f.write(json_str)
        else:
            with open(warp_data_file_path, 'r', encoding='utf-8') as f:
                warp_data = json.loads(f.read())
        self.warp_data = warp_data

        # Load TPSetting data
        if not os.path.exists(tp_setting_file_path):
            tp_setting_data = {}
            with open(tp_setting_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(
                    tp_setting_data,
                    indent=4,
                    ensure_ascii=False
                )
                f.write(json_str)
        else:
            with open(tp_setting_file_path, 'r', encoding='utf-8') as f:
                tp_setting_data = json.loads(f.read())
        self.tp_setting_data = tp_setting_data

        # Load config data
        if not os.path.exists(config_data_file_path):
            config_data = {
                'max_home_per_player': 5,
                'tpr_range': 2000,
                'tpr_cool_down': 60,
                'tpr_protect_time': 20,
                'back_valid_time': 30,
                'navigation_valid_time': 300,
                'is_enable': {
                    'home': True,
                    'warp': True,
                    'tpa_and_tpahere': True,
                    'tpr': True,
                    'back': True
                }
            }
            with open(config_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(
                    config_data,
                    indent=4,
                    ensure_ascii=False
                )
                f.write(json_str)
        else:
            with open(config_data_file_path, 'r', encoding='utf-8') as f:
                config_data = json.loads(f.read())
        self.config_data = config_data

        # Load lang data
        self.lang_data = lang.load_lang(self, lang_dir)

        self.record_tpr = {}
        self.record_death = {}
        self.record_navigation = {}

    def on_enable(self):
        self.sender_wrapper = CommandSenderWrapper(
            self.server.command_sender,
            on_message=None
        )

        self.register_events(self)
        self.logger.info(
            f'{ColorFormat.YELLOW}'
            f'UTP is enabled...'
        )

    commands = {
        'utp': {
            'description': 'Call out the main form of UTP',
            'usages': ['/utp'],
            'permissions': ['utp.command.utp']
        }
    }

    permissions = {
        'utp.command.utp': {
            'description': 'Call out the main form of UTP',
            'default': True
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> None:
        if command.name == 'utp':
            if not isinstance(sender, Player):
                sender.send_message(
                    f'{ColorFormat.RED}'
                    f'This command can only be executed by a player...'
                )
                return

            player = sender

            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "main_form.title")}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "main_form.content")}',
            )

            if self.config_data['is_enable']['home']:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.home")}',
                    icon='textures/items/ender_pearl',
                    on_click=self.home
                )

            if self.config_data['is_enable']['warp']:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.warp")}',
                    icon='textures/ui/worldsIcon',
                    on_click=self.warp
                )

            if self.config_data['is_enable']['tpa_and_tpahere']:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.tpa_and_tpahere")}',
                    icon='textures/ui/dressing_room_customization',
                    on_click=self.tpa_and_tpahere
                )

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.tp_setting")}',
                    icon='textures/ui/icon_setting',
                    on_click=self.tp_setting
                )

            if self.config_data['is_enable']['tpr']:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.tpr")}',
                    icon='textures/ui/icon_random',
                    on_click=self.tpr
                )

            if self.config_data['is_enable']['back']:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.back")}',
                    icon='textures/ui/friend_glyph_desaturated',
                    on_click=self.back_to_last_death_point
                )

            if player.is_op:
                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.reload")}',
                    icon='textures/ui/icon_setting',
                    on_click=self.reload_config_data
                )

            if not os.path.exists(menu_file_path):
                main_form.on_close = None

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.close")}',
                    icon='textures/ui/cancel',
                    on_click=None
                )
            else:
                main_form.on_close = self.back_to_menu

                main_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "main_form.button.back_to_zx_ui")}',
                    icon='textures/ui/refresh_light',
                    on_click=self.back_to_menu
                )

            if not player.is_op:
                function_enable_num = 0
                for function_status in self.config_data['is_enable'].values():
                    if function_status:
                        function_enable_num += 1

                if function_enable_num == 0:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "open_main_form.message.fail")}'
                    )
                    return

            player.send_form(main_form)

    # Home
    def home(self, player: Player) -> None:
        home_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "home_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "home_form.content")}...',
            on_close=self.back_to_main_form
        )

        home_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "home_form.button.addhome")}',
            icon='textures/ui/color_plus',
            on_click=self.add_home
        )

        for home_name, home_info in self.home_data[player.name].items():
            home_loc = home_info['loc']
            home_dim = home_info['dim']

            home_form.add_button(
                f'{ColorFormat.WHITE}'
                f'{home_name}\n'
                f'{ColorFormat.YELLOW}'
                f'[{self.get_text(player, "dimension")}]: {home_dim}',
                icon='textures/items/ender_eye',
                on_click=self.home_info(home_name, home_loc, home_dim)
            )

        home_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.back_to_main_form
        )

        player.send_form(home_form)

    # Add home
    def add_home(self, player: Player) -> None:
        home_player_already_has = [key for key in self.home_data[player.name].keys()]

        if len(home_player_already_has) >= self.config_data['max_home_per_player']:
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "addhome.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "addhome.message.fail_reason_2")}'
            )
            return

        loc = [
            int(player.location.x),
            int(player.location.y),
            int(player.location.z)
        ]
        dim = player.dimension.name

        textinput = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'[{self.get_text(player, "coordinates")}]: '
                  f'{ColorFormat.WHITE}'
                  f'({loc[0]}, {loc[1]}, {loc[2]})\n'
                  f'{ColorFormat.GREEN}'
                  f'[{self.get_text(player, "dimension")}]: '
                  f'{ColorFormat.WHITE}'
                  f'{dim}\n\n'
                  f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "addhome_form.textinput.label")}',
            placeholder=f'{self.get_text(player, "addhome_form.textinput.placeholder")}'
        )

        add_home_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "addhome_form.title")}',
            controls=[textinput],
            on_close=self.home,
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "addhome_form.submit_button")}'
        )

        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)

            if len(data[0]) == 0:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "message.type_error")}'
                )
                return

            if data[0] in home_player_already_has:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "addhome.message.fail")}: '
                    f'{ColorFormat.WHITE}' +
                    self.get_text(player, "addhome.message.fail.reason_1").format(data[0])
                )
                return

            home_name = data[0]
            self.home_data[player.name][home_name] = {
                'loc': loc,
                'dim': dim
            }
            self.save_home_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "addhome.message.success")}'
            )

        add_home_form.on_submit = on_submit

        player.send_form(add_home_form)

    # Home info
    def home_info(self, home_name, home_loc, home_dim):

        def on_click(player: Player):
            home_info_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "home_info_form.title")}: {home_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "home_info_form.content")}',
                on_close=self.home
            )

            home_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "home_info_form.button.tp")}',
                icon='textures/ui/realmsIcon',
                on_click=self.home_tp(home_loc, home_dim)
            )

            destination_type = 'home'
            home_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "navigate")}',
                icon='textures/ui/pointer',
                on_click=self.start_navigation(destination_type, home_name, home_loc, home_dim)
            )

            home_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "home_info_form.button.edithome")}',
                icon='textures/ui/hammer_l',
                on_click=self.home_edit(home_name, home_loc, home_dim)
            )

            home_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.home
            )

            player.send_form(home_info_form)

        return on_click

    # Home edit
    def home_edit(self, home_name, home_loc, home_dim):

        def on_click(player: Player):
            home_edit_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "edithome_form.title")}: {home_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "edithome_form.content")}',
                on_close=self.home
            )

            home_edit_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "edithome_form.button.updatehome")}',
                icon='textures/ui/refresh',
                on_click=self.home_update(home_name)
            )

            home_edit_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "edithome_form.button.deletehome")}',
                icon='textures/ui/cancel',
                on_click=self.home_delete(home_name, home_loc, home_dim)
            )

            home_edit_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.home
            )

            player.send_form(home_edit_form)

        return on_click

    # Home update
    def home_update(self, home_name):

        def on_click(player: Player):
            home_update_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "updatehome_form.title")}: {home_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "updatehome_form.content")}',
                on_close=self.home,
            )

            home_update_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "updatehome_form.button.renamehome")}',
                icon='textures/ui/icon_book_writable',
                on_click=self.home_update_name(home_name)
            )

            home_update_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "updatehome_form.button.updatelocation")}',
                icon='textures/ui/realmsIcon',
                on_click=self.home_update_tp(home_name)
            )

            home_update_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.home
            )

            player.send_form(home_update_form)

        return on_click

    # Home rename
    def home_update_name(self, home_name):

        def on_click(player: Player):
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "renamehome_form.textinput.label")}',
                default_value=home_name,
                placeholder=f'{self.get_text(player, "renamehome_form.textinput.placeholder")}'
            )

            home_update_name_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "renamehome_form.title")}: {home_name}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "renamehome_form.submit_button")}',
                on_close=self.home
            )

            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)

                if len(data[0]) == 0:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "message.type_error")}'
                    )
                    return

                new_home_name = data[0]

                home_player_already_has = [key for key in self.home_data[player.name].keys()]
                if new_home_name in home_player_already_has:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "renamehome.message.fail")}: '
                        f'{ColorFormat.WHITE}' +
                        self.get_text(player, "renamehome.message.fail.reason").format(data[0])
                    )
                    return

                self.home_data[player.name][new_home_name] = self.home_data[player.name][home_name]
                if new_home_name != home_name:
                    self.home_data[player.name].pop(home_name)
                self.save_home_data()

                player.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "renamehome.message.success")}'
                )

            home_update_name_form.on_submit = on_submit

            player.send_form(home_update_name_form)

        return on_click

    # Home teleport point update
    def home_update_tp(self, home_name):

        def on_click(player: Player):
            new_home_loc = [
                int(player.location.x),
                int(player.location.y),
                int(player.location.z)
            ]
            new_home_dim = player.dimension.name

            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "home_updatelocation_form.title")}{home_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "home_updatelocation_form.content")}\n'
                        f'[{self.get_text(player, "coordinates")}]: '
                        f'{ColorFormat.WHITE}'
                        f'({new_home_loc[0]}, {new_home_loc[1]}, {new_home_loc[2]})\n'
                        f'{ColorFormat.GREEN}'
                        f'[{self.get_text(player, "dimension")}]: '
                        f'{ColorFormat.WHITE}'
                        f'{new_home_dim}',
                on_close=self.home
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "home_updatelocation_form.button.confirm")}',
                icon='textures/ui/realms_slot_check',
                on_click=self.home_update_tp_confirm(home_name, new_home_loc, new_home_dim)
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.home
            )

            player.send_form(confirm_form)

        return on_click

    def home_update_tp_confirm(self, home_name, new_home_loc, new_home_dim):

        def on_click(player: Player):
            self.home_data[player.name][home_name]['loc'] = new_home_loc
            self.home_data[player.name][home_name]['dim'] = new_home_dim
            self.save_home_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "home_updatelocation.message.success")}'
            )

        return on_click

    # Home delete
    def home_delete(self, home_name, home_loc, home_dim):

        def on_click(player: Player):
            confirm_form = ActionForm(
                 title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                       f'{self.get_text(player, "deletehome_form.title")}: {home_name}',
                 content=f'{ColorFormat.GREEN}'
                         f'{self.get_text(player, "deletehome_form.content")}\n'
                         f'[{self.get_text(player, "coordinates")}]: '
                         f'{ColorFormat.WHITE}'
                         f'({home_loc[0]}, {home_loc[1]}, {home_loc[2]})\n'
                         f'{ColorFormat.GREEN}'
                         f'[{self.get_text(player, "dimension")}]: '
                         f'{ColorFormat.WHITE}'
                         f'{home_dim}',
                 on_close=self.home
            )

            confirm_form.add_button(
                 f'{ColorFormat.YELLOW}'
                 f'{self.get_text(player, "deletehome_form.button.confirm")}',
                 icon='textures/ui/realms_slot_check',
                 on_click=self.home_delete_confirm(home_name)
            )

            confirm_form.add_button(
                 f'{ColorFormat.YELLOW}'
                 f'{self.get_text(player, "button.back")}',
                 icon='textures/ui/refresh_light',
                 on_click=self.home
            )

            player.send_form(confirm_form)

        return on_click

    def home_delete_confirm(self, home_name):

        def on_click(player: Player):
            self.home_data[player.name].pop(home_name)
            self.save_home_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "deletehome.message.success")}'
            )

        return on_click

    # Home teleport
    def home_tp(self, home_loc, home_dim):

        def on_click(player: Player):
            if home_dim == 'Overworld':
                target_dim = self.server.level.get_dimension('OVERWORLD')
            elif home_dim == 'Nether':
                target_dim = self.server.level.get_dimension('NETHER')
            else:
                target_dim = self.server.level.get_dimension('THEEND')
            target_loc = Location(
                target_dim,
                x=float(home_loc[0]),
                y=float(home_loc[1]),
                z=float(home_loc[2])
            )
            player.teleport(target_loc)

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "tphome.message.success")}'
            )

        return on_click

    # Save home data
    def save_home_data(self) -> None:
        with open(home_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(
                self.home_data,
                indent=4,
                ensure_ascii=False
            )
            f.write(json_str)

    # Warp
    def warp(self, player: Player) -> None:
        warp_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "warp_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "warp_form.content")}',
            on_close=self.back_to_main_form
        )

        if player.is_op:
            warp_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "warp_form.button.addwarp")}',
                icon='textures/ui/color_plus',
                on_click=self.add_warp
            )

        for warp_name, warp_info in self.warp_data.items():
            warp_loc = warp_info['loc']
            warp_dim = warp_info['dim']

            warp_form.add_button(
                f'{ColorFormat.WHITE}'
                f'{warp_name}\n'
                f'{ColorFormat.YELLOW}'
                f'[{self.get_text(player, "dimension")}]: {warp_dim}',
                icon='textures/items/ender_eye',
                on_click=self.warp_info(warp_name, warp_loc, warp_dim)
            )

        warp_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.back_to_main_form
        )

        player.send_form(warp_form)

    # Add warp
    def add_warp(self, player: Player) -> None:
        warp_loc = [
            int(player.location.x),
            int(player.location.y),
            int(player.location.z)
        ]
        warp_dim = player.dimension.name

        textinput = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'[{self.get_text(player, "coordinates")}]: '
                  f'{ColorFormat.WHITE}'
                  f'({warp_loc[0]}, {warp_loc[1]}, {warp_loc[2]})\n'
                  f'{ColorFormat.GREEN}'
                  f'[{self.get_text(player, "dimension")}]: '
                  f'{ColorFormat.WHITE}'
                  f'{warp_dim}\n\n'
                  f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "addwarp_form.textinput.label")}',
            placeholder=f'{self.get_text(player, "addwarp_form.textinput.placeholder")}'
        )

        add_warp_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "addwarp_form.title")}',
            controls=[textinput],
            on_close=self.warp,
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "addwarp_form.submit_button")}'
        )

        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)

            if len(data[0]) == 0:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "message.type_error")}'
                )
                return

            warp_already_exist = [key for key in self.warp_data.keys()]
            if data[0] in warp_already_exist:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "addwarp.message.fail")}: '
                    f'{ColorFormat.WHITE}' +
                    self.get_text(player, "addwarp.message.fail.reason").format(data[0])
                )
                return

            warp_name = data[0]
            self.warp_data[warp_name] = {
                'loc': warp_loc,
                'dim': warp_dim
            }
            self.save_warp_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "addwarp.message.success")}'
            )

        add_warp_form.on_submit = on_submit

        player.send_form(add_warp_form)

    # Warp info
    def warp_info(self, warp_name, warp_loc, warp_dim):

        def on_click(player: Player):
            warp_info_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "warp_info_form.title")}: {warp_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "warp_info_form.content")}',
                on_close=self.warp
            )

            warp_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "warp_info_form.button.tp")}',
                icon='textures/ui/realmsIcon',
                on_click=self.warp_tp(warp_loc, warp_dim)
            )

            destination_type = 'warp'
            warp_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "navigate")}',
                icon='textures/ui/pointer',
                on_click=self.start_navigation(destination_type, warp_name, warp_loc, warp_dim)
            )

            if player.is_op:
                warp_info_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "warp_info_form.button.editwarp")}',
                    icon='textures/ui/hammer_l',
                    on_click=self.warp_edit(warp_name, warp_loc, warp_dim)
                )

            warp_info_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.warp
            )

            player.send_form(warp_info_form)
        return on_click

    # Warp teleport
    def warp_tp(self, warp_loc, warp_dim):

        def on_click(player: Player):
            if warp_dim == 'Overworld':
                target_dim = self.server.level.get_dimension('OVERWORLD')
            elif warp_dim == 'Nether':
                target_dim = self.server.level.get_dimension('NETHER')
            else:
                target_dim = self.server.level.get_dimension('THEEND')
            target_loc = Location(
                target_dim,
                x=float(warp_loc[0]),
                y=float(warp_loc[1]),
                z=float(warp_loc[2])
            )

            player.teleport(target_loc)

            player.send_message(f'{ColorFormat.YELLOW}'
                                f'{self.get_text(player, "tpwarp.message.success")}')

        return on_click

    # Warp edit
    def warp_edit(self, warp_name, warp_loc, warp_dim):

        def on_click(player: Player):
            warp_edit_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "editwarp_form.title")}: {warp_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "editwarp_form.content")}',
                on_close=self.warp
            )

            warp_edit_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "editwarp_form.button.updatewarp")}',
                icon='textures/ui/refresh',
                on_click=self.warp_update(warp_name)
            )

            warp_edit_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "editwarp_form.button.deletewarp")}',
                icon='textures/ui/cancel',
                on_click=self.warp_delete(warp_name, warp_loc, warp_dim)
            )

            warp_edit_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.warp
            )

            player.send_form(warp_edit_form)

        return on_click

    # Warp update
    def warp_update(self, warp_name):

        def on_click(player: Player):
            warp_update_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "updatewarp_form.title")}: {warp_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "updatewarp_form.content")}',
                on_close=self.warp
            )

            warp_update_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "updatewarp_form.button.renamewarp")}',
                icon='textures/ui/icon_book_writable',
                on_click=self.warp_update_name(warp_name)
            )

            warp_update_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "updatewarp_form.button.updatelocation")}',
                icon='textures/ui/realmsIcon',
                on_click=self.warp_update_tp(warp_name)
            )

            warp_update_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.warp
            )

            player.send_form(warp_update_form)

        return on_click

    # Warp rename
    def warp_update_name(self, warp_name):

        def on_click(player: Player):
            textinput = TextInput(
                label=f'{ColorFormat.GREEN}'
                      f'{self.get_text(player, "renamewarp_form.textinput.label")}\n',
                default_value=warp_name,
                placeholder=f'{self.get_text(player, "renamewarp_form.textinput.placeholder")}'
            )

            warp_update_name = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "renamewarp_form.title")}: {warp_name}',
                controls=[textinput],
                on_close=self.warp,
                submit_button=f'{ColorFormat.YELLOW}'
                              f'{self.get_text(player, "renamewarp_form.submit_button")}'
            )

            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)

                if len(data[0]) == 0:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "message.type_error")}'
                    )
                    return

                new_warp_name = data[0]

                warp_already_exist = [key for key in self.warp_data.keys()]
                if new_warp_name in warp_already_exist:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "renamewarp.message.fail")}: '
                        f'{ColorFormat.WHITE}' +
                        self.get_text(player, "renamewarp.message.fail.reason").format(data[0])
                    )
                    return

                self.warp_data[new_warp_name] = self.warp_data[warp_name]
                if new_warp_name != warp_name:
                    self.warp_data.pop(warp_name)
                self.save_warp_data()

                player.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "renamewarp.message.success")}'
                )

            warp_update_name.on_submit = on_submit

            player.send_form(warp_update_name)

        return on_click

    # Warp teleport point update
    def warp_update_tp(self, warp_name):

        def on_click(player: Player):
            new_warp_loc = [
                int(player.location.x),
                int(player.location.y),
                int(player.location.z)
            ]
            new_warp_dim = player.dimension.name

            confirm_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                      f'{self.get_text(player, "warp_updatelocation_form.title")}: {warp_name}',
                content=f'{ColorFormat.GREEN}'
                        f'{self.get_text(player, "warp_updatelocation_form.content")}\n'
                        f'[{self.get_text(player, "coordinates")}]: '
                        f'{ColorFormat.WHITE}'
                        f'({new_warp_loc[0]}, {new_warp_loc[1]}, {new_warp_loc[2]})\n'
                        f'{ColorFormat.GREEN}'
                        f'[{self.get_text(player, "dimension")}]: '
                        f'{ColorFormat.WHITE}'
                        f'{new_warp_dim}',
                on_close=self.warp
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "warp_updatelocation_form.button.confirm")}',
                icon='textures/ui/realms_slot_check',
                on_click=self.warp_update_tp_confirm(warp_name, new_warp_loc, new_warp_dim)
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.warp
            )

            player.send_form(confirm_form)

        return on_click
    
    def warp_update_tp_confirm(self, warp_name, new_warp_loc, new_warp_dim):

        def on_click(player: Player):
            self.warp_data[warp_name]['loc'] = new_warp_loc
            self.warp_data[warp_name]['dim'] = new_warp_dim
            self.save_warp_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "warp_updatelocation.message.success")}'
            )

        return on_click

    # Warp delete
    def warp_delete(self, warp_name, warp_loc, warp_dim):

        def on_click(player: Player):
            confirm_form = ActionForm(
                 title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                       f'{self.get_text(player, "deletewarp_form.title")}: {warp_name}',
                 content=f'{ColorFormat.GREEN}'
                         f'{self.get_text(player, "deletewarp_form.content")}\n'
                         f'[{self.get_text(player, "coordinates")}]: '
                         f'{ColorFormat.WHITE}'
                         f'({warp_loc[0]}, {warp_loc[1]}, {warp_loc[2]})\n'
                         f'{ColorFormat.GREEN}'
                         f'[{self.get_text(player, "dimension")}]: '
                         f'{ColorFormat.WHITE}'
                         f'{warp_dim}',
                 on_close=self.warp
             )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "deletewarp_form.button.confirm")}',
                icon='textures/ui/realms_slot_check',
                on_click=self.warp_delete_confirm(warp_name)
            )

            confirm_form.add_button(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "button.back")}',
                icon='textures/ui/refresh_light',
                on_click=self.warp
            )

            player.send_form(confirm_form)

        return on_click

    def warp_delete_confirm(self, warp_name):

        def on_click(player: Player):
            self.warp_data.pop(warp_name)
            self.save_warp_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "deletewarp.message.success")}'
            )

        return on_click

    # Save warp data
    def save_warp_data(self) -> None:
        with open(warp_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(
                self.warp_data,
                indent=4,
                ensure_ascii=False
            )
            f.write(json_str)

    # Home & Warp navigation
    def start_navigation(self, destination_type, name, loc, dim):

        def on_click(player: Player):
            if player.dimension.name != dim:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "start_navigation.message.fail")}: '
                    f'{ColorFormat.WHITE}'
                    f'{self.get_text(player, "start_navigation.message.fail.reason_1")}'
                )
                return

            if self.record_navigation.get(player.name) is not None:
                if (
                        self.record_navigation[player.name]['name'] == name
                        and
                        self.record_navigation[player.name]['destination_type'] == destination_type
                ):
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "start_navigation.message.fail")}: '
                        f'{ColorFormat.WHITE}' +
                        self.get_text(player, "start_navigation.message.fail.reason_2").format(name)
                    )
                    return

                task: Task = self.record_navigation[player.name]['task']
                self.server.scheduler.cancel_task(task.task_id)

                self.record_navigation.pop(player.name)

            navigation_task = self.server.scheduler.run_task(
                self,
                lambda x=player: self.navigation_task(player),
                delay=0,
                period=1
            )

            time_start = time.time()

            self.record_navigation[player.name]= {
                'name': name,
                'loc': loc,
                'dim': dim,
                'destination_type': destination_type,
                'time_start': time_start,
                'task': navigation_task
            }

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "start_navigation.message.success")}\n'
                f'{self.get_text(player, "destination")}: '
                f'{ColorFormat.WHITE}'
                f'{name}\n'
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "type")}: '
                f'{ColorFormat.WHITE}'
                f'{destination_type}'
            )

        return on_click

    def navigation_task(self, player: Player):
        target_task:Task = self.record_navigation[player.name]['task']

        if player.name.find(' ') != -1:
            player_name = f'"{player.name}"'
        else:
            player_name = player.name

        time_start = self.record_navigation[player.name]['time_start']
        time_current = time.time()
        time_expense = int(time_current - time_start)
        if time_expense > self.config_data['navigation_valid_time']:
            self.server.scheduler.cancel_task(
                target_task.task_id
            )
            self.record_navigation.pop(player.name)

            self.server.dispatch_command(
                self.sender_wrapper,
                f'title {player_name} actionbar '
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "overtime")}'
            )

            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "navigation.message.cancel")}'
            )
            return

        time_remain = self.config_data['navigation_valid_time'] - time_expense

        target_dim = self.record_navigation[player.name]['dim']
        if player.dimension.name != target_dim:
            self.server.scheduler.cancel_task(
                target_task.task_id
            )
            self.record_navigation.pop(player.name)

            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "navigation.message.cancel")}'
            )
            return

        target_name = self.record_navigation[player.name]['name']
        target_loc = self.record_navigation[player.name]['loc']

        player_loc = [
            math.floor(player.location.x),
            math.floor(player.location.y),
            math.floor(player.location.z)
        ]

        distance = int(
            (
                    (player_loc[0] - target_loc[0]) ** 2 +
                    (player_loc[2] - target_loc[2]) ** 2
            ) ** 0.5
        )
        if distance <= 4:
            self.server.scheduler.cancel_task(
                target_task.task_id
            )
            self.record_navigation.pop(player.name)

            self.server.dispatch_command(
                self.sender_wrapper,
                f'title {player_name} actionbar '
                f'{ColorFormat.GREEN}'
                f'{self.get_text(player, "arrive")}'
            )
            return

        player_yaw = math.floor(player.location.yaw) + 90
        vector_a = [
            math.cos(math.radians(player_yaw)),
            math.sin(math.radians(player_yaw))
        ]
        vector_b = [
            target_loc[0] - player_loc[0],
            target_loc[2] - player_loc[2]
        ]
        dot_product = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
        cross_product = vector_a[0] * vector_b[1] - vector_a[1] * vector_b[0]
        rad = math.atan2(cross_product, dot_product)
        degree = -math.floor(math.degrees(rad))

        self.server.dispatch_command(
            self.sender_wrapper,
            f'title {player_name} actionbar '
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "destination")}: '
            f'{ColorFormat.WHITE}'
            f'{target_name}  '
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "yaw_angle")}: '
            f'{ColorFormat.WHITE}'
            f'{degree}°  '
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "distance")}: '
            f'{ColorFormat.WHITE}'
            f'{distance}  '
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "time_remain")}: '
            f'{ColorFormat.WHITE}'
            f'{time_remain}s'
        )

    @event_handler
    def on_player_left(self, event: PlayerQuitEvent):
        if self.record_navigation.get(event.player.name) is not None:
            task: Task = self.record_navigation[event.player.name]['task']
            self.server.scheduler.cancel_task(task.task_id)
            self.record_navigation.pop(event.player.name)

    # TPA & TPAHere
    def tpa_and_tpahere(self, player: Player) -> None:
        # Get the list of players' name who have block TPA & TPAHere.
        tpa_deny_player_list = []
        for key, value in self.tp_setting_data.items():
            if not value:
                tpa_deny_player_list.append(key)

        online_player_list = []
        # Filter out the list of players' name available for TPA & TPAHere
        for online_player in self.server.online_players:
            if online_player.name != player.name:
                if online_player.name not in tpa_deny_player_list:
                    online_player_list.append(online_player.name)

        if len(online_player_list) == 0:
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "tpa_and_tpahere.message.fail")}'
            )
            return

        dropdown1 = Dropdown(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "tpa_and_tpahere_form.dropdown_1.label")}',
            options=online_player_list
        )

        mode_list = ['tpa', 'tpahere']
        dropdown2 = Dropdown(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "tpa_and_tpahere_form.dropdown_2.label")}',
            options=mode_list
        )

        tpa_and_tpahere_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "tpa_and_tpahere_form.title")}',
            controls=[dropdown1, dropdown2],
            on_close=self.back_to_main_form,
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "tpa_and_tpahere_form.submit_button")}'
        )

        def on_submit(player: Player, json_str: str):
            request_player_name = player.name

            data = json.loads(json_str)

            target_player_name = online_player_list[data[0]]
            mode = mode_list[data[1]]

            if mode == 'tpa':
                # Check whether the target player for TPA request is online.
                if not self.server.get_player(target_player_name):
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "tpa.message.fail_1")}: '
                        f'{ColorFormat.WHITE}' +
                        self.get_text(player, "tpa_and_tpahere.message.fail.reason.offline").format(target_player_name)
                    )
                    return

                # Send a prompt message to the player who initiated the TPA request.
                player.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "tpa.message.success")}'
                )

                # Send a form to the target player for TPA request.
                target_player = self.server.get_player(target_player_name)

                tpa_form = ActionForm(
                    title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                          f'{self.get_text(target_player, "tpa_form.title")}',
                    content=ColorFormat.GREEN +
                            self.get_text(target_player, "tpa_form.content").format(player.name),
                    on_close=self.tpa_denny(request_player_name)
                )

                tpa_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(target_player, "tpa_form.button.accept")}',
                    icon='textures/ui/realms_slot_check',
                    on_click=self.tpa_accept(request_player_name)
                )

                tpa_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(target_player, "tpa_form.button.deny")}',
                    icon='textures/ui/cancel',
                    on_click=self.tpa_denny(request_player_name)
                )

                target_player.send_form(tpa_form)
            else: # mode = tpahere
                # Check whether the target player for TPAHere request is online.
                if not self.server.get_player(target_player_name):
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "tpahere.message.fail_1")}: '
                        f'{ColorFormat.WHITE}' +
                        self.get_text(player, "tpa_and_tpahere.message.fail.reason.offline").format(target_player_name)
                    )
                    return

                # Send a prompt message to the player who initiated the TPAHere request.
                player.send_message(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(player, "tpahere.message.success")}'
                )

                # Send a form to the target player for TPAHere request.
                target_player = self.server.get_player(target_player_name)

                tpahere_form = ActionForm(
                    title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                          f'{self.get_text(target_player, "tpahere_form.title")}',
                    content=ColorFormat.GREEN +
                            self.get_text(target_player, "tpahere_form.content").format(player.name),
                    on_close=self.tpahere_denny(request_player_name)
                )
                tpahere_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(target_player, "tpahere_form.button.accept")}',
                    icon='textures/ui/realms_slot_check',
                    on_click=self.tpahere_accept(request_player_name)
                )

                tpahere_form.add_button(
                    f'{ColorFormat.YELLOW}'
                    f'{self.get_text(target_player, "tpahere_form.button.deny")}',
                    icon='textures/ui/cancel',
                    on_click=self.tpahere_denny(request_player_name)
                )

                target_player.send_form(tpahere_form)

        tpa_and_tpahere_form.on_submit = on_submit

        player.send_form(tpa_and_tpahere_form)

    # TPA - accept
    def tpa_accept(self, request_player_name):

        def on_click(target_player: Player):
            # Check whether the player who initiated the TPA request is offline.
            if not self.server.get_player(request_player_name):
                target_player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(target_player, "tpa.message.fail_2")}: '
                    f'{ColorFormat.WHITE}' +
                    self.get_text(target_player, "tpa_and_tpahere.message.fail.reason.offline").format(request_player_name)
                )
                return

            request_player = self.server.get_player(request_player_name)
            request_player.teleport(target_player)

        return on_click

    # TPA - deny
    def tpa_denny(self, request_player_name):

        def on_click(target_player: Player):
            # Check whether the player who initiated the TPA request is offline.
            if not self.server.get_player(request_player_name):
                return None

            request_player = self.server.get_player(request_player_name)
            request_player.send_message(
                ColorFormat.RED +
                self.get_text(request_player, "tpa.message.deny").format(target_player.name)
            )
            return None

        return on_click

    # TPAHere - accept
    def tpahere_accept(self, request_player_name):

        def on_click(target_player: Player):
            # Check whether the player who initiated the TPAHere request is offline.
            if not self.server.get_player(request_player_name):
                target_player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(target_player, "tpahere.message.fail_2")}: '
                    f'{ColorFormat.WHITE}' +
                    self.get_text(target_player, "tpa_and_tpahere.message.fail.reason.offline").format(request_player_name)
                )
                return

            request_player = self.server.get_player(request_player_name)
            target_player.teleport(request_player)

        return on_click

    # TPAHere - deny
    def tpahere_denny(self, request_player_name):
        def on_click(target_player: Player):
            # Check whether the player who initiated the TPA request is offline.
            if not self.server.get_player(request_player_name):
                return None


            request_player = self.server.get_player(request_player_name)
            request_player.send_message(
                ColorFormat.RED +
                self.get_text(request_player, "tpahere.message.deny").format(target_player.name)
            )
            return None

        return on_click

    # TP setting (TPA & TPAHere)
    def tp_setting(self, player: Player) -> None:
        toggle = Toggle(
            label=f'{ColorFormat.YELLOW}'
                  f'{self.get_text(player, "tpsetting_form.toggle.lable")}'
        )
        if self.tp_setting_data[player.name]:
            toggle.default_value = True
        else:
            toggle.default_value = False

        tp_setting_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "tpsetting_form.title")}',
            controls=[toggle],
            on_close=self.back_to_main_form,
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "tpsetting_form.submit_button")}'
        )

        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)

            if data[0]:
                update_tp_setting = True
            else:
                update_tp_setting = False
            self.tp_setting_data[player.name] = update_tp_setting
            self.save_tp_setting_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "tpsetting.message.success")}'
            )

        tp_setting_form.on_submit = on_submit

        player.send_form(tp_setting_form)

    # Save TP setting data
    def save_tp_setting_data(self) -> None:
        with open(tp_setting_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(
                self.tp_setting_data,
                indent=4,
                ensure_ascii=False)
            f.write(json_str)

    # TPR
    def tpr(self, player: Player) -> None:
        if not self.record_tpr.get(player.name):
            pass
        else:
            request_time = time.time()
            if int(request_time - self.record_tpr[player.name]) <= self.config_data['tpr_cool_down']:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "tpr.message.fail")}: '
                    f'{ColorFormat.WHITE}'
                    f'{self.get_text(player, "tpr.message.fail.reason")}'
                )
                return

        player_pos = [
            int(player.location.x),
            int(player.location.z)
        ]

        if player.name.find(' ') != -1:
            player_name = f'"{player.name}"'
        else:
            player_name = player.name

        request_time = time.time()

        self.server.dispatch_command(
            self.sender_wrapper,
            f'spreadplayers {player_pos[0]} {player_pos[1]} 0 '
            f'{self.config_data["tpr_range"]} {player_name}'
        )

        self.server.dispatch_command(
            self.sender_wrapper,
            f'effect {player_name} resistance {self.config_data["tpr_protect_time"]} 255 true'
        )

        self.record_tpr[player.name] = request_time

        for online_player in self.server.online_players:
            online_player.send_message(
                f'{ColorFormat.YELLOW}'
                f'[{self.get_text(online_player, "tpr.message.success_1")}]: '
                f'{ColorFormat.WHITE}' +
                self.get_text(online_player, "tpr.message.success_2").format(player.name)
            )

    # Monitor the players' death.
    @event_handler
    def on_player_death(self, event: PlayerDeathEvent):
        player_death_time = time.time()
        player_death_loc = [
            int(event.player.location.x),
            int(event.player.location.y),
            int(event.player.location.z)
        ]
        player_death_dim = event.player.dimension.name
        self.record_death[event.player.name] = {
            'death_time': player_death_time,
            'death_loc': player_death_loc,
            'death_dim': player_death_dim
        }

    # Back to the last death point.
    def back_to_last_death_point(self, player: Player) -> None:
        if not self.record_death.get(player.name):
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "back.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "back.message.fail.reason")}'
            )
            return

        request_time = time.time()
        if int(request_time - self.record_death[player.name]['death_time']) <= self.config_data['back_valid_time']:
            if self.record_death[player.name]['death_dim'] == 'Overworld':
                target_dim = self.server.level.get_dimension('OVERWORLD')
            elif self.record_death[player.name]['death_dim'] == 'Nether':
                target_dim = self.server.level.get_dimension('NETHER')
            else:
                target_dim = self.server.level.get_dimension('THEEND')
            death_loc = self.record_death[player.name]['death_loc']
            target_loc = Location(
                target_dim,
                x=float(death_loc[0]),
                y=float(death_loc[1]),
                z=float(death_loc[2])
            )
            player.teleport(target_loc)

            self.record_death.pop(player.name)

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "back.message.success")}'
            )
        else:
            self.record_death.pop(player.name)
            player.send_message(
                f'{ColorFormat.RED}'
                f'{self.get_text(player, "back.message.fail")}: '
                f'{ColorFormat.WHITE}'
                f'{self.get_text(player, "back.message.fail.reason")}'
            )
            return

    # Reload configurations
    def reload_config_data(self, player: Player) -> None:
        reload_config_data_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "config_form.title")}',
            content=f'{ColorFormat.GREEN}'
                    f'{self.get_text(player, "config_form.content")}',
            on_close=self.back_to_main_form
        )

        reload_config_data_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "config_form.button.utp_config")}',
            icon='textures/ui/icon_setting',
            on_click=self.reload_utp_config
        )

        reload_config_data_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "config_form.button.utp_toggle")}',
            icon='textures/ui/toggle_on',
            on_click=self.reload_utp_function
        )

        reload_config_data_form.add_button(
            f'{ColorFormat.YELLOW}'
            f'{self.get_text(player, "button.back")}',
            icon='textures/ui/refresh_light',
            on_click=self.back_to_main_form
        )

        player.send_form(reload_config_data_form)

    # Reload global configurations
    def reload_utp_config(self, player: Player) -> None:
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_config_form.textinput_1.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["max_home_per_player"]}',
            placeholder=f'{self.get_text(player, "utp_config_form.textinput.placeholder")}',
            default_value=f'{self.config_data["max_home_per_player"]}'
        )

        textinput2 = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_config_form.textinput_2.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["tpr_range"]}',
            placeholder=f'{self.get_text(player, "utp_config_form.textinput.placeholder")}',
            default_value=f'{self.config_data["tpr_range"]}'
        )

        textinput3 = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_config_form.textinput_3.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["tpr_cool_down"]} (s)',
            placeholder=f'{self.get_text(player, "utp_config_form.textinput.placeholder")}',
            default_value=f'{self.config_data["tpr_cool_down"]}'
        )

        textinput4 = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_config_form.textinput_4.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["tpr_protect_time"]}',
            placeholder=f'{self.get_text(player, "utp_config_form.textinput.placeholder")}',
            default_value=f'{self.config_data["tpr_protect_time"]}'
        )

        textinput5 = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_config_form.textinput_5.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["back_valid_time"]} (s)',
            placeholder=f'{self.get_text(player, "utp_config_form.textinput.placeholder")}',
            default_value=f'{self.config_data["back_valid_time"]}'
        )

        textinput6 = TextInput(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_config_form.textinput_6.label")}: '
                  f'{ColorFormat.WHITE}'
                  f'{self.config_data["navigation_valid_time"]} (s)',
            placeholder=f'{self.get_text(player, "utp_config_form.textinput.placeholder")}',
            default_value=f'{self.config_data["navigation_valid_time"]}'
        )

        reload_config_data_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "utp_config_form.title")}',
            controls=[
                textinput1,
                textinput2,
                textinput3,
                textinput4,
                textinput5,
                textinput6
            ],
            on_close=self.reload_config_data,
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "utp_config_form.submit_button")}'
        )

        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)

            for i in range(len(data)):
                if len(data[i]) == 0:
                    player.send_message(
                        f'{ColorFormat.RED}'
                        f'{self.get_text(player, "message.type_error")}'
                    )
                    return

            try:
                update_max_home_per_player = int(data[0])
                update_tpr_range = int(data[1])
                update_tpr_cool_down = int(data[2])
                update_tpr_protect_time = int(data[3])
                update_back_valid_time = int(data[4])
                update_navigation_valid_time = int(data[5])
            except ValueError:
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "message.type_error")}'
                )
                return

            if (
                    update_max_home_per_player <= 0
                    or
                    update_tpr_range <= 0
                    or
                    update_tpr_cool_down <= 0
                    or
                    update_tpr_protect_time <=0
                    or
                    update_back_valid_time <= 0
                    or
                    update_navigation_valid_time <= 0
            ):
                player.send_message(
                    f'{ColorFormat.RED}'
                    f'{self.get_text(player, "message.type_error")}'
                )
                return

            self.config_data['max_home_per_player'] = update_max_home_per_player
            self.config_data['tpr_range'] = update_tpr_range
            self.config_data['tpr_cool_down'] = update_tpr_cool_down
            self.config_data['tpr_protect_time'] = update_tpr_protect_time
            self.config_data['back_valid_time'] = update_back_valid_time
            self.config_data['navigation_valid_time'] = update_navigation_valid_time
            self.save_config_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "utp_config.message.success")}'
            )

        reload_config_data_form.on_submit = on_submit

        player.send_form(reload_config_data_form)

    # Toggle on/off functions of UTP
    def reload_utp_function(self, player: Player) -> None:
        toggle1 = Toggle(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_toggle_form.toggle_1.label")}',
        )
        if self.config_data['is_enable']['home']:
            toggle1.default_value = True
        else:
            toggle1.default_value = False

        toggle2 = Toggle(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_toggle_form.toggle_2.label")}',
        )
        if self.config_data['is_enable']['warp']:
            toggle2.default_value = True
        else:
            toggle2.default_value = False

        toggle3 = Toggle(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_toggle_form.toggle_3.label")}'
        )
        if self.config_data['is_enable']['tpa_and_tpahere']:
            toggle3.default_value = True
        else:
            toggle3.default_value = False

        toggle4 = Toggle(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_toggle_form.toggle_4.label")}'
        )
        if self.config_data['is_enable']['tpr']:
            toggle4.default_value = True
        else:
            toggle4.default_value = False

        toggle5 = Toggle(
            label=f'{ColorFormat.GREEN}'
                  f'{self.get_text(player, "utp_toggle_form.toggle_5.label")}'
        )
        if self.config_data['is_enable']['back']:
            toggle5.default_value = True
        else:
            toggle5.default_value = False

        reload_utp_function_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}'
                  f'{self.get_text(player, "utp_toggle_form.title")}',
            controls=[toggle1, toggle2, toggle3, toggle4, toggle5],
            submit_button=f'{ColorFormat.YELLOW}'
                          f'{self.get_text(player, "utp_toggle_form.submit_button")}',
            on_close=self.reload_config_data
        )

        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)

            self.config_data['is_enable']['home'] = data[0]
            self.config_data['is_enable']['warp'] = data[1]
            self.config_data['is_enable']['tpa_and_tpahere'] = data[2]
            self.config_data['is_enable']['tpr'] = data[3]
            self.config_data['is_enable']['back'] = data[4]
            self.save_config_data()

            player.send_message(
                f'{ColorFormat.YELLOW}'
                f'{self.get_text(player, "utp_toggle.message.success")}'
            )

        reload_utp_function_form.on_submit = on_submit

        player.send_form(reload_utp_function_form)

    # Save config data
    def save_config_data(self) -> None:
        with open(config_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(
                self.config_data,
                indent=4,
                ensure_ascii=False)
            f.write(json_str)

    def back_to_menu(self, player: Player) -> None:
        player.perform_command('cd')

    def back_to_main_form(self, player: Player) -> None:
        player.perform_command('utp')

    # Get text
    def get_text(self, player: Player, text_key: str) -> str:
        player_lang = player.locale
        try:
            if self.lang_data.get(player_lang) is None:
                text_value = self.lang_data['en_US'][text_key]
            else:
                if self.lang_data[player_lang].get(text_key) is None:
                    text_value = self.lang_data['en_US'][text_key]
                else:
                    text_value = self.lang_data[player_lang][text_key]
            return text_value
        except:
            return text_key

    # Monitor players' joining server.
    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        if not self.home_data.get(event.player.name):
            self.home_data[event.player.name] = {}
            self.save_home_data()
        if self.tp_setting_data.get(event.player.name) is None:
            self.tp_setting_data[event.player.name] = True
            self.save_tp_setting_data()
