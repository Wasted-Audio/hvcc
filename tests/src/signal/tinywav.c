/**
 * Copyright (c) 2015-2022, Martin Roth (mhroth@gmail.com)
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



#include <assert.h>
#include <string.h>
#if _WIN32
#include <winsock.h>
#include <malloc.h>
#pragma comment(lib, "Ws2_32.lib")
#else
#include <alloca.h>
#include <netinet/in.h>
#endif
#include "tinywav.h"

int tinywav_open_write(TinyWav *tw,
    int16_t numChannels, int32_t samplerate,
    TinyWavSampleFormat sampFmt, TinyWavChannelFormat chanFmt,
    const char *path) {
#if _WIN32
  errno_t err = fopen_s(&tw->f, path, "wb");
  assert(err == 0);
#else
  tw->f = fopen(path, "wb");
#endif
  assert(tw->f != NULL);
  tw->numChannels = numChannels;
  tw->numFramesInHeader = -1; // not used for writer
  tw->totalFramesReadWritten = 0;
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

int tinywav_open_read(TinyWav *tw, const char *path, TinyWavChannelFormat chanFmt) {
  tw->f = fopen(path, "rb");
  assert(tw->f != NULL);
  size_t ret = fread(&tw->h, sizeof(TinyWavHeader), 1, tw->f);
  assert(ret > 0);
  assert(tw->h.ChunkID == htonl(0x52494646));        // "RIFF"
  assert(tw->h.Format == htonl(0x57415645));         // "WAVE"
  assert(tw->h.Subchunk1ID == htonl(0x666d7420));    // "fmt "

  // skip over any other chunks before the "data" chunk
  bool additionalHeaderDataPresent = false;
  while (tw->h.Subchunk2ID != htonl(0x64617461)) {   // "data"
    fseek(tw->f, 4, SEEK_CUR);
    fread(&tw->h.Subchunk2ID, 4, 1, tw->f);
    additionalHeaderDataPresent = true;
  }
  assert(tw->h.Subchunk2ID == htonl(0x64617461));    // "data"
  if (additionalHeaderDataPresent) {
    // read the value of Subchunk2Size, the one populated when reading 'TinyWavHeader' structure is wrong
    fread(&tw->h.Subchunk2Size, 4, 1, tw->f);
  }

  tw->numChannels = tw->h.NumChannels;
  tw->chanFmt = chanFmt;

  if (tw->h.BitsPerSample == 32 && tw->h.AudioFormat == 3) {
    tw->sampFmt = TW_FLOAT32; // file has 32-bit IEEE float samples
  } else if (tw->h.BitsPerSample == 16 && tw->h.AudioFormat == 1) {
    tw->sampFmt = TW_INT16; // file has 16-bit int samples
  } else {
    tw->sampFmt = TW_FLOAT32;
    printf("Warning: wav file has %d bits per sample (int), which is not natively supported yet. Treating them as float; you may want to convert them manually after reading.\n", tw->h.BitsPerSample);
  }

  tw->numFramesInHeader = tw->h.Subchunk2Size / (tw->numChannels * tw->sampFmt);
  tw->totalFramesReadWritten = 0;

  return 0;
}

int tinywav_read_f(TinyWav *tw, void *data, int len) {
  switch (tw->sampFmt) {
    case TW_INT16: {
      int16_t *interleaved_data = (int16_t *) alloca(tw->numChannels*len*sizeof(int16_t));
      size_t samples_read = fread(interleaved_data, sizeof(int16_t), tw->numChannels*len, tw->f);
      int valid_len = (int) samples_read / tw->numChannels;
      switch (tw->chanFmt) {
        case TW_INTERLEAVED: { // channel buffer is interleaved e.g. [LRLRLRLR]
          for (int pos = 0; pos < tw->numChannels * valid_len; pos++) {
            ((float *) data)[pos] = (float) interleaved_data[pos] / INT16_MAX;
          }
          return valid_len;
        }
        case TW_INLINE: { // channel buffer is inlined e.g. [LLLLRRRR]
          for (int i = 0, pos = 0; i < tw->numChannels; i++) {
            for (int j = i; j < valid_len * tw->numChannels; j += tw->numChannels, ++pos) {
              ((float *) data)[pos] = (float) interleaved_data[j] / INT16_MAX;
            }
          }
          return valid_len;
        }
        case TW_SPLIT: { // channel buffer is split e.g. [[LLLL],[RRRR]]
          for (int i = 0, pos = 0; i < tw->numChannels; i++) {
            for (int j = 0; j < valid_len; j++, ++pos) {
              ((float **) data)[i][j] = (float) interleaved_data[j*tw->numChannels + i] / INT16_MAX;
            }
          }
          return valid_len;
        }
        default: return 0;
      }
    }
    case TW_FLOAT32: {
      float *interleaved_data = (float *) alloca(tw->numChannels*len*sizeof(float));
      size_t samples_read = fread(interleaved_data, sizeof(float), tw->numChannels*len, tw->f);
      int valid_len = (int) samples_read / tw->numChannels;
      switch (tw->chanFmt) {
        case TW_INTERLEAVED: { // channel buffer is interleaved e.g. [LRLRLRLR]
          memcpy(data, interleaved_data, tw->numChannels*valid_len*sizeof(float));
          return valid_len;
        }
        case TW_INLINE: { // channel buffer is inlined e.g. [LLLLRRRR]
          for (int i = 0, pos = 0; i < tw->numChannels; i++) {
            for (int j = i; j < valid_len * tw->numChannels; j += tw->numChannels, ++pos) {
              ((float *) data)[pos] = interleaved_data[j];
            }
          }
          return valid_len;
        }
        case TW_SPLIT: { // channel buffer is split e.g. [[LLLL],[RRRR]]
          for (int i = 0, pos = 0; i < tw->numChannels; i++) {
            for (int j = 0; j < valid_len; j++, ++pos) {
              ((float **) data)[i][j] = interleaved_data[j*tw->numChannels + i];
            }
          }
          return valid_len;
        }
        default: return 0;
      }
    }
    default: return 0;
  }

  return len;
}

void tinywav_close_read(TinyWav *tw) {
  fclose(tw->f);
  tw->f = NULL;
}

int tinywav_write_f(TinyWav *tw, void *f, int len) {
  switch (tw->sampFmt) {
    case TW_INT16: {
      int16_t *z = (int16_t *) alloca(tw->numChannels*len*sizeof(int16_t));
      switch (tw->chanFmt) {
        case TW_INTERLEAVED: {
          const float *const x = (const float *const) f;
          for (int i = 0; i < tw->numChannels*len; ++i) {
            z[i] = (int16_t) (x[i] * (float) INT16_MAX);
          }
          break;
        }
        case TW_INLINE: {
          const float *const x = (const float *const) f;
          for (int i = 0, k = 0; i < len; ++i) {
            for (int j = 0; j < tw->numChannels; ++j) {
              z[k++] = (int16_t) (x[j*len+i] * (float) INT16_MAX);
            }
          }
          break;
        }
        case TW_SPLIT: {
          const float **const x = (const float **const) f;
          for (int i = 0, k = 0; i < len; ++i) {
            for (int j = 0; j < tw->numChannels; ++j) {
              z[k++] = (int16_t) (x[j][i] * (float) INT16_MAX);
            }
          }
          break;
        }
        default: return 0;
      }

      tw->totalFramesReadWritten += len;
      size_t samples_written = fwrite(z, sizeof(int16_t), tw->numChannels*len, tw->f);
      return (int) samples_written / tw->numChannels;
    }
    case TW_FLOAT32: {
      float *z = (float *) alloca(tw->numChannels*len*sizeof(float));
      switch (tw->chanFmt) {
        case TW_INTERLEAVED: {
          tw->totalFramesReadWritten += len;
          return (int) fwrite(f, sizeof(float), tw->numChannels*len, tw->f);
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

      tw->totalFramesReadWritten += len;
      size_t samples_written = fwrite(z, sizeof(float), tw->numChannels*len, tw->f);
      return (int) samples_written / tw->numChannels;
    }
    default: return 0;
  }
}

void tinywav_close_write(TinyWav *tw) {
  uint32_t data_len = tw->totalFramesReadWritten * tw->numChannels * tw->sampFmt;

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
