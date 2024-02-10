/*
Copyright (c) 2015, Dimitri Diakopoulos All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef AUDIO_DECODER_H
#define AUDIO_DECODER_H

#include "Common.h"
#include <utility>
#include <map>
#include <memory>
#include <exception>

namespace nqr
{

struct UnsupportedExtensionEx : public std::runtime_error
{
    UnsupportedExtensionEx() : std::runtime_error("Unsupported file extension") {}
};

struct LoadPathNotImplEx : public std::runtime_error
{
    LoadPathNotImplEx() : std::runtime_error("Loading from path not implemented") {}
};

struct LoadBufferNotImplEx : public std::runtime_error
{
    LoadBufferNotImplEx() : std::runtime_error("Loading from buffer not implemented") {}
};

struct BaseDecoder
{
    virtual void LoadFromPath(nqr::AudioData * data, const std::string & path) = 0;
    virtual void LoadFromBuffer(nqr::AudioData * data, const std::vector<uint8_t> & memory) = 0;
    virtual std::vector<std::string> GetSupportedFileExtensions() = 0;
};

typedef std::pair<std::string, std::shared_ptr<nqr::BaseDecoder>> DecoderPair;

class NyquistIO
{
public:

    NyquistIO();
    ~NyquistIO();

    void Load(AudioData * data, const std::string & path);
    void Load(AudioData *data, std::string extension, const std::vector<uint8_t> & buffer);

    bool IsFileSupported(const std::string path) const;

private:

    std::string ParsePathForExtension(const std::string & path) const;

    std::shared_ptr<nqr::BaseDecoder> GetDecoderForExtension(const std::string ext);

    void BuildDecoderTable();

    void AddDecoderToTable(std::shared_ptr<nqr::BaseDecoder> decoder);

    std::map<std::string, std::shared_ptr<BaseDecoder>> decoderTable;

    NO_MOVE(NyquistIO);
};

} // end namespace nqr

#endif