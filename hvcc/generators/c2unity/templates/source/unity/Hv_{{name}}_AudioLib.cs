{%- set hasParams = true if parameters|length > 0 -%}
{%- set hasEvents = true if events|length > 0 -%}
{%- set hasTables = true if tables|length > 0 -%}
{{copyright}}

using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using UnityEngine;
using UnityEngine.Assertions;
using AOT;

#if UNITY_EDITOR
using UnityEditor;

[CustomEditor(typeof(Hv_{{patch_name}}_AudioLib))]
public class Hv_{{patch_name}}_Editor : Editor {

  [MenuItem("Heavy/{{patch_name}}")]
  static void CreateHv_{{patch_name}}() {
    GameObject target = Selection.activeGameObject;
    if (target != null) {
      target.AddComponent<Hv_{{patch_name}}_AudioLib>();
    }
  }
  {%- if hasParams or hasEvents or hasTables %}

  private Hv_{{patch_name}}_AudioLib _dsp;

  private void OnEnable() {
    _dsp = target as Hv_{{patch_name}}_AudioLib;
  }

  public override void OnInspectorGUI() {
    bool isEnabled = _dsp.IsInstantiated();
    if (!isEnabled) {
      EditorGUILayout.LabelField("Press Play!",  EditorStyles.centeredGreyMiniLabel);
    }
    GUILayout.BeginVertical();
    {% if hasEvents -%}
    // EVENTS
    GUI.enabled = isEnabled;
    EditorGUILayout.Space();
    {%- for k, v in events %}

    // {{v.display}}
    if (GUILayout.Button("{{v.display}}")) {
      _dsp.SendEvent(Hv_{{patch_name}}_AudioLib.Event.{{k|title}});
    }
    {%- endfor %}
    {%- endif %}
    {% if hasParams -%}
    // PARAMETERS
    GUI.enabled = true;
    EditorGUILayout.Space();
    EditorGUI.indentLevel++;
    {%- for k, v in parameters %}

    // {{v.display}}
    GUILayout.BeginHorizontal();
    float {{k}} = _dsp.GetFloatParameter(Hv_{{patch_name}}_AudioLib.Parameter.{{k|title}});
    float new{{k|title}} = EditorGUILayout.Slider("{{v.display}}", {{k}}, {{v.attributes.min}}f, {{v.attributes.max}}f);
    if ({{k}} != new{{k|title}}) {
      _dsp.SetFloatParameter(Hv_{{patch_name}}_AudioLib.Parameter.{{k|title}}, new{{k|title}});
    }
    GUILayout.EndHorizontal();
    {%- endfor %}

    EditorGUI.indentLevel--;
    {%- endif %}

    {% if hasTables -%}
    // TABLES
    GUI.enabled = true;
    EditorGUILayout.Space();
    EditorGUI.indentLevel++;
    {%- for k, v in tables %}

    // {{v.display}}
    EditorGUI.BeginChangeCheck();
    AudioClip {{k}}Clip = EditorGUILayout.ObjectField("{{v.display}}", _dsp.{{k}}Clip, typeof(AudioClip), false) as AudioClip;
    if (EditorGUI.EndChangeCheck()) {
      _dsp.{{k}}Clip = {{k}}Clip;
    }
    {%- endfor %}

    EditorGUI.indentLevel--;
    {%- endif %}

    GUILayout.EndVertical();
  }
  {%- endif %}
}
#endif // UNITY_EDITOR

[RequireComponent (typeof (AudioSource))]
public class Hv_{{patch_name}}_AudioLib : MonoBehaviour {
  {% if hasEvents %}
  // Events are used to trigger bangs in the patch context (thread-safe).
  // Example usage:
  /*
    void Start () {
        Hv_{{patch_name}}_AudioLib script = GetComponent<Hv_{{patch_name}}_AudioLib>();
        script.SendEvent(Hv_{{patch_name}}_AudioLib.Event.{{events[0][0]|title}});
    }
  */
  public enum Event : uint {
    {%- for k, v in events %}
    {{k|title}} = {{v.hash}},
    {%- endfor %}
  }
  {% endif %}
  {%- if hasParams %}
  // Parameters are used to send float messages into the patch context (thread-safe).
  // Example usage:
  /*
    void Start () {
        Hv_{{patch_name}}_AudioLib script = GetComponent<Hv_{{patch_name}}_AudioLib>();
        // Get and set a parameter
        float {{parameters[0][0]}} = script.GetFloatParameter(Hv_{{patch_name}}_AudioLib.Parameter.{{parameters[0][0]|title}});
        script.SetFloatParameter(Hv_{{patch_name}}_AudioLib.Parameter.{{parameters[0][0]|title}}, {{parameters[0][0]}} + 0.1f);
    }
  */
  public enum Parameter : uint {
    {%- for k,v in parameters %}
    {{k|title}} = {{v.hash}},
    {%- endfor %}
  }
  {% endif %}
  {%- if hasTables %}
  // Tables within the patch context can be filled directly with audio content
  // Example usage:
  /*
    public AudioClip clip;

    void Start () {
        Hv_{{patch_name}}_AudioLib script = GetComponent<Hv_{{patch_name}}_AudioLib>();
        // copy clip contents into a temporary buffer
        float[] buffer = new float[clip.samples];
        clip.GetData(buffer, 0);
        // fill a buffer called "channelL"
        looper.FillTableWithFloatBuffer((uint) Hv_{{patch_name}}_AudioLib.Table.Channell, buffer);
        // notify a (non-exposed) receiver of the buffer size
        looper.SendFloatToReceiver("setTableSize-channelL", clip.samples);
    }
  */
  public enum Table : uint {
    {%- for k,v in tables %}
    {{k|title}} = {{v.hash}},
    {%- endfor %}
  }
  {% endif %}
  // Delegate method for receiving float messages from the patch context (thread-safe).
  // Example usage:
  /*
    void Start () {
        Hv_{{patch_name}}_AudioLib script = GetComponent<Hv_{{patch_name}}_AudioLib>();
        script.RegisterSendHook();
        script.FloatReceivedCallback += OnFloatMessage;
    }

    void OnFloatMessage(Hv_{{patch_name}}_AudioLib.FloatMessage message) {
        Debug.Log(message.receiverName + ": " + message.value);
    }
  */
  public class FloatMessage {
    public string receiverName;
    public float value;

    public FloatMessage(string name, float x) {
      receiverName = name;
      value = x;
    }
  }
  public delegate void FloatMessageReceived(FloatMessage message);
  public FloatMessageReceived FloatReceivedCallback;

  {%- for k, v in parameters %}
  public float {{k}} = {{v.attributes.default}}f;
  {%- endfor %}
  {%- for k, v in tables %}
  public AudioClip {{k}}Clip = null;
  {%- endfor %}

  // internal state
  private Hv_{{patch_name}}_Context _context;

  public bool IsInstantiated() {
    return (_context != null);
  }

  public void RegisterSendHook() {
    _context.RegisterSendHook();
  }
  {% if hasEvents %}
  // see Hv_{{patch_name}}_AudioLib.Event for definitions
  public void SendEvent(Hv_{{patch_name}}_AudioLib.Event e) {
    if (IsInstantiated()) _context.SendBangToReceiver((uint) e);
  }
  {% endif %}
  {%- if hasParams %}
  // see Hv_{{patch_name}}_AudioLib.Parameter for definitions
  public float GetFloatParameter(Hv_{{patch_name}}_AudioLib.Parameter param) {
    switch (param) {
      {%- for k, v in parameters %}
      case Parameter.{{k|title}}: return {{k}};
      {%- endfor %}
      default: return 0.0f;
    }
  }

  public void SetFloatParameter(Hv_{{patch_name}}_AudioLib.Parameter param, float x) {
    switch (param) {
      {%- for k, v in parameters %}
      case Parameter.{{k|title}}: {
        x = Mathf.Clamp(x, {{v.attributes.min}}f, {{v.attributes.max}}f);
        {{k}} = x;
        break;
      }
      {%- endfor %}
      default: return;
    }
    if (IsInstantiated()) _context.SendFloatToReceiver((uint) param, x);
  }
  {% endif %}
  public void SendFloatToReceiver(string receiverName, float x) {
    _context.SendFloatToReceiver(StringToHash(receiverName), x);
  }

  public void FillTableWithMonoAudioClip(string tableName, AudioClip clip) {
    if (clip.channels > 1) {
      Debug.LogWarning("Hv_{{patch_name}}_AudioLib: Only loading first channel of '" +
          clip.name + "' into table '" +
          tableName + "'. Multi-channel files are not supported.");
    }
    float[] buffer = new float[clip.samples]; // copy only the 1st channel
    clip.GetData(buffer, 0);
    _context.FillTableWithFloatBuffer(StringToHash(tableName), buffer);
  }

  public void FillTableWithMonoAudioClip(uint tableHash, AudioClip clip) {
    if (clip.channels > 1) {
      Debug.LogWarning("Hv_{{patch_name}}_AudioLib: Only loading first channel of '" +
          clip.name + "' into table '" +
          tableHash + "'. Multi-channel files are not supported.");
    }
    float[] buffer = new float[clip.samples]; // copy only the 1st channel
    clip.GetData(buffer, 0);
    _context.FillTableWithFloatBuffer(tableHash, buffer);
  }

  public void FillTableWithFloatBuffer(string tableName, float[] buffer) {
    _context.FillTableWithFloatBuffer(StringToHash(tableName), buffer);
  }

  public void FillTableWithFloatBuffer(uint tableHash, float[] buffer) {
    _context.FillTableWithFloatBuffer(tableHash, buffer);
  }

  public uint StringToHash(string str) {
    return _context.StringToHash(str);
  }

  private void Awake() {
    _context = new Hv_{{patch_name}}_Context((double) AudioSettings.outputSampleRate);
    {% if hasTables -%}
    // Note: only copies first channel from audio clips
    {%- for k, v in tables %}
    if ({{k}}Clip != null) {
      // load buffer {{v.display}}
      int length = {{k}}Clip.samples;
      float[] buffer = new float[length];
      {{k}}Clip.GetData(buffer, 0);
      _context.FillTableWithFloatBuffer((uint) Hv_{{patch_name}}_AudioLib.Table.{{k|title}}, buffer);
      _context.SendFloatToReceiver(_context.StringToHash("setTableSize-{{v.display}}"), length);
    }
    {%- endfor %}
    {%- endif %}
  }
  {% if hasParams %}
  private void Start() {
    {%- for k, v in parameters %}
    _context.SendFloatToReceiver((uint) Parameter.{{k|title}}, {{k}});
    {%- endfor %}
  }
  {% endif %}
  private void Update() {
    // retreive sent messages
    if (_context.IsSendHookRegistered()) {
      Hv_{{patch_name}}_AudioLib.FloatMessage tempMessage;
      while ((tempMessage = _context.msgQueue.GetNextMessage()) != null) {
        FloatReceivedCallback(tempMessage);
      }
    }
  }

  private void OnAudioFilterRead(float[] buffer, int numChannels) {
    Assert.AreEqual(numChannels, _context.GetNumOutputChannels()); // invalid channel configuration
    _context.Process(buffer, buffer.Length / numChannels); // process dsp
  }
}

class Hv_{{patch_name}}_Context {

#if UNITY_IOS && !UNITY_EDITOR
  private const string _dllName = "__Internal";
#else
  private const string _dllName = "Hv_{{patch_name}}_AudioLib";
#endif

  // Thread-safe message queue
  public class SendMessageQueue {
    private readonly object _msgQueueSync = new object();
    private readonly Queue<Hv_{{patch_name}}_AudioLib.FloatMessage> _msgQueue = new Queue<Hv_{{patch_name}}_AudioLib.FloatMessage>();

    public Hv_{{patch_name}}_AudioLib.FloatMessage GetNextMessage() {
      lock (_msgQueueSync) {
        return (_msgQueue.Count != 0) ? _msgQueue.Dequeue() : null;
      }
    }

    public void AddMessage(string receiverName, float value) {
      Hv_{{patch_name}}_AudioLib.FloatMessage msg = new Hv_{{patch_name}}_AudioLib.FloatMessage(receiverName, value);
      lock (_msgQueueSync) {
        _msgQueue.Enqueue(msg);
      }
    }
  }

  public readonly SendMessageQueue msgQueue = new SendMessageQueue();
  private readonly GCHandle gch;
  private readonly IntPtr _context; // handle into unmanaged memory
  private SendHook _sendHook = null;

  [DllImport (_dllName)]
  private static extern IntPtr hv_{{patch_name}}_new_with_options(double sampleRate, int poolKb, int inQueueKb, int outQueueKb);

  [DllImport (_dllName)]
  private static extern int hv_processInlineInterleaved(IntPtr ctx,
      [In] float[] inBuffer, [Out] float[] outBuffer, int numSamples);

  [DllImport (_dllName)]
  private static extern void hv_delete(IntPtr ctx);

  [DllImport (_dllName)]
  private static extern double hv_getSampleRate(IntPtr ctx);

  [DllImport (_dllName)]
  private static extern int hv_getNumInputChannels(IntPtr ctx);

  [DllImport (_dllName)]
  private static extern int hv_getNumOutputChannels(IntPtr ctx);

  [DllImport (_dllName)]
  private static extern void hv_setSendHook(IntPtr ctx, SendHook sendHook);

  [DllImport (_dllName)]
  private static extern void hv_setPrintHook(IntPtr ctx, PrintHook printHook);

  [DllImport (_dllName)]
  private static extern int hv_setUserData(IntPtr ctx, IntPtr userData);

  [DllImport (_dllName)]
  private static extern IntPtr hv_getUserData(IntPtr ctx);

  [DllImport (_dllName)]
  private static extern void hv_sendBangToReceiver(IntPtr ctx, uint receiverHash);

  [DllImport (_dllName)]
  private static extern void hv_sendFloatToReceiver(IntPtr ctx, uint receiverHash, float x);

  [DllImport (_dllName)]
  private static extern uint hv_msg_getTimestamp(IntPtr message);

  [DllImport (_dllName)]
  private static extern bool hv_msg_hasFormat(IntPtr message, string format);

  [DllImport (_dllName)]
  private static extern float hv_msg_getFloat(IntPtr message, int index);

  [DllImport (_dllName)]
  private static extern bool hv_table_setLength(IntPtr ctx, uint tableHash, uint newSampleLength);

  [DllImport (_dllName)]
  private static extern IntPtr hv_table_getBuffer(IntPtr ctx, uint tableHash);

  [DllImport (_dllName)]
  private static extern float hv_samplesToMilliseconds(IntPtr ctx, uint numSamples);

  [DllImport (_dllName)]
  private static extern uint hv_stringToHash(string s);

  private delegate void PrintHook(IntPtr context, string printName, string str, IntPtr message);

  private delegate void SendHook(IntPtr context, string sendName, uint sendHash, IntPtr message);

  public Hv_{{patch_name}}_Context(double sampleRate, int poolKb={{pool_sizes_kb.internal}}, int inQueueKb={{pool_sizes_kb.inputQueue}}, int outQueueKb={{pool_sizes_kb.outputQueue}}) {
    gch = GCHandle.Alloc(msgQueue);
    _context = hv_{{patch_name}}_new_with_options(sampleRate, poolKb, inQueueKb, outQueueKb);
    hv_setPrintHook(_context, new PrintHook(OnPrint));
    hv_setUserData(_context, GCHandle.ToIntPtr(gch));
  }

  ~Hv_{{patch_name}}_Context() {
    hv_delete(_context);
    GC.KeepAlive(_context);
    GC.KeepAlive(_sendHook);
    gch.Free();
  }

  public void RegisterSendHook() {
    // Note: send hook functionality only applies to messages containing a single float value
    if (_sendHook == null) {
      _sendHook = new SendHook(OnMessageSent);
      hv_setSendHook(_context, _sendHook);
    }
  }

  public bool IsSendHookRegistered() {
    return (_sendHook != null);
  }

  public double GetSampleRate() {
    return hv_getSampleRate(_context);
  }

  public int GetNumInputChannels() {
    return hv_getNumInputChannels(_context);
  }

  public int GetNumOutputChannels() {
    return hv_getNumOutputChannels(_context);
  }

  public void SendBangToReceiver(uint receiverHash) {
    hv_sendBangToReceiver(_context, receiverHash);
  }

  public void SendFloatToReceiver(uint receiverHash, float x) {
    hv_sendFloatToReceiver(_context, receiverHash, x);
  }

  public void FillTableWithFloatBuffer(uint tableHash, float[] buffer) {
    if (hv_table_getBuffer(_context, tableHash) != IntPtr.Zero) {
      hv_table_setLength(_context, tableHash, (uint) buffer.Length);
      Marshal.Copy(buffer, 0, hv_table_getBuffer(_context, tableHash), buffer.Length);
    } else {
      Debug.Log(string.Format("Table '{0}' doesn't exist in the patch context.", tableHash));
    }
  }

  public uint StringToHash(string s) {
    return hv_stringToHash(s);
  }

  public int Process(float[] buffer, int numFrames) {
    return hv_processInlineInterleaved(_context, buffer, buffer, numFrames);
  }

  [MonoPInvokeCallback(typeof(PrintHook))]
  private static void OnPrint(IntPtr context, string printName, string str, IntPtr message) {
    float timeInSecs = hv_samplesToMilliseconds(context, hv_msg_getTimestamp(message)) / 1000.0f;
    Debug.Log(string.Format("{0} [{1:0.000}]: {2}", printName, timeInSecs, str));
  }

  [MonoPInvokeCallback(typeof(SendHook))]
  private static void OnMessageSent(IntPtr context, string sendName, uint sendHash, IntPtr message) {
    if (hv_msg_hasFormat(message, "f")) {
      SendMessageQueue msgQueue = (SendMessageQueue) GCHandle.FromIntPtr(hv_getUserData(context)).Target;
      msgQueue.AddMessage(sendName, hv_msg_getFloat(message, 0));
    }
  }
}
{# force new line #}
