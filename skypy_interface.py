from cosmosis.datablock import option_section
from cosmosis.runtime import register_new_parameter
from skypy.pipeline import Pipeline

def parameter_expand(lower, start=None, upper=None, *prior):
    if isinstance(lower, list):
        return parameter_expand(*lower)
    elif isinstance(lower, dict):
        return parameter_expand(**lower)
    else:
        return lower, start or lower, upper or start or lower, *prior

def setup(options):
    module_name = options['pipeline', 'current_module']

    filename = options.get_string(option_section, 'pipeline')
    pipeline = Pipeline.read(filename)

    for parameter_name, parameter_value in pipeline.parameters.items():
        register_new_parameter(options,
                               module_name,
                               parameter_name,
                               *parameter_expand(parameter_value))

    results = options.get_string(option_section, 'results')

    results_map = {}
    for line in results.splitlines():
        section_name, skypy_label = tuple(map(str.strip, line.split('=')))
        section, _, name = section_name.partition('--')
        results_map[section, name] = skypy_label

    return module_name, pipeline, results_map

def execute(block, config):
    module_name, pipeline, results_map = config

    parameters = {parameter_name: block[module_name, parameter_name]
                  for parameter_name in pipeline.parameters}

    pipeline.execute(parameters)

    for section_name, skypy_label in results_map.items():
        block[section_name] = pipeline[skypy_label]

    return 0
