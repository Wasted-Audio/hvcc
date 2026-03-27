void sndFileOperator(uint32_t sendHash, const HvMessage *m)
{
  switch (sendHash) {
    case HV_HASH_SND_READ:     // __hv_snd_read
    case HV_HASH_SND_READ_RES: // __hv_snd_read_resize
    {
      const float sndID = hv_msg_getFloat(m, 0);
      const char *fileName = hv_msg_getSymbol(m, 1);
      const char *tableName = hv_msg_getSymbol(m, 2);

      char sndRecInfo[32];
      char sndRecSamples[32];
      snprintf(sndRecInfo, 32, "%d__hv_snd_info", (int) sndID);
      snprintf(sndRecSamples, 32, "%d__hv_snd_samples", (int) sndID);

      FRESULT sta = f_open(&file, fileName, (FA_OPEN_EXISTING | FA_READ));
      if (sta != FR_OK) {
        hardware.som.PrintLine("Failed to open file: %s", fileName);
        return;
      }

      FileReader reader(&file);
      WavParser parser;
      if (!parser.parse(reader)) {
        hardware.som.PrintLine("Error parsing file: %s", fileName);
        f_close(&file);
        return;
      }

      const auto& info = parser.info();
      const hv_uint32_t tableHash = hv_string_to_hash(tableName);

      const int bitsPerSample = info.bitsPerSample;
      const int bytesPerSample = bitsPerSample / 8;
      const int framesInFile = parser.dataSize() / bytesPerSample;

      if (sendHash == HV_HASH_SND_READ_RES) {
        hv->setLengthForTable(tableHash, (hv_uint32_t)framesInFile);
      }

      float *table = hv->getBufferForTable(tableHash);
      const int tableSize = hv->getLengthForTable(tableHash);

      f_lseek(&file, parser.dataOffset());

      int framesToRead = (framesInFile > tableSize) ? tableSize : framesInFile;
      int framesRead = 0;
      UINT br = 0;

      while (framesRead < framesToRead) {
        uint32_t bytesToReadThisChunk = sizeof(file_buf);
        uint32_t framesLeft = framesToRead - framesRead;

        if (bytesToReadThisChunk > framesLeft * bytesPerSample) {
          bytesToReadThisChunk = framesLeft * bytesPerSample;
        }

        if (bytesToReadThisChunk == 0) break;

        FRESULT fres = f_read(&file, file_buf, bytesToReadThisChunk, &br);
        if (fres != FR_OK || br == 0) break;

        const int framesInChunk = br / bytesPerSample;
        uint8_t *ptr = (uint8_t *)file_buf;

        for (int i = 0; i < framesInChunk; ++i) {
          float sample = 0.0f;
          if (bitsPerSample == 16) {
            sample = (float)(*((int16_t *)ptr)) / 32768.0f;
          } else if (bitsPerSample == 24) {
            // 24-bit PCM is little-endian signed integer
            int32_t val = (ptr[0] << 8) | (ptr[1] << 16) | (ptr[2] << 24);
            sample = (float)val / 2147483648.0f;
          } else if (bitsPerSample == 32) {
            if (info.audioFormat == 3) { // IEEE Float
              sample = *((float *)ptr);
            } else { // 32-bit PCM
              sample = (float)(*((int32_t *)ptr)) / 2147483648.0f;
            }
          }
          table[framesRead++] = sample;
          ptr += bytesPerSample;
        }
      }

      hv->sendMessageToReceiverV(
        hv_string_to_hash(sndRecInfo), 0, "ffffs",
        (float) info.sampleRate,  // sample rate
        44.0,                     // header size
        1.0,                      // channels (tables are single buffer)
        (float) bytesPerSample,   // bytes per sample
        "l"                       // endianness
      );

      hv->sendFloatToReceiver(
        hv_string_to_hash(sndRecSamples),
        (float) framesRead
      );

      f_close(&file);
      break;
    }
    default: break;
  }
}
