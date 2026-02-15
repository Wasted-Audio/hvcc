{{copyright}}

#if _MSC_VER || _WIN32 || _WIN64
#include <malloc.h>
#define DLL_EXPORT __declspec(dllexport) extern
#else
#include <alloca.h>
#define DLL_EXPORT	
#endif

#include <string.h>
#include "m_pd.h"
#include "Heavy_{{name}}.h"

static t_class *{{struct_name}}_class;

typedef struct _{{struct_name}} {
  t_object x_obj;
  {# declare inlets and outlets #}
  {%- for i in range(1, num_input_channels) %}
  t_inlet *inlet{{i}};
  {%- endfor %}
  {%- for i in range(num_output_channels) %}
  t_outlet *outlet{{i}};
  {%- endfor %}
  t_outlet *msgOutlet;

  HeavyContextInterface *hv;
  t_float f; // dummy
} t_{{struct_name}};

static void printHook(HeavyContextInterface *c, const char *receiverName, const char *msgString, const HvMessage *m) {
  double timestampMs = 1000.0 * ((double) hv_msg_getTimestamp(m)) / hv_getSampleRate(c);
  post("[{{display_name}} @ %0.3gms] %s: %s", timestampMs, receiverName, msgString);
}

static void sendHook(HeavyContextInterface *c, const char *receiverName, unsigned int receiverHash, const HvMessage * m) {
  if (!strcmp(receiverName, "HV_TO_PD")) {
    t_outlet *const outlet = ((t_{{struct_name}} *) hv_getUserData(c))->msgOutlet;
    if (hv_msg_getNumElements(m) == 1) {
      if (hv_msg_isFloat(m, 0)) {
        outlet_float(outlet, hv_msg_getFloat(m, 0));
      } else if (hv_msg_isBang(m, 0)) {
        outlet_bang(outlet);
      } else if (hv_msg_isSymbol(m, 0)) {
        outlet_symbol(outlet, gensym(hv_msg_getSymbol(m, 0)));
      } else return;
    } else {
      const int argc = (int) hv_msg_getNumElements(m);
      t_atom *argv = (t_atom *) alloca(argc*sizeof(t_atom));
      for (int i = 0; i < argc; i++) {
        if (hv_msg_isFloat(m, i)) {
          SETFLOAT(argv+i, hv_msg_getFloat(m, i));
        } else if (hv_msg_isSymbol(m, i)) {
          SETSYMBOL(argv+i, gensym(hv_msg_getSymbol(m, i)));
        } else return;
      }
      outlet_list(outlet, NULL, argc, argv);
    }
  }
}

static void *{{struct_name}}_new(t_symbol *s, int argc, t_atom *argv) {
  t_{{struct_name}} *x = (t_{{struct_name}} *) pd_new({{struct_name}}_class);
  {%- for i in range(1, num_input_channels) %}
  x->inlet{{i}} = signalinlet_new(&x->x_obj, 0.0f);
  {%- endfor %}
  {%- for i in range(num_output_channels) %}
  x->outlet{{i}} = outlet_new(&x->x_obj, &s_signal);
  {%- endfor %}
  x->msgOutlet = outlet_new(&x->x_obj, &s_anything);

  x->hv = hv_{{name}}_new((double) sys_getsr());
  hv_setUserData(x->hv, x);
  hv_setPrintHook(x->hv, printHook);
  hv_setSendHook(x->hv, sendHook);

  return (void *) x;
}

static void {{struct_name}}_free(t_{{struct_name}} *x) {
  {%- for i in range(num_input_channels-1) %}
  inlet_free(x->inlet{{i+1}});
  {%- endfor %}
  {%- for i in range(num_output_channels) %}
  outlet_free(x->outlet{{i}});
  {%- endfor %}
  outlet_free(x->msgOutlet);
  hv_delete(x->hv);
}

static t_int *{{struct_name}}_perform(t_int *w) {
  t_{{struct_name}} *x = (t_{{struct_name}} *) w[1];
  {%- if num_input_channels > 0 %}
  float *inputChannels[{{num_input_channels}}] = {
  {%- for i in range(num_input_channels) %}
    (t_sample *) w[{{i+2}}],
  {%- endfor %}
  };
  {%- else %}
  float **inputChannels = NULL;
  {%- endif %}
  {%- if num_output_channels > 0 %}
  float *outputChannels[{{num_output_channels}}] = {
  {%- for i in range(num_output_channels) %}
    (t_sample *) w[{{num_input_channels+i+2}}],
  {%- endfor %}
  };
  {%- else %}
  float **outputChannels = NULL;
  {%- endif %}
  int n = (int) (w[{{num_input_channels+num_output_channels+2}}]);

  hv_process(x->hv, inputChannels, outputChannels, n);

  return (w+{{num_input_channels+num_output_channels+3}});
}

static void {{struct_name}}_dsp(t_{{struct_name}} *x, t_signal **sp) {
  dsp_add({{struct_name}}_perform,
      {{num_input_channels+num_output_channels+2}}, x,
      {%- for i in range(num_input_channels) %}
      sp[{{i}}]->s_vec,
      {%- endfor %}
      {%- for i in range(num_input_channels|max(1), num_input_channels|max(1)+num_output_channels) %}
      sp[{{i}}]->s_vec,
      {%- endfor %}
      sp[0]->s_n);
}

static void {{struct_name}}_onMessage(t_{{struct_name}} *x, t_symbol *s0, int argc, t_atom* argv) {
  // convert a Pd message into a Heavy message
  HvMessage *msg = (HvMessage *) alloca(hv_msg_getByteSize(argc > 0 ? argc : 1));
  if (argc > 0) {
    hv_msg_init(msg, argc, 0);
    for (int i = 0; i < argc; i++) {
      switch (argv[i].a_type) {
        case A_FLOAT: hv_msg_setFloat(msg, i, atom_getfloat(argv+i)); break;
        case A_SYMBOL: hv_msg_setSymbol(msg, i, atom_getsymbol(argv+i)->s_name); break;
        default: return;
      }
    }
  } else {
    hv_msg_init(msg, 1, 0);
    hv_msg_setBang(msg, 0);
  }
  hv_sendMessageToReceiver(x->hv, hv_stringToHash(s0->s_name), 0.0, msg);
}

DLL_EXPORT void {{struct_name}}_setup() {
  {{struct_name}}_class = class_new(gensym("{{display_name}}"),
      (t_newmethod) {{struct_name}}_new,
      (t_method) {{struct_name}}_free,
      sizeof(t_{{struct_name}}),
      CLASS_DEFAULT, A_GIMME, 0);
  class_addmethod({{struct_name}}_class, (t_method) {{struct_name}}_dsp, gensym("dsp"), 0);
  class_addanything({{struct_name}}_class, (t_method) {{struct_name}}_onMessage);
  CLASS_MAINSIGNALIN({{struct_name}}_class, t_{{struct_name}}, f);
}
{# force new line #}
