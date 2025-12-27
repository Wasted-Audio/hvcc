/**
 * Copyright (c) 2023 Wasted Audio
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

#include <math.h>
#include <string.h>
#include "HvSignalRFFT.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// A power-of-2 Cooley-Tukey FFT implementation.
// The data is arranged as an array of complex numbers: [re, im, re, im, ...]
static void cfft_inplace(float data[], const int n) {
  // n must be a power of 2
  const int num_points = n << 1;
  int j = 1;
  for (int i = 1; i < num_points; i += 2) {
    if (j > i) {
      // swap data[i-1] with data[j-1] and data[i] with data[j]
      float tempr = data[j-1];
      data[j-1] = data[i-1];
      data[i-1] = tempr;
      float tempi = data[j];
      data[j] = data[i];
      data[i] = tempi;
    }
    int m = n;
    while (m >= 2 && j > m) {
      j -= m;
      m >>= 1;
    }
    j += m;
  }

  int mmax = 2;
  while (num_points > mmax) {
    int istep = mmax << 1;
    float theta = -2.0f * (float) M_PI / mmax;
    float wpr = -2.0f * sinf(0.5f * theta) * sinf(0.5f * theta);
    float wpi = sinf(theta);
    float wr = 1.0f;
    float wi = 0.0f;
    for (int m = 1; m < mmax; m += 2) {
      for (int i = m; i <= num_points; i += istep) {
        j = i + mmax;
        float tempr = wr * data[j-1] - wi * data[j];
        float tempi = wr * data[j] + wi * data[j-1];
        data[j-1] = data[i-1] - tempr;
        data[j] = data[i] - tempi;
        data[i-1] += tempr;
        data[i] += tempi;
      }
      float wtemp = wr;
      wr = wr * wpr - wi * wpi + wr;
      wi = wi * wpr + wtemp * wpi + wi;
    }
    mmax = istep;
  }
}

// Perform a real FFT using a complex FFT of the same size.
static void rfft_forward(SignalRFFT *o, float *real_data) {
  const int n = hTable_getSize(&o->input);

  // Allocate buffer for complex data
  float *complex_data = (float *) hv_alloca(2 * n * sizeof(float));

  // Copy real data to complex buffer with imag part as 0
  for (int i = 0; i < n; i++) {
    complex_data[2*i] = real_data[i];
    complex_data[2*i+1] = 0.0f;
  }

  // Perform n-point complex FFT
  cfft_inplace(complex_data, n);

  // Copy first n/2+1 results to output tables
  float *out_real = hTable_getBuffer(&o->outputReal);
  float *out_imag = hTable_getBuffer(&o->outputImagin);
  for (int i = 0; i < n/2 + 1; i++) {
    out_real[i] = complex_data[2*i];
    out_imag[i] = complex_data[2*i+1];
  }
}

hv_size_t sRFFT_init(SignalRFFT *o, const int size) {
  o->pos = 0;
  o->read_pos = 0;
  hv_size_t numBytes = hTable_init(&o->input, size);
  numBytes += hTable_init(&o->outputReal, size/2+1);
  numBytes += hTable_init(&o->outputImagin, size/2+1);
  return numBytes;
}

void sRFFT_free(SignalRFFT *o) {
  hTable_free(&o->input);
  hTable_free(&o->outputReal);
  hTable_free(&o->outputImagin);
}

static void __hv_rfft_perform_fft(SignalRFFT *o) {
  const hv_size_t size = hTable_getSize(&o->input);
  const hv_size_t hopSize = size / 2;
  float *input_buffer = hTable_getBuffer(&o->input);

  // Perform RFFT on the raw, unwindowed data.
  // rfft_forward is non-destructive, so we can pass the buffer directly.
  rfft_forward(o, input_buffer);

  // Shift buffer for overlap
  memmove(input_buffer, input_buffer + hopSize, hopSize * sizeof(float));
  o->pos = hopSize;
}

void __hv_rfft_f(SignalRFFT *o, hv_bInf_t bIn, hv_bOutf_t bOut0, hv_bOutf_t bOut1) {
  const hv_size_t size = hTable_getSize(&o->input);
  const hv_size_t outSize = hTable_getSize(&o->outputReal);

  float *inputBuffer = hTable_getBuffer(&o->input);
  float *outReal = hTable_getBuffer(&o->outputReal);
  float *outImag = hTable_getBuffer(&o->outputImagin);

#if HV_SIMD_AVX
  hv_assert(0); // __hv_rfft_f() not implemented
#elif HV_SIMD_SSE
  hv_assert(0); // __hv_rfft_f() not implemented
#elif HV_SIMD_NEON
  hv_assert(0); // __hv_rfft_f() not implemented
#else // HV_SIMD_NONE
  inputBuffer[o->pos] = bIn;
  o->pos++;
  if (o->pos >= size) {
    __hv_rfft_perform_fft(o);
  }

  *bOut0 = outReal[o->read_pos];
  *bOut1 = outImag[o->read_pos];
  o->read_pos++;
  if (o->read_pos >= outSize) o->read_pos = 0;
#endif
}

void sRFFT_onMessage(HeavyContextInterface *_c, SignalRFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    default: return;
  }
}

static void cifft_inplace(float data[], const int n) {
  const int num_points = n << 1;
  int j = 1;
  for (int i = 1; i < num_points; i += 2) {
    if (j > i) {
      float tempr = data[j-1]; data[j-1] = data[i-1]; data[i-1] = tempr;
      float tempi = data[j]; data[j] = data[i]; data[i] = tempi;
    }
    int m = n;
    while (m >= 2 && j > m) { j -= m; m >>= 1; }
    j += m;
  }

  int mmax = 2;
  while (num_points > mmax) {
    int istep = mmax << 1;
    float theta = 2.0f * (float) M_PI / mmax; // sign change for inverse
    float wpr = -2.0f * sinf(0.5f * theta) * sinf(0.5f * theta);
    float wpi = sinf(theta);
    float wr = 1.0f;
    float wi = 0.0f;
    for (int m = 1; m < mmax; m += 2) {
      for (int i = m; i <= num_points; i += istep) {
        j = i + mmax;
        float tempr = wr * data[j-1] - wi * data[j];
        float tempi = wr * data[j] + wi * data[j-1];
        data[j-1] = data[i-1] - tempr;
        data[j] = data[i] - tempi;
        data[i-1] += tempr;
        data[i] += tempi;
      }
      float wtemp = wr;
      wr = wr * wpr - wi * wpi + wr;
      wi = wi * wpr + wtemp * wpi + wi;
    }
    mmax = istep;
  }
}

static void rifft_forward(SignalRIFFT *o) {
  const int n = hTable_getSize(&o->output);
  const int half_n = n/2;
  float *in_real = hTable_getBuffer(&o->inputReal);
  float *in_imag = hTable_getBuffer(&o->inputImagin);
  float *out_time = hTable_getBuffer(&o->output);

  // Allocate buffer for full complex spectrum
  float *complex_spectrum = (float *) hv_alloca(2 * n * sizeof(float));

  // Reconstruct full spectrum from half spectrum
  for (int i = 0; i <= half_n; ++i) {
    complex_spectrum[2*i] = in_real[i];
    complex_spectrum[2*i+1] = in_imag[i];
  }
  for (int i = 1; i < half_n; ++i) {
    complex_spectrum[2*(n-i)] = in_real[i];
    complex_spectrum[2*(n-i)+1] = -in_imag[i]; // Conjugate
  }

  // Perform IFFT
  cifft_inplace(complex_spectrum, n);

  // Copy real part to output table. No 1/N scaling to match Pd.
  for (int i=0; i<n; ++i) {
    out_time[i] = complex_spectrum[2*i];
  }
}

hv_size_t sRIFFT_init(SignalRIFFT *o, const int size) {
  o->pos = 0;
  o->read_pos = 0;
  hv_size_t numBytes = hTable_init(&o->inputReal, size/2+1);
  numBytes += hTable_init(&o->inputImagin, size/2+1);
  numBytes += hTable_init(&o->output, size);
  return numBytes;
}

void sRIFFT_free(SignalRIFFT *o) {
  hTable_free(&o->inputReal);
  hTable_free(&o->inputImagin);
  hTable_free(&o->output);
}

void __hv_rifft_f(SignalRIFFT *o, hv_bInf_t bIn0, hv_bInf_t bIn1, hv_bOutf_t bOut) {
  const hv_size_t size = hTable_getSize(&o->output);
  const hv_size_t inSize = hTable_getSize(&o->inputReal);

  float *inReal = hTable_getBuffer(&o->inputReal);
  float *inImag = hTable_getBuffer(&o->inputImagin);
  float *output = hTable_getBuffer(&o->output);

#if HV_SIMD_AVX
  hv_assert(0); // __hv_rifft_f() not implemented
#elif HV_SIMD_SSE
  hv_assert(0); // __hv_rifft_f() not implemented
#elif HV_SIMD_NEON
  hv_assert(0); // __hv_rifft_f() not implemented
#else // HV_SIMD_NONE
  // buffer input spectrum
  inReal[o->pos] = bIn0;
  inImag[o->pos] = bIn1;
  o->pos++;

  if (o->pos >= inSize) {
    rifft_forward(o);
    o->pos = 0;
  }

  // output time-domain signal
  *bOut = output[o->read_pos];
  o->read_pos++;
  if (o->read_pos >= size) {
    o->read_pos = 0;
  }
#endif
}

void sRIFFT_onMessage(HeavyContextInterface *_c, SignalRIFFT *o, int letIndex,
    const HvMessage *m, void *sendMessage) {
  switch (letIndex) {
    default: return;
  }
}
