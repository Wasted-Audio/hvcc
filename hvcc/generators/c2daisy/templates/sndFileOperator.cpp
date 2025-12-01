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

      if (sta != FR_OK) {
        hardware.som.PrintLine("Failed to open file");
      }

      FileReader reader(&file);
      WavParser parser;

      if(!parser.parse(reader))
      {
          hardware.som.PrintLine("Error parsing file: %s", fileName);
      }
      const auto& info = parser.info();
      static int w_start = parser.dataOffset() * 8;
      static int data_size = parser.dataSize();

      hardware.som.PrintLine("Data start: %d", w_start);
      hardware.som.PrintLine("Data size: %d", data_size);
      hardware.som.PrintLine("Buffer size: %d", FILE_BUF_SIZE);
      hardware.som.PrintLine("Buffer size: %d", sizeof(file_buf));

      UINT br = 0;
      int chunk = 0;

      f_lseek(&file, parser.dataOffset());

      int to_read = tableSize * sizeof(float);

      while( to_read > 0 ) {
        FRESULT fres = f_read(&file, file_buf, 512, &br);
        if (fres != FR_OK) {
          hardware.som.PrintLine("Error reading file: %s", fileName);
        } else {

          int values = br / sizeof(float);

          // hardware.som.PrintLine("Values: %d", values);

          for (int i = 0; i < values; i++) {
            if (chunk < tableSize) {
              table[chunk] = file_buf[i];
              chunk++;
            } else {
              break;
            }
          }
          to_read -= br;
        }
      }


      hv->sendMessageToReceiverV(
        hv_string_to_hash(sndRecInfo), 0, "ffffs",
        (float) info.sampleRate,    // sample rate
        44.0,                       // header size
        1.0,                        // channels
        (float) info.bitsPerSample, // bytes per sample
        "l"                         // endianness
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
