import rpy2.situation
import os


a = rpy2.situation.get_r_home()
print(rpy2.situation.get_r_flags(a, '--ldflags')[0].L)
# for libpath in rpy2.situation.get_r_flags(a, '--ldflags')[0].L:
#             os.add_dll_directory(libpath)
print("DEBUG R_HOME:", a)