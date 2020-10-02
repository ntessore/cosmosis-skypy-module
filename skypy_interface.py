from cosmosis.datablock import names, option_section
from cosmosis.runtime import register_new_parameter
from skypy.pipeline import Pipeline

def setup(options):
    module_name = options['pipeline', '_cosmosis_active_module']

    filename = options.get_string(option_section, 'pipeline')
    pipeline = Pipeline.read(filename)

    for parameter_name, parameter_value in pipeline.parameters.items():
        register_new_parameter(
            options,
            module_name,
            parameter_name,
            parameter_value,  # min value
            parameter_value,  # start value
            parameter_value,  # max value
            # optional prior could go here
        )

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
