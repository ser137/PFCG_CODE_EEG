import serial

# Setup trigger box
def trigg_box(is_, name_):
    if is_ == 1:
        mmbts = serial.Serial()
        mmbts.port = name_  
        mmbts.open()
    else:
        mmbts = []
    return mmbts   