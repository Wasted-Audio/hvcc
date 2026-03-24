    {%- for object in gui_objects -%}
        {%- if object.type == 'canvas' %}
    // canvas
    {{object.id}} = new PDCanvas({{parent}});
    {{object.id}}->setSize({{object.size.x}} * scaleFactor, {{object.size.y}} * scaleFactor);
    {{object.id}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
    {{object.id}}->setColors(nvgRGB{{object.bg_color.as_rgb_tuple()}});
        {%- elif object.type == 'comment' %}
    // comment
    {{object.id}} = new PDComment({{parent}});
    std::string {{object.id}}String = "{{object.text}}";
    {{object.id}}->setText({{object.id}}String);
    {{object.id}}->setFontSize(15 * scaleFactor);
    {{object.id}}->setAbsolutePos({{object.position.x}} * scaleFactor, {{object.position.y}} * scaleFactor);
            {%- if object.width != None %}
    {{object.id}}->setSize((7 * {{object.width}}) * scaleFactor, 15 * scaleFactor);
            {%- else %}
    {{object.id}}->setSize((7 * {{object.id}}String.length()) * scaleFactor, 15 * scaleFactor);
            {%- endif -%}
        {%- endif -%}
    {%- endfor %}
