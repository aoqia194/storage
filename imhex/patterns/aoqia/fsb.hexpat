/// Author: aoqia <aoqia@aoqia.dev>

#pragma description Fmod Sound Bank
#pragma magic [ 46 53 42 ?? ] @ 0x00
#pragma endian little

// Namespaces

namespace fsb {
    enum Mode : u32 {
        NONE,
        PCM8,
        PCM16,
        PCM24,
        PCM32,
        PCMFLOAT,
        GCADPCM,
        IMAADPCM,
        VAG,
        HEVAG,
        XMA,
        MPEG,
        CELT,
        AT9,
        XWMA,
        VORBIS,
    };
    
    struct Sample {
        u8 sampleHeader[parent.header.sampleHeadersSize];
        u8 sampleData[parent.header.sampleDataSize];
    };
    
    /// Assuming FSB5 here because the games I wrote this for
    ///   don't use any older version.
    struct Header {
        char id[4];
        s32 version;
        u32 sampleCount;
        u32 sampleHeadersSize;
        u32 nameTableSize;
        u32 sampleDataSize;
        Mode mode;
        u8 unk0[8] [[hidden]];
        u8 hash[16];
        u8 unk1[8] [[hidden]];

        if (version == 0) {
            u32 unk2;
        }
    };
    
    struct Fsb {
        Header header;
        Sample samples[header.sampleCount];
    };
}

#ifndef FSB_SUBPATTERN
fsb::Fsb fsb @ 0x00;
#endif