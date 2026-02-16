using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using System.Runtime.InteropServices;

namespace GoPro.Utils
{
	public class MiniDump
	{
		internal class Native
		{
			public enum MINIDUMP_STREAM_TYPE : uint
			{
				UnusedStream = 0u,
				ReservedStream0 = 1u,
				ReservedStream1 = 2u,
				ThreadListStream = 3u,
				ModuleListStream = 4u,
				MemoryListStream = 5u,
				ExceptionStream = 6u,
				SystemInfoStream = 7u,
				ThreadExListStream = 8u,
				Memory64ListStream = 9u,
				CommentStreamA = 10u,
				CommentStreamW = 11u,
				HandleDataStream = 12u,
				FunctionTableStream = 13u,
				UnloadedModuleListStream = 14u,
				MiscInfoStream = 15u,
				MemoryInfoListStream = 16u,
				ThreadInfoListStream = 17u,
				HandleOperationListStream = 18u,
				TokenStream = 19u,
				JavaScriptDataStream = 20u,
				SystemMemoryInfoStream = 21u,
				ProcessVmCountersStream = 22u,
				ThreadNamesStream = 24u,
				LastReservedStream = 65535u
			}

			public struct MINIDUMP_DIRECTORY
			{
				public MINIDUMP_STREAM_TYPE StreamType;

				public MINIDUMP_LOCATION_DESCRIPTOR Location;
			}

			public struct MINIDUMP_LOCATION_DESCRIPTOR
			{
				public uint DataSize;

				public uint Rva;
			}

			[StructLayout(LayoutKind.Sequential, Pack = 4)]
			public struct MINIDUMP_EXCEPTION_STREAM
			{
				public uint ThreadId;

				public uint __alignment;

				public MINIDUMP_EXCEPTION ExceptionRecord;

				public MINIDUMP_LOCATION_DESCRIPTOR ThreadContext;
			}

			[StructLayout(LayoutKind.Sequential, Pack = 4)]
			public struct MINIDUMP_EXCEPTION
			{
				public uint ExceptionCode;

				public uint ExceptionFlags;

				public ulong ExceptionRecord;

				public ulong ExceptionAddress;

				public uint NumberParameters;

				public uint __unusedAlignment;

				public ulong[] ExceptionInformation;
			}

			[StructLayout(LayoutKind.Sequential, Pack = 4)]
			public struct MINIDUMP_MODULE_LIST
			{
				public uint NumberOfModules;

				public IntPtr Modules;
			}

			[StructLayout(LayoutKind.Sequential, Pack = 4)]
			public struct MINIDUMP_MODULE
			{
				public ulong BaseOfImage;

				public uint SizeOfImage;

				public uint CheckSum;

				public uint TimeDateStamp;

				public uint ModuleNameRva;

				public VS_FIXEDFILEINFO VersionInfo;

				public MINIDUMP_LOCATION_DESCRIPTOR CvRecord;

				public MINIDUMP_LOCATION_DESCRIPTOR MiscRecord;

				public ulong Reserved0;

				public ulong Reserved1;
			}

			public struct VS_FIXEDFILEINFO
			{
				public uint dwSignature;

				public uint dwStrucVersion;

				public uint dwFileVersionMS;

				public uint dwFileVersionLS;

				public uint dwProductVersionMS;

				public uint dwProductVersionLS;

				public uint dwFileFlagsMask;

				public uint dwFileFlags;

				public uint dwFileOS;

				public uint dwFileType;

				public uint dwFileSubtype;

				public uint dwFileDateMS;

				public uint dwFileDateLS;
			}

			[StructLayout(LayoutKind.Sequential, Pack = 4)]
			public struct MINIDUMP_UNLOADED_MODULE_LIST
			{
				public uint SizeOfHeader;

				public uint SizeOfEntry;

				public uint NumberOfEntries;
			}

			[StructLayout(LayoutKind.Sequential, Pack = 4)]
			public struct MINIDUMP_UNLOADED_MODULE
			{
				public ulong BaseOfImage;

				public uint SizeOfImage;

				public uint CheckSum;

				public uint TimeDateStamp;

				public uint ModuleNameRva;
			}

			[DllImport("dbghelp.dll", SetLastError = true)]
			public static extern bool MiniDumpReadDumpStream(IntPtr BaseOfDump, MINIDUMP_STREAM_TYPE StreamNumber, ref MINIDUMP_DIRECTORY Dir, ref IntPtr StreamPointer, ref uint StreamSize);
		}

		private MemoryMappedFile mFile;

		private MemoryMappedViewStream mViewStream;

		public bool Open(string filepath)
		{
			if (mFile != null)
			{
				Close();
			}
			try
			{
				mFile = MemoryMappedFile.CreateFromFile(filepath);
				mViewStream = mFile.CreateViewStream();
			}
			catch (Exception)
			{
			}
			if (mFile != null)
			{
				return mViewStream != null;
			}
			return false;
		}

		public string GetLimitedStackTrace()
		{
			if (mViewStream == null)
			{
				return null;
			}
			IntPtr intPtr = mViewStream.SafeMemoryMappedViewHandle.DangerousGetHandle();
			Native.MINIDUMP_DIRECTORY Dir = default(Native.MINIDUMP_DIRECTORY);
			IntPtr StreamPointer = IntPtr.Zero;
			uint StreamSize = 0u;
			if (!Native.MiniDumpReadDumpStream(intPtr, Native.MINIDUMP_STREAM_TYPE.ExceptionStream, ref Dir, ref StreamPointer, ref StreamSize))
			{
				return null;
			}
			ulong num = (ulong)Marshal.ReadInt64(StreamPointer, 24);
			if (!Native.MiniDumpReadDumpStream(intPtr, Native.MINIDUMP_STREAM_TYPE.ModuleListStream, ref Dir, ref StreamPointer, ref StreamSize))
			{
				return null;
			}
			ulong num2 = 0uL;
			ulong num3 = 0uL;
			Native.MINIDUMP_MODULE_LIST mINIDUMP_MODULE_LIST = Marshal.PtrToStructure<Native.MINIDUMP_MODULE_LIST>(StreamPointer);
			for (int i = 0; i < mINIDUMP_MODULE_LIST.NumberOfModules; i++)
			{
				Native.MINIDUMP_MODULE mINIDUMP_MODULE = Marshal.PtrToStructure<Native.MINIDUMP_MODULE>(StreamPointer + 4 + i * Marshal.SizeOf<Native.MINIDUMP_MODULE>());
				if (num >= mINIDUMP_MODULE.BaseOfImage && num <= mINIDUMP_MODULE.BaseOfImage + mINIDUMP_MODULE.SizeOfImage)
				{
					num2 = mINIDUMP_MODULE.BaseOfImage;
					num3 = mINIDUMP_MODULE.ModuleNameRva;
					break;
				}
			}
			if ((num2 == 0L || num3 == 0L) && Native.MiniDumpReadDumpStream(intPtr, Native.MINIDUMP_STREAM_TYPE.UnloadedModuleListStream, ref Dir, ref StreamPointer, ref StreamSize))
			{
				Native.MINIDUMP_UNLOADED_MODULE_LIST mINIDUMP_UNLOADED_MODULE_LIST = Marshal.PtrToStructure<Native.MINIDUMP_UNLOADED_MODULE_LIST>(StreamPointer);
				for (int j = 0; j < mINIDUMP_UNLOADED_MODULE_LIST.NumberOfEntries; j++)
				{
					Native.MINIDUMP_UNLOADED_MODULE mINIDUMP_UNLOADED_MODULE = Marshal.PtrToStructure<Native.MINIDUMP_UNLOADED_MODULE>(StreamPointer + 4 + j * Marshal.SizeOf<Native.MINIDUMP_UNLOADED_MODULE>());
					if (num >= mINIDUMP_UNLOADED_MODULE.BaseOfImage && num <= mINIDUMP_UNLOADED_MODULE.BaseOfImage + mINIDUMP_UNLOADED_MODULE.SizeOfImage)
					{
						num2 = mINIDUMP_UNLOADED_MODULE.BaseOfImage;
						num3 = mINIDUMP_UNLOADED_MODULE.ModuleNameRva;
						break;
					}
				}
			}
			string result = "unknown";
			if (num2 != 0L && num3 != 0L)
			{
				int len = Marshal.ReadInt32(intPtr + (int)num3) / 2;
				string fileName = Path.GetFileName(Marshal.PtrToStringUni(intPtr + (int)num3 + 4, len));
				ulong num4 = num - num2;
				result = $"{fileName}:0x{num4:X}";
			}
			return result;
		}

		public void Close()
		{
			if (mViewStream != null)
			{
				mViewStream.Dispose();
				mViewStream = null;
			}
			if (mFile != null)
			{
				mFile.Dispose();
				mFile = null;
			}
		}
	}
}
