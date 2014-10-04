import cnoise
import ctypes
import ntype

CHUNKSIZE=128
FRAMERATE=48000

global_vars=[(ctypes.c_int,'global_chunk_size',CHUNKSIZE),(ctypes.c_int,'global_frame_rate',FRAMERATE)]

lib=cnoise.NoiseLib(global_vars)

lib.load('blocks')

#n_double=ntype.TypeFactory(lib['noise'].simple_alloc,lib['noise'].simple_free,lib['noise'].simple_copy,ctypes.c_int(ctypes.sizeof(ctypes.c_double)),'double')
#n_int=ntype.TypeFactory(lib['noise'].simple_alloc,lib['noise'].simple_free,lib['noise'].simple_copy,ctypes.c_int(ctypes.sizeof(ctypes.c_int)),'int')
#n_chunk=ntype.TypeFactory(lib['noise'].simple_alloc,lib['noise'].simple_free,lib['noise'].simple_copy,ctypes.c_int(ctypes.sizeof(ctypes.c_double)*CHUNKSIZE),'chunk')

