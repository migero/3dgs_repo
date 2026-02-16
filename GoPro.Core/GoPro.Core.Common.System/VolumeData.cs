using System;
using common.system;
using std;

namespace GoPro.Core.Common.System
{
	public class VolumeData : EventArgs
	{
		private string _003Cbacking_store_003EDrivePath;

		private DriveType _003Cbacking_store_003EDriveKind;

		private string _003Cbacking_store_003EVolumeNumber;

		private string _003Cbacking_store_003EVolumeName;

		public string VolumeName
		{
			get
			{
				return _003Cbacking_store_003EVolumeName;
			}
			set
			{
				_003Cbacking_store_003EVolumeName = value;
			}
		}

		public string VolumeNumber
		{
			get
			{
				return _003Cbacking_store_003EVolumeNumber;
			}
			set
			{
				_003Cbacking_store_003EVolumeNumber = value;
			}
		}

		public DriveType DriveKind
		{
			get
			{
				return _003Cbacking_store_003EDriveKind;
			}
			set
			{
				_003Cbacking_store_003EDriveKind = value;
			}
		}

		public string DrivePath
		{
			get
			{
				return _003Cbacking_store_003EDrivePath;
			}
			set
			{
				_003Cbacking_store_003EDrivePath = value;
			}
		}

		public unsafe VolumeData(common.system.VolumeData* data)
		{
			//IL_0029: Expected I, but got I8
			//IL_0039: Expected I, but got I8
			DrivePath = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)data);
			DriveKind = *(DriveType*)((long)(IntPtr)data + 32);
			VolumeNumber = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)data + 40));
			VolumeName = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)data + 72));
			GC.KeepAlive(this);
		}

		public VolumeData()
		{
		}
	}
}
