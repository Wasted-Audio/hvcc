studio.plugins.registerPluginDescription("{{name}}", {
  companyName: "PlugData",
  productName: "{{name|capitalize}}",
  parameters: {
    {%- for param, i in in_params %}
    "{{param}}": {
      displayName: "{{param|capitalize}}"
    },
    {%- endfor %}
  },
});
