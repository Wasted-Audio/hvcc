void sndFileOperator(uint32_t sendHash)
{
  switch (sendHash) {
    case HV_HASH_SND_READ:     // __hv_snd_read
    case HV_HASH_SND_READ_RES: // __hv_snd_read_resize
    {
      char sndRecInfo[32];
      char sndRecSamples[32];
      snprintf(sndRecInfo, 32, "%d__hv_snd_info", (int) sndID_stored);
      snprintf(sndRecSamples, 32, "%d__hv_snd_samples", (int) sndID_stored);

      FRESULT sta = f_open(&file, sndFileName, (FA_OPEN_EXISTING | FA_READ));
      if (sta != FR_OK) {
        hardware.som.PrintLine("Failed to open file: %s", sndFileName);
        return;
      }

      FileReader reader(&file);
      WavParser parser;
      if (!parser.parse(reader)) {
        hardware.som.PrintLine("Error parsing file: %s", sndFileName);
        f_close(&file);
        return;
      }

      const auto& info = parser.info();
      const hv_uint32_t tableHash = hv_string_to_hash(sndTableName);

      const int bitsPerSample = info.bitsPerSample;
      const int bytesPerSample = bitsPerSample / 8;
      const int framesInFile = parser.dataSize() / bytesPerSample;

      if (sendHash == HV_HASH_SND_READ_RES) {
        hv->setLengthForTable(tableHash, (hv_uint32_t)framesInFile);
      }

      float *table = hv->getBufferForTable(tableHash);
      const int tableSize = hv->getLengthForTable(tableHash);

      // hardware.som.PrintLine("table ptr: %p", (void*)table);

      f_lseek(&file, parser.dataOffset());

      int framesToRead = (framesInFile > tableSize) ? tableSize : framesInFile;
      int framesRead = 0;
      UINT br = 0;

      // hardware.som.PrintLine("bits per sample: %d", bitsPerSample);
      // hardware.som.PrintLine("file_buf size: %d", sizeof(file_buf));

      // hardware.som.PrintLine("audioFormat: %d", info.audioFormat);
      // hardware.som.PrintLine("subFormat: %d", info.subFormat);
      // hardware.som.PrintLine("dataOffset: %d", parser.dataOffset());
      // hardware.som.PrintLine("dataSize: %d", parser.dataSize());
      // hardware.som.PrintLine("framesInFile: %d", framesInFile);
      // hardware.som.PrintLine("bytesPerSample: %d", bytesPerSample);
      // hardware.som.PrintLine("validBitsPerSample: %d", info.validBitsPerSample);
      // hardware.som.PrintLine("tableSize: %d", tableSize);

      // int chunkCount = 0;
      uint8_t s24_carry[2] = {0, 0};
      while (framesRead < framesToRead) {

        // trim to a multiple of bytesPerSample
        uint32_t bytesToReadThisChunk = (sizeof(file_buf) / bytesPerSample) * bytesPerSample;
        uint32_t framesLeft = framesToRead - framesRead;

        // read min of either the buffer size or the remaining frames
        if (bytesToReadThisChunk > framesLeft * bytesPerSample) {
          bytesToReadThisChunk = framesLeft * bytesPerSample;
        }

        if (bytesToReadThisChunk == 0) break;

        FRESULT fres = f_read(&file, file_buf, bytesToReadThisChunk, &br);
        // hardware.som.PrintLine("chunk %d: fres=%d br=%d framesRead=%d",
        //     chunkCount++, fres, br, framesRead);
        // SCB_InvalidateDCache_by_Addr((uint32_t*)file_buf, bytesToReadThisChunk);
        if (fres != FR_OK || br == 0) break;

        const int framesInChunk = br / bytesPerSample;
        uint8_t *ptr = (uint8_t *)file_buf;

        for (int i = 0; i < framesInChunk; ++i) {
          // if (framesRead < 5) {
          //   int32_t s;
          //   memcpy(&s, ptr, sizeof(s));
          //   hardware.som.PrintLine("frame %d: raw=%ld float=%f", framesRead, s, (double)((float)s / 2147483648.0f));
          // }

          float sample = 0.0f;
          if (bitsPerSample == 16) {
            // sample = (float)(*((int16_t *)ptr)) / 32768.0f;
            int16_t s;
            memcpy(&s, ptr, sizeof(s));
            sample = (float)s / 32768.0f;
          } else if (bitsPerSample == 24) {
            // int32_t val = (int32_t)(
            //     ((uint32_t)ptr[0])        |
            //     ((uint32_t)ptr[1] << 8)   |
            //     ((uint32_t)ptr[2] << 16)
            // );
            // // sign-extend bit 23
            // if (val & 0x800000) val |= 0xFF000000;
            // sample = (float)val / 8388608.0f; // 2^23
              int n = i * 3;
              uint8_t b0 = (n == 0) ? s24_carry[0] : ptr[n - 2];
              uint8_t b1 = (n == 0) ? s24_carry[1] : ptr[n - 1];
              uint8_t b2 = ptr[n];
              int32_t val = (int32_t)((uint32_t)b0 | ((uint32_t)b1 << 8) | ((uint32_t)b2 << 16));
              if (val & 0x800000) val |= 0xFF000000;
              sample = (float)val / 8388608.0f;
          } else if (bitsPerSample == 32) {
            bool isFloat = (info.audioFormat == 3) ||
                (info.audioFormat == 0xFFFE && info.subFormat == 3);

            if (isFloat) {
              float f;
              memcpy(&f, ptr, sizeof(f));
              sample = f;
            } else {
              int32_t s;
              memcpy(&s, ptr, sizeof(s));
              s = ((s & 0xFFFF0000u) >> 16) | ((s & 0x0000FFFFu) << 16);
              sample = (float)s / 2147483648.0f;
            }
          }
          int idx = framesRead; // save before increment
          table[framesRead++] = sample;
          if (idx == 500) {
              hardware.som.PrintLine("table[500] during load=%f", (double)table[500]);
          }
          if (idx == 500) {
              hardware.som.PrintLine("raw: %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x",
                  ptr[0], ptr[1], ptr[2], ptr[3], ptr[4], ptr[5], ptr[6], ptr[7],
                  ptr[8], ptr[9], ptr[10], ptr[11], ptr[12], ptr[13], ptr[14], ptr[15]);
          }
          // if (idx == 500) {
          //     hardware.som.PrintLine("raw bytes: %02x %02x %02x %02x", ptr[0], ptr[1], ptr[2], ptr[3]);
          //     int32_t s;
          //     memcpy(&s, ptr, sizeof(s));
          //     hardware.som.PrintLine("raw int32: %ld", s);
          // }
          // if (idx % 1024 == 0) {
          //     hardware.som.PrintLine("chunk start table[%d]=%f",
          //         idx, (double)table[idx]);
          // }
          // if (idx == 500) {
          //     hardware.som.PrintLine("file_buf: %p", (void*)file_buf);
          //     hardware.som.PrintLine("ptr:      %p", (void*)ptr);
          //     hardware.som.PrintLine("expected offset: %d", (int)(ptr - file_buf));
          // }
          ptr += bytesPerSample;
        }
        if (bitsPerSample == 24) {
          s24_carry[0] = ((uint8_t*)file_buf)[br - 2]; // data[chunk_end + 0]
          s24_carry[1] = ((uint8_t*)file_buf)[br - 1]; // data[chunk_end + 1]
        }
      }

      // hardware.som.PrintLine("table[1023]=%f table[1024]=%f",
      //     (double)table[1023], (double)table[1024]);

      // hardware.som.PrintLine("table[15000]=%f table[15001]=%f",
      //     (double)table[15000], (double)table[15001]);

      // SCB_CleanDCache_by_Addr((uint32_t*)table, tableSize * sizeof(float));

      // hardware.som.PrintLine("table ptr: %p", (void*)table);

      // float sum = 0.0f;
      // float minVal = table[0], maxVal = table[0];
      // for (int i = 0; i < tableSize; i++) {
      //     sum += table[i];
      //     if (table[i] < minVal) minVal = table[i];
      //     if (table[i] > maxVal) maxVal = table[i];
      // }
      // hardware.som.PrintLine("sum=%f min=%f max=%f", (double)sum, (double)minVal, (double)maxVal);

      // for (int i = 0; i < 10; i++) {
      //     hardware.som.PrintLine("table[%d]=%f", i, (double)table[i]);
      // }
      // hardware.som.PrintLine("---");
      // for (int i = 1020; i < 1028; i++) {
      //     hardware.som.PrintLine("table[%d]=%f", i, (double)table[i]);
      // }

      // for (int chunk = 0; chunk < 30; chunk++) {
      //     float sum = 0.0f;
      //     int start = chunk * 1024;
      //     int end = start + 1024;
      //     if (end > tableSize) end = tableSize;
      //     for (int i = start; i < end; i++) sum += table[i];
      //     hardware.som.PrintLine("chunk %d sum=%f", chunk, sum);
      // }

      // hardware.som.PrintLine("file_buf: %p", (void*)file_buf);
      // hardware.som.PrintLine("table:    %p", (void*)table);
      // hardware.som.PrintLine("table end: %p", (void*)(table + tableSize));

      // hardware.som.PrintLine("table[100]=%f table[500]=%f table[900]=%f",
      //   (double)table[100], (double)table[500], (double)table[900]);
      hardware.som.PrintLine("table[500] after load=%f", (double)table[500]);

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
    case HV_HASH_SND_WRITE: // __hv_snd_write
    {
      const hv_uint32_t tableHash = hv_string_to_hash(sndTableName);
      SndWriteState &s = snd_write_state;

      s.table      = hv->getBufferForTable(tableHash);
      s.tableSize  = hv->getLengthForTable(tableHash);
      s.sampleRate = hv->getSampleRate();
      s.written    = 0;
      snprintf(s.recInfo,    32, "%d__hv_snd_info",    (int)sndID_stored);
      snprintf(s.recSamples, 32, "%d__hv_snd_samples", (int)sndID_stored);

      wav_writer.OpenFile(sndFileName);

      if (!wav_writer.IsRecording()) {
        hardware.som.PrintLine("Failed to open wav for writing: %s", sndFileName);
        return;
      }

      s.active = true;
      hardware.som.PrintLine("write started, %d samples", s.tableSize);
      break;
    }
    default: break;
  }
}
