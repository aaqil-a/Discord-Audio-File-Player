from ctypes import create_string_buffer
import struct

"""
Add two audio frames together.
Adapted from pydub/pyaudioop.py.
"""
def add_audio_bytes(b1: bytes, b2:bytes, sample_size):
    clip = lambda v : max(min(v, 0x7FFFFFFF), -0x7FFFFFFF)
    sample_count = int(len(b1) / sample_size)
    result = create_string_buffer(len(b1))

    for i in range(sample_count):
        start = i * sample_size
        end = start + sample_size
    
        sample1 = struct.unpack_from('i', memoryview(b1)[start:end])[0]
        sample2 = struct.unpack_from('i', memoryview(b2)[start:end])[0]

        sample1_r = (sample1 >> 16) 
        sample2_r = (sample2 >> 16) 
        
        sample1_l = sample1 & 0xFFFF 
        sample2_l = sample2 & 0xFFFF

        # Check if 16 LSB (left channel audio)
        # should be negative
        if sample1_l & 0x8000:
            sample1_l -= 0x10000
        if sample2_l & 0x8000:
            sample2_l -= 0x10000

        sample_r = int((sample1_r + sample2_r)/2)
        sample_l = int((sample1_l + sample2_l)/2)
        sample = clip(sample_l | (sample_r << 16))
        
        struct.pack_into('i', result, i*sample_size, sample)

    return result.raw
