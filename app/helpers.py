# =============================================================================
#       place to hold functions that are used all over the app
#
#       anything here should be more-or-less self contained in that they
#       shouldn't need to interact with the workings of the application
# =============================================================================

def filter_argtype_and_arg(
        passed_arg_type,
        allowed_arg_types,
        passed_arg):
    '''
    filter out arguments passed through the URL, as templated to look like:
        request.url_root/route_base/passed_arg_type/passed_arg
    where:
        - passed_arg_type can be any string (description of what to do)
        - passed_arg must be an integer (generally a db table id)
    '''
   
    garb = [None, '']

    # is_base only true when both url args are None
    is_base = False

    # default case
    if passed_arg_type == None and passed_arg == None:
        passed_args_ok = True
        is_base = True

    # arg type not passed but argument is passed
    elif passed_arg_type in garb and passed_arg not in garb:
        passed_args_ok =  False

    # arg type passed but arg not passed
    elif passed_arg_type not in garb and passed_arg in garb:
        passed_args_ok =  False

    # -------------------------------------------------------------------------
    # at this point, we should have an arg_type and arg, both not None
    # -------------------------------------------------------------------------

    # ensure arg_type is in list of allowed_arg_types
    if (passed_arg_type not in allowed_arg_types):
        passed_args_ok = False

    try:
        # ensure arg is an integer
        passed_arg = int(passed_arg)
    
    except:
        passed_args_ok = False

    # -------------------------------------------------------------------------
    # at this point, we have an allowed arg_type and an integer arg 
    # -------------------------------------------------------------------------
    passed_args_ok = True

    return (is_base, passed_args_ok)

