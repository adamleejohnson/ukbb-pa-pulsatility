# Adam L. Johnson, M.D. (aljohnson@mgh.harvard.edu)
# Cardiovascular Research Center, Division of Cardiology
# Massachusetts General Hospital
 
import os
import re

class str2(str):
    def basename(self):
        return str2(os.path.basename(self))

    def dirname(self):
        return str2(os.path.dirname(self))

    def rchop(self, suffix):
        if suffix and self.endswith(suffix):
            return str2(self[:-len(suffix)])
        else:
            return str2(self)

    def removeSubstr(self, charArray):
        if (not hasattr(charArray, '__len__')) or isinstance(charArray, str):
            charArray = [charArray]
        for s in charArray:
            self = ''.join(self.split(s))
        return str2(self)

# NNUNET PATIENT FILENAMES


def format_patient_filename(prefix, patient_name, frame_num, index, suffix=''):
    return prefix + "_" + patient_name + ('_%.3d_%.8d') % (frame_num, index) + suffix


def deconstruct_patient_filename(filename: str):
    fname = os.path.basename(filename.split('.')[0])
    regex = '^([^_]+)_(.+)_(\d{3})_(\d{8})(_\d{4})?$'
    re_match = re.match(regex, fname)
    if re_match:
        index = re_match.group(4)
        frame = re_match.group(3)
        name = re_match.group(2)
        prefix = re_match.group(1)
        return prefix, name, frame, index
    else:
        raise NameError("Filename %s not in correct format" % fname)


def validate_patient_filename_format(filename):
    fname = os.path.basename(filename)
    try:
        deconstruct_patient_filename(fname)
        return True
    except NameError:
        return False


def standardize_patient_name(input_string: str) -> str:
    ostr = input_string
    for s in [' ', '/', '\\']:
        ostr = '_'.join(ostr.split(s))
    return re.sub("__+", "_", ostr)
