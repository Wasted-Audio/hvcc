void {{class_name}}::sndFileOperator(uint32_t sendHash, const HvMessage *m)
{
  switch (sendHash) {
    case HV_HASH_SND_READ: // __hv_snd_read
    {
      float sndID = hv_msg_getFloat(m, 0);
      const char *fileName = hv_msg_getSymbol(m, 1);
      const char *tableName = hv_msg_getSymbol(m, 2);

      auto filePath = getSpecialDir(kSpecialDirDocumentsForPlugin) + std::string("/Samples/") + std::string(fileName);

      char sndRecInfo[32];
      char sndRecSamples[32];
      char *bufInfo = sndRecInfo;
      char *bufSamples = sndRecSamples;

      snprintf(bufInfo, 31, "%d__hv_snd_info", (int) sndID);
      snprintf(bufSamples, 31, "%d__hv_snd_samples", (int) sndID);

      hv_uint32_t tableHash = hv_string_to_hash(tableName);
      float *table = _context->getBufferForTable(tableHash);
      int tableSize = _context->getLengthForTable(tableHash);

      TinyWav tw;
      tinywav_open_read(&tw, filePath.c_str(), TW_INLINE);

      tinywav_read_f(&tw, table, tableSize);

      _context->sendMessageToReceiverV(
        hv_string_to_hash(sndRecInfo), 0, "ffffs",
        (float) tw.h.SampleRate,  // sample rate
        44.0,                     // header size
        1.0,                      // channels
        (float) tw.sampFmt,       // bytes per sample
        "l"                       // endianness
      );

      _context->sendFloatToReceiver(
        hv_string_to_hash(sndRecSamples),
        float(tableSize)
      );

      tinywav_close_read(&tw);

      break;
    }
    case HV_HASH_SND_READ_RES: // __hv_snd_read_resize
    {
      float sndID = hv_msg_getFloat(m, 0);
      const char *fileName = hv_msg_getSymbol(m, 1);
      const char *tableName = hv_msg_getSymbol(m, 2);

      auto filePath = getSpecialDir(kSpecialDirDocumentsForPlugin) + std::string("/Samples/") + std::string(fileName);

      char sndRecInfo[32];
      char sndRecSamples[32];
      char *bufInfo = sndRecInfo;
      char *bufSamples = sndRecSamples;

      snprintf(bufInfo, 31, "%d__hv_snd_info", (int) sndID);
      snprintf(bufSamples, 31, "%d__hv_snd_samples", (int) sndID);

      hv_uint32_t tableHash = hv_string_to_hash(tableName);

      TinyWav tw;
      tinywav_open_read(&tw, filePath.c_str(), TW_INLINE);
      int tableSize = tw.numFramesInHeader;

      _context->setLengthForTable(tableHash, (uint32_t)tableSize);
      float *table = _context->getBufferForTable(tableHash);

      tinywav_read_f(&tw, table, tableSize);

      _context->sendMessageToReceiverV(
        hv_string_to_hash(sndRecInfo), 0, "ffffs",
        (float) tw.h.SampleRate,  // sample rate
        44.0,                     // header size
        1.0,                      // channels
        (float) tw.sampFmt,       // bytes per sample
        "l"                       // endianness
      );

      _context->sendFloatToReceiver(
        hv_string_to_hash(sndRecSamples),
        float(tableSize)
      );

      tinywav_close_read(&tw);

      break;
    }
    case HV_HASH_SND_WRITE: // __hv_snd_write
    {
      float sndID = hv_msg_getFloat(m, 0);
      const char *fileName = hv_msg_getSymbol(m, 1);
      const char *tableName = hv_msg_getSymbol(m, 2);

      auto filePath = getSpecialDir(kSpecialDirDocumentsForPlugin) + std::string("/Samples/") + std::string(fileName);

      char sndRecInfo[32];
      char sndRecSamples[32];
      char *bufInfo = sndRecInfo;
      char *bufSamples = sndRecSamples;

      snprintf(bufInfo, 31, "%d__hv_snd_info", (int) sndID);
      snprintf(bufSamples, 31, "%d__hv_snd_samples", (int) sndID);

      hv_uint32_t tableHash = hv_string_to_hash(tableName);
      float *table = _context->getBufferForTable(tableHash);
      int tableSize = _context->getLengthForTable(tableHash);

      TinyWav tw;
      tinywav_open_write(
        &tw, 1,
        _context->getSampleRate(),
        TW_FLOAT32, TW_INLINE,
        filePath.c_str()
      );
      tinywav_write_f(&tw, table, tableSize);

      _context->sendMessageToReceiverV(
        hv_string_to_hash(sndRecInfo), 0, "ffffs",
        (float) tw.h.SampleRate,  // sample rate
        44.0,                     // header size
        1.0,                      // channels
        (float) tw.sampFmt,       // bytes per sample
        "l"                       // endianness
      );

      _context->sendFloatToReceiver(
        hv_string_to_hash(sndRecSamples),
        float(tableSize)
      );

      tinywav_close_write(&tw);

      break;
    }
    default: break;
  }
}
