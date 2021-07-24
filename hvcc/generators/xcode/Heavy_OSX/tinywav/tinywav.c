/**
 * Copyright (c) 2015, Martin Roth (mhroth@gmail.com)
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 * REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 * INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 * LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 * OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */


#include <netinet/in.h>
#include "tinywav.h"

typedef struct TinyWavHeader {
  uint32_t ChunkID;
  uint32_t ChunkSize;
  uint32_t Format;
  uint32_t Subchunk1ID;
  uint32_t Subchunk1Size;
  uint16_t AudioFormat;
  uint16_t NumChannels;
  uint32_t SampleRate;
  uint32_t ByteRate;
  uint16_t BlockAlign;
  uint16_t BitsPerSample;
  uint32_t Subchunk2ID;
  uint32_t Subchunk2Size;
} TinyWavHeader;

int tinywav_new(TinyWav *tw,
    int16_t numChannels, int32_t samplerate,
    TinyWavSampleFormat sampFmt, TinyWavChannelFormat chanFmt,
    const char *path) {
  tw->f = fopen(path, "w");
  tw->numChannels = numChannels;
  tw->totalFramesWritten = 0;
  tw->sampFmt = sampFmt;
  tw->chanFmt = chanFmt;

  // prepare WAV header
  TinyWavHeader h;
  h.ChunkID = htonl(0x52494646); // "RIFF"
  h.ChunkSize = 0; // fill this in on file-close
  h.Format = htonl(0x57415645); // "WAVE"
  h.Subchunk1ID = htonl(0x666d7420); // "fmt "
  h.Subchunk1Size = 16; // PCM
  h.AudioFormat = (tw->sampFmt-1); // 1 PCM, 3 IEEE float
  h.NumChannels = numChannels;
  h.SampleRate = samplerate;
  h.ByteRate = samplerate * numChannels * tw->sampFmt;
  h.BlockAlign = numChannels * tw->sampFmt;
  h.BitsPerSample = 8*tw->sampFmt;
  h.Subchunk2ID = htonl(0x64617461); // "data"
  h.Subchunk2Size = 0; // fill this in on file-close

  // write WAV header
  fwrite(&h, sizeof(TinyWavHeader), 1, tw->f);

  return 0;
}

size_t tinywav_write_f(TinyWav *tw, void *f, int len) {
  switch (tw->sampFmt) {
    case TW_INT16: {
      int16_t z[tw->numChannels*len];
      switch (tw->chanFmt) {
        case TW_INTERLEAVED: {
          return 0;
        }
        case TW_INLINE: {
          const float *const x = (const float *const) f;
          for (int i = 0, k = 0; i < len; ++i) {
            for (int j = 0; j < tw->numChannels; ++j) {
              z[k++] = (int16_t) (x[j*len+i] * 32767.0f);
            }
          }
          break;
        }
        case TW_SPLIT: {
          const float **const x = (const float **const) f;
          for (int i = 0, k = 0; i < len; ++i) {
            for (int j = 0; j < tw->numChannels; ++j) {
              z[k++] = (int16_t) (x[j][i] * 32767.0f);
            }
          }
          break;
        }
        default: return 0;
      }

      tw->totalFramesWritten += len;
      return fwrite(z, sizeof(int16_t), tw->numChannels*len, tw->f);
      break;
    }
    case TW_FLOAT32: {
      float z[tw->numChannels*len];
      switch (tw->chanFmt) {
        case TW_INTERLEAVED: {
          return 0;
        }
        case TW_INLINE: {
          const float *const x = (const float *const) f;
          for (int i = 0, k = 0; i < len; ++i) {
            for (int j = 0; j < tw->numChannels; ++j) {
              z[k++] = x[j*len+i];
            }
          }
          break;
        }
        case TW_SPLIT: {
          const float **const x = (const float **const) f;
          for (int i = 0, k = 0; i < len; ++i) {
            for (int j = 0; j < tw->numChannels; ++j) {
              z[k++] = x[j][i];
            }
          }
          break;
        }
        default: return 0;
      }

      tw->totalFramesWritten += len;
      return fwrite(z, sizeof(float), tw->numChannels*len, tw->f);
    }
    default: return 0;
  }
}

void tinywav_close(TinyWav *tw) {
  uint32_t data_len = tw->totalFramesWritten * tw->numChannels * tw->sampFmt;

  // set length of data
  fseek(tw->f, 4, SEEK_SET);
  uint32_t chunkSize_len = 36 + data_len;
  fwrite(&chunkSize_len, sizeof(uint32_t), 1, tw->f);

  fseek(tw->f, 40, SEEK_SET);
  fwrite(&data_len, sizeof(uint32_t), 1, tw->f);

  fclose(tw->f);
  tw->f = NULL;
}

bool tinywav_isOpen(TinyWav *tw) {
  return (tw->f != NULL);
}
