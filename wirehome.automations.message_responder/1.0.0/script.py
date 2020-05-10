config = {}
subscriptions = []


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    if type == "enable":
        return __enable__()
    if type == "disable":
        return __disable__()
    else:
        return wirehome.response_creator.not_supported(type)


def __initialize__():
    __enable__()


def __enable__():
    global subscriptions
    subscriptions = []

    observations = config.get("observations", {})

    for observation_uid in observations:
        input_messages = observations.get(observation_uid, {}).get("input_messages", {})

        for input_message_uid in input_messages:
            input_message = input_messages.get(input_message_uid, {})
            filter = input_message.get("filter", {})

            print("Subscribing for input messages '{}'".format(
                input_message_uid))

            subscription_uid = wirehome.context["component_uid"] + \
                ":input_message_filter->" + input_message_uid

            wirehome.message_bus.subscribe(subscription_uid, filter, __input_message_callback__)
            subscriptions.append(subscription_uid)


def __disable__():
    global subscriptions
    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)

    subscriptions = []


def __input_message_callback__(message):
    observations = config.get("observations", {})
    for observation_uid in observations:
        component_messages = observations.get(observation_uid, {}).get("component_messages", {})

        for component_message_uid in component_messages:
            component_message = component_messages.get(component_message_uid, {})

            component_uid = component_message.get("component_uid", "")
            message = component_message.get("message", {})

            wirehome.component_registry.process_message(component_uid, message)