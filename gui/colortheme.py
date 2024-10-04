from gui import util


class CustomColorTheme():
    px1 = 24
    px2 = 16
    px3 = 14
    FONT_1 = f"font-family: 'Segoe UI'; font-size: {px1}px; font-weight: normal;"
    BOLD_FONT_1 = f"font-family: 'Segoe UI'; font-size: {px1}px; font-weight: bold;"
    FONT_2 = f"font-family: 'Segoe UI'; font-size: {px2}px; font-weight: normal;"
    MONO_FONT_2 = f"font-family: 'Consolas'; font-size: {px2}px; font-weight: normal;"
    BOLD_FONT_2 = f"font-family: 'Segoe UI'; font-size: {px2}px; font-weight: bold;"
    FONT_3 = f"font-family: 'Segoe UI'; font-size: {px3}px; font-weight: normal;"
    BOLD_FONT_3 = f"font-family: 'Segoe UI'; font-size: {px3}px; font-weight: bold;"
    BACKGROUND = "#2c2c2c"
    ACCENT = "#454344"
    ACCENT_1 = "#676465"
    ACCENT_2 = "#3a9f69"
    ACCENT_3 = "#111111"
    PLAY = "#35a984"
    PAUSE = "#e14949"
    TICK_MARK = "#a0bacd"
    TIMELINE = "#d8c6e6"
    BUTTON_1 = "#007ACC"
    BUTTON_2 = "#f2f2f2"
    DETAILS = "#e5e5e5"
    DETAILSHIGHLIGHT = "#E2A34E"
    
    def get_scroll_log_style(name):
        return f'''
        {name} {{
            background-color: {CustomColorTheme.ACCENT_3};
            border: none;
        }}
        QScrollBar {{
            width: 15px;
        }}
        '''
        
    def get_scroll_accent_style(name):
        return f'''
        {name} {{
            background-color: {CustomColorTheme.ACCENT};
            border: none;
        }}
        QScrollBar {{
            width: 15px;
        }}
        '''
        
    def get_button_2_style(name, color = None):
        if color is None:
            color = CustomColorTheme.BUTTON_2
            
        return f'''
        {name} {{
            {CustomColorTheme.FONT_2}
            background-color: {color};
            padding: 3px 10px;
            border: 1px solid {color};
            border-radius: 2px;
        }}
        {name}:hover {{
            background-color: {util.lighten_hex_color(color, factor= .3)};
        }}
        '''