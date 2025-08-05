/// Author: aoqia <aoqia@aoqia.dev>

#pragma description ChromeEngine 6 RPACK
#pragma magic [ 52 50 36 4C ] @ 0x00
#pragma endian little

import std.core;
import std.mem;
import std.ptr;
import std.io;
import std.array;
import std.string;

import hex.core;

import type.magic;

namespace rpack {
    enum FileType : u8 {
        MSH = 16,
        TEX = 32,
        SHD = 48,
        ANM = 64,
        ANM2 = 66,
        FX = 80,
    };
    
    struct FileName : std::IIndexed {
        char name[while(std::mem::read_unsigned($, 1) != 0x00)] [[
            name(this.index)
        ]];
    } [[inline]];
    
    struct NameTablePtr {
        u32 offset;
    } [[inline]];
    
    struct NameTable : std::IIndexed {
        u32 offset = parent.nameTablePtrs[this.index].offset;
        rpack::FileName filename @ parent.nameTableStart + offset;
    } [[inline]];

    /// A map of file-specific data.
    struct Filemap {
        u8 partCount;
        u8 unk0 [[hidden]];
        rpack::FileType filetype;
        u8 unk1 [[hidden]];
        u32 fileIdx;
        /// The starting (index, address, offset?) of the first starting part.
        u32 firstPart;
    };

    /// Represents a part of an embedded file.
    struct Filepart {
        /// 0 to (header sectionCount - 1)
        u8 sectionIdx;
        u8 unk0 [[hidden]];
        u16 fileIdx;
        /// Relative to section offset.
        u32 offset;
        u32 unpackedSize;
        /// 0 means not packed.
        u32 packedSize;
    };

    struct Section {
       rpack::FileType filetype;
       u8 unk0 [[hidden]];
       u8 unk1 [[hidden]];
       u8 unk2 [[hidden]];
       /// From base address/SOF.
       u32 offset;
       /// Excluding 0x00.
       u32 unpackedSize;
       /// Excluding 0x00.
       u32 packedSize;
       u32 partCount;
    };
    
    /// Represents a collection of data adding up to a whole file.
    struct Subfile : std::IIndexed {
        u32 firstPart = parent.parent.maps[parent.index].firstPart;
        u8 sectionIdx = parent.parent.parts[firstPart].sectionIdx;
        u32 partOffset = parent.parent.parts[firstPart].offset;
        u32 unpackedSize = parent.parent.parts[firstPart].unpackedSize;
        u32 packedSize = parent.parent.parts[firstPart].packedSize;

        u8 sectionType = parent.parent.sections[sectionIdx].filetype;
        u32 sectionOffset = parent.parent.sections[sectionIdx].offset;
        
        if (sectionType == rpack::FileType::TEX) {
            // TODO: Handle texture-specific stuff here.
        } else {
            u8 filedata[packedSize > 0 ? packedSize : unpackedSize] @ sectionOffset + partOffset;
        }
    };
    
    /// Represents the data of a file.
    struct File : std::IIndexed {
        rpack::Subfile subfiles[1];
    } [[
        name(parent.nameTable[this.index].filename.name)
    ]];

    /// The main RPACK header.
    struct Header {
        type::Magic<"RP6L"> magic;
        u32 version;
        /// 0 = uncompressed, 1 = zlib, the rest unk.
        u32 compressionType;
        u32 partCount;
        u32 sectionCount;
        u32 fileCount;
        /// Size of the name table in bytes.
        u32 nameTableSize;
        /// Count of all the filename strings in the table.
        /// Mostly the same as fileCount.
        u32 nameTableCount;
        u32 blockSize;
    };
    
    /// A struct representing an entire RP6L RPACK file from 0x00.
    struct Rpack {
        rpack::Header header;
        rpack::Section sections[header.sectionCount];
        rpack::Filepart parts[header.partCount];
        rpack::Filemap maps[header.nameTableCount];
        rpack::NameTablePtr nameTablePtrs[header.nameTableCount];
        
        u32 nameTableStart = $;
        rpack::NameTable nameTable[header.nameTableCount];

        /// The files aren't continuous, they are fragmented.
        rpack::File files[header.fileCount];
    } [[
        name("RPACK"),
        comment("A Chromeengine 6 RPACK file that embeds files"
            + " in itself to get loaded virtually by the game."
            + "\n\nUsed by games such as:"
            + "\n  - Dead Island"
            + "\n  - Dead Island: Riptide"
            + "\n  - Dying Light")
    ]];
}

#ifndef RPACK_SUBPATTERN
rpack::Rpack rpack @ 0x00;
#endif