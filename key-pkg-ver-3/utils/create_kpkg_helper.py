import sys, os

def get_file_content(key_file_path):
    is_file = os.path.isfile(key_file_path)
    if not is_file:
        return None
    try:
        with open(key_file_path) as key_file:
            key_file_content = key_file.read()
            return key_file_content
    except FileNotFoundError:
        # raise Exception("Unable to read the file!")
        return None


def package_exists(key_packages_list, target_list, operation):
    """returns index if key package exists, -1 otherwise

    Args:
        key_packages_list (list of dictionaries): list of dictionaries
        target_list (enum): enum: ['ALLOWED_LIST','REVOKED_LIST']
        operation (enum): enum: ['APPEND','DELETE', 'REPLACE']

    Returns:
        _int_: returns index if key package exists, -1 otherwise
    """
    for i in range(len(key_packages_list)):
        if key_packages_list[i]['target_list'] == target_list and key_packages_list[i]['operation'] == operation:
            return i
    return -1


class Key:
    def __init__(self, key_type, key_name, key_file_content, key_metadata):
        self.key_type = key_type  # cann't be empty
        self.key_name = key_name  # cann't be empty
        self.key_metadata = key_metadata # can be empty, cannot be more than 128 chars
        self.key_value = key_file_content