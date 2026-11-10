studio.plugins.registerPluginDescription("{{name}}", {
  companyName: "Wasted Audio",
  productName: "{{name|capitalize}}",
  parameters: {
    {%- for param, i in in_params %}
    "{{param}}": {
      displayName: "{{param|capitalize}}"
    },
    {%- endfor %}
  },
});
