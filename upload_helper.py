def validate_input( trans, error_map, param_values, page_param_map ):
    """
        Validates the user input, before execution.
    """
    if "collection_date" in param_values.keys():
        import re
        re.compile("(^[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?(/[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?)?$)|(^not collected$)|(^not provided$)|(^restricted access$)")
        match = regex.match(param_values["collection_date"])
        if match == None:
            error_map["collection_date"] = "Date format is not correct"

