def process_adapter_message(message):
    """ 
    This method is called from the component logic.
    It is up to the developer of the logic to decide how a message
    will look like. In the end both parties must support the same
    set of messages to be compatible.

    One often used message in Wirehome is the _initialize_ message. This
    message is sent on system startup or of the component/adapter is being
    initialized. So that message type should be used and supported by the adapter.
    Even if there is no initialization is required the adapter should respond
    with a _success_ message.

    For component adapters the following messages must be supported:
    - initialize = For initialization like attaching to queues etc.
    - destroy    = For cleanup like detaching from queues etc.)

    In order to be compatible with a certain component logic the documentation of the
    logic must be consulted.
    """

    type = message.get("type", None)

    if type == "initialize":
        pass # Do the stuff for init and return with success ({"type": "success"}).        
    if type == "destroy":
        pass # Do the cleanup and return with success ({"type": "success"}).  
    elif type == "turn_off":
        pass # Turn the device off and return with success.
    elif type == "turn_on":
        pass # Turn the device on and return with success.
    else:
        """ 
        It is recommended to return an exception message for all messages which are not
        supported. This will make debugging easier etc.
        """
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }

"""
Some component adapters may push data to the component logic instead of waiting for messages.
This applies for e.g. buttons or temperature sensors.
In order to push messages with updates to the component logic the function _publish_adapter_message(message : dict)_ is available.
It must not be declared. It will be injected by Wirehome.Core automatically.
The following example shows how to invoke the function.
"""

def on_temperature_update():
    temp_from_sensor = 23 # Example

    message = {
        "type": "sensor_value_updated", # Must be supported from the component logic.
        "value": temp_from_sensor
    }

    publish_adapter_message(message)


"""
Sometimes it is required to know the context of the current adapter.
So where it is running? What is the component logic? What version is executed etc.
Those information is available in a dictionary called _context_.
Printing the dictionary to the console will show all available values.
"""