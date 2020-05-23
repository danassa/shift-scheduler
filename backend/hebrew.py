import PySimpleGUI as sg

# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# -----------------A custom version of PySimpleGui Popup to allow justification to the right ------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def HebrewPopup(*args, title=None, button_color=None, background_color=None, text_color=None, button_type=sg.POPUP_BUTTONS_OK, auto_close=False,
          auto_close_duration=None, custom_text=(None, None), non_blocking=True, icon=None, line_width=None, font=None, no_titlebar=False, grab_anywhere=False,
          keep_on_top=True, location=(None, None)):
    """
    Popup - Display a popup Window with as many parms as you wish to include.  This is the GUI equivalent of the
    "print" statement.  It's also great for "pausing" your program's flow until the user can read some error messages.

    :param *args:  Variable number of your arguments.  Load up the call with stuff to see!
    :type *args: (Any)
    :param title:   Optional title for the window. If none provided, the first arg will be used instead.
    :type title: (str)
    :param button_color: Color of the buttons shown (text color, button color)
    :type button_color: Tuple[str, str]
    :param background_color:  Window's background color
    :type background_color: (str)
    :param text_color:  text color
    :type text_color: (str)
    :param button_type:  NOT USER SET!  Determines which pre-defined buttons will be shown (Default value = POPUP_BUTTONS_OK). There are many Popup functions and they call Popup, changing this parameter to get the desired effect.
    :type button_type: (int)
    :param auto_close:  If True the window will automatically close
    :type auto_close: (bool)
    :param auto_close_duration:  time in seconds to keep window open before closing it automatically
    :type auto_close_duration: (int)
    :param custom_text:  A string or pair of strings that contain the text to display on the buttons
    :type custom_text: Union[Tuple[str, str], str]
    :param non_blocking:  If True then will immediately return from the function without waiting for the user's input.
    :type non_blocking: (bool)
    :param icon:  icon to display on the window. Same format as a Window call
    :type icon: Union[str, bytes]
    :param line_width:  Width of lines in characters.  Defaults to MESSAGE_BOX_LINE_WIDTH
    :type line_width: (int)
    :param font:  specifies the font family, size, etc
    :type font: Union[str, tuple(font name, size, modifiers]
    :param no_titlebar:  If True will not show the frame around the window and the titlebar across the top
    :type no_titlebar: (bool)
    :param grab_anywhere:  If True can grab anywhere to move the window. If no_titlebar is True, grab_anywhere should likely be enabled too
    :type grab_anywhere: (bool)
    :param location:   Location on screen to display the top left corner of window. Defaults to window centered on screen
    :type location: Tuple[int, int]
    :return: Returns text of the button that was pressed.  None will be returned if user closed window with X
    :rtype: Union[str, None]
    """

    if not args:
        args_to_print = ['']
    else:
        args_to_print = args
    if line_width != None:
        local_line_width = line_width
    else:
        local_line_width = sg.MESSAGE_BOX_LINE_WIDTH
    _title = title if title is not None else args_to_print[0]
    window = sg.Window(_title, text_justification='r', element_justification='r', auto_size_text=True, background_color=background_color, button_color=button_color,
                    auto_close=auto_close, auto_close_duration=auto_close_duration, icon=icon, font=font,
                    no_titlebar=no_titlebar, grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location)
    max_line_total, total_lines = 0, 0
    for message in args_to_print:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        if message.count('\n'):
            message_wrapped = message
        else:
            message_wrapped = sg.textwrap.fill(message, local_line_width)
        message_wrapped_lines = message_wrapped.count('\n') + 1
        longest_line_len = max([len(l) for l in message.split('\n')])
        width_used = min(longest_line_len, local_line_width)
        max_line_total = max(max_line_total, width_used)
        # height = _GetNumLinesNeeded(message, width_used)
        height = message_wrapped_lines
        window.AddRow(
            sg.Text(message_wrapped, auto_size_text=True, text_color=text_color, background_color=background_color))
        total_lines += height

    if non_blocking:
        PopupButton = sg.DummyButton  # important to use or else button will close other windows too!
    else:
        PopupButton = sg.Button
    # show either an OK or Yes/No depending on paramater
    if custom_text != (None, None):
        if type(custom_text) is not tuple:
            window.AddRow(PopupButton(custom_text, size=(len(custom_text), 1), button_color=button_color, focus=True,
                                      bind_return_key=True))
        elif custom_text[1] is None:
            window.AddRow(
                PopupButton(custom_text[0], size=(len(custom_text[0]), 1), button_color=button_color, focus=True,
                            bind_return_key=True))
        else:
            window.AddRow(PopupButton(custom_text[0], button_color=button_color, focus=True, bind_return_key=True,
                                      size=(len(custom_text[0]), 1)),
                          PopupButton(custom_text[1], button_color=button_color, size=(len(custom_text[0]), 1)))
    elif button_type is sg.POPUP_BUTTONS_YES_NO:
        window.AddRow(PopupButton('Yes', button_color=button_color, focus=True, bind_return_key=True, pad=((20, 5), 3),
                                  size=(5, 1)), PopupButton('No', button_color=button_color, size=(5, 1)))
    elif button_type is sg.POPUP_BUTTONS_CANCELLED:
        window.AddRow(
            PopupButton('Cancelled', button_color=button_color, focus=True, bind_return_key=True, pad=((20, 0), 3)))
    elif button_type is sg.POPUP_BUTTONS_ERROR:
        window.AddRow(PopupButton('Error', size=(6, 1), button_color=button_color, focus=True, bind_return_key=True,
                                  pad=((20, 0), 3)))
    elif button_type is sg.POPUP_BUTTONS_OK_CANCEL:
        window.AddRow(PopupButton('OK', size=(6, 1), button_color=button_color, focus=True, bind_return_key=True),
                      PopupButton('Cancel', size=(6, 1), button_color=button_color))
    elif button_type is sg.POPUP_BUTTONS_NO_BUTTONS:
        pass
    else:
        window.AddRow(PopupButton('OK', size=(5, 1), button_color=button_color, focus=True, bind_return_key=True,
                                  pad=((20, 0), 3)))

    if non_blocking:
        button, values = window.Read(timeout=0)
    else:
        button, values = window.Read()
        window.close(); del window

    return button