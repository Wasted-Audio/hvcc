{{copyright}}

#include "DistrhoUI.hpp"
#include "DistrhoPluginInfo.h"
#include "nanovg.h"

#include "pdvg.hpp"


START_NAMESPACE_DISTRHO

class {{class_name}} : public UI,
                             public PDSliderEventHandler::Callback,
                             public PDToggleEventHandler::Callback,
                             public PDRadioEventHandler::Callback,
                             public PDNumberEventHandler::Callback,
                             public PDKnobEventHandler::Callback,
                             public PDBangEventHandler::Callback
{
public:
    {{class_name}}();
    ~{{class_name}}();

protected:
    void parameterChanged(uint32_t index, float value) override;
    void onNanoDisplay() override;
    void sliderValueChanged(SubWidget *const widget, float value) override;
    void switchClicked(SubWidget *const widget, bool down) override;
    void bangClicked(SubWidget *const widget) override;
    void radioValueChanged(SubWidget *const widget, uint index) override;
    void numberValueChanged(SubWidget *const widget, float value) override;
    void knobValueChanged(SubWidget *const widget, float value) override;

private:
    ScopedPointer<PDMainpatch> mainPatch;
    {%- for type in widgets.keys() %}
        {%- for widget in widgets[type] %}
            {%- if type == 'graph' %}
                {%- set object = 'PDSubpatch' %}
            {%- elif type == 'canvas' %}
                {%- set object = 'PDCanvas' %}
            {%- elif type == 'comment' %}
                {%- set object = 'PDComment' %}
            {%- elif type == 'bang' %}
                {%- set object = 'PDBang' %}
            {%- elif type == 'toggle' %}
                {%- set object = 'PDToggle' %}
            {%- elif type in ['vradio', 'hradio'] %}
                {%- set object = 'PDRadio' %}
            {%- elif type in ['vslider', 'hslider'] %}
                {%- set object = 'PDSlider' %}
            {%- elif type == 'knob' %}
                {%- set object = 'PDKnob' %}
            {%- elif type == 'number' %}
                {%- set object = 'PDNumber' %}
            {%- elif type == 'float' %}
                {%- set object = 'PDFloat' %}
            {%- endif %}
    ScopedPointer<{{object}}> {{widget}};
        {%- endfor %}
    {%- endfor %}

    DISTRHO_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR({{class_name}})
};

END_NAMESPACE_DISTRHO
