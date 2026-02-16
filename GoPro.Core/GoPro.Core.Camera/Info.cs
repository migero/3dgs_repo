using System;
using System.Runtime.InteropServices;
using camera;
using std;

namespace GoPro.Core.Camera
{
	public class Info : EventArgs
	{
		private string _003Cbacking_store_003EFriendlyName;

		private string _003Cbacking_store_003EClientAddress;

		private string _003Cbacking_store_003EGatewayAddress;

		private string _003Cbacking_store_003EName;

		private string _003Cbacking_store_003EModel;

		private int _003Cbacking_store_003EModelNumber;

		private string _003Cbacking_store_003ESerialNumber;

		private string _003Cbacking_store_003ESdCardId;

		private SdCardStateType _003Cbacking_store_003ESdCardState;

		public bool VolumeAvailable
		{
			[return: MarshalAs(UnmanagedType.U1)]
			get
			{
				int num = ((SdCardState == SdCardStateType.NoWarning || SdCardState == SdCardStateType.CardInserted || SdCardState == SdCardStateType.CardFull) ? 1 : 0);
				return (byte)num != 0;
			}
		}

		public SdCardStateType SdCardState
		{
			get
			{
				return _003Cbacking_store_003ESdCardState;
			}
			set
			{
				_003Cbacking_store_003ESdCardState = value;
			}
		}

		public string SdCardId
		{
			get
			{
				return _003Cbacking_store_003ESdCardId;
			}
			set
			{
				_003Cbacking_store_003ESdCardId = value;
			}
		}

		public string SerialNumber
		{
			get
			{
				return _003Cbacking_store_003ESerialNumber;
			}
			set
			{
				_003Cbacking_store_003ESerialNumber = value;
			}
		}

		public int ModelNumber
		{
			get
			{
				return _003Cbacking_store_003EModelNumber;
			}
			set
			{
				_003Cbacking_store_003EModelNumber = value;
			}
		}

		public string Model
		{
			get
			{
				return _003Cbacking_store_003EModel;
			}
			set
			{
				_003Cbacking_store_003EModel = value;
			}
		}

		public string Name
		{
			get
			{
				return _003Cbacking_store_003EName;
			}
			set
			{
				_003Cbacking_store_003EName = value;
			}
		}

		public string GatewayAddress
		{
			get
			{
				return _003Cbacking_store_003EGatewayAddress;
			}
			set
			{
				_003Cbacking_store_003EGatewayAddress = value;
			}
		}

		public string ClientAddress
		{
			get
			{
				return _003Cbacking_store_003EClientAddress;
			}
			set
			{
				_003Cbacking_store_003EClientAddress = value;
			}
		}

		public string FriendlyName
		{
			get
			{
				return _003Cbacking_store_003EFriendlyName;
			}
			set
			{
				_003Cbacking_store_003EFriendlyName = value;
			}
		}

		public unsafe Info(Descriptor* cameraInfo)
		{
			//IL_001d: Expected I, but got I8
			//IL_002d: Expected I, but got I8
			//IL_003d: Expected I, but got I8
			//IL_0050: Expected I, but got I8
			//IL_0072: Expected I, but got I8
			//IL_0085: Expected I, but got I8
			FriendlyName = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)cameraInfo);
			ClientAddress = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)cameraInfo + 32));
			GatewayAddress = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)cameraInfo + 64));
			Name = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)cameraInfo + 96));
			Model = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)cameraInfo + 128));
			ModelNumber = *(int*)((long)(IntPtr)cameraInfo + 160);
			SerialNumber = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)cameraInfo + 168));
			SdCardId = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)cameraInfo + 200));
			SdCardState = *(SdCardStateType*)((long)(IntPtr)cameraInfo + 232);
		}

		public Info()
		{
		}
	}
}
