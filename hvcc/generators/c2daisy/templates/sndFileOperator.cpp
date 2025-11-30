void sndFileOperator(uint32_t sendHash, const HvMessage *m)
{
  switch (sendHash) {
    case HV_HASH_SND_READ: // __hv_snd_read
    {
      float sndID = hv_msg_getFloat(m, 0);
      const char *fileName = hv_msg_getSymbol(m, 1);
      const char *tableName = hv_msg_getSymbol(m, 2);

      char sndRecInfo[32];
      char sndRecSamples[32];
      char *bufInfo = sndRecInfo;
      char *bufSamples = sndRecSamples;

      snprintf(bufInfo, 31, "%d__hv_snd_info", (int) sndID);
      snprintf(bufSamples, 31, "%d__hv_snd_samples", (int) sndID);

      hv_uint32_t tableHash = hv_string_to_hash(tableName);
      float *table = hv->getBufferForTable(tableHash);
      int tableSize = hv->getLengthForTable(tableHash);

      auto sta = f_open(&file, fileName, (FA_OPEN_EXISTING | FA_READ));

      FileReader reader(&file);
      WavParser parser;

      const auto& info = parser.info();
      hv->sendMessageToReceiverV(
        hv_string_to_hash(sndRecInfo), 0, "ffffs",
        (float) info.sampleRate,  // sample rate
        44.0,                     // header size
        1.0,                      // channels
        (float) info.bitsPerSample,       // bytes per sample
        "l"                       // endianness
      );

      hv->sendFloatToReceiver(
        hv_string_to_hash(sndRecSamples),
        float(tableSize)
      );

      f_close(&file);

      break;
    }
    default: break;
  }
}
