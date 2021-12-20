
from copy import deepcopy


def filter_match(set, key, match, key_exclude=None, match_exclude=None):
    if (key_exclude is not None and match_exclude is not None):
        return filter(lambda x: x.get(key, '') == match and x.get(key_exclude, '') != match_exclude, set)
    else:
        return filter(lambda x: x.get(key, '') == match, set)


def verify_param_exists(name, original_name, components, input=True):
    for comp in components:

        # Dealing with the cvouts the way we have it set up is really annoying
        if comp['component'] == 'CVOuts':

            if name == comp['name']:
                if input:
                    raise TypeError(
                        f'Parameter "{original_name}" cannot be used as an {"input" if input else "output"}')
                return
        else:
            variants = [mapping['name'].format_map(
                {'name': comp['name']}) for mapping in comp['mapping']]
            if name in variants:
                if input and comp['direction'] == 'output' or not input and comp['direction'] == 'input':
                    raise TypeError(
                        f'Parameter "{original_name}" cannot be used as an {"input" if input else "output"}')
                return

    raise NameError(f'Unknown parameter "{original_name}"')


def verify_param_direction(name, components):
    for comp in components:
        if comp['component'] == 'CVOuts':
            if name == comp['name']:
                return True
        else:
            variants = [mapping['name'].format_map(
                {'name': comp['name']}) for mapping in comp['mapping']]
            if name in variants:
                return True


def get_root_component(variant, original_name, components):
    for comp in components:
        if comp['component'] == 'CVOuts':
            if variant == comp['name']:
                return variant
        else:
            variants = [mapping['name'].format_map(
                {'name': comp['name']}) for mapping in comp['mapping']]
            if variant in variants:
                return comp['name']
    raise NameError(f'Unknown parameter "{original_name}"')


def get_component_mapping(component_variant, original_name, component, components):
    for variant in component['mapping']:
        if component['component'] == 'CVOuts':
            stripped = variant['name'].format_map({'name': ''})
            if stripped in component['name']:
                return variant
        elif variant['name'].format_map({'name': component['name']}) == component_variant:
            return variant
    raise NameError(f'Unknown parameter "{original_name}"')


def verify_param_used(component, params_in, params_out, params_in_original_name, params_out_original_name, components):
    # Exclude parents, since they don't have 1-1 i/o mapping
    if component.get('is_parent', False):
        return True
    for param in {**params_in, **params_out}:
        root = get_root_component(
            param, ({**params_in_original_name, **params_out_original_name})[param], components)
        if root == component['name']:
            return True
    return False


def de_alias(name, aliases, components):
    low = name.lower()
    # simple case
    if low in aliases:
        return aliases[low]
    # aliased variant
    potential_aliases = list(filter(lambda x: x in low, aliases))
    for alias in potential_aliases:
        try:
            target_component = list(filter_match(
                components, 'name', aliases[alias]))[0]
            # The CVOuts setup really bothers me
            if target_component['component'] != 'CVOuts':
                for mapping in target_component['mapping']:
                    if mapping['name'].format_map({'name': alias}) == low:
                        return mapping['name'].format_map({'name': aliases[alias]})
        except IndexError:
            # No matching alias from filter
            pass
    # otherwise, it's a direct parameter or unkown one
    return low


def parse_parameters(parameters, components, aliases, object_name):
    """
    Parses the `parameters` passed from hvcc and generates getters and setters
    according to the info in `components`. The `aliases` help disambiguate parameters
    and the `object_name` sets the identifier for the generated Daisy hardware class,
    in this case `hardware`.
    """

    # Verify that the params are valid and remove unused components
    replacements = {}
    params_in = {}
    params_in_original_names = {}
    for key, item in parameters['in']:
        de_aliased = de_alias(key, aliases, components)
        params_in[de_aliased] = item
        params_in_original_names[de_aliased] = key

    params_out = {}
    params_out_original_names = {}
    for key, item in parameters['out']:
        de_aliased = de_alias(key, aliases, components)
        params_out[de_aliased] = item
        params_out_original_names[de_aliased] = key

    [verify_param_exists(key, params_in_original_names[key],
                         components, input=True) for key in params_in]
    [verify_param_exists(key, params_out_original_names[key],
                         components, input=False) for key in params_out]

    for i in range(len(components) - 1, -1, -1):
        if not verify_param_used(
                components[i], params_in, params_out,
                params_in_original_names, params_out_original_names,
                components):
            components.pop(i)

    out_idx = 0

    replacements['parameters'] = []
    replacements['output_parameters'] = []
    replacements['loop_write_in'] = []
    replacements['callback_write_out'] = []
    replacements['loop_write_out'] = []
    replacements['hook_write_out'] = []
    replacements['callback_write_in'] = []

    for param_name, param in params_in.items():
        root = get_root_component(
            param_name, params_in_original_names[param_name], components)
        component = list(filter_match(components, 'name', root))[0]
        param_struct = {
            "hash_enum": params_in_original_names[param_name], 'name': root, 'type': component['component'].upper()}
        replacements['parameters'].append(param_struct)
        mapping = get_component_mapping(
            param_name, params_in_original_names[param_name], component, components)

        write_location = 'callback_write_in' if mapping.get(
            'where', 'callback') == 'callback' else 'loop_write_in'
        component_info = deepcopy(component)
        component_info['name'] = root
        component_info['class_name'] = object_name
        # A bit of a hack to get cv_1, etc to be written as CV_1
        component_info['name_upper'] = root.upper()
        component_info['value'] = f'output_data[{out_idx}]'
        component_info['default_prefix'] = component.get(
            "default_prefix", '') if component.get('default', False) else ''
        process = mapping["get"].format_map(component_info)

        replacements[write_location].append(
            {"process": process, "bool": mapping.get('bool', False),
                "hash_enum": params_in_original_names[param_name]})

    for param_name, param in params_out.items():
        root = get_root_component(
            param_name, params_out_original_names[param_name], components)
        component = list(filter_match(components, 'name', root))[0]

        mapping = get_component_mapping(
            param_name, params_out_original_names[param_name], component, components)

        default_prefix = component.get(
            "default_prefix", '') if component.get('default', False) else ''

        write_locations = {'callback': 'callback_write_out',
                           'loop': 'loop_write_out',
                           'hook': 'hook_write_out'}

        write_location = write_locations.get(mapping.get('where', 'callback'), 'callback_write_out')

        param_struct = {
            'hash_enum': params_out_original_names[param_name],
            'index': out_idx, 'name': param_name,
            'hook': write_location == 'hook_write_out'}
        replacements['output_parameters'].append(param_struct)

        component_info = deepcopy(component)
        component_info['hash_enum'] = params_out_original_names[param_name]
        component_info['name'] = root
        component_info['class_name'] = object_name
        component_info['value'] = f'output_data[{out_idx}]' if \
            write_location != 'hook_write_out' else 'sig'
        component_info['default_prefix'] = default_prefix
        write = mapping["set"].format_map(component_info)

        replacements[write_location].append(
            {"name": param_name,
             "process": write,
             "bool": mapping.get('bool', False),
             "value": component_info['value']})

        out_idx += 1

    replacements['output_comps'] = len(replacements['output_parameters'])

    return replacements
