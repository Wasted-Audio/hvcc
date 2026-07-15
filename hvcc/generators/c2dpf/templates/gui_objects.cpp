    {%- for object in gui_objects -%}
        {%- if object.type == 'canvas' %}
    // canvas
    {{object.id}} = new PDCanvas({{parent}});
    {{object.id}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.id}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.id}}->setColors(nvgRGB{{object.bg_color.as_rgb_tuple()}});
            {%- if object.label != None %}
    {{object.id}}->setLabel("{{object.label.text}}",
                {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].cnv_text_color is not none %}
        Colors::cnvTextColor,
                {%- else %}
        nvgRGB{{object.label.color.as_rgb_tuple()}},
                {%- endif %}
        {{object.label.position.x}} * scaleFactor, {{object.label.position.y}} * scaleFactor, {{object.label.font_size}} * scaleFactor);
            {%- endif %}
        {%- elif object.type == 'comment' %}
    // comment
    {{object.id}} = new PDComment({{parent}});
    std::string {{object.id}}String = "{{object.text}}";
    {{object.id}}->setText({{object.id}}String);
    {{object.id}}->setFontSize(15 * scaleFactor);
    {{object.id}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
            {%- if object.width != None %}
    {{object.id}}->setSize((7.4 * {{object.width}}) * scaleFactor, 15 * scaleFactor);
            {%- else %}
    {{object.id}}->setSize((7.4 * {{object.id}}String.length()) * scaleFactor, 15 * scaleFactor);
            {%- endif -%}
        {%- elif object.type == 'bang' %}
    // bang
    {{object.parameter}} = new PDBang({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setColors(
            {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].bg_color is not none and meta.ui_themes[meta.ui_theme].cnvTextColor is not none %}
        Colors::bgColor,
        Colors::cnvTextColor
            {%- else %}
        nvgRGB{{object.bg_color.as_rgb_tuple()}},
        nvgRGB{{object.fg_color.as_rgb_tuple()}}
            {%- endif %}
    );
    {{object.parameter}}->setInterval({{object.flash_time}});
{% include 'gui_label.cpp' %}
    {{parent}}->addManagedChild({{object.parameter}});
        {%- elif object.type == 'toggle' %}
    // toggle
    {{object.parameter}} = new PDToggle({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setColors(
            {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].bg_color is not none and meta.ui_themes[meta.ui_theme].cnvTextColor is not none %}
        Colors::bgColor,
        Colors::cnvTextColor
            {%- else %}
        nvgRGB{{object.bg_color.as_rgb_tuple()}},
        nvgRGB{{object.fg_color.as_rgb_tuple()}}
            {%- endif %}
    );
    {{parent}}->addManagedChild({{object.parameter}});
        {%- elif object.type in ['vradio', 'hradio'] %}
    // {{object.type}}
    {{object.parameter}} = new PDRadio({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setStep({{object.options}});
            {%- if object.type == "hradio" %}
    {{object.parameter}}->setHorizontal();
            {%- endif %}
    {{object.parameter}}->setColors(
            {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].bg_color is not none and meta.ui_themes[meta.ui_theme].cnvTextColor is not none %}
        Colors::bgColor,
        Colors::cnvTextColor
            {%- else %}
        nvgRGB{{object.bg_color.as_rgb_tuple()}},
        nvgRGB{{object.fg_color.as_rgb_tuple()}}
            {%- endif %}
    );
{% include 'gui_label.cpp' %}
    {{parent}}->addManagedChild({{object.parameter}});
        {%- elif object.type in ['vslider', 'hslider'] %}
    // {{object.type}}
    {{object.parameter}} = new PDSlider({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setSliderArea(0, 0, {{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
            {%- if object.type == "vslider" %}
    {{object.parameter}}->setStartPos(0, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setEndPos(0, 0);
    {{object.parameter}}->setInverted(true);
            {%- elif object.type == "hslider" %}
    {{object.parameter}}->setStartPos(0, 0);
    {{object.parameter}}->setEndPos({{object.size.x}} * scaleFactor, 0);
    {{object.parameter}}->setHorizontal();
            {%- endif %}
    {{object.parameter}}->setRange({{object.min}}f, {{object.max}}f);
        {%- for k, v in receivers + senders %}
            {%- if v.display == object.parameter %}
    {{object.parameter}}->setDefault({{v.attributes.default}}f);
            {%- endif %}
        {%- endfor %}
    {{object.parameter}}->setUsingLogScale({{object.logarithmic|lower}});
    {{object.parameter}}->setSteadyOnClick({{object.steady|lower}});
    {{object.parameter}}->setColors(
            {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].bg_color is not none and meta.ui_themes[meta.ui_theme].cnvTextColor is not none %}
        Colors::bgColor,
        Colors::cnvTextColor
            {%- else %}
        nvgRGB{{object.bg_color.as_rgb_tuple()}},
        nvgRGB{{object.fg_color.as_rgb_tuple()}}
            {%- endif %}
    );
{% include 'gui_label.cpp' %}
    {{parent}}->addManagedChild({{object.parameter}});
        {%- elif object.type == 'knob' %}
    // knob
    {{object.parameter}} = new PDKnob({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setKnobArea(0.0f, 0.0f, {{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setRange({{object.min}}f, {{object.max}}f);
        {%- for k, v in receivers + senders %}
            {%- if v.display == object.parameter %}
    {{object.parameter}}->setDefault({{v.attributes.default}}f);
            {%- endif %}
        {%- endfor %}
    {{object.parameter}}->setShowArc({{object.arc_show|lower}});
    {{object.parameter}}->setAngular({{object.ang_range}}, {{object.ang_offset}});
    {{object.parameter}}->setDrawSquare({{object.square|lower}});
    {{object.parameter}}->setShowTicks({{object.ticks|lower}});
    {{object.parameter}}->setSteps({{object.steps}});
    {{object.parameter}}->setShowArc({{object.arc_show|lower}});
    {{object.parameter}}->setJumpOnClick({{object.jump|lower}});
    {{object.parameter}}->setDiscrete({{object.discrete|lower}});
    {{object.parameter}}->setUsingLogScale(PDKnobEventHandler::LogMode::{{object.log_mode|upper}});
    {{object.parameter}}->setColors(
        {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].bg_color is not none and meta.ui_themes[meta.ui_theme].cnvTextColor is not none and meta.ui_themes[meta.ui_theme].io_color is not none %}
        Colors::bgColor,
        Colors::cnvTextColor,
        Colors::ioColor
            {%- else %}
        nvgRGB{{object.bg_color.as_rgb_tuple()}},
        nvgRGB{{object.fg_color.as_rgb_tuple()}},
        nvgRGB{{object.arc_color.as_rgb_tuple()}}
            {%- endif %}
    );
    {{object.parameter}}->setLabelStyle({{object.label_pos.x}} * scaleFactor, {{object.label_pos.y}} * scaleFactor, {{object.label_size}} * scaleFactor);
    {{object.parameter}}->setShowLabel(LabelShow::{{object.label_show.name|upper}});
    {{parent}}->addManagedChild({{object.parameter}});
        {%- elif object.type == 'number' %}
    // number
    {{object.parameter}} = new PDNumber({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setRange({{object.min}}f, {{object.max}}f);
        {%- for k, v in receivers + senders %}
            {%- if v.display == object.parameter %}
    {{object.parameter}}->setDefault({{v.attributes.default}}f);
            {%- endif %}
        {%- endfor %}
    {{object.parameter}}->setColors(
            {%- if meta.ui_theme is not none and meta.ui_themes[meta.ui_theme].bg_color is not none and meta.ui_themes[meta.ui_theme].cnvTextColor is not none %}
        Colors::bgColor,
        Colors::cnvTextColor
            {%- else %}
        nvgRGB{{object.bg_color.as_rgb_tuple()}},
        nvgRGB{{object.fg_color.as_rgb_tuple()}}
            {%- endif %}
    );
{% include 'gui_label.cpp' %}
    {{parent}}->addManagedChild({{object.parameter}});
        {%- elif object.type == 'float' %}
    // float
    {{object.parameter}} = new PDFloat({{parent}}, this);
    {{object.parameter}}->setId(k{{object.parameter|capitalize}});
    {{object.parameter}}->setSize({{object.size.x}} * scaleFactor, ({{object.size.y}} * 1.5f) * scaleFactor);
    {{object.parameter}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.parameter}}->setRange({{object.min}}f, {{object.max}}f);
        {%- for k, v in receivers + senders %}
            {%- if v.display == object.parameter %}
    {{object.parameter}}->setDefault({{v.attributes.default}}f);
            {%- endif %}
        {%- endfor %}
    {{object.parameter}}->setLabel("{{object.label_text}}", ({{object.font_height}} + 2) * scaleFactor, LabelPos::{{object.label_pos.name|capitalize}});
    {{parent}}->addManagedChild({{object.parameter}});
        {%- endif %}
    {%- endfor %}
