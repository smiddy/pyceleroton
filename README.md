# pyceleroton
API for celeroton frequency converters and motors

Documentation can be found at http://pythonhosted.org/pyceleroton

## class celerotonCC75
The class
celerotonCC75 is used for frequency converters of the CC75
series. pyserial is applied for serial communication with
the controller. Furthermore, threading is used for the
monitoring.

*Requires*: pyserial (>=2.7)

Parameter `serPort`: Serial port of controller

type `serPort`: int or str

*Example*:

    ctCC75_400 = celerotonCC75('COM10')
    # Set up a temperature monitoring
    monitVar = "temperature"
    threshold = 60
    ctCC75_400.monitor(monitVar, threshold)
    time.sleep(2)
    print(ctCC75_400.thread.is_alive())
    # Get the reference motor speed
    wantedVar = "reference speed"
    result = ctCC75_400.readValue(wantedVar)
    print("Motor will start with", result, "rpm.")
    ctCC75_400.start()
    time.sleep(3)
    ctCC75_400.stop()
    ctCC75_400.close()

'''
