{{copyright}}

using UnityEngine;
using UnityEditor;
using System.Collections;
using System;

namespace Fabric {

  [CustomEditor(typeof(Hv_{{patch_name}}_FabricDSP))]
  public class Hv_{{patch_name}}_FabricDSPEditor : Editor {

    [MenuItem("Fabric/Components/Heavy/{{patch_name}}")]
    static void CreateHv_{{patch_name}}_FabricGameObject() {
      GameObject target = Selection.activeGameObject;
      if (target == null) return;

      GameObject component = new GameObject("Hv_{{patch_name}}_FabricGameObject");
      component.transform.parent = target.transform;
      component.AddComponent<AudioComponent>();
      component.AddComponent<Hv_{{patch_name}}_FabricDSP>();
    }
    {%- if (in_parameters|length > 0) or (out_parameters|length > 0) %}

    private Hv_{{patch_name}}_FabricDSP _dsp;
    {%- if in_parameters|length > 0 %}
    private bool _showInParams = true;
    {%- endif %}
    {%- if out_parameters|length > 0 %}
    private bool _showOutParams = true;
    {%- endif %}

    private void OnEnable() {
      _dsp = target as Hv_{{patch_name}}_FabricDSP;
    }

    public override void OnInspectorGUI() {
      {% if in_parameters|length > 0 -%}
      if (_showInParams = EditorGUILayout.Foldout(_showInParams, "Input Parameters:")) {
        GUILayout.BeginVertical("Box");
        {%- for k,v in in_parameters %}
        // {{v.display}}
        GUILayout.BeginHorizontal();
        EditorGUILayout.PrefixLabel("{{v.display}}:");
        _dsp.{{k}}.SetValue(EditorGUILayout.Slider(_dsp.{{k}}.GetTargetValue(), _dsp.{{k}}.Min, _dsp.{{k}}.Max));
        GUILayout.Label("(" + _dsp.{{k}}.GetValue() + ")", GUILayout.Width(50));
        GUILayout.EndHorizontal();
        {%- endfor %}
        GUILayout.EndVertical();
      }
      {% endif -%}
      {% if out_parameters|length > 0 -%}
      if (_showOutParams = EditorGUILayout.Foldout(_showOutParams, "Output Parameters")) {
        string[] globalParameterNames = EventManager.Instance._globalParameterManager._globalRTParameters.Keys();
        GUILayout.BeginVertical("Box");
        {%- for k,v in out_parameters %}
        ShowOutputParameter("{{v.display}}:", {{loop.index-1}}, ref globalParameterNames); // {{v.display}}
        {%- endfor %}
        GUILayout.EndVertical();
      }
      {%- endif %}
      GUIHelpers.CheckGUIHasChanged(_dsp.gameObject);
    }
    {%- if out_parameters|length > 0 %}
    private void ShowOutputParameter(string label, int index, ref string[] globalParameterNames) {
      if (index < _dsp.bindingsKeys.Count) {

        GUILayout.BeginHorizontal();
        EditorGUILayout.PrefixLabel(label);
        GUILayout.FlexibleSpace();

        int selection = Array.IndexOf(globalParameterNames, _dsp.bindingsValues[index]);
        selection = EditorGUILayout.Popup("", selection, globalParameterNames);

        if (GUILayout.Button("Del") || selection < 0 ) {
          _dsp.bindingsValues[index] = "";
          _dsp.RefreshBindings();
        } else {
          if (_dsp.bindingsValues[index] != globalParameterNames[selection]) {
            _dsp.bindingsValues[index] = globalParameterNames[selection];
            _dsp.RefreshBindings();
          }
        }
        GUILayout.EndHorizontal();
      }
    }
    {%- endif %}
    {%- endif %}
  }
}
{# force new line #}
