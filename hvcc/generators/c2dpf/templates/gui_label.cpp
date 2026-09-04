            {%- if object.label != None %}
    {{object.parameter}}->setLabel("{{object.label.text}}",
                {%- if meta.ui_theme_set is sameas true and meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].cnv_text_color is not none %}
        Colors::cnvTextColor,
                {%- else %}
        nvgRGB{{object.label.color.as_rgb_tuple()}},
                {%- endif %}
        {{object.label.position.x}} * scaleFactor, {{object.label.position.y}} * scaleFactor, {{object.label.font_size}} * scaleFactor);
            {%- endif %}
