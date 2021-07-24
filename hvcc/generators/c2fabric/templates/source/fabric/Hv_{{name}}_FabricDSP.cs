{{copyright}}

using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.Assertions;
using AOT;

namespace Fabric {

  public class Hv_{{patch_name}}_FabricDSP : DSPComponent {
    {% if in_events|length > 0 %}
    public enum EventIn : uint {
      {%- for k, v in in_events %}
      {{k}} = {{v.hash}},
      {%- endfor %}
    }
    {% endif -%}
    {% if out_events|length > 0 %}
    public enum EventOut : uint {
      {%- for k, v in out_events %}
      {{k}} = {{v.hash}},
      {%- endfor %}
    }
    {% endif -%}
    {% if in_parameters|length > 0 %}
    public enum ParameterIn : uint {
      {%- for k,v in in_parameters %}
      {{k}} = {{v.hash}},
      {%- endfor %}
    }
    {% endif -%}
    {% if out_parameters|length > 0 %}
    public enum ParameterOut : uint {
      {%- for k,v in out_parameters %}
      {{k}} = {{v.hash}},
      {%- endfor %}
    }
    {% endif %}

    {%- if in_parameters|length > 0 %}
    [HideInInspector]
    [SerializeField]
    {%- for k, v in in_parameters %}
    public DSPParameter {{k}} = new DSPParameter({{v.attributes.default}}f, {{v.attributes.min}}f, {{v.attributes.max}}f); // {{v.display}}
    {%- endfor %}
    {% endif %}

    {%- if out_parameters|length > 0 %}
    [HideInInspector]
    [System.NonSerialized]
    public List<uint> bindingsKeys = new List<uint> {
    {%- for k,v in out_parameters %}
    {%- set comma = "," if loop.index != out_parameters|length else "" %}
      {{v.hash}}{{comma}} // {{k}}
    {%- endfor %}
    };

    [HideInInspector]
    [SerializeField]
    public List<string> bindingsValues = new List<string> {
    {%- for k,v in out_parameters %}
    {%- set comma = "," if loop.index != out_parameters|length else "" %}
      ""{{comma}} // {{k}}
    {%- endfor %}
    };

    private Dictionary<uint, string> _bindings = new Dictionary<uint, string>();

    public void Awake() {
      RefreshBindings();
    }

    public void RefreshBindings() {
      for (int i = 0; i < bindingsKeys.Count; ++i) {
        _bindings[bindingsKeys[i]] = bindingsValues[i];
      }
    }
    {%- endif %}
    public override string GetTypeByName() {
      return "Hv_{{patch_name}}_Fabric";
    }

    public override void OnInitialise(bool addToAudioSourceGameObject) {
      if (addToAudioSourceGameObject) {
        this.OnInitialise("Hv_{{patch_name}}_Fabric");
      }

      Type = DSPType.External;
      {%- for k, v in in_parameters %}
      AddParameter("{{v.display}}", {{k}});
      {%- endfor %}
      UpdateParameters();
    }

    public override UnityEngine.Component CreateComponent(GameObject gameObject) {
      Heavy.Plugin plug = gameObject.AddComponent<Heavy.Plugin>();
      {% if (out_parameters|length > 0) or (out_events|length > 0) -%}
      plug.ReceivedMessageCallback += OnMessageReceived;
      {% endif -%}
      plug.LoadLibrary("{{patch_name}}");
      return plug;
    }
    {% if in_parameters|length > 0 %}
    public override void UpdateParameters() {
      for (int i = 0; i < _dspInstances.Count; i++) {
        Heavy.Plugin plug = _dspInstances[i] as Heavy.Plugin;
        if (plug) {
          {%- for k,v in in_parameters %}
          if (!{{k}}.HasReachedTarget()) {
            plug.SetFloatParameter((uint) Hv_{{patch_name}}_FabricDSP.ParameterIn.{{k}}, {{k}}.GetValue()); // {{v.display}}
          }
          {%- endfor %}
        }
      }
      base.UpdateParameters();
    }
    {% endif %}
    {% if (out_parameters|length > 0) or (out_events|length > 0) -%}
    private void OnMessageReceived(Heavy.Message msg) {
      {%- if out_parameters|length > 0 %}
      switch (msg.destination) {
        {%- for k,v in out_parameters %}
        case (uint) ParameterOut.{{k}}: {
          if (msg.IsFloat(0)) {
            UpdateGlobalParameter(msg.destination, msg.GetFloat(0));
          }
          break;
        }
        {%- endfor %}
        default: break;
      }
      {%- endif %}
      {%- if out_events|length > 0 %}
      switch (msg.destination) {
        {%- for k,v in out_events %}
        case (uint) EventOut.{{k}}: {
          {%- if k == "finished" %}
          if (msg.IsBang(0)) {
            Component component = gameObject.GetComponent<Fabric.Component>();
            if (component != null) {
              component.Stop();
            }
          }
          {%- else %}
          // send event {{v.display}}
          {%- endif %}
          break;
        }
        {%- endfor %}
        default: break;
      }
      {%- endif %}
    }
    {%- endif %}

    {% if (out_parameters|length > 0) -%}
    private void UpdateGlobalParameter(uint hash, float value) {
      string globalParameterName = "";
      if (_bindings.TryGetValue(hash, out globalParameterName)) {
        EventManager.Instance.SetGlobalParameter(globalParameterName, value);
      } else {
        Debug.LogError(
          string.Format("Hv_sine_FabricDSP: {0} doesn't exist in parameter bindings.", hash),
          gameObject);
      }
    }
    {%- endif %}
  }
}
{# force new line #}
