{{copyright}}

#include "Heavy_{{name}}.hpp"

#include <new>

#define Context(_c) static_cast<Heavy_{{name}} *>(_c)


/*
 * C Functions
 */

extern "C" {
  HV_EXPORT HeavyContextInterface *hv_{{name}}_new(double sampleRate) {
    // allocate aligned memory
    void *ptr = hv_malloc(sizeof(Heavy_{{name}}));
    // ensure non-null
    if (!ptr) return nullptr;
    // call constructor
    new(ptr) Heavy_{{name}}(sampleRate);
    return Context(ptr);
  }

  HV_EXPORT HeavyContextInterface *hv_{{name}}_new_with_options(double sampleRate,
      int poolKb, int inQueueKb, int outQueueKb) {
    // allocate aligned memory
    void *ptr = hv_malloc(sizeof(Heavy_{{name}}));
    // ensure non-null
    if (!ptr) return nullptr;
    // call constructor
    new(ptr) Heavy_{{name}}(sampleRate, poolKb, inQueueKb, outQueueKb);
    return Context(ptr);
  }

  HV_EXPORT void hv_{{name}}_free(HeavyContextInterface *instance) {
    // call destructor
    Context(instance)->~Heavy_{{name}}();
    // free memory
    hv_free(instance);
  }
} // extern "C"



{% if table_data_list|length > 0 -%}
/*
 * Table Data
 */
{% for x in table_data_list %}
{{x}}
{%- endfor %}
{%- endif %}



/*
 * Class Functions
 */

Heavy_{{name}}::Heavy_{{name}}(double sampleRate, int poolKb, int inQueueKb, int outQueueKb)
    : HeavyContext(sampleRate, poolKb, inQueueKb, outQueueKb) {
  {%- for x in init_list %}
  numBytes += {{x}}
  {%- endfor %}
  {% if "__hv_init" in send_receive %}
  // schedule a message to trigger all loadbangs via the __hv_init receiver
  scheduleMessageForReceiver({{send_receive["__hv_init"]["hash"]}}, msg_initWithBang(HV_MESSAGE_ON_STACK(1), 0));
  {%- endif %}
}

Heavy_{{name}}::~Heavy_{{name}}() {
  {%- if free_list|length > 0 %}
  {%- for x in free_list %}
  {{x}}
  {%- endfor %}
  {%- else %}
  // nothing to free
  {%- endif %}
}

HvTable *Heavy_{{name}}::getTableForHash(hv_uint32_t tableHash) {
  {%- if send_table|length > 0 -%}
  switch (tableHash) {
    {%- for k,v in send_table.items() %}
    case {{v.hash}}: return &hTable_{{v.id}}; // {{v.display}}
    {%- endfor %}
    default: return nullptr;
  }
  {%- else %}
  return nullptr;
  {%- endif %}
}

void Heavy_{{name}}::scheduleMessageForReceiver(hv_uint32_t receiverHash, HvMessage *m) {
  switch (receiverHash) {
    {%- for k,v in send_receive.items() %}
    case {{v.hash}}: { // {{v.display}}
      {%- for obj_id in v.ids %}
      mq_addMessageByTimestamp(&mq, m, 0, &cReceive_{{obj_id}}_sendMessage);
      {%- endfor %}
      break;
    }
    {%- endfor %}
    default: return;
  }
}

int Heavy_{{name}}::getParameterInfo(int index, HvParameterInfo *info) {
  if (info != nullptr) {
    switch (index) {
      {%- for v in (send_receive|extern).values() %}
      case {{loop.index-1}}: {
        info->name = "{{v.display}}";
        info->hash = {{v.hash}};
        {%- if v.extern == "param" %}
        info->type = HvParameterType::HV_PARAM_TYPE_PARAMETER_IN;
        info->minVal = {{v.attributes.min}}f;
        info->maxVal = {{v.attributes.max}}f;
        info->defaultVal = {{v.attributes.default}}f;
        {%- else %}
        info->type = HvParameterType::HV_PARAM_TYPE_EVENT_IN;
        info->minVal = 0.0f;
        info->maxVal = 0.0f;
        info->defaultVal = 0.0f;
        {%- endif %}
        break;
      }
      {%- endfor %}
      default: {
        info->name = "invalid parameter index";
        info->hash = 0;
        info->type = HvParameterType::HV_PARAM_TYPE_PARAMETER_IN;
        info->minVal = 0.0f;
        info->maxVal = 0.0f;
        info->defaultVal = 0.0f;
        break;
      }
    }
  }
  return {{send_receive|extern|length}};
}



/*
 * Send Function Implementations
 */

{% for x in impl_list %}
void Heavy_{{name}}::{{x}}
{% if not loop.last -%}

{%- endif %}
{%- endfor %}



/*
 * Context Process Implementation
 */

int Heavy_{{name}}::process(float **inputBuffers, float **outputBuffers, int n) {
  while (hLp_hasData(&inQueue)) {
    hv_uint32_t numBytes = 0;
    ReceiverMessagePair *p = reinterpret_cast<ReceiverMessagePair *>(hLp_getReadBuffer(&inQueue, &numBytes));
    hv_assert(numBytes >= sizeof(ReceiverMessagePair));
    scheduleMessageForReceiver(p->receiverHash, &p->msg);
    hLp_consume(&inQueue);
  }

  {%- if signal.numInputBuffers > 0 or signal.numOutputBuffers > 0 %}
  const int n4 = n & ~HV_N_SIMD_MASK; // ensure that the block size is a multiple of HV_N_SIMD

  // temporary signal vars
  {%- if signal.numTemporaryBuffers.float > 0 %}
  hv_bufferf_t {% for i in range(signal.numTemporaryBuffers.float) %}Bf{{i}}{% if not loop.last %}, {%endif%}{% endfor %};
  {%- endif %}
  {%- if signal.numTemporaryBuffers.integer > 0 %}
  hv_bufferi_t {% for i in range(signal.numTemporaryBuffers.integer) %}Bi{{i}}{% if not loop.last %}, {%endif%}{% endfor %};
  {%- endif %}

  // input and output vars
  {%- if signal.numOutputBuffers > 0 %}
  hv_bufferf_t {% for i in range(signal.numOutputBuffers) %}O{{i}}{% if not loop.last %}, {%endif%}{% endfor %};
  {%- endif %}
  {%- if signal.numInputBuffers > 0 %}
  hv_bufferf_t {% for i in range(signal.numInputBuffers) %}I{{i}}{% if not loop.last %}, {%endif%}{% endfor %};
  {%- endif %}

  // declare and init the zero buffer
  hv_bufferf_t ZERO; __hv_zero_f(VOf(ZERO));

  hv_uint32_t nextBlock = blockStartTimestamp;
  for (int n = 0; n < n4; n += HV_N_SIMD) {

    // process all of the messages for this block
    nextBlock += HV_N_SIMD;
    while (mq_hasMessageBefore(&mq, nextBlock)) {
      MessageNode *const node = mq_peek(&mq);
      node->sendMessage(this, node->let, node->m);
      mq_pop(&mq);
    }

    {% if signal.numInputBuffers > 0 -%}
    // load input buffers
    {%- for i in range(signal.numInputBuffers) %}
    __hv_load_f(inputBuffers[{{i}}]+n, VOf(I{{i}}));
    {%- endfor %}
    {%- endif %}

    {% if signal.numOutputBuffers > 0 -%}
    // zero output buffers
    {%- for i in range(signal.numOutputBuffers) %}
    __hv_zero_f(VOf(O{{i}}));
    {%- endfor %}
    {%- endif %}

    // process all signal functions
    {%- for f in process_list %}
    {{f}}
    {%- endfor %}

    // save output vars to output buffer
    {%- if signal.numOutputBuffers > 0 %}
    {%- for i in range(signal.numOutputBuffers) %}
    __hv_store_f(outputBuffers[{{i}}]+n, VIf(O{{i}}));
    {%- endfor %}
    {%- else %}
    // no output channels
    {%- endif %}
  }

  blockStartTimestamp = nextBlock;

  return n4; // return the number of frames processed
  {%- else %}
  {# if this is a control-only patch, the process loop is substantially simpler. #}
  hv_uint32_t nextBlock = blockStartTimestamp + n;
  while (mq_hasMessageBefore(&mq, nextBlock)) {
    MessageNode *const node = mq_peek(&mq);
    node->sendMessage(this, node->let, node->m);
    mq_pop(&mq);
  }

  blockStartTimestamp = nextBlock;
  return n;
  {%- endif %}
}

int Heavy_{{name}}::processInline(float *inputBuffers, float *outputBuffers, int n4) {
  hv_assert(!(n4 & HV_N_SIMD_MASK)); // ensure that n4 is a multiple of HV_N_SIMD

  // define the heavy input buffer for {{signal.numInputBuffers}} channel(s)
  {%- if signal.numInputBuffers == 0 %}
  float **const bIn = NULL;
  {%- elif signal.numInputBuffers == 1 %}
  float **const bIn = &inputBuffers;
  {%- else %}
  float **const bIn = reinterpret_cast<float **>(hv_alloca({{signal.numInputBuffers}}*sizeof(float *)));
  {%- for i in range(signal.numInputBuffers) %}
  bIn[{{i}}] = inputBuffers+({{i}}*n4);
  {%- endfor %}
  {%- endif %}

  // define the heavy output buffer for {{signal.numOutputBuffers}} channel(s)
  {%- if signal.numOutputBuffers == 0 %}
  float **const bOut = NULL;
  {%- elif signal.numOutputBuffers == 1 %}
  float **const bOut = &outputBuffers;
  {%- else %}
  float **const bOut = reinterpret_cast<float **>(hv_alloca({{signal.numOutputBuffers}}*sizeof(float *)));
  {%- for i in range(signal.numOutputBuffers) %}
  bOut[{{i}}] = outputBuffers+({{i}}*n4);
  {%- endfor %}
  {%- endif %}

  int n = process(bIn, bOut, n4);
  return n;
}

int Heavy_{{name}}::processInlineInterleaved(float *inputBuffers, float *outputBuffers, int n4) {
  hv_assert(n4 & ~HV_N_SIMD_MASK); // ensure that n4 is a multiple of HV_N_SIMD

  // define the heavy input buffer for {{signal.numInputBuffers}} channel(s), uninterleave
  {%- if signal.numInputBuffers == 0 %}
  float *const bIn = NULL;
  {%- elif signal.numInputBuffers == 1 %}
  float *const bIn = inputBuffers;
  {%- elif signal.numInputBuffers == 2 %}
  float *const bIn = reinterpret_cast<float *>(hv_alloca(2*n4*sizeof(float)));
  #if HV_SIMD_SSE || HV_SIMD_AVX
  for (int i = 0, j = 0; j < n4; j += 4, i += 8) {
    __m128 a = _mm_load_ps(inputBuffers+i);                // LRLR
    __m128 b = _mm_load_ps(inputBuffers+4+i);              // LRLR
    __m128 x = _mm_shuffle_ps(a, b, _MM_SHUFFLE(2,0,2,0)); // LLLL
    __m128 y = _mm_shuffle_ps(a, b, _MM_SHUFFLE(3,1,3,1)); // RRRR
    _mm_store_ps(bIn+j, x);
    _mm_store_ps(bIn+n4+j, y);
  }
  #elif HV_SIMD_NEON
  for (int i = 0, j = 0; j < n4; j += 4, i += 8) {
    float32x4x2_t a = vld2q_f32(inputBuffers+i); // load and uninterleave
    vst1q_f32(bIn+j, a.val[0]);
    vst1q_f32(bIn+n4+j, a.val[1]);
  }
  #else // HV_SIMD_NONE
  for (int j = 0; j < n4; ++j) {
    {%- for i in range(signal.numInputBuffers) %}
    bIn[{{i}}*n4+j] = inputBuffers[{{i}}+{{signal.numInputBuffers}}*j];
    {%- endfor %}
  }
  #endif
  {%- else %}
  float *const bIn = (float *) hv_alloca({{signal.numInputBuffers}}*n4*sizeof(float));
  for (int j = 0; j < n4; ++j) {
    {%- for i in range(signal.numInputBuffers) %}
    bIn[{{i}}*n4+j] = inputBuffers[{{i}}+{{signal.numInputBuffers}}*j];
    {%- endfor %}
  }
  {%- endif %}

  // define the heavy output buffer for {{signal.numOutputBuffers}} channel(s)
  {%- if signal.numOutputBuffers == 0 %}
  float *const bOut = NULL;
  {%- elif signal.numOutputBuffers == 1 %}
  float *const bOut = outputBuffers;
  {%- else %}
  float *const bOut = reinterpret_cast<float *>(hv_alloca({{signal.numOutputBuffers}}*n4*sizeof(float)));
  {%- endif %}

  int n = processInline(bIn, bOut, n4);

  {% if signal.numOutputBuffers == 2 -%}
  // interleave the heavy output into the output buffer
  #if HV_SIMD_AVX
  for (int i = 0, j = 0; j < n4; j += 8, i += 16) {
    __m256 x = _mm256_load_ps(bOut+j);    // LLLLLLLL
    __m256 y = _mm256_load_ps(bOut+n4+j); // RRRRRRRR
    __m256 a = _mm256_unpacklo_ps(x, y);  // LRLRLRLR
    __m256 b = _mm256_unpackhi_ps(x, y);  // LRLRLRLR
    _mm256_store_ps(outputBuffers+i, a);
    _mm256_store_ps(outputBuffers+8+i, b);
  }
  #elif HV_SIMD_SSE
  for (int i = 0, j = 0; j < n4; j += 4, i += 8) {
    __m128 x = _mm_load_ps(bOut+j);    // LLLL
    __m128 y = _mm_load_ps(bOut+n4+j); // RRRR
    __m128 a = _mm_unpacklo_ps(x, y);  // LRLR
    __m128 b = _mm_unpackhi_ps(x, y);  // LRLR
    _mm_store_ps(outputBuffers+i, a);
    _mm_store_ps(outputBuffers+4+i, b);
  }
  #elif HV_SIMD_NEON
  // https://community.arm.com/groups/processors/blog/2012/03/13/coding-for-neon--part-5-rearranging-vectors
  for (int i = 0, j = 0; j < n4; j += 4, i += 8) {
    float32x4_t x = vld1q_f32(bOut+j);
    float32x4_t y = vld1q_f32(bOut+n4+j);
    float32x4x2_t z = {x, y};
    vst2q_f32(outputBuffers+i, z); // interleave and store
  }
  #else // HV_SIMD_NONE
  for (int i = 0; i < {{signal.numOutputBuffers}}; ++i) {
    for (int j = 0; j < n4; ++j) {
      outputBuffers[i+{{signal.numOutputBuffers}}*j] = bOut[i*n4+j];
    }
  }
  #endif
  {%- elif signal.numOutputBuffers > 2 %}
  // interleave the heavy output into the output buffer
  for (int i = 0; i < {{signal.numOutputBuffers}}; ++i) {
    for (int j = 0; j < n4; ++j) {
      outputBuffers[i+{{signal.numOutputBuffers}}*j] = bOut[i*n4+j];
    }
  }
  {%- endif %}

  return n;
}
{# force newline #}
