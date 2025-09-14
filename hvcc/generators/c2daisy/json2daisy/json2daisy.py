import jinja2
import json
import os

from importlib import resources
from typing import Optional


def map_load(pair: list, json_defs_file: str):
    """
    Helper for loading and processing the definitions, component list, etc
    """

    # load the default components
    comp_string = resources.files('json2daisy').joinpath(json_defs_file).read_text()
    component_defs = json.loads(comp_string)

    pair[1]['name'] = pair[0]

    # the default if it exists
    component = component_defs.get(pair[1]['component'], None)
    if (component):
        # copy component defs into the def
        # TODO this should be recursive for object structures..
        for k in component:
            if k not in pair[1]:
                pair[1][k] = component[k]
    else:
        raise Exception(f'unknown component "{pair[1]["component"]}"')

    return pair[1]


def filter_match(
    component_set: list,
    key: str,
    match: str,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> filter:
    if (key_exclude is not None and match_exclude):
        return filter(lambda x: x.get(key, '') == match and x.get(key_exclude, '') != match_exclude, component_set)
    else:
        return filter(lambda x: x.get(key, '') == match, component_set)


def filter_matches(
    component_set: list,
    key: str,
    matches: list,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> filter:
    if (key_exclude is not None and match_exclude):
        return filter(lambda x: x.get(key, '') in matches and x.get(key_exclude, '') != match_exclude, component_set)
    else:
        return filter(lambda x: x.get(key, '') in matches, component_set)


def filter_has(
    component_set: list,
    key: str,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> filter:
    if (key_exclude is not None and match_exclude):
        return filter(lambda x: x.get(key, '') != '' and x.get(key_exclude, '') != match_exclude, component_set)
    else:
        return filter(lambda x: x.get(key, '') != '', component_set)


# filter out the components we need, then map them onto the init for that part
def filter_map_init(
    component_set: list,
    key: str,
    match: str,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> str:
    filtered = filter_match(component_set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
    return "\n    ".join(map(lambda x: x['map_init'].format_map(x), filtered))


# this function is not used anywhere?
def filter_map_set(
    component_set: list,
    key: str,
    match: str,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> str:
    filtered = filter_match(component_set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
    return "\n    ".join(
        map(lambda x: x['mapping'][0]['set'].format_map(x['mapping'][0]['name'].format_map(x)), filtered)
    )


def filter_map_ctrl(
    component_set: list,
    key: str,
    matches: list,
    init_key: str,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> str:
    component_filt = filter_matches(component_set, key, matches, key_exclude=key_exclude, match_exclude=match_exclude)
    component_map = map(lambda x, i: {**x, 'i': i}, component_filt, range(1000))
    return "\n    ".join(map(lambda x: x[init_key].format_map(x), component_map))


# filter out the components with a certain field, then fill in the template
def filter_map_template(
    component_set: list,
    name: str,
    key_exclude: Optional[str] = None,
    match_exclude: bool = False
) -> str:
    filtered = filter_has(component_set, name, key_exclude=key_exclude, match_exclude=match_exclude)
    return "\n    ".join(map(lambda x: x[name].format_map(x), filtered))


def flatten_pin_dicts(comp: dict) -> dict:
    newcomp = {}
    for key, val in comp.items():
        if (isinstance(val, dict) and key == 'pin'):
            for subkey, subval in val.items():
                newcomp[f'{key}_{subkey}'] = subval
        else:
            newcomp[key] = val

    return newcomp


def flatten_index_dicts(comp: dict) -> dict:
    newcomp = {}
    for key, val in comp.items():
        if (isinstance(val, dict) and key == 'index'):
            for subkey, subval in val.items():
                newcomp[f'{key}_{subkey}'] = subval
        else:
            newcomp[key] = val

    return newcomp


def generate_header(board_description_dict: dict) -> 'tuple[str, dict]':
    """
    Generate a C++ Daisy board header from a dictionary board description.

    Returns a tuple containing the board
    header as a string and an information dictionary.

    The dictionary provides sufficient information to
    generate interface code, including component getters
    and setters, audio channel count, etc.
    """

    target = board_description_dict

    # flesh out target components:
    components = target.get('components', {})
    parents = target.get('parents', {})

    for key in parents:
        parents[key]['is_parent'] = True
    components.update(parents)

    seed_defs = os.path.join("resources", 'component_defs.json')
    patchsm_defs = os.path.join("resources", 'component_defs_patchsm.json')
    petalsm_defs = os.path.join("resources", 'component_defs_petalsm.json')
    definitions = {'seed': seed_defs, 'patch_sm': patchsm_defs, 'petal_125b_sm': petalsm_defs}
    som = target.get('som', 'seed')

    try:
        json_defs_file = definitions[som]
    except KeyError:
        raise NameError(f'Unkown som "{som}"')

    # alphabetize by component name
    components = sorted(components.items(), key=lambda x: x[1]['component'])
    # components = list(map(map_load, components))
    components = list(map(lambda p: map_load(p, json_defs_file), components))

    # flatten pin dicts into multiple entries
    # e.g. "pin": {"a": 12} => "pin_a": 12
    components = [flatten_pin_dicts(comp) for comp in components]
    components = [flatten_index_dicts(comp) for comp in components]

    target['components'] = components
    if 'name' not in target:
        target['name'] = 'custom'

    if 'aliases' not in target:
        target['aliases'] = {}

    if 'display' in target:
        # apply defaults if not present in config
        target['display']['driver'] = target['display'].get('driver', "daisy::SSD130x4WireSpi128x64Driver")
        target['display']['config'] = target['display'].get('config', [])
        target['display']['dim'] = target['display'].get('dim', [128, 64])

        target['defines']['OOPSY_TARGET_HAS_OLED'] = 1
        target['defines']['OOPSY_OLED_DISPLAY_WIDTH'] = target['display']['dim'][0]
        target['defines']['OOPSY_OLED_DISPLAY_HEIGHT'] = target['display']['dim'][1]

        target['displayprocess'] = target['display'].get('process', '')

    replacements = {}
    replacements['name'] = target['name']
    replacements['som'] = som
    replacements['external_codecs'] = target.get('external_codecs', [])

    som_classes = {
        'seed': 'daisy::DaisySeed',
        'patch_sm': 'daisy::patch_sm::DaisyPatchSM',
        'petal_125b_sm': 'daisy::Petal125BSM',
    }

    replacements['som_class'] = som_classes.get(som, som_classes['seed'])

    replacements['display_conditional'] = ('#include "dev/oled_ssd130x.h"' if ('display' in target) else "")
    replacements['target_name'] = target['name']
    replacements['init'] = filter_map_template(components, 'init', key_exclude='default', match_exclude=True)

    replacements['analogcount'] = len(list(filter_matches(
        components, 'component', ['AnalogControl', 'AnalogControlBipolar', 'CD4051'],
        key_exclude='default', match_exclude=True)))

    replacements['init_single'] = filter_map_ctrl(
        components, 'component', ['AnalogControl', 'AnalogControlBipolar', 'CD4051'],
        'init_single', key_exclude='default', match_exclude=True)
    replacements['ctrl_init'] = filter_map_ctrl(
        components, 'component', ['AnalogControl', 'AnalogControlBipolar'],
        'map_init', key_exclude='default', match_exclude=True)

    comp_string = resources.files('json2daisy').joinpath(json_defs_file).read_text()
    definitions_dict = json.loads(comp_string)

    for name in definitions_dict:
        if name not in ('AnalogControl', 'AnalogControlBipolar', 'CD4051'):
            replacements[name] = filter_map_init(
                components, 'component', name, key_exclude='default', match_exclude=True)

    if 'display' in target:
        replacements['dispdec'] = f'daisy::OledDisplay<{target["display"]["driver"]}> display;'
        replacements['display'] = f"""
        daisy::OledDisplay<{target['display']['driver']}>::Config display_config;
        display_config.driver_config.transport_config.Defaults();
        {"".join(map(lambda x: x, target['display'].get('config', {})))}
        display.Init(display_config);
          display.Fill(0);
          display.Update();
        """
    else:
        replacements['display'] = ''

    if 'defines' in target:
        if target['defines'].get('OOPSY_TARGET_HAS_MIDI_INPUT'):
            target['has_midi'] = True
            replacements['midi'] = """daisy::MidiUartHandler midi;"""

    replacements['process'] = filter_map_template(
        components, 'process', key_exclude='default', match_exclude=True)
    replacements['loopprocess'] = filter_map_template(
        components, 'loopprocess', key_exclude='default', match_exclude=True)

    replacements['postprocess'] = filter_map_template(
        components, 'postprocess', key_exclude='default', match_exclude=True)
    replacements['displayprocess'] = filter_map_template(
        components, 'display', key_exclude='default', match_exclude=True)
    replacements['hidupdaterates'] = filter_map_template(
        components, 'updaterate', key_exclude='default', match_exclude=True)

    license_string = resources.files('json2daisy').joinpath('resources/LICENSE').read_text()
    replacements['license'] = '/*\n * ' + '\n * '.join([line for line in license_string.split('\n')]) + '\n */'

    component_declarations = list(filter(lambda x: not x.get('default', False), components))
    component_declarations = list(filter(lambda x: x.get('typename', '') != '', component_declarations))

    if len(component_declarations) > 0:
        replacements['comps'] = ";\n  ".join(
            map(lambda x: x['typename'].format_map(x) + ' ' + x['name'], component_declarations)
        ) + ';'

    non_class_declarations = list(filter(lambda x: 'non_class_decl' in x, component_declarations))

    if len(non_class_declarations) > 0:
        replacements['non_class_declarations'] = "\n".join(
            map(lambda x: x['non_class_decl'].format_map(x), non_class_declarations)
        )

    # env_opts = {"trim_blocks": True, "lstrip_blocks": True}

    # Ideally, this would be what we use, but we'll need to get the jinja PackageLoader class working
    # loader = jinja2.PackageLoader(__name__)
    # env = jinja2.Environment(loader=loader, **env_opts)
    # rendered_header = env.get_template('daisy.h').render(replacements)

    # This following works, but is really annoying
    header_str = resources.files('json2daisy').joinpath(os.path.join('templates', 'daisy.h')).read_text()
    header_env = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        trim_blocks=True,
        lstrip_blocks=True
    ).from_string(header_str)

    rendered_header = header_env.render(replacements)

    # removing all unnecessary fields
    for comp in components:
        if 'map_init' in comp:
            del comp['map_init']
        if 'typename' in comp:
            del comp['typename']

    audio_info = target.get('audio', None)
    audio_channels = audio_info.get('channels', 2) if audio_info is not None else 2

    # This dictionary contains the necessary information to automatically (or manually)
    # write code to interface with the generated board
    board_info = {
        'name': target['name'],
        'components': components,
        'aliases': target['aliases'],
        'channels': audio_channels,
        'has_midi': target.get('has_midi', False),
        'displayprocess': target.get('displayprocess', '')
      }

    return rendered_header, board_info


def generate_header_from_file(description_file: str) -> 'tuple[str, dict]':
    """
    Generate a C++ Daisy board header from a JSON description file.

    Returns a tuple containing the board
    header as a string and an information dictionary.

    The dictionary provides sufficient information to
    generate interface code, including component getters
    and setters, audio channel count, etc.
    """

    with open(description_file, 'rb') as file:
        daisy_description = json.load(file)

    return generate_header(daisy_description)


def generate_header_from_name(board_name: str) -> 'tuple[str, dict]':
    """
    Generate a C++ Daisy board header for an existing daisy board.

    Returns a tuple containing the board
    header as a string and an information dictionary.

    The dictionary provides sufficient information to
    generate interface code, including component getters
    and setters, audio channel count, etc.
    """

    try:
        description_file = os.path.join('resources', f'{board_name}.json')
        daisy_description = resources.files(__package__).joinpath(description_file).read_text()
        daisy_description_dict = json.loads(daisy_description)
    except FileNotFoundError:
        raise FileNotFoundError(f'Unknown Daisy board   "{board_name}"')

    return generate_header(daisy_description_dict)
