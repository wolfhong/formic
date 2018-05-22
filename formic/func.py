import os
# from formic import get_path_components


cwd = os.getcwd()
print(cwd)
cwd = os.path.join(os.sep, 'a', 'b', 'c')
cwd = os.sep
cwd = os.sep + os.sep + 'a' + os.sep + 'b'
print(cwd)
# print(get_path_components(cwd))
print((os.path.splitdrive(cwd)))
