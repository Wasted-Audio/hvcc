import argparse
import os
import json
import jinja2

#############################################################
### Python script to turn JSON into board support files ###
# Author: beserge #
# Largely adapted from grrrwaaa's oopsy #
#############################################################

json_defaults_file = "component_defaults.json"
json_defaults_patchsm = "component_defaults_patchsm.json"

def verify_param_exists(name, original_name, components, input=True):
	print(name, original_name)
	for comp in components:

		# Dealing with the cvouts the way we have it set up is really annoying
		if comp['component'] == 'CVOuts':
			
			if name == comp['name']:
				if input:
					raise TypeError(f'Parameter "{original_name}" cannot be used as an {"input" if input else "output"}')
				return
		else:
			variants = [mapping['name'].format_map({'name': comp['name']}) for mapping in comp['mapping']]
			if name in variants:
				if input and comp['direction'] == 'output' or not input and comp['direction'] == 'input':
					raise TypeError(f'Parameter "{original_name}" cannot be used as an {"input" if input else "output"}')
				return

	raise NameError(f'Unknown parameter "{original_name}"')

def verify_param_direction(name, components):
	for comp in components:
		if comp['component'] == 'CVOuts':
			if name == comp['name']:
				return True
		else:
			variants = [mapping['name'].format_map({'name': comp['name']}) for mapping in comp['mapping']]
			if name in variants:
				return True

def get_root_component(variant, original_name, components):
	for comp in components:
		if comp['component'] == 'CVOuts':
			if variant == comp['name']:
				return variant
		else:
			variants = [mapping['name'].format_map({'name': comp['name']}) for mapping in comp['mapping']]
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
	for param in params_in | params_out:
		root = get_root_component(param, (params_in_original_name | params_out_original_name)[param], components)
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
		target_component = list(filter_match(components, 'name', aliases[alias]))[0]
		# The CVOuts setup really bothers me
		if target_component['component'] != 'CVOuts':
			for mapping in target_component['mapping']:
				if mapping['name'].format_map({'name': alias}) == low:
					return mapping['name'].format_map({'name': aliases[alias]})
	# otherwise, it's a direct parameter or unkown one
	return low

# helper for loading and processing the defaults, component list, etc
def map_load(pair):
	# load the default components
	inpath = os.path.abspath(json_defaults_file)
	infile = open(inpath, 'r').read()
	component_defaults = json.loads(infile)

	pair[1]['name'] = pair[0]

	# the default if it exists
	component = component_defaults[pair[1]['component']]
	if(component):
		# copy component defaults into the def
		# TODO this should be recursive for object structures..
		for k in component:
			if not k in pair[1]: 
				pair[1][k] = component[k]
	else:
		raise Exception("undefined component kind: ", pair[1]['component'])

	return pair[1]

def filter_match(set, key, match, key_exclude=None, match_exclude=None):
	if (key_exclude is not None and match_exclude is not None):
		return filter(lambda x: x.get(key, '') == match and x.get(key_exclude, '') != match_exclude, set)
	else:
		return filter(lambda x: x.get(key, '') == match, set)

def filter_has(set, key, key_exclude=None, match_exclude=None):
	if (key_exclude is not None and match_exclude is not None):
		return filter(lambda x: x.get(key, '') != '' and x.get(key_exclude, '') != match_exclude, set)
	else:
		return filter(lambda x: x.get(key, '') != '', set)

# filter out the components we need, then map them onto the init for that part
def filter_map_init(set, key, match, key_exclude=None, match_exclude=None):
	filtered = filter_match(set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
	return "\n\t\t".join(map(lambda x: x['map_init'].format_map(x), filtered)) 

def filter_map_set(set, key, match, key_exclude=None, match_exclude=None):
	filtered = filter_match(set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
	return "\n\t\t".join(map(lambda x: x['mapping'][0]['set'].format_map(x['mapping'][0]['name'].format_map(x)), filtered))

def filter_map_ctrl(set, key, match, init_key, key_exclude=None, match_exclude=None):
	set = filter_match(set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
	set = map(lambda x, i: x | {'i': i}, set, range(1000))
	return "\n\t\t".join(map(lambda x: x[init_key].format_map(x), set))

# filter out the components with a certain field, then fill in the template
def filter_map_template(set, name, key_exclude=None, match_exclude=None):
	filtered = filter_has(set, name, key_exclude=key_exclude, match_exclude=match_exclude)
	return "\n\t\t".join(map(lambda x: x[name].format_map(x), filtered))

def flatten_pin_dicts(comp):
	newcomp = {}
	for key,val in comp.items():
		if (isinstance(val, dict) and key == 'pin'):
			for subkey, subval in val.items():
				newcomp[key + '_' + subkey] = subval
		else:
			newcomp[key] = val

	return newcomp

def bools_to_lower_str(comp):
	new_comp = {}
	for key, val in comp.items():
		new_comp[key] = str(val).lower() if isinstance(val, bool) else val

	return new_comp

def get_output_array(components):
	output_comps = len(list(filter_match(components, 'direction', 'out')))
	return 'float output_data[{output_comps}];'

def generate_target_struct(target, hpp_temp, cpp_temp, defaults, parameters=[], name='seed', class_name='', copyright=''):
	# flesh out target components:
	target = json.loads(target)
	components = target['components']

	driver = target.get('driver', 'seed')

	global json_defaults_file
	try:
		json_defaults_file = defaults[driver]
	except KeyError:
		raise NameError(f'Unkown driver board "{driver}"')

	# alphabetize by component name
	components = sorted(components.items(), key=lambda x: x[1]['component'])
	components = list(map(map_load, components))

	# flatten pin dicts into multiple entries
	# e.g. "pin": {"a": 12} => "pin_a": 12
	components = [flatten_pin_dicts(comp) for comp in components]

	"""
	This corrupts booleans that might be used for python parsing, and
	so should be avoided. If the user wants to insert C parameters, they
	should just be strings
	"""
	# # convert booleans to properly cased strings
	# components = [bools_to_lower_str(comp) for comp in components]

	target['components'] = components
	if not 'name' in target:
		target['name'] = 'custom'

	if not 'aliases' in target:
		target['aliases'] = {}

	if 'display' in target:
		# apply defaults
		target['display'] = {
			'driver': "daisy::SSD130x4WireSpi128x64Driver",
			'config': [],
			'dim': [128, 64]
		}
		
		target['defines']['OOPSY_TARGET_HAS_OLED'] = 1
		target['defines']['OOPSY_OLED_DISPLAY_WIDTH'] = target['display']['dim'][0]
		target['defines']['OOPSY_OLED_DISPLAY_HEIGHT'] = target['display']['dim'][1]

	# Verify that the params are valid and remove unused components
	params_in = {}
	params_in_original_names = {}
	for key, item in parameters['in']:
		de_aliased = de_alias(key, target['aliases'], components)
		params_in[de_aliased] = item
		params_in_original_names[de_aliased] = key

	params_out = {}
	params_out_original_names = {}
	for key, item in parameters['out']:
		de_aliased = de_alias(key, target['aliases'], components)
		params_out[de_aliased] = item
		params_out_original_names[de_aliased] = key

	[verify_param_exists(key, params_in_original_names[key], components, input=True) for key in params_in]
	[verify_param_exists(key, params_out_original_names[key], components, input=False) for key in params_out]

	for i in range(len(components) - 1, -1, -1):
		if not verify_param_used(components[i], params_in, params_out, params_in_original_names, params_out_original_names, components):
			components.pop(i)

	replacements = {}
	replacements['name'] = name
	replacements['driver'] = driver
	replacements['external_codecs'] = target.get('external_codecs', [])

	replacements['class_name'] = class_name

	replacements['display_conditional'] = ('#include "dev/oled_ssd130x.h"' if ('display' in target) else  "")
	replacements['target_name'] = target['name']
	replacements['init'] = filter_map_template(components, 'init', key_exclude='default', match_exclude=True)

	replacements['switch'] = filter_map_init(components, 'typename', 'daisy::Switch', key_exclude='default', match_exclude=True)
	replacements['gatein'] = filter_map_init(components, 'typename', 'daisy::GateIn', key_exclude='default', match_exclude=True)
	replacements['encoder'] = filter_map_init(components, 'typename', 'daisy::Encoder', key_exclude='default', match_exclude=True)
	replacements['switch3'] = filter_map_init(components, 'typename', 'daisy::Switch3', key_exclude='default', match_exclude=True)
	replacements['analogcount'] = len(list(filter_match(components, 'typename', 'daisy::AnalogControl', key_exclude='default', match_exclude=True)))

	replacements['init_single'] = filter_map_ctrl(components, 'typename', 'daisy::AnalogControl', 'init_single', key_exclude='default', match_exclude=True)
	replacements['ctrl_init'] = filter_map_ctrl(components, 'typename', 'daisy::AnalogControl', 'map_init', key_exclude='default', match_exclude=True)	

	replacements['led'] = filter_map_init(components, 'typename', 'daisy::Led', key_exclude='default', match_exclude=True)
	replacements['rgbled'] = filter_map_init(components, 'typename', 'daisy::RgbLed', key_exclude='default', match_exclude=True)
	replacements['gateout'] = filter_map_init(components, 'typename', 'daisy::dsy_gpio', key_exclude='default', match_exclude=True)
	replacements['dachandle'] = filter_map_init(components, 'typename', 'daisy::DacHandle::Config', key_exclude='default', match_exclude=True)

	# replacements['callback_write_out'] = filter_map_set(components, 'direction', 'out')
	
	replacements['display'] = '// no display' if not 'display' in target else \
		'daisy::OledDisplay<' + target['display']['driver'] + '>::Config display_config;\n\t\t' +\
		'display_config.driver_config.transport_config.Defaults();\n\t\t' +\
		"".join(map(lambda x: x, target['display'].get('config', {}))) +\
		'display.Init(display_config);\n'

	replacements['process'] = filter_map_template(components, 'process', key_exclude='default', match_exclude=True)
	# There's also this after {process}. I don't see any meta in the defaults json at this time. Is this needed?
	# ${components.filter((e) => e.meta).map((e) => e.meta.map(m=>`${template(m, e)}`).join("")).join("")}

	replacements['postprocess'] = filter_map_template(components, 'postprocess', key_exclude='default', match_exclude=True)
	replacements['displayprocess'] = filter_map_template(components, 'display', key_exclude='default', match_exclude=True)
	replacements['hidupdaterates'] = filter_map_template(components, 'updaterate', key_exclude='default', match_exclude=True)

	replacements['comps'] = ";\n\t".join(map(lambda x: x['typename'] + ' ' + x['name'], components)) + ';'
	replacements['dispdec'] = ('daisy::OledDisplay<' + target['display']['driver'] + '> display;') if ('display' in target) else  "// no display"

	replacements['output_arrays'] = get_output_array(components)

	replacements['parameters'] = []
	replacements['output_parameters'] = []
	replacements['callback_write_out'] = ''
	replacements['loop_write_out'] = ''
	replacements['callback_write_in'] = []
	out_idx = 0

	for param_name, param in params_in.items():
		root = get_root_component(param_name, params_in_original_names[param_name], components)
		component = list(filter_match(components, 'name', root))[0]
		param_struct = {'hash': param['hash'], 'name': root, 'type': component['component'].upper()}
		replacements['parameters'].append(param_struct)
		mapping = get_component_mapping(param_name, params_in_original_names[param_name], component, components)

		# A bit of a hack to get cv_1, etc to be written as CV_1
		input_name = root.upper() if driver == 'patch_sm' and component['component'] == 'AnalogControl' else root
		process = mapping["get"].format_map({"name": input_name})

		replacements['callback_write_in'].append({"process": process, "bool": mapping["bool"], "hash": param["hash"]})

	for param_name, param in params_out.items():
		root = get_root_component(param_name, params_out_original_names[param_name], components)
		component = list(filter_match(components, 'name', root))[0]
		param_struct = {'hash': param['hash'], 'index': out_idx, 'name': param_name}
		replacements['output_parameters'].append(param_struct)
		mapping = get_component_mapping(param_name, params_out_original_names[param_name], component, components)

		write_location = 'callback_write_out' if mapping.get('where', 'callback') == 'callback' else 'loop_write_out'

		replacements[write_location] += f'\n\t\t{mapping["set"].format_map({"name": root, "value": "output_data[{}]".format(out_idx)})}'

		out_idx += 1

	replacements['output_comps'] = len(replacements['output_parameters'])
		

	# initialize the jinja template environment
	env = jinja2.Environment()

	env.trim_blocks = True
	env.lstrip_blocks = True

	env.loader = jinja2.FileSystemLoader(
			os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

	template_hpp = env.get_template(hpp_temp).render(replacements)

	template_cpp = env.get_template(cpp_temp).render(replacements)

	return template_hpp, template_cpp

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Utility for generating board support files from JSON.')
	parser.add_argument('json_input', help='Path to json file.')
	parser.add_argument('-o', '--output', help='Path to output to. Defaults to board_support.h', default='HeavyDaisy')

	args = parser.parse_args()
	inpath = os.path.abspath(args.json_input)
	outpath = os.path.abspath(args.output)

	print('Generating Board File...')
	infile = open(inpath, 'r').read()
	template_hpp, template_cpp = generate_target_struct(infile)
	open(outpath + '.hpp', 'w').write(template_hpp)
	open(outpath + '.cpp', 'w').write(template_cpp)