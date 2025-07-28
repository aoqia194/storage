/// Author: aoqia (she/her) <aoqia@aoqia.dev>

#pragma description Chromeengine Sound Bank
#pragma magic [ 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ] @ 0x00
#pragma endian little

#include "std/core"
#include "std/string"
#include "hex/core"

#define FSB_SUBPATTERN
#include "aoqia/fsb"

namespace csb {
    struct Vfsb : fsb::Fsb {} [[
        name(parent.vfsbHeaders[std::core::array_index()].filename)
    ]];

    /// A header that contains data about a linked embedded FSB file.
    struct VfsbHeader {
        char filename[64] [[
            name("File name"),
            comment("Name of the FSB file excluding the extension."
                + " The FSB nametable is stripped most times"
                + ", and this is where the name is actually stored.")
        ]];

        s32 offset [[
            name("vFSB offset"),
            comment("Offset in bytes to where the virtual FSB starts.")
        ]];

        s32 size [[
            name("vFSB size"),
            comment("Size of the virtual FSB in bytes.")
        ]];

        s32 [[hidden]];
        s32 [[hidden]];
        s32 [[hidden]];
        s32 [[hidden]];
    } [[
        name(filename)
    ]];
    
    /// The main CSB header that starts at +0x40 in all CSB files.
    struct Header {
        s32 size [[
            name("Header size"),
            comment("Size of this header itself in bytes.")
        ]];

        s32 vfsbCount [[
            name("vFSB count"),
            comment("Amount of virtual (embedded) FSB files in the file.")
        ]];

        s32 unk0 [[hidden]];
    };
    
    /// A struct representing an entire CSB file from 0x00.
    struct Csb {
        /// The first 64 bytes seem to always be 00.
        padding[64];
    
        Header header [[
            name("Header")
        ]];
    
        VfsbHeader vfsbHeaders[header.vfsbCount] [[
            name("vFSB headers"),
            comment("Headers with information about each virtual (embedded) FSB file."
                + " This is different from an actual FSB header!")
        ]];
        
        Vfsb vfsbFiles[header.vfsbCount] [[
            name("vFSB files"),
            comment("FSB files that are embedded in the CSB."
                + " These are just normal FSB5 files that can be extracted directly.")
        ]];
    } [[
        name("CSB"),
        comment("A Chromeengine Sound Bank file that embeds fmod FSB files"
            + " in itself to get loaded virtually by the game."
            + "\n\nUsed by games such as:"
            + "\n  - Dead Island"
            + "\n  - Dead Island: Riptide"
            + "\n  - Dying Light")
    ]];
}

#ifndef CSB_SUBPATTERN
csb::Csb csb @ 0x00;
#endif


// Add the embedded FSBs as virtual files.
for (u32 i = 0, i < csb.header.vfsbCount, i += 1) {
    hex::core::add_virtual_file(
        std::format("{}.fsb", csb.vfsbHeaders[i].filename),
        csb.vfsbFiles[i]);
}