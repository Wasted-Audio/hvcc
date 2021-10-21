import argparse
import os
import json
import jinja2

#############################################################
### Python script to turn JSON into board support files ###
# Author: beserge #
# Largely adapted from grrrwaaa's oopsy #
#############################################################

# TODO: add an argument to make these paths configurable
json_defaults_file = "component_defaults.json"
template_path = 'template'

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

def filter_match(set, key, match):
	return filter(lambda x: x.get(key, '') == match, set)

def filter_has(set, key):
	return filter(lambda x: x.get(key, '') != '', set)

# filter out the components we need, then map them onto the init for that part
def filter_map_init(set, key, match):
	filtered = filter_match(set, key, match)
	return "\n\t\t".join(map(lambda x: x['map_init'].format_map(x), filtered)) 

def filter_map_ctrl(set, key, match, init_key):
	set = filter_match(set, key, match)
	set = map(lambda x, i: x | {'i': i}, set, range(1000))
	return "\n\t\t".join(map(lambda x: x[init_key].format_map(x), set))

# filter out the components with a certain field, then fill in the template
def filter_map_template(set, name):
	filtered = filter_has(set, name)
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

def generate_target_struct(target, hpp_temp, cpp_temp, defaults, class_name='', copyright=''):
	# flesh out target components:
	global json_defaults_file
	json_defaults_file = defaults
	target = json.loads(target)
	components = target['components']

	# alphabetize by component name
	components = sorted(components.items(), key=lambda x: x[1]['component'])
	components = list(map(map_load, components))

	# flatten pin dicts into multiple entries
	# e.g. "pin": {"a": 12} => "pin_a": 12
	components = [flatten_pin_dicts(comp) for comp in components]

	# convert booleans to properly cased strings
	components = [bools_to_lower_str(comp) for comp in components]

	target['components'] = components
	if not 'name' in target:
		target['name'] = 'custom'

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

	replacements = {}
	replacements['name'] = target['name']
	if 'driver' not in target:
		target['driver'] = 'seed'
	replacements['driver'] = target['driver']

	replacements['class_name'] = class_name

	replacements['display_conditional'] = ('#include "dev/oled_ssd130x.h"' if ('display' in target) else  "")
	replacements['target_name'] = target['name']
	replacements['init'] = filter_map_template(components, 'init')

	replacements['switch'] = filter_map_init(components, 'typename', 'daisy::Switch')
	replacements['gatein'] = filter_map_init(components, 'typename', 'daisy::GateIn')
	replacements['encoder'] = filter_map_init(components, 'typename', 'daisy::Encoder')
	replacements['switch3'] = filter_map_init(components, 'typename', 'daisy::Switch3')
	replacements['encoder'] = filter_map_init(components, 'typename', 'daisy::Encoder')
	replacements['analogcount'] = 'static const int ANALOG_COUNT = ' + str(len(list(filter_match(components, 'typename', 'daisy::AnalogControl')))) + ';'

	replacements['init_single'] = filter_map_ctrl(components, 'typename', 'daisy::AnalogControl', 'init_single')
	replacements['ctrl_init'] = filter_map_ctrl(components, 'typename', 'daisy::AnalogControl', 'map_init')	

	replacements['led'] = filter_map_init(components, 'typename', 'daisy::Led')
	replacements['rgbled'] = filter_map_init(components, 'typename', 'daisy::RgbLed')
	replacements['gateout'] = filter_map_init(components, 'typename', 'daisy::dsy_gpio')
	replacements['dachandle'] = filter_map_init(components, 'typename', 'daisy::DacHandle::Config')
	
	replacements['display'] = '// no display' if not 'display' in target else \
		'daisy::OledDisplay<' + target['display']['driver'] + '>::Config display_config;\n\t\t' +\
		'display_config.driver_config.transport_config.Defaults();\n\t\t' +\
		"".join(map(lambda x: x, target['display'].get('config', {}))) +\
		'display.Init(display_config);\n'

	replacements['process'] = filter_map_template(components, 'process')
	# There's also this after {process}. I don't see any meta in the defaults json at this time. Is this needed?
	# ${components.filter((e) => e.meta).map((e) => e.meta.map(m=>`${template(m, e)}`).join("")).join("")}

	replacements['postprocess'] = filter_map_template(components, 'postprocess')
	replacements['displayprocess'] = filter_map_template(components, 'display')
	replacements['hidupdaterates'] = filter_map_template(components, 'updaterate')

	replacements['comps'] = ";\n\t".join(map(lambda x: x['typename'] + ' ' + x['name'], components)) + ';'
	replacements['dispdec'] = ('daisy::OledDisplay<' + target['display']['driver'] + '> display;') if ('display' in target) else  "// no display"

	# [print(x) for x in target['components']]

	replacements['parameters'] = []
	valid_comps = ['AnalogControl', 'Switch', 'Encoder']
	analog_count = 0
	for comp in target['components']:
		if comp['component'] in valid_comps:
			param = {'name': comp['name'], 'type': comp['component'].upper()}
			replacements['parameters'].append(param)



	# initialize the jinja template environment
	env = jinja2.Environment()

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