anat_modalities = {
    'T1w': 'T1 weighted',

}
def split_file_name(filename):
    components = filename.split('_')
    components_list = [comp.split('-') for comp in components]
    return components_list

